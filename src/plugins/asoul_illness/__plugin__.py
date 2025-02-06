import importlib.resources as impl_res
import json
from random import choice

from melobot import PluginPlanner, send_text
from melobot.protocols.onebot.v11 import on_message
from melobot.utils.parse import CmdArgs

from ...platform.onebot import COMMON_CHECKER, PARSER_FACTORY
from ...platform.onebot import CmdArgFmtter as Fmtter

AsoulIllness = PluginPlanner("1.0.0")
ILL_QUOTATIONS = json.loads(
    impl_res.files(__package__).joinpath("data.json").read_text(encoding="utf-8")
)


@AsoulIllness.use
@on_message(
    checker=COMMON_CHECKER,
    parser=PARSER_FACTORY.get(
        targets=["发病", "ill"],
        formatters=[
            Fmtter(
                validate=lambda x: len(x) <= 20,
                src_desc="发病对象",
                src_expect="字符数 <= 20",
            )
        ],
    ),
)
async def be_ill(args: CmdArgs) -> None:
    target = args.vals[0]
    text_pair = choice(ILL_QUOTATIONS)
    text, person = text_pair["text"], text_pair["person"]
    text = text.replace(person, target)
    await send_text(text)
