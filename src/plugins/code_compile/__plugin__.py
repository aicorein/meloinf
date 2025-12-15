from typing import Annotated
from urllib.parse import quote

from melobot import PluginPlanner, send_text
from melobot.di import Reflect
from melobot.handle import get_event, stop
from melobot.log import logger
from melobot.protocols.onebot.v11 import (
    Adapter,
    MessageEvent,
    NodeGocqCustomSegment,
    TextSegment,
    on_message,
)
from melobot.session import suspend
from melobot.utils import if_, lock, timelimit
from melobot.utils.parse import get_cmd_arg as c_arg

from ...domain.onebot import COMMON_CHECKER, PARSER_FACTORY
from ...domain.onebot import CmdArgFmtter as Fmtter
from ...env import ENVS
from ...utils import async_http, get_headers

CodeCompile = PluginPlanner("1.3.0")


COMPILE_URL = "https://www.runoob.com/try/compile2.php"
COMPILE_TOKEN = "dadefd4c8adfb0e7d2221d31e1639f0c"
REQ_HEADERS = get_headers() | {"Content-Type": "application/x-www-form-urlencoded"}
COMPILE_CMD_PARSER = PARSER_FACTORY.get(
    targets=["code", "运行代码"],
    formatters=[
        Fmtter(
            convert=lambda x: x.lower() if x is not None else x,
            validate=lambda x: x in ["cpp", "cs", "py", "rs", None],
            src_desc="编程语言类型",
            src_expect="是以下值之一（兼容大小写）：[cpp, cs, py, rs]",
            default=None,
        )
    ],
)
CALC_CMD_PARSER = PARSER_FACTORY.get(targets=["calc", "计算"])


@timelimit(lambda: ("运行超时，任务已取消", None), timeout=10)
async def compile(code: str, lang_id: int, ext: str) -> tuple[str, Exception | None]:
    quoted_code = quote(code, safe=r"!*'()")
    data = f"code={quoted_code}&token={COMPILE_TOKEN}&language={lang_id}&fileext={ext}"

    async with async_http(COMPILE_URL, "post", headers=REQ_HEADERS, data=data) as resp:
        if resp.status != 200:
            logger.error(f"远端编译请求失败，状态码：{resp.status}")
            return "远端编译请求失败...\n请稍后再试，或联系 bot 管理员解决", None

        try:
            ret = await resp.json()
            if ret["errors"] != "\n\n":
                output = ret["errors"].strip("\n")
            else:
                output = ret["output"].strip("\n")
            return output, None

        except Exception as e:
            return "远端编译请求失败...\n请稍后再试，或联系 bot 管理员解决", e


@CodeCompile.use
async def calc_exp(expression: str) -> tuple[str, Exception | None]:
    code = f"print(eval('{expression}'))"
    return await compile(code, 15, "py3")


async def send_with_forward(adapter: Adapter, sender_id: int, input: str, output: str) -> None:
    output = output if len(output) <= 1000 else output[:1000] + "..."
    # print(output)
    await adapter.send_forward(
        [
            NodeGocqCustomSegment(sender_id, ENVS.bot.proj_name, [TextSegment(f"输入：\n{input}")]),
            NodeGocqCustomSegment(sender_id, ENVS.bot.proj_name, [TextSegment(output)]),
        ]
    )


@CodeCompile.use
@on_message(checker=COMMON_CHECKER, legacy_session=True)
@if_(lambda: COMPILE_CMD_PARSER.parse(get_event().text), reject=stop)
@lock(lambda: send_text("其他人正在调用 【代码运行】功能，稍后再试..."))
async def compile_code(adapter: Adapter, event: Annotated[MessageEvent, Reflect()]) -> None:
    args = await COMPILE_CMD_PARSER.parse(event.text)
    if args is None:
        return

    lang = args.vals[0]
    match lang:
        case None:
            await send_text("可以运行的语言类型：cpp, cs, py, rs")
            return
        case "cpp":
            lang_id, ext = 7, "cpp"
        case "cs":
            lang_id, ext = 10, "cs"
        case "py":
            lang_id, ext = 15, "py3"
        case "rs":
            lang_id, ext = 9, "rs"

    await send_text("输入代码开始运行")
    if not await suspend(timeout=10):
        await send_text("等待超时，已取消运行任务")
        return

    await send_text("正在运行中，请稍后...")
    output, exc = await compile(event.text, lang_id, ext)
    await send_with_forward(adapter, event.user_id, event.text, output)
    if exc:
        raise exc from None


@CodeCompile.use
@on_message(checker=COMMON_CHECKER, legacy_session=True)
@if_(lambda: CALC_CMD_PARSER.parse(get_event().text), reject=stop)
@lock(lambda: send_text("其他人正在调用【计算】功能，稍后再试..."))
async def calc(adapter: Adapter, event: Annotated[MessageEvent, Reflect()]) -> None:
    await send_text("输入表达式开始求值（遵循 py 语法）")
    if not await suspend(timeout=10):
        await send_text("等待超时，已取消求值任务")
        return
    if len(event.text) > 100:
        await send_text("表达式过长（长度 > 100），拒绝操作")
        return

    await send_text("计算中，请稍后...")
    output, exc = await calc_exp(event.text)
    await send_with_forward(adapter, event.user_id, event.text, output)
    if exc:
        raise exc from None
