from melobot import PluginPlanner, send_text
from melobot.protocols.onebot.v11 import (
    Adapter,
    MessageEvent,
    NodeGocqCustomSegment,
    TextSegment,
    on_message,
)
from melobot.utils.parse import CmdArgs

from ...domain.onebot import COMMON_CHECKER, PARSER_FACTORY
from ...domain.onebot import CmdArgFmtter as Fmtter
from ...env import ENVS
from .decks import DeckStore, safe_r_gen

DECKS_MAP = {cmd: group for group in DeckStore.get_all().values() for cmd in group.cmds}

DiceSimulator = PluginPlanner("1.2.0")


@DiceSimulator.use
@on_message(
    checker=COMMON_CHECKER,
    parser=PARSER_FACTORY.get(
        targets=["r", "随机"],
        formatters=[
            Fmtter(
                validate=lambda x: len(x) <= 15,
                src_desc="掷骰表达式",
                src_expect="字符数 <= 15",
            )
        ],
    ),
)
async def roll(adapter: Adapter, args: CmdArgs) -> None:
    await adapter.send_reply(await safe_r_gen(args.vals[0]))


@DiceSimulator.use
@on_message(
    checker=COMMON_CHECKER,
    parser=PARSER_FACTORY.get(
        targets=["draw", "抽牌"],
        formatters=[
            Fmtter(
                src_desc="牌堆名",
                src_expect="若缺乏牌堆名参数，则显示当前可用牌堆",
                default=None,
            ),
            Fmtter(
                convert=int,
                validate=lambda x: 1 <= x <= 10,
                src_desc="抽牌次数",
                src_expect="1 <= 次数 <= 10",
                default=1,
            ),
        ],
    ),
)
async def draw_cards(adapter: Adapter, event: MessageEvent, args: CmdArgs) -> None:
    deck_name: str
    freq: int
    deck_name, freq = args.vals

    if deck_name is None:
        output = "当前可用牌堆：\n ● " + "\n ● ".join(DECKS_MAP.keys())
        output += "\n本功能牌堆来源于：\n ● dice 论坛\n ● Github: @Vescrity"
        await adapter.send_forward(
            [NodeGocqCustomSegment(event.user_id, ENVS.bot.proj_name, [TextSegment(output)])]
        )
        return

    if deck_name not in DECKS_MAP:
        await send_text(f"牌堆【{deck_name}】不存在")
        return

    deck_grp = DECKS_MAP[deck_name]
    samples = deck_grp.decks[deck_name].draw(sample_num=freq, replace=True)
    samples = list(map(lambda x: x.replace("\n\n", "\n").strip(), samples))
    if len(samples) <= 1:
        await adapter.send_reply(samples[0])
        return

    await adapter.send_forward(
        [
            NodeGocqCustomSegment(event.user_id, ENVS.bot.proj_name, [TextSegment(sample)])
            for sample in samples
        ]
    )


@DiceSimulator.use
@on_message(checker=COMMON_CHECKER, parser=PARSER_FACTORY.get(targets=["dice", "dice模拟器"]))
async def dice_info() -> None:
    output = "【dice 模拟器信息】\n ● 牌堆文件数：{}\n ● 牌堆总词条数：{}".format(
        len(DeckStore.get_all()), DeckStore.get_count()
    )
    await send_text(output)
