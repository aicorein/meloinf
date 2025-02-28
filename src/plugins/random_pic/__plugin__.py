from random import choice

from melobot import GenericLogger, PluginPlanner, send_text
from melobot.protocols.onebot.v11 import Adapter, ImageSendSegment, on_message
from melobot.utils import cooldown, timelimit

from ...platform.onebot import COMMON_CHECKER, PARSER_FACTORY
from ...utils import async_http, base64_encode, get_headers

API_URLS = [
    "http://img.xjh.me/random_img.php?return=302",
    "https://www.loliapi.com/acg/",
    "http://api.anosu.top/img/",
    "https://iw233.cn/api.php?sort=cdniw",
]

# + [f"https://api.r10086.com/樱道随机图片api接口.php?图片系列=动漫综合{i}" for i in range(1, 18)]

RandomPic = PluginPlanner("1.2.0")


@RandomPic.use
@on_message(
    checker=COMMON_CHECKER,
    parser=PARSER_FACTORY.get(targets=["随机图", "pic"]),
    decos=[
        cooldown(
            lambda: send_text("已有随机图任务在运行，稍后再试~"),
            lambda t: send_text(f"随机图功能冷却中，剩余：{t:.2f}s"),
            interval=5,
        ),
        timelimit(lambda: send_text("随机图获取超时，请稍候再试..."), timeout=60),
    ],
)
async def random_picture(adapter: Adapter, logger: GenericLogger) -> None:
    url = choice(API_URLS)

    async with async_http(url, "get", headers=get_headers(), verify_ssl=False) as resp:
        if resp.status != 200:
            logger.error(f"请求失败：{resp.status}")
            await send_text("图片获取失败...请稍后再试=")
            return

        try:
            data = await resp.read()

        except Exception:
            await send_text("图片获取失败...请稍后再试")
            raise

    img_data = base64_encode(data)
    handles = await adapter.with_echo(adapter.send)(ImageSendSegment(file=img_data))
    await handles[0]
