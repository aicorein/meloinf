import importlib
from typing import Annotated, Callable

import melobot
from melobot import PluginPlanner, get_bot, send_text
from melobot.di import Reflect
from melobot.handle import get_event, stop
from melobot.protocols.onebot.v11 import Adapter, ImageSegment, MessageEvent, on_message
from melobot.session import suspend
from melobot.utils import if_not

from ...platform.onebot import COMMON_CHECKER, PARSER_FACTORY, get_owner_checker
from ...utils import base64_encode
from .. import base_utils


class Store:
    checker = get_owner_checker(
        fail_cb=lambda: get_bot()
        .get_adapter(Adapter)
        .send_reply("你无权使用【核心调试】功能")
    )
    parser = PARSER_FACTORY.get(["核心调试", "core-dbg"])


CoreDbg = PluginPlanner("1.1.0")


async def format_send(send_func: Callable, s: str) -> None:
    if len(s) <= 300:
        await send_func(s)
    elif len(s) > 10000:
        await send_func("<返回结果长度大于 10000，请使用调试器>")
    else:
        data = base_utils.txt2img(s, wrap_len=70, font_size=16)
        data = base64_encode(data)
        await send_func(ImageSegment(file=data))


@CoreDbg.use
@on_message(
    checker=COMMON_CHECKER,
    legacy_session=True,
    decos=[
        if_not(lambda: Store.parser.parse(get_event().text), reject=stop),
        if_not(lambda: Store.checker.check(get_event()), reject=stop),
    ],
)
async def core_dbg(adapter: Adapter, ev: Annotated[MessageEvent, Reflect()]) -> None:
    await send_text(
        "【你已进入核心调试状态】\n" + "注意 ⚠️：错误操作可能导致崩溃，请谨慎操作！"
    )
    await send_text(
        "【输入求值表达式以查看值】\n"
        "例：bot.name\n"
        "输入 $e$ 退出调试\n"
        "输入 $i$ 导入一个模块\n"
        "输入 $m$ 修改当前查看的值"
    )

    pointer = None
    imports = {}
    var_map = {"bot": get_bot(), "melobot": melobot}

    while True:
        await suspend()

        match ev.text:
            case "$e$":
                await send_text("已退出核心调试状态")
                await stop()

            case "$i$":
                await send_text("【开始导入在调试时可用的模块】\n" + "$e$ 退出导入操作")
                await suspend()

                try:
                    text = ev.text
                    if text == "$e$":
                        await send_text("已退出导入操作")
                        continue

                    mod = importlib.import_module(text)
                    imports[text] = mod
                    var_map.update(imports)
                    await send_text(f"{text} 导入完成 ✅")

                except Exception as e:
                    await send_text(f"尝试导入模块时发生异常 ❌：{str(e)}")

            case "$m$":
                if pointer is None:
                    await send_text("修改指针为空，拒绝操作 ❌")
                    continue

                await send_text(
                    "【输入修改后的值：】\n"
                    "$e$ 退出修改操作\n"
                    f"当前指向对象：{pointer}"
                )
                await suspend()

                try:
                    text = ev.text
                    if text == "$e$":
                        await send_text("已退出修改操作")
                        continue

                    exec(f"{pointer}={text}", var_map)
                    val = eval(f"{pointer}", var_map)
                    await format_send(
                        send_text, f"修改后的值为：{val}\n" f"类型：{type(val)}"
                    )

                except Exception as e:
                    await send_text(f"尝试修改值并重新显示时发生异常 ❌：{str(e)}")

            case _:
                try:
                    text = ev.text
                    val = eval(f"{text}", var_map)
                    pointer = text
                    await format_send(adapter.send_reply, str(val))

                except Exception as e:
                    await send_text(f"获取值时出现异常 ❌：{str(e)}")
