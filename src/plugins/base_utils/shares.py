import datetime as dt
import time

from melobot.plugin import SyncShare


class GetInterval:
    def __init__(self, start: float) -> None:
        self.start_moment = start

    def __get__(self, *_, **__) -> float:
        return time.time() - self.start_moment


class GetFormatInterval:
    def __init__(self, start: float) -> None:
        self.start_moment = start

    def __get__(self, *_, **__) -> str:
        def format_nums(*time_num: int) -> list[str]:
            return [str(num) if num >= 10 else "0" + str(num) for num in time_num]

        interval = int(time.time() - self.start_moment)
        days = interval // 3600 // 24
        hours = interval // 3600 % 24
        mins = interval // 60 % 60
        secs = interval % 60
        times = format_nums(days, hours, mins, secs)
        return f"{times[0]}d {times[1]}h {times[2]}m {times[3]}s"


class Store:
    bot_info: str = (
        "[Core]\n"
        "name：{}\n"
        "core：{} {}\n"
        "proj：{} {}\n"
        "src：{}\n"
        "python：{} | {}\n"
        "adapters：{}\n"
        "plugins：{}"
    )
    bot_status: str = (
        "[Status]\n"
        "start at: {}\n"
        "alive time: {}\n"
        "recv ob11 events: {}\n"
        "sent ob11 actions: {}"
    )

    onebot_recv_events: int = 0
    onebot_sent_actions: int = 0

    onebot_name: str = "<unkown>"
    onebot_id: int = -1
    onebot_app_name: str = "<unkown>"
    onebot_app_ver: str = "<unkown>"
    onebot_protocol_ver: str = "<unkown>"
    onebot_other_infos: dict[str, str] = {}
    onebot_info_str: str = (
        "[OneBot]\n" "app：{}\n" "ver：{}\n" "protocol_ver：{}\n" "other_info：{}"
    )

    start_moment: float = time.time()
    format_start_moment: str = dt.datetime.now().strftime("%m-%d %H:%M:%S")
    running_time: float = GetInterval(start_moment)
    format_running_time: str = GetFormatInterval(start_moment)


def add_share(name: str) -> SyncShare:
    return SyncShare(name, lambda: getattr(Store, name), static=True)


onebot_name: SyncShare[str] = add_share("onebot_name")
onebot_id: SyncShare[int] = add_share("onebot_id")
onebot_app_name: SyncShare[str] = add_share("onebot_app_name")
onebot_app_ver: SyncShare[str] = add_share("onebot_app_ver")
onebot_protocol_ver: SyncShare[str] = add_share("onebot_protocol_ver")
onebot_other_infos: SyncShare[dict[str, str]] = add_share("onebot_other_infos")
start_moment: SyncShare[float] = add_share("start_moment")
format_start_moment: SyncShare[str] = add_share("format_start_moment")
running_time: SyncShare[float] = add_share("running_time")
format_running_time: SyncShare[str] = add_share("format_running_time")
