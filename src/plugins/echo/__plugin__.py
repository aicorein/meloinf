from melobot import PluginPlanner, send_text
from melobot.protocols.onebot.v11 import on_message
from melobot.utils.parse import CmdArgs

from ...domain.onebot import COMMON_CHECKER, PARSER_FACTORY

Echo = PluginPlanner("1.0.0", auto_import=True)


@Echo.use
@on_message(
    parser=PARSER_FACTORY.get(["echo", "print", "repost", "复读"]),
    checker=COMMON_CHECKER,
)
async def onebot_echo(args: CmdArgs) -> None:
    if len(args.vals):
        await send_text(args.vals[0])
