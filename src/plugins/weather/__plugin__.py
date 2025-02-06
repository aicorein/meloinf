from contextlib import asynccontextmanager
from typing import AsyncGenerator

import aiohttp
from melobot import GenericLogger, PluginPlanner, get_bot, send_text
from melobot.protocols.onebot.v11 import Adapter, ImageSendSegment, on_message
from melobot.utils import lock, timelimit
from melobot.utils.parse import CmdArgs

from ...env import ENVS
from ...platform.onebot import COMMON_CHECKER, PARSER_FACTORY
from ...platform.onebot import CmdArgFmtter as Fmtter
from ...utils import async_http, get_headers
from .make_fig import gen_weather_fig

WeatherUtils = PluginPlanner("1.1.0")


API_KEY = ENVS.bot.weather_key
CITY_LOOKUP_URL = "https://geoapi.qweather.com/v2/city/lookup"
WEATHER_NOW_URL = "https://devapi.qweather.com/v7/weather/now"
WEATHER_7D_URL = "https://devapi.qweather.com/v7/weather/7d"


@asynccontextmanager
async def _send_req(url: str, city: str) -> AsyncGenerator[aiohttp.ClientResponse, None]:
    async with async_http(
        url,
        "get",
        headers=get_headers(),
        params={"location": city, "key": API_KEY},
    ) as resp:
        yield resp


@WeatherUtils.use
@on_message(
    checker=COMMON_CHECKER,
    parser=PARSER_FACTORY.get(
        targets=["天气", "weather"],
        formatters=[
            Fmtter(
                validate=lambda x: len(x) <= 10,
                src_desc="城市名",
                src_expect="字符数 <= 10",
            ),
            Fmtter(
                convert=int,
                validate=lambda x: 1 <= x <= 7,
                src_desc="需要预报的天数",
                src_expect="1<=天数<=7",
                default=3,
            ),
        ],
    ),
    decos=[
        lock(lambda: send_text("请等待前一个天气获取任务完成，稍后再试~")),
        timelimit(
            lambda: get_bot()
            .get_adapter(Adapter)
            .send_reply("天气信息获取超时，请稍候再试..."),
            timeout=25,
        ),
    ],
)
async def weather(adapter: Adapter, logger: GenericLogger, args: CmdArgs) -> None:
    city, days = args.vals
    textlines: list[str] = []
    min_temps: list[int] = []
    max_temps: list[int] = []

    async with _send_req(CITY_LOOKUP_URL, city) as resp:
        if resp.status != 200:
            logger.error(f"城市 id 查询请求失败：{resp.status}")
            await adapter.send_reply(
                "城市 id 查询失败...请稍后再试，或联系 bot 管理员解决"
            )
            return
        res = await resp.json()

    if res["code"] == "404" or "location" not in res:
        await send_text(f"检索不到城市 {city}，请检查输入哦~")
        return

    link = res["location"][0]["fxLink"]
    city_id = res["location"][0]["id"]

    async with _send_req(WEATHER_NOW_URL, city_id) as resp:
        if resp.status != 200:
            logger.error(f"城市当前天气获取请求失败：{resp.status}")
            await adapter.send_reply(
                "城市当前天气获取失败...请稍后再试，或联系 bot 管理员解决"
            )
            return
        res = await resp.json()

    textlines.append(f"{res['now']['text']} {res['now']['temp']} 度")

    async with _send_req(WEATHER_7D_URL, city_id) as resp:
        if resp.status != 200:
            logger.error(f"城市多天天气获取请求失败：{resp.status}")
            await adapter.send_reply(
                "城市多天天气获取失败...请稍后再试，或联系 bot 管理员解决"
            )
            return
        res = await resp.json()

    for data in res["daily"]:
        textlines.append(f" ● {data['textDay']} {data['tempMin']} ~ {data['tempMax']} 度")
        min_temps.append(int(data["tempMin"]))
        max_temps.append(int(data["tempMax"]))

    texts = "\n".join(textlines[1 : days + 1])
    output = (
        f"城市 {city}：\n"
        f"【今日天气】{textlines[0]}\n"
        f"【近 {days} 天天气（包括今天）】\n"
        f"{texts}\n【详细参见】{link}"
    )

    await send_text(output)
    fig_b64 = gen_weather_fig(min_temps[:days], max_temps[:days])
    handles = await adapter.with_echo(adapter.send)(ImageSendSegment(file=fig_b64))
    await handles[0]
