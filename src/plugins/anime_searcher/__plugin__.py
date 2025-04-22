from typing import Annotated
from urllib.parse import quote

from melobot import PluginPlanner, send_text
from melobot.di import Reflect
from melobot.handle import get_event, stop
from melobot.protocols.onebot.v11 import (
    Adapter,
    MessageEvent,
    NodeGocqCustomSegment,
    TextSegment,
    on_message,
)
from melobot.session import suspend
from melobot.utils import cooldown, if_not

from ...domain.onebot import COMMON_CHECKER, PARSER_FACTORY
from ...env import ENVS
from ...utils import async_http, get_headers

AnimeSearcher = PluginPlanner("1.2.0")

ANIME_SEARCH_API = "https://api.trace.moe/search?anilistInfo&cutBorders&url="
ANIME_SEARCH_CMD_PARSER = PARSER_FACTORY.get(["番剧识别", "anime"])


@AnimeSearcher.use
@on_message(
    checker=COMMON_CHECKER,
    legacy_session=True,
    decos=[
        if_not(lambda: ANIME_SEARCH_CMD_PARSER.parse(get_event().text), reject=stop),
        cooldown(
            lambda: send_text("当前有一个识番任务运行中，稍候再试~"),
            lambda t: send_text(f"识番功能冷却中，剩余：{t:.2f}s"),
            interval=8,
        ),
    ],
)
async def anime_search(adapter: Adapter, event: Annotated[MessageEvent, Reflect()]) -> None:
    await send_text("发送番剧截图开始识别")

    if not await suspend(timeout=20):
        await send_text("等待发送图片超时，识番任务已取消")
        return

    urls: list[str] = list(map(str, event.get_datas("image", "url")))
    if len(urls) <= 0:
        await send_text("发送的消息中没有图片，识番任务结束")
        return

    req_url = ANIME_SEARCH_API + quote(urls[0])
    async with async_http(req_url, "get", headers=get_headers()) as resp:
        if resp.status != 200:
            await send_text(f"番剧识别 api 返回异常，状态码：{resp.status}")
            return
        res = await resp.json()

    textlines: list[str] = []
    for item in res["result"]:
        _from = round(item["from"])
        _to = round(item["to"])
        _from = f"{_from // 60}:{_from % 60}"
        _to = f"{_to // 60}:{_to % 60}"

        filename = item["filename"]
        sim = round(item["similarity"] * 100, 2)
        title = item["anilist"]["title"]["native"]

        textlines.append(
            f"【番名：{title}】\n"
            f"相似度：{sim}%\n"
            f"文件：{filename}\n"
            f"起始时间：{_from}~{_to}"
        )

    msg_nodes = list(
        map(
            lambda text: NodeGocqCustomSegment(
                uin=event.user_id, name=ENVS.bot.proj_name, content=[TextSegment(text)]
            ),
            textlines,
        )
    )
    await adapter.send_forward(msg_nodes)
