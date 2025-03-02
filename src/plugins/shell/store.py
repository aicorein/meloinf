import asyncio
import os
import sys
from pathlib import Path

from melobot import get_bot
from melobot.protocols.onebot.v11 import Adapter

from ...platform.onebot import PARSER_FACTORY
from ...platform.onebot import CmdArgFmtter as Fmtter
from ...platform.onebot import get_owner_checker


class Store:
    cwd = str(Path(__file__).parent.resolve())
    shell: asyncio.subprocess.Process
    executable = "powershell" if sys.platform == "win32" else "sh"
    encoding = "utf-8" if sys.platform != "win32" else "gbk"
    line_sep = os.linesep
    pointer: tuple[int, int | None] | None = None
    tasks: list[asyncio.Task]
    stdin: asyncio.StreamWriter
    stdout: asyncio.StreamReader
    stderr: asyncio.StreamReader

    _buf: list[tuple[float, str]] = []
    _cache_time = 0.3

    shell_checker = get_owner_checker(
        fail_cb=lambda: get_bot().get_adapter(Adapter).send_reply("你无权使用【命令行】功能")
    )
    shell_cmd_paser = PARSER_FACTORY.get(
        targets="shell",
        formatters=[Fmtter(src_desc="命令内容", src_expect="字符串", default=None)],
    )
