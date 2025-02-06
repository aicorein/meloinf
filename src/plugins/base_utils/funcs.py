import io

from PIL import Image, ImageDraw, ImageFont

from ...env import ENVS


def _txt2img(
    text: str,
    font_size: int = 18,
    bg_color: str = "white",
    color: str = "black",
    margin: tuple[int, int] = (10, 10),
    align: str = "left",
) -> Image.Image:
    font = ImageFont.truetype(ENVS.bot.txt2img_font, size=font_size)
    img = Image.new("RGB", (1000, 1000))
    draw = ImageDraw.Draw(img)
    left, top, right, bottom = draw.multiline_textbbox((0, 0), text, font)
    width, height = right - left, bottom - top
    if margin:
        width += 2 * margin[0]
        height += 2 * margin[1]
    img = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    draw_point = (0 + margin[0], 0 + margin[1]) if margin else (0, 0)
    draw.multiline_text(draw_point, text, font=font, fill=color, align=align)
    return img


def wrap_s(s: str, wrap_len: int) -> list[str]:
    return [s[i : i + wrap_len] for i in range(0, len(s), wrap_len)]


def txt2img(
    s: str,
    wrap_len: int = 70,
    font_size: int = 18,
    bg_color: str = "white",
    color: str = "black",
    margin: tuple[int, int] = (10, 10),
) -> bytes:
    lines = s.split("\n")
    for idx, l in enumerate(lines):
        if len(l) > wrap_len:
            lines[idx] = "\n".join(wrap_s(l, wrap_len))
    text = "\n".join(lines)
    img = _txt2img(text, font_size, bg_color, color, margin)
    imgio = io.BytesIO()
    img.save(imgio, format="JPEG", quality=95)
    return imgio.getvalue()


# def txt2msgs(s: str, one_msg_len: int = 300):
#     txt_list = list(map(lambda x: x.strip("\n"), wrap_s(s, one_msg_len)))
#     return [text_msg(txt) for txt in txt_list]
