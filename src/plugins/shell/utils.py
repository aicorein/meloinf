import asyncio as aio
import subprocess
import time

import psutil
from melobot import get_bot, send_text
from melobot.exceptions import BotException
from melobot.handle import stop
from melobot.protocols.onebot.v11 import Adapter, ImageSendSegment, Segment

from ...utils import base64_encode
from .. import base_utils
from .store import Store


class ShellPluginException(BotException): ...


async def shell_run(cmd: str) -> str:
    p = await aio.create_subprocess_shell(
        cmd, stderr=aio.subprocess.PIPE, stdout=aio.subprocess.PIPE, cwd=Store.cwd
    )
    out, err = await p.communicate()
    if err == b"":
        output = out.decode(encoding=Store.encoding).strip(Store.line_sep)
    else:
        output = err.decode(encoding=Store.encoding).strip(Store.line_sep)
    return output


async def open_ishell(adapter: Adapter) -> None:
    Store.shell = await aio.create_subprocess_exec(
        Store.executable,
        shell=False,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=Store.cwd,
    )
    if (
        Store.shell.stdout is None
        or Store.shell.stderr is None
        or Store.shell.stdin is None
    ):
        raise ShellPluginException("ShellPlugin 进程输入输出异常")
    Store.stdin = Store.shell.stdin
    Store.stdout = Store.shell.stdout
    Store.stderr = Store.shell.stderr
    Store.tasks = [
        aio.create_task(watch_output(Store.stdout)),
        aio.create_task(watch_output(Store.stderr)),
        aio.create_task(watch_buf(adapter)),
    ]


async def close_ishell() -> None:
    for t in Store.tasks:
        t.cancel()
    if Store.shell.returncode is None:
        Store.shell.terminate()
        await Store.shell.wait()


async def watch_output(stream: aio.StreamReader) -> None:
    try:
        while True:
            try:
                stream_bytes = await stream.readline()
                output = stream_bytes.decode(Store.encoding).rstrip(Store.line_sep)
                if not output:
                    await aio.sleep(0.1)
                    continue
                if Store.pointer:
                    Store._buf.append((time.perf_counter(), output))

            except Exception as e:
                get_bot().logger.warning(f"ShellPlugin 输出转发遇到问题，警告：{e}")
    except aio.CancelledError:
        pass
    except KeyboardInterrupt:
        pass


async def watch_buf(adapter: Adapter) -> None:
    try:
        while True:
            if len(Store._buf) == 0:
                pass
            elif abs(Store._buf[-1][0] - time.perf_counter()) <= Store._cache_time:
                pass
            else:
                s = "\n".join([t[1] for t in Store._buf])
                Store._buf.clear()
                if s == "":
                    continue
                if Store.pointer:
                    p = Store.pointer
                    msg: str | Segment
                    if len(s) > 200:
                        data = base_utils.txt2img(s)
                        b64_data = base64_encode(data)
                        msg = ImageSendSegment(file=b64_data)
                    else:
                        msg = s
                    await adapter.send_custom(msg, p[0], p[1])
            await aio.sleep(0.2)
    except aio.CancelledError:
        pass
    except Exception as e:
        get_bot().logger.error(f"ShellPlugin 缓存异常，错误：{e}")


def send_to_shell(s: str) -> None:
    Store.stdin.write(f"{s}\n".encode(Store.encoding))


async def ishell_run(text: str) -> None:
    match text:
        case "$cc$":
            kill_childs()
        case "$e$":
            Store.pointer = None
            await send_text("shell 交互模式已关闭")
            await stop()
        case "$\\n$":
            send_to_shell("\n")
        case "exit":
            await send_text("请使用 $e$ 退出，而不是 exit")
            await stop()
        case _:
            send_to_shell(text)


def kill_childs() -> None:
    p = psutil.Process(Store.shell.pid)
    children = p.children()
    for child in children:
        child.terminate()
