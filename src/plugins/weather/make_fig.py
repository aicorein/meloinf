import io
import os
from math import ceil, floor
from pathlib import Path
from random import choice
from typing import TYPE_CHECKING

from melobot import lazy_load
from melobot.utils import get_id, singleton

from ...env import ENVS
from ...utils import base64_encode

if TYPE_CHECKING:
    import matplotlib as mpl
    import matplotlib.font_manager as fm
    import PIL
    from matplotlib import pyplot as plt
else:
    _g = globals()
    lazy_load(_g, "matplotlib", alias="mpl")
    lazy_load(_g, "matplotlib.font_manager", alias="fm")
    lazy_load(_g, "PIL")
    lazy_load(_g, "matplotlib", item="pyplot", alias="plt")


CWD: str
BG_DIR: str
BG_IMAGES: list["PIL.Image.Image"] = []


@singleton
def mpl_pil_init() -> None:
    global CWD, BG_IMAGES, BG_DIR
    mpl.use("Agg")
    plt.ioff()
    fe = fm.FontEntry(fname=ENVS.bot.figure_font, name=ENVS.bot.figure_font.split("/")[-1])
    fm.fontManager.ttflist.insert(0, fe)
    mpl.rcParams["font.family"] = fe.name
    plt.rcParams["axes.unicode_minus"] = False
    CWD = str(Path(__file__).parent.resolve())
    BG_DIR = os.path.join(CWD, "bgs")
    for filename in os.listdir(BG_DIR):
        BG_IMAGES.append(PIL.Image.open(os.path.join(BG_DIR, filename)))


def get_ylim(base_v: int, steps: int, min_t: int, max_t: int) -> tuple[int, int]:
    fv = abs(min_t - base_v) / steps
    v = floor(fv)
    y_low = base_v + v * steps
    if fv == v:
        y_low -= steps
    fv = abs(max_t - base_v) / steps
    v = ceil(fv)
    y_up = base_v + v * steps
    if fv == v:
        y_up += steps
    return y_low, y_up


def gen_weather_fig(min_temps: list[int], max_temps: list[int]) -> str:
    mpl_pil_init()
    data_len = len(min_temps)
    fig_id = get_id()
    min_t, max_t = min(min_temps), max(max_temps)
    lower_v, upper_v, steps = -100, 100, 4
    day_s, day_e = 1, data_len
    fig = plt.figure(num=fig_id, figsize=(6.4, 5))
    figio = io.BytesIO()
    imgio = io.BytesIO()
    ax = fig.gca()

    ax.set_xticks(range(day_s, day_e + 1))
    ax.set_yticks(range(lower_v, upper_v + 1, 4))
    ax.set_ylim(get_ylim(lower_v, steps, min_t, max_t))
    ax.set_xlim(day_s - 0.5, day_e + 0.5)
    ax.set_xlabel("第 n 天（包含今天）")
    ax.set_ylabel("温度（°C）")
    ax.plot(range(1, data_len + 1), min_temps, marker="*", color="deepskyblue")
    ax.plot(range(1, data_len + 1), max_temps, marker="*", color="deeppink")
    ax.grid(True, axis="y", linestyle="--")
    fig.savefig(figio, dpi=150)
    fig.clf()

    im1 = PIL.Image.open(figio)
    im2 = choice(BG_IMAGES).convert("RGBA").crop((0, 0, 960, 750))
    im3 = PIL.Image.blend(im2, im1, 0.82)
    im3.convert("RGB").save(imgio, format="JPEG", quality=95)
    fig_b64 = base64_encode(imgio.getvalue())
    return fig_b64
