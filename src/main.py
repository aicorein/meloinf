import asyncio
import sys

if sys.platform != "win32":
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

from melobot import Bot
from melobot.log import Logger
from melobot.protocols.onebot.v11 import OneBotV11Protocol

from env import ENVS, get_onebot_io

bot = Bot(
    ENVS.bot.bot_name,
    logger=Logger(ENVS.bot.bot_name, level=ENVS.bot.log_level, to_dir="../logs", two_stream=True),
)
bot.add_protocol(OneBotV11Protocol(get_onebot_io()))
bot.load_plugins_dir("plugins", load_depth=3)
bot.run()
