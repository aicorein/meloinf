import pathlib
import tomllib

dir_path = pathlib.Path(__file__).parent
env_path = dir_path.joinpath("env.toml")
with open(env_path, mode="rb") as fp:
    ALL_CONFIG = tomllib.load(fp)

BOT_CONFIG = ALL_CONFIG["bot"]
ONEBOT_CONFIG = ALL_CONFIG["onebot"]


def to_abs_path(path: str) -> str:
    _path = pathlib.Path(path)
    if pathlib.Path(_path).is_absolute():
        return str(_path)
    return str(dir_path.joinpath(_path).resolve(True))


class BotEnvs:
    def __init__(self) -> None:
        self.proj_name: str = BOT_CONFIG["bot_proj_name"]
        self.proj_ver: str = BOT_CONFIG["bot_proj_ver"]
        self.proj_src: str = BOT_CONFIG["bot_proj_src"]
        self.bot_name: str = BOT_CONFIG["bot_name"]
        self.bot_nicknames: list[str] = BOT_CONFIG["bot_nickname"]
        self.uni_cmd_start: str | list[str] = BOT_CONFIG["uni_cmd_start"]
        self.uni_cmd_sep: str | list[str] = BOT_CONFIG["uni_cmd_sep"]
        self.word_lib: str = to_abs_path(BOT_CONFIG["word_lib"])
        self.http_proxy: str = BOT_CONFIG["http_proxy"]
        self.figure_font: str = to_abs_path(BOT_CONFIG["figure_font"])
        self.weather_key: str = BOT_CONFIG["weather_key"]
        self.dice_config: str = to_abs_path(BOT_CONFIG["dice_config"])
        self.dice_data_dir: str = to_abs_path(BOT_CONFIG["dice_data_dir"])
        self.dice_base_r: tuple[int, int] = tuple(BOT_CONFIG["dice_base_r"])
        self.txt2img_font: str = to_abs_path(BOT_CONFIG["txt2img_font"])
        self.baidu_translate_appid: str = BOT_CONFIG["baidu_translate_appid"]
        self.baidu_translate_key: str = BOT_CONFIG["baidu_translate_key"]
        self.hash_salt: str = BOT_CONFIG["hash_salt"]
        self.news_time: str = BOT_CONFIG["everyday_news_time"]
        self.moonshot_key: str = BOT_CONFIG["moonshot_key"]


class OneBotEnvs:
    def __init__(self) -> None:
        self.access_token: str = ONEBOT_CONFIG["access_token"]
        self.forward_ws: str = ONEBOT_CONFIG["forward_ws"]
        self.owner_id: int = ONEBOT_CONFIG["owner_id"]
        self.owner_names: list[str] = ONEBOT_CONFIG["owner_names"]
        self.super_users: list[int] = ONEBOT_CONFIG["super_users"]
        self.white_users: list[int] = ONEBOT_CONFIG["white_users"]
        self.black_users: list[int] = ONEBOT_CONFIG["black_users"]
        self.white_groups: list[int] = ONEBOT_CONFIG["white_groups"]
        self.news_gruop: list[int] = ONEBOT_CONFIG["everyday_news_group"]


class Envs:
    def __init__(self) -> None:
        self.bot = BotEnvs()
        self.onebot = OneBotEnvs()


ENVS = Envs()
