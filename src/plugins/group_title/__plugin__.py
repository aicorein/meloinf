from melobot import PluginPlanner, send_text
from melobot.di import inject_deps
from melobot.handle import stop
from melobot.protocols.onebot.v11 import Adapter, GroupMessageEvent, on_message
from melobot.utils import RWContext
from melobot.utils.parse import CmdArgs, CmdParser

from ...platform.onebot import COMMON_CHECKER, get_owner_checker


class Store:
    flag = False
    flag_rw = RWContext()
    owner_checker = get_owner_checker()


GroupTitle = PluginPlanner("1.0.0")


@GroupTitle.use
@on_message(checker=COMMON_CHECKER, parser=CmdParser("!", "$", ["title", "头衔"]))
async def title_manager(
    adapter: Adapter, event: GroupMessageEvent, args: CmdArgs
) -> None:
    if len(args.vals) <= 0:
        return await send_text("不支持的群头衔功能指令")

    match args.vals[0]:
        case "set" | "设置":
            async with Store.flag_rw.read():
                if not Store.flag:
                    return await send_text("群头衔相关功能未被启用")

                gtitle = " ".join(args.vals[1:])
                if gtitle == "":
                    return await send_text("群头衔值不能为空")
                return await adapter.set_group_special_title(
                    event.group_id, event.user_id, title=gtitle
                )

        case "enable" | "启用" | "开启":
            await owner_check()  # pylint: disable=no-value-for-parameter
            async with Store.flag_rw.write():
                Store.flag = True
                return await send_text("群头衔相关功能已启用 ✅")

        case "disable" | "禁用" | "关闭" | "禁用":
            await owner_check()  # pylint: disable=no-value-for-parameter
            async with Store.flag_rw.write():
                Store.flag = False
                return await send_text("群头衔相关功能已禁用 ✅")

        case _:
            return await send_text("不支持的群头衔功能指令")


@inject_deps
async def owner_check(adapter: Adapter, event: GroupMessageEvent) -> None:
    if not await Store.owner_checker.check(event):
        await adapter.send_reply("无权执行此操作")
        await stop()
