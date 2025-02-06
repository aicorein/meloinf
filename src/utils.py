import base64
import re
from contextlib import asynccontextmanager
from copy import deepcopy
from typing import AsyncGenerator, Literal, Optional

import aiohttp

from .env import ALL_CONFIG, ENVS

ENG_PUNC = r"""!"#$%&',.:;?@\^"""
WITHOUT_DOLLAR_ENG_PUNC = r"""!"#%&',.:;?@\^"""
HANS_PUNC = "。，、；：？！…—·ˉ¨‘’“”々～‖∶＂＇｀〃．"


def remove_punctuation(s: str) -> str:
    punc = ENG_PUNC + HANS_PUNC
    return re.sub(rf"[{re.escape(punc)}]", "", s)


def base64_encode(data: bytes) -> str:
    """
    返回 base64 编码的数据，携带 `base64://` 标志
    """
    code = "base64://"
    code += base64.b64encode(data).decode("utf-8")
    return code


def get_headers() -> dict:
    return deepcopy(ALL_CONFIG["http_headers"])


@asynccontextmanager
async def async_http(
    url: str,
    method: Literal["get", "post"],
    headers: Optional[dict] = None,
    params: Optional[dict] = None,
    data: Optional[dict] = None,
    json: Optional[dict] = None,
    proxy: bool = False,
    verify_ssl: bool = True,
) -> AsyncGenerator[aiohttp.ClientResponse, None]:
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(verify_ssl=verify_ssl), headers=headers
    ) as http_session:
        kwargs = {}
        if proxy:
            kwargs["proxy"] = ENVS.http_proxy
        if json:
            kwargs["json"] = json
        if params:
            kwargs["params"] = params
        if method == "get":
            async with http_session.get(url, **kwargs) as resp:
                yield resp
        else:
            async with http_session.post(url, data=data, **kwargs) as resp:
                yield resp
