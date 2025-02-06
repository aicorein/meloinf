import asyncio
import sys

if sys.platform != "win32":
    # pylint: disable=import-error
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

from melobot import Bot
from melobot.log import Logger, LogLevel
from melobot.protocols.onebot.v11 import ForwardWebSocketIO, OneBotV11Protocol

from env import ENVS

bot = Bot("meloinf", logger=Logger("meloinf", level=LogLevel.DEBUG))
bot.add_protocol(OneBotV11Protocol(ForwardWebSocketIO(ENVS.onebot.forward_ws)))
bot.load_plugins_dir("plugins", load_depth=3)
bot.run()
