from melobot import Plugin, session
from melobot import send
from melobot import ArgFormatter as Format

from ..env import COMMON_CHECKER, PASER_GEN
from .gen import Generator


bullshit_gen = Plugin.on_message(checker=COMMON_CHECKER,
                                 parser=PASER_GEN.gen(["狗屁不通生成", "bullshit"],
                                                      formatters=[
                                                          Format(verify=lambda x: len(x) <= 15,
                                                                 src_desc="文章主题",
                                                                 src_expect="字符数 <= 15")
                                                      ]))


class BullshitGen(Plugin):
    def __init__(self) -> None:
        super().__init__()
        self.length = 200

    @bullshit_gen
    async def bullshit_gen(self) -> None:
        theme = session.args.vals.pop(0)
        output = Generator(theme, self.length).generate()
        await send(output)