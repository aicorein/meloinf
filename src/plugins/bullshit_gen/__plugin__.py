import math
import random
import string

from melobot import Plugin, send_text
from melobot.protocols.onebot.v11 import on_message
from melobot.protocols.onebot.v11.handle import GetParseArgs
from melobot.protocols.onebot.v11.utils import CmdArgFormatter as Fmtter
from melobot.protocols.onebot.v11.utils import ParseArgs

from ...platform.onebot import COMMON_CHECKER, PARSER_FACTORY
from .gen import BullShitGenerator


class BullShitGen(Plugin):
    def __init__(self) -> None:
        super().__init__()
        self.version = "1.1.0"
        self.flows = (bullshit_gen, error_codes)


GEN_LENGTH = 200
PUNC = string.punctuation + r"。，、；：？！…—·ˉ¨‘’“”々～‖∶＂＇｀〃．"


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
async def bullshit_gen(args: ParseArgs = GetParseArgs()) -> None:
    theme = args.vals[0]
    output = BullShitGenerator(theme, GEN_LENGTH).generate()
    await send_text(output)


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