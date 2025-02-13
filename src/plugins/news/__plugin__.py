import asyncio
import datetime

from melobot import GenericLogger, PluginPlanner, get_bot, send_text
from melobot.exceptions import BotException
from melobot.plugin import PluginLifeSpan
from melobot.protocols.onebot.v11 import Adapter, ImageSendSegment, on_message
from melobot.utils import async_at

from ...env import ENVS
from ...platform.onebot import COMMON_CHECKER, PARSER_FACTORY
from ...utils import async_http, base64_encode, get_headers

EveryDayNews = PluginPlanner("1.0.0")

bot = get_bot()

NEWS_API = "https://api.03c3.cn/api/zb?type=img"
NEWS_TIME = tuple(map(int, ENVS.bot.news_time.split(":")))
if len(NEWS_TIME) != 3:
    raise ValueError("每日新闻时间的配置，必须是完整的 <时:分:秒> 格式")
NEWS_GROUP = ENVS.onebot.news_gruop


class EveryDayNewsError(BotException): ...


async def get_news_image() -> str | None:
    async with async_http(NEWS_API, "get", headers=get_headers()) as resp:
        if resp.status != 200:
            get_bot().logger.error(f"每日新闻图片获取异常，状态码：{resp.status}")
            return None
        data = await resp.content.read()
        data = base64_encode(data)
        return data


class Store:
    news_cache: tuple[datetime.datetime, str] | None = None

    @classmethod
    async def fresh_news_cache(cls, logger: GenericLogger) -> None:
        cur_t = datetime.datetime.now()
        today = datetime.datetime(cur_t.year, cur_t.month, cur_t.day)
        if (
            Store.news_cache is None
            or today != Store.news_cache[0]
        ):
            data = await get_news_image()
            if data is None:
                logger.warning("每日新闻图片缓存异常，获取的图片为空")
                raise EveryDayNewsError("每日新闻图片缓存异常，获取的图片为空")
            cls.news_cache = (today, data)
            logger.info("每日新闻图片缓存已更新")

    @classmethod
    async def get_news_cache(cls, logger: GenericLogger) -> str:
        await Store.fresh_news_cache(logger)
        return Store.news_cache[1]


@EveryDayNews.on(PluginLifeSpan.INITED)
async def pinit(logger: GenericLogger) -> None:
    await Store.fresh_news_cache(logger)


@bot.on_started
async def news_arrange(adapter: Adapter, logger: GenericLogger) -> None:
    if len(NEWS_GROUP) == 0:
        return

    while True:
        cur_t = datetime.datetime.now()
        news_t = datetime.datetime(
            cur_t.year, cur_t.month, cur_t.day, NEWS_TIME[0], NEWS_TIME[1], NEWS_TIME[2]
        )

        if cur_t > news_t:
            news_t += datetime.timedelta(days=1)

        async def timed_send_news() -> None:
            data = await Store.get_news_cache(logger)
            for gid in NEWS_GROUP:
                await adapter.send_custom(ImageSendSegment(file=data), group_id=gid)

        try:
            logger.info(
                f"下次每日新闻发送时间：{news_t.strftime('%Y-%m-%d %H:%M:%S')}，定时任务已启动"
            )
            await async_at(timed_send_news(), news_t.timestamp())
            logger.info("每日新闻已发送")
        except asyncio.CancelledError:
            logger.info("每日新闻的定时任务已取消")
            # 特别注意这个 break，没有将会无法终止 bot 程序
            break


@EveryDayNews.use
@on_message(
    checker=COMMON_CHECKER, parser=PARSER_FACTORY.get(targets=["news", "每日新闻"])
)
async def manual_news(logger: GenericLogger) -> None:
    data = await Store.get_news_cache(logger)
    await send_text(ImageSendSegment(file=data))
