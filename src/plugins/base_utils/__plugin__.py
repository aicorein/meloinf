import os
import pickle
import platform
import time
from dataclasses import dataclass
from pathlib import Path

from melobot import GenericLogger, MetaInfo, PluginPlanner, get_bot, send_text
from melobot.adapter import AdapterLifeSpan
from melobot.bot import CLI_RUNTIME
from melobot.protocols.onebot.v11 import (
    Adapter,
    EchoRequireCtx,
    GroupMessageEvent,
    GroupRole,
    LevelRole,
    MessageEvent,
    on_message,
)
from melobot.utils import unfold_ctx

from ...env import ENVS
from ...platform.onebot import COMMON_CHECKER, PARSER_FACTORY, get_owner_checker, get_role
from .funcs import txt2img, wrap_s
from .shares import (
    Store,
    format_running_time,
    format_start_moment,
    onebot_app_name,
    onebot_app_ver,
    onebot_id,
    onebot_name,
    onebot_other_infos,
    onebot_protocol_ver,
    running_time,
    start_moment,
)

BaseUtils = PluginPlanner(
    "1.3.0",
    shares=[
        onebot_app_name,
        onebot_app_ver,
        onebot_id,
        onebot_name,
        onebot_other_infos,
        onebot_protocol_ver,
        start_moment,
        format_start_moment,
        running_time,
        format_running_time,
    ],
    funcs=[txt2img, wrap_s],
)


bot = get_bot()
ob_adapter: Adapter = bot.get_adapter(Adapter)


@ob_adapter.on(AdapterLifeSpan.BEFORE_EVENT_HANDLE)
async def count_events(*_, **__) -> None:
    Store.onebot_recv_events += 1


@ob_adapter.on(AdapterLifeSpan.BEFORE_ACTION_EXEC)
async def count_actions(*_, **__) -> None:
    Store.onebot_sent_actions += 1


@bot.on_started
async def get_onebot_login_info(adapter: Adapter, logger: GenericLogger) -> None:
    with EchoRequireCtx().unfold(True):
        echo = await (await adapter.get_login_info())[0]
    data = echo.data
    if echo.is_ok():
        Store.onebot_name = data["nickname"]
        Store.onebot_id = data["user_id"]
        logger.info("成功获得 OneBot 账号信息并存储")
    else:
        logger.warning("获取 OneBot 账号信息失败")


@bot.on_started
async def get_onebot_app_info(adapter: Adapter, logger: GenericLogger) -> None:
    with EchoRequireCtx().unfold(True):
        echo = await (await adapter.get_version_info())[0]
    data = echo.data
    if echo.is_ok():
        Store.onebot_app_name = data.pop("app_name")
        Store.onebot_app_ver = data.pop("app_version")
        Store.onebot_protocol_ver = data.pop("protocol_version")
        Store.onebot_other_infos = data
        logger.info("成功获得 onebot 实现程序的信息并存储")
    else:
        logger.warning("获取 onebot 实现程序的信息失败")


@BaseUtils.use
@on_message(parser=PARSER_FACTORY.get(targets=["info", "信息"]), checker=COMMON_CHECKER)
async def reply_info() -> None:
    output = Store.bot_info.format(
        ENVS.bot.bot_name,
        MetaInfo.name,
        MetaInfo.ver,
        ENVS.bot.proj_name,
        ENVS.bot.proj_ver,
        ENVS.bot.proj_src.lstrip("https://"),
        platform.python_version(),
        platform.system(),
        f'[{", ".join(a.protocol for a in bot.get_adapters(lambda _: True))}]',
        f"{len(bot.get_plugins())}",
    )
    output2 = Store.onebot_info_str.format(
        Store.onebot_app_name,
        Store.onebot_app_ver,
        Store.onebot_protocol_ver,
        Store.onebot_other_infos,
    )
    await send_text("\n\n".join((output, output2)))


@BaseUtils.use
@on_message(checker=COMMON_CHECKER, parser=PARSER_FACTORY.get(targets=["status", "状态"]))
async def reply_status() -> None:
    output = Store.bot_status.format(
        Store.format_start_moment,
        Store.format_running_time,
        Store.onebot_recv_events,
        Store.onebot_sent_actions,
    )
    await send_text(output)


@BaseUtils.use
@on_message(checker=COMMON_CHECKER, parser=PARSER_FACTORY.get(targets=["auth", "权限"]))
async def check_auth(adapter: Adapter, event: MessageEvent) -> None:
    lvl_role, grp_role = get_role(event)
    strs = [
        ENVS.bot.bot_nicknames[0],
        lvl_role >= LevelRole.OWNER,
        lvl_role >= LevelRole.SU,
        lvl_role >= LevelRole.WHITE,
        lvl_role >= LevelRole.NORMAL,
    ]

    output1 = "当前对 {} 具有权限：\n ● owner：{}\n ● superuser：{}\n ● white_user：{}\n ● normal_user：{}"
    output1 = output1.format(*strs)

    if event.is_group():
        strs = [
            grp_role >= GroupRole.OWNER,
            grp_role >= GroupRole.ADMIN,
            grp_role >= GroupRole.MEMBER,
        ]
        output2 = "\n ● group_owner: {}\n ● group_admin: {}\n ● group_member: {}"
        output2 = output2.format(*strs)
        await adapter.send_reply(output1 + output2)
    else:
        await adapter.send_reply(output1)


@BaseUtils.use
@on_message(
    checker=get_owner_checker(),
    parser=PARSER_FACTORY.get(targets=["stop", "close", "关机"]),
    decos=[unfold_ctx(lambda: EchoRequireCtx().unfold(True))],
)
async def stop_bot() -> None:
    await (await send_text("下班啦~"))[0]
    await bot.close()


@dataclass
class RestartInfo:
    uid: int
    gid: int | None
    time: float


RESTART_FLAG_NAME = "re.flag"
RESTART_FLAG_PATH = str(Path(__file__).parent.joinpath(RESTART_FLAG_NAME).resolve())


@BaseUtils.use
@on_message(
    checker=get_owner_checker(),
    parser=PARSER_FACTORY.get(targets=["restart", "重启"]),
    decos=[unfold_ctx(lambda: EchoRequireCtx().unfold(True))],
)
async def restart_bot(event: MessageEvent) -> None:
    if CLI_RUNTIME not in os.environ:
        await send_text(
            "重启失败\n" "启用重启功能，需要用以下方式运行：\n" "python -m melobot run ..."
        )
        return

    await (await send_text("正在重启中..."))[0]
    info = RestartInfo(
        event.user_id,
        event.group_id if isinstance(event, GroupMessageEvent) else None,
        time.time_ns() / 1e9,
    )
    with open(RESTART_FLAG_PATH, "wb") as fp:
        pickle.dump(info, fp)
    await bot.restart()


@bot.on_started
async def restart_tip(adapter: Adapter) -> None:
    if not os.path.exists(RESTART_FLAG_PATH):
        return

    try:
        with open(RESTART_FLAG_PATH, "rb") as fp:
            info: RestartInfo = pickle.load(fp)

        interval = time.time_ns() / 1e9 - info.time
        text = f"重启完成，耗时 {interval:.3f} s"
        await adapter.send_custom(text, info.uid, info.gid)
    finally:
        os.remove(RESTART_FLAG_PATH)
