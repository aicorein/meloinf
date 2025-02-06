import re
from random import choice, random

from melobot import PluginPlanner, get_bot, send_text
from melobot.handle import get_event, stop
from melobot.protocols.onebot.v11 import Adapter, MessageEvent, on_message
from melobot.utils import if_not, lock
from melobot.utils.parse import CmdArgs, CmdParser

from ...env import ENVS
from ...platform.onebot import COMMON_CHECKER, PARSER_FACTORY
from ...platform.onebot import CmdArgFmtter as Fmtter
from ...platform.onebot import get_white_checker
from ...utils import ENG_PUNC, HANS_PUNC, remove_punctuation
from .. import base_utils as BASE_INFO
from .wdict import BOT_FLAG, OWNER_FLAG, SENDER_FLAG, WORD_DICT, add_pair

bot = get_bot()
OB_ADAPTER = bot.get_adapter(Adapter)
assert isinstance(OB_ADAPTER, Adapter)

SPECIAL_PROB = 0.001
BOT_NAME = ENVS.bot.bot_name
NICKNAMES = ENVS.bot.bot_nicknames
NICKNAME = NICKNAMES[-1]
OB_OWNER_NAME = ENVS.onebot.owner_names[0]
OB_OWNER_ID = ENVS.onebot.owner_id

TEACH_PARSER = CmdParser(
    cmd_start="*",
    cmd_sep="##",
    targets=["wlib-teach", "词条扩充"],
    fmtters=[
        Fmtter(
            validate=lambda x: len(x) <= 20 and "##" not in x,
            src_desc="触发语句",
            src_expect="字符数 <= 20 且不包含 ## 符号",
        ),
        Fmtter(
            validate=lambda x: len(x) <= 200 and "##" not in x,
            src_desc="回复语句",
            src_expect="字符数 <= 200 且不包含 ## 符号",
        ),
    ],
)
TEACH_CHECKER = get_white_checker(
    fail_cb=lambda: OB_ADAPTER.send_reply("你无权使用【词条扩充】功能")
)


WordLib = PluginPlanner("1.4.0")


@WordLib.use
@on_message(checker=COMMON_CHECKER)
async def make_reply(event: MessageEvent) -> None:
    text = event.text.replace("\n", "").strip(" ")
    text = remove_punctuation(text)
    text = re.sub(rf"({'|'.join(NICKNAMES)})", BOT_FLAG, text)

    keys: set[str] = set()
    for qid in event.get_datas("at", "qq"):
        if qid == BASE_INFO.onebot_id:
            keys.add(f"{BOT_FLAG}{text}")
            keys.add(f"{text}{BOT_FLAG}")
            break
    keys.add(text)

    output = get_random_reply(event, keys)
    if len(output):
        await send_text(output)


@WordLib.use
@on_message(checker=COMMON_CHECKER, parser=PARSER_FACTORY.get(["wlib-info", "词库信息"]))
async def get_wlib_info() -> None:
    await send_text(f"● 当前加载词库文件：words.txt\n● 词条数：{len(WORD_DICT)}")


@WordLib.use
@on_message(
    checker=COMMON_CHECKER,
    parser=TEACH_PARSER,
    decos=[
        if_not(lambda: TEACH_CHECKER.check(get_event()), reject=stop),
        lock(
            lambda: OB_ADAPTER.send_reply(
                f"{NICKNAME} 学不过来啦，等 {NICKNAME} 先学完上一句嘛~"
            )
        ),
    ],
)
async def wlib_teach(adapter: Adapter, args: CmdArgs) -> None:
    ask, ans = args.vals
    punc = ENG_PUNC.replace("$", "") + HANS_PUNC
    ask = re.sub(rf"[{re.escape(punc)}]", "", ask)
    res = add_pair(ask, ans)

    if res:
        await adapter.send_reply(f"{NICKNAME} 学会啦！")
    else:
        await adapter.send_reply(f"这个 {NICKNAME} 已经会了哦~")


def get_random_reply(event: MessageEvent, keys: list[str]) -> str:
    res: list[str] = []
    for k in keys:
        v = WORD_DICT.get(k)
        if v:
            res.extend(v)
    output = choice(res) if len(res) > 0 else ""

    if BOT_FLAG in output:
        output = output.replace(BOT_FLAG, NICKNAME)

    if SENDER_FLAG in output:
        if event.is_private():
            sender_name = event.sender.nickname
        else:
            sender_name = (
                event.sender.card
                if event.sender.card not in ("", None)
                else event.sender.nickname
            )
        output = output.replace(SENDER_FLAG, sender_name)

    if OWNER_FLAG in output:
        output = output.replace(OWNER_FLAG, OB_OWNER_NAME)

    if output != "":
        if random() < SPECIAL_PROB:
            output = "[恭喜你触发了千分之一概率的隐藏回复]"
    return output
