import asyncio
import sys

if sys.platform != "win32":
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

sys.path.insert(0, r"E:/projects/Python/git-proj/melobot/src")
from melobot import Bot
from melobot.log import Logger, LogLevel
from melobot.protocols.onebot.v11 import OneBotV11Protocol

from env import get_onebot_io

bot = Bot("meloinf", logger=Logger("meloinf", level=LogLevel.DEBUG))
bot.add_protocol(OneBotV11Protocol(get_onebot_io()))
bot.load_plugins_dir("plugins", load_depth=3)
bot.run()
