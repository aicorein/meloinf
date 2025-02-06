import math
import random
import string

from melobot import PluginPlanner, send_text
from melobot.protocols.onebot.v11 import on_message
from melobot.utils.parse import CmdArgs

from ...platform.onebot import COMMON_CHECKER, PARSER_FACTORY
from ...platform.onebot import CmdArgFmtter as Fmtter
from .gen import BullShitGenerator

BullShitGen = PluginPlanner("1.1.0")


GEN_LENGTH = 200
PUNC = string.punctuation + r"。，、；：？！…—·ˉ¨‘’“”々～‖∶＂＇｀〃．"


@BullShitGen.use
@on_message(
    checker=COMMON_CHECKER,
    parser=PARSER_FACTORY.get(
        targets=["狗屁不通生成", "bullshit"],
        formatters=[
            Fmtter(
                validate=lambda x: len(x) <= 20,
                src_desc="文章主题",
                src_expect="字符数 <= 20",
            )
        ],
    ),
)
async def bullshit_gen(args: CmdArgs) -> None:
    theme = args.vals[0]
    output = BullShitGenerator(theme, GEN_LENGTH).generate()
    await send_text(output)


@BullShitGen.use
@on_message(
    checker=COMMON_CHECKER, parser=PARSER_FACTORY.get(targets=["乱码生成", "ecode"])
)
async def error_codes() -> None:
    _len = random.randint(50, 300)
    chars = [chr(random.randint(0x0021, 0x9FFF)) for i in range(_len)]
    chars.extend([random.choice(PUNC) for _ in range(math.ceil(_len / 5))])
    random.shuffle(chars)
    output = "".join(chars)[:_len]
    await send_text(output)
