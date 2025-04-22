import hashlib
from typing import Annotated

from melobot import PluginPlanner, send_text
from melobot.di import Reflect
from melobot.handle import get_event, stop
from melobot.log import logger
from melobot.protocols.onebot.v11 import Adapter, MessageEvent, on_message
from melobot.session import SessionStore, get_session_store, suspend
from melobot.utils import cooldown, if_not

from ...domain.onebot import COMMON_CHECKER, PARSER_FACTORY
from ...domain.onebot import CmdArgFmtter as Fmtter
from ...env import ENVS
from ...utils import async_http, get_headers

Translator = PluginPlanner("1.0.0")

API_URL = "https://fanyi-api.baidu.com/api/trans/vip/translate"
API_APPID = ENVS.bot.baidu_translate_appid
API_HASH_SALT = ENVS.bot.hash_salt
API_KEY = ENVS.bot.baidu_translate_key

REQ_HEADERS = get_headers() | {"Content-Type": "application/x-www-form-urlencoded"}
TRANSLATE_CMD_PARSER = PARSER_FACTORY.get(
    targets=["translate", "trans", "翻译"],
    formatters=[
        Fmtter(
            validate=lambda x: x in ["en", "zh", "jp"],
            src_desc="翻译目标语种",
            src_expect="值为 [en, zh, jp] 其中之一",
            default="zh",
        ),
        Fmtter(
            validate=lambda x: len(x) <= 1000 if x is not None else True,
            src_desc="要翻译的文本",
            src_expect="字符数 <= 1000",
            default=None,
        ),
    ],
)


@Translator.use
@on_message(
    checker=COMMON_CHECKER,
    legacy_session=True,
    decos=[
        if_not(
            lambda: TRANSLATE_CMD_PARSER.parse(get_event().text),
            reject=stop,
            accept=lambda args: get_session_store().set("args", args) if args else None,
        ),
        cooldown(
            lambda: send_text("当前有一个翻译任务运行中，稍候再试~"),
            lambda t: send_text(f"翻译功能冷却中，剩余：{t:.2f}s"),
            interval=8,
        ),
    ],
)
async def translate_text(
    adapter: Adapter,
    store: SessionStore,
    event: Annotated[MessageEvent, Reflect()],
) -> None:
    lang, _text = store["args"].vals

    if _text is None:
        await send_text("输入要翻译的文本")
        if not await suspend(timeout=20):
            await send_text("等待超时，翻译任务已取消")
            return
        text = event.text
    else:
        text = _text

    sign = API_APPID + text + API_HASH_SALT + API_KEY
    md5 = hashlib.md5()
    md5.update(sign.encode("utf-8"))
    data = {
        "q": text,
        "from": "auto",
        "to": lang,
        "appid": API_APPID,
        "salt": API_HASH_SALT,
        "sign": md5.hexdigest(),
    }

    async with async_http(API_URL, "post", headers=REQ_HEADERS, data=data) as resp:
        if resp.status != 200:
            logger.error(f"翻译请求失败，状态码：{resp.status}")
            await send_text("翻译获取失败...请稍后再试，或联系 bot 管理员解决")
            return
        try:
            data = await resp.json()
        except Exception:
            await send_text("翻译获取失败...请稍后再试，或联系 bot 管理员解决")
            raise

    _from, to, translated = (
        data["from"],
        data["to"],
        "\n".join(res["dst"] for res in data["trans_result"]),
    )
    output = f"【模式 {_from} -> {to}】\n{translated}"
    await adapter.send_reply(output)
