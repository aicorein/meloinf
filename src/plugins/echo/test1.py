from typing import cast

from melobot import Flow
from melobot.adapter import Event, TextEvent
from melobot.di import inject_deps
from melobot.handle import nextn, node
from melobot.log import logger
from melobot.protocols.onebot.v11 import GroupMessageEvent, PrivateMessageEvent
from melobot.utils import RWContext, unfold_ctx
from melobot.utils.match import StartMatcher

from .__plugin__ import COMMON_CHECKER, Echo

f = Flow("test")
rw_ctx = RWContext(read_limit=2)
sm = StartMatcher(".cf")
Echo.use(f)


async def pre_guard(e: Event) -> bool:
    if not await COMMON_CHECKER.check(e):
        return False
    e = cast(TextEvent, e)
    if not await sm.match(e.text):
        return False
    return True


f.set_guard(pre_guard)


@f.start
@node
async def n1() -> None:
    logger.info("test start")


@f.after(n1)
@node
@unfold_ctx(rw_ctx.read)
@inject_deps
# 通过依赖注入区分调用结点
async def n2(e: PrivateMessageEvent) -> None:
    await nextn()


@f.after(n1)
@node
@unfold_ctx(rw_ctx.write)
@inject_deps
# 通过依赖注入区分调用结点
def n3(e: GroupMessageEvent) -> bool:
    # 阻止运行下一结点
    logger.info("test interrupted")
    return False


@node
def nx() -> None:
    logger.info("to nx")


@node
def ny() -> None:
    logger.info("to ny")


@f.fork(nx, ny)
@node
def nw() -> None:
    logger.info("to nw")


# 合并流
@f.merge(n2, n3)
@f.before(nw)
@node
def final_n() -> None:
    logger.info("test finished")
