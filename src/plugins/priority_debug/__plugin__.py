from functools import partial

from melobot import Bot, GenericLogger, PluginLifeSpan, PluginPlanner, send_text
from melobot.handle import Flow, get_event, stop
from melobot.protocols.onebot.v11 import EchoRequireCtx, MessageEvent, on_message
from melobot.session import Rule, Session, SessionStore, enter_session
from melobot.utils import if_not, unfold_ctx

from ...platform.onebot import PARSER_FACTORY, get_owner_checker

PriorityDebug = PluginPlanner("1.0.0")
OWNER_CHECKER = get_owner_checker()
when_message = partial(
    on_message,
    checker=OWNER_CHECKER,
    parser=PARSER_FACTORY.get("prior-dbg"),
    decos=[unfold_ctx(lambda: EchoRequireCtx().unfold(True))],
)


@PriorityDebug.on(PluginLifeSpan.INITED)
async def init_p(logger: GenericLogger) -> None:
    logger.info("已调用 PriorityDebug 插件的初始化函数")


def get_flow(priority: int) -> Flow:
    async def _dyn_created_flow() -> None:
        await (await send_text(f"priority {priority}"))[0]

    return when_message(priority=priority)(_dyn_created_flow)


@PriorityDebug.use
@when_message(priority=6)
async def flow_update1() -> None:
    await (await send_text("priority 6 [first]\npriority 0 [second]"))[0]
    flow_update1.update_priority(0)


@PriorityDebug.use
@when_message(priority=4)
async def flow_update3(bot: Bot) -> None:
    if flow_update3.priority == 4:
        await (
            await send_text(
                "priority 4 [first]\npriority 3 [second]\n"
                "[Fork: priority 7]\n[Fork: priority -4]\n[Fork priority: 1]"
            )
        )[0]
        bot.add_flows(get_flow(7), get_flow(-4), get_flow(1))
        flow_update3.update_priority(3)
    else:
        await (await send_text("priority 4 [first]\npriority 3 [second]"))[0]


@PriorityDebug.use
@when_message(priority=-2)
async def flow_update2() -> None:
    await (await send_text("priority -2 [first]\npriority 8[second]"))[0]
    flow_update2.update_priority(8)


@PriorityDebug.use
@when_message(temp=True)
async def temp_echo() -> None:
    await (await send_text("priority 0 [temp]"))[0]


PARSER = PARSER_FACTORY.get(
    "stest",
)

rule = Rule[MessageEvent].new(lambda e1, e2: e1.scope == e2.scope)


@PriorityDebug.use
@on_message(
    checker=OWNER_CHECKER,
    decos=[
        if_not(lambda: PARSER.parse(get_event().text), reject=stop),
        unfold_ctx(lambda: enter_session(rule, keep=True)),
    ],
)
async def session_test(session: Session, store: SessionStore) -> None:
    cnt = store.setdefault("cnt", 0)
    await send_text(f"{cnt}")
    if cnt == 3:
        session.stop_keep()
    else:
        store.set("cnt", cnt + 1)
