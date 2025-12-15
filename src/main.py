from melobot import Bot
from melobot.log import Logger, set_module_logger
from melobot.protocols.onebot.v11 import OneBotV11Protocol
from uvloop import Loop

from env import ENVS, get_onebot_io

log_args = {
    "level": ENVS.bot.log_level,
    "to_dir": "../logs",
    "red_error": False,
    "legacy": False,
    "is_parallel": True,
}

set_module_logger("melobot", Logger("core", **log_args))
set_module_logger(
    "melobot.bot.dispatch", Logger("core.dispatch", **(log_args | {"to_console": False}))
)

bot = Bot(ENVS.bot.bot_name, logger=Logger(ENVS.bot.proj_name, **log_args))
bot.add_protocol(OneBotV11Protocol(get_onebot_io()))
bot.load_plugins_dir("plugins", load_depth=3)
bot.run(loop_factory=Loop)
