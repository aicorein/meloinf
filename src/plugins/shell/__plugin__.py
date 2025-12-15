from typing import Annotated

from melobot import PluginPlanner, send_text
from melobot.bot import bot
from melobot.di import Depends, Reflect, inject_deps
from melobot.handle import get_event, stop
from melobot.log import logger
from melobot.protocols.onebot.v11 import Adapter, MessageEvent, on_message
from melobot.session import get_session_arg, get_session_store, suspend
from melobot.utils import if_

from ...domain.onebot import COMMON_CHECKER
from .store import Store
from .utils import close_ishell, ishell_run, open_ishell, shell_run

Shell = PluginPlanner(version="1.3.0")


@bot.on_started
async def open_shell_service(adapter: Adapter) -> None:
    await open_ishell(adapter)
    logger.info("ShellPlugin 服务已开启")


@bot.on_stopped
async def close_shell_service() -> None:
    await close_ishell()
    logger.info("ShellPlugin 服务已关闭")


@Shell.use
@on_message(checker=COMMON_CHECKER, legacy_session=True)
@if_(
    lambda: Store.shell_cmd_paser.parse(get_event().text),
    reject=stop,
    accept=lambda args: get_session_store().set("cmd_args", args) if args else None,
)
@if_(lambda: Store.shell_checker.check(get_event()), reject=stop)
@inject_deps
async def run_in_shell(
    event: Annotated[MessageEvent, Reflect()],
    cmd: Annotated[str | None, Depends(get_session_arg("cmd_args"), lambda args: args.vals[0])],
) -> None:
    if cmd is None:
        Store.pointer = (
            event.user_id,
            event.group_id if event.is_group() else None,
        )
        tip = (
            "已进入交互 shell。\n"
            + "使用 $\\n$ 发送一个回车\n"
            + "使用 $cc$ 结束其内部程序执行\n"
            + "使用 $e$ 退出交互状态"
        )
        await send_text(tip)

        while True:
            if not await suspend(timeout=30):
                await send_text("长时间无操作，已自动退出交互命令行")
                break
            await ishell_run(event.text)
        return

    output = await shell_run(cmd)
    await send_text(output)
