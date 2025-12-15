from typing import Annotated

from melobot import PluginPlanner, send_text
from melobot.di import Reflect
from melobot.protocols.onebot.v11 import Adapter, GroupMessageEvent, on_message
from melobot.session import suspend

from ...domain.onebot import COMMON_CHECKER, PARSER_FACTORY

GroupTitle = PluginPlanner("1.0.0")
parser = PARSER_FACTORY.get(["title", "头衔"])


@GroupTitle.use
@on_message(checker=COMMON_CHECKER, legacy_session=True)
async def title_manager(adapter: Adapter, event: Annotated[GroupMessageEvent, Reflect()]) -> None:
    args = await parser.parse(event.text)
    if args is None:
        return

    if len(args.vals) >= 1:
        title = args.vals[0]
    else:
        await send_text("请提供新的群头衔")
        if not await suspend(timeout=30):
            return await adapter.send_reply("操作超时，已取消")
        title = event.text

    if title.strip() == "":
        return await adapter.send_reply("群头衔值不能为空")
    await adapter.set_group_special_title(event.group_id, event.user_id, title=title)
