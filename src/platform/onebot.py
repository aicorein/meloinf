from melobot import send_text
from melobot.protocols.onebot.v11 import LevelRole
from melobot.protocols.onebot.v11.utils import (
    CmdParserFactory,
    FormatInfo,
    MsgCheckerFactory,
)
from melobot.typ import AsyncCallable

from ..env import ENVS

CHECKER_FACTORY = MsgCheckerFactory(
    owner=ENVS.onebot.owner_id,
    super_users=ENVS.onebot.super_users,
    white_users=ENVS.onebot.white_users,
    black_users=ENVS.onebot.black_users,
    white_groups=ENVS.onebot.white_groups,
)
PARSER_FACTORY = CmdParserFactory(ENVS.bot.uni_cmd_start, ENVS.bot.uni_cmd_sep)


def get_owner_checker(fail_cb: AsyncCallable[[], None] | None = None):
    """
    获得一个 owner 级别的权限检查器
    """
    wc = CHECKER_FACTORY.get_group(LevelRole.OWNER) | CHECKER_FACTORY.get_private(
        LevelRole.OWNER
    )
    wc.set_fail_cb(fail_cb)
    return wc


def get_su_checker(fail_cb: AsyncCallable[[], None] | None = None):
    """
    获得一个 superuser 级别的权限检查器
    """
    wc = CHECKER_FACTORY.get_group(LevelRole.SU) | CHECKER_FACTORY.get_private(
        LevelRole.SU
    )
    wc.set_fail_cb(fail_cb)
    return wc


def get_white_checker(fail_cb: AsyncCallable[[], None] | None = None):
    """
    获得一个 white_user 级别的权限检查器
    """
    wc = CHECKER_FACTORY.get_group(LevelRole.WHITE) | CHECKER_FACTORY.get_private(
        LevelRole.WHITE
    )
    wc.set_fail_cb(fail_cb)
    return wc


COMMON_CHECKER = CHECKER_FACTORY.get_group(
    role=LevelRole.NORMAL
) | CHECKER_FACTORY.get_private(LevelRole.NORMAL)


class FormatCb:
    @staticmethod
    async def convert_fail(info: FormatInfo) -> None:
        e_class = info.exc.__class__.__qualname__
        src = repr(info.src) if isinstance(info.src, str) else info.src

        tip = f"第 {info.idx + 1} 个参数"
        tip += (
            f"（{info.src_desc}）无法处理，给定的值为：{src}。"
            if info.src_desc
            else f"给定的值 {src} 无法处理。"
        )

        tip += f"参数要求：{info.src_expect}。" if info.src_expect else ""
        tip += f"\n详细错误描述：[{e_class}] {info.exc}"
        tip = f"命令 {info.name} 参数格式化失败：\n{tip}"
        await send_text(tip)

    @staticmethod
    async def validate_fail(info: FormatInfo) -> None:
        src = repr(info.src) if isinstance(info.src, str) else info.src

        tip = f"第 {info.idx + 1} 个参数"
        tip += (
            f"（{info.src_desc}）不符合要求，给定的值为：{src}。"
            if info.src_desc
            else f"给定的值 {src} 不符合要求。"
        )

        tip += f"参数要求：{info.src_expect}。" if info.src_expect else ""
        tip = f"命令 {info.name} 参数格式化失败：\n{tip}"
        await send_text(tip)

    @staticmethod
    async def arg_lack(info: FormatInfo) -> None:
        tip = f"第 {info.idx + 1} 个参数"
        tip += f"（{info.src_desc}）缺失。" if info.src_desc else "缺失。"
        tip += f"参数要求：{info.src_expect}。" if info.src_expect else ""
        tip = f"命令 {info.name} 参数格式化失败：\n{tip}"
        await send_text(tip)