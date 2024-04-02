from io import BytesIO
from typing import cast

from fastapi import FastAPI, Query
from fastapi.responses import Response
from freetype import Face
from PIL import Image, ImageDraw, ImageFont

SIZE = 128
FONT_PATH = "./assets/fonts/NanumGothicExtraBold.otf"
FONT_FACE = Face(FONT_PATH)
FONT = ImageFont.truetype(FONT_PATH, 85)

app: FastAPI = FastAPI()


@app.get("/")
async def get_meung_image(
    char: str = Query(min_length=1, max_length=1),
    color: str = Query(pattern=r"[0-9a-fA-F]{6}"),
):
    if image := generate_image(char, color):
        return Response(image.getvalue(), media_type="image/png")
    else:
        return Response(status_code=404)


def generate_image(char: str, color: str):

    if FONT_FACE.get_char_index(char) == 0:
        print("The character does not exist in the font")
        return

    image = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle(((0, 0), (SIZE, SIZE)), SIZE // 8, color)

    bbox = FONT.getmask(char, anchor="lt").getbbox()
    offset = (SIZE // 2) - (bbox[0] + bbox[2]) // 2, (SIZE // 2) - (
        bbox[1] + bbox[3]
    ) // 2

    rgb_color = cast(tuple[int, int, int], (*[int(x, 16) for x in (color[1:3], color[3:5], color[5:7])],))

    contrast = abs(calculate_contrast((0, 0, 0), rgb_color)), abs(calculate_contrast((255, 255, 255), rgb_color))

    text_color = "black" if contrast[0] > contrast[1] else "white"

    draw.text(offset, char, font=FONT, anchor="lt", fill=text_color)
    image_bytes = BytesIO()
    image.save(image_bytes, "png")
    return image_bytes


# calculate contrast

B_EXP = 1.414
B_THRESH = 0.022

P_IN = 0.0005
P_OUT = 0.1

R_SCALE = 1.14
W_OFFSET = 0.027


def srgb_to_y(srgb: tuple[int, int, int]) -> float:
    linear_srgb = map(lambda x: (x / 255) ** 2.4, srgb)
    return sum(map(lambda x, y: x * y, linear_srgb, [0.2126729, 0.7151522, 0.0721750]))


# soft clamp black levels
def f_clamp(y_c: float) -> float:
    if y_c >= B_THRESH:
        return y_c
    else:
        return y_c + (B_THRESH - y_c) ** B_EXP


def calculate_contrast(srgb_txt: tuple[int, int, int], srgb_bg: tuple[int, int, int]) -> float:
    y_txt = f_clamp(srgb_to_y(srgb_txt))
    y_bg = f_clamp(srgb_to_y(srgb_bg))

    c = 0.0

    # clamp noise then scale
    if abs(y_bg - y_txt) < P_IN:
        c = 0.0
    elif y_txt < y_bg:
        s_norm = y_bg ** 0.56 - y_txt ** 0.57
        c = s_norm * R_SCALE
    elif y_txt > y_bg:
        s_rev = y_bg ** 0.65 - y_txt ** 0.62
        c = s_rev * R_SCALE

    s_apc = 0.0

    # clamp minimum contrast then offset
    if abs(c) < P_OUT:
        s_apc = 0.0
    elif c > 0:
        s_apc = c - W_OFFSET
    elif c < 0:
        s_apc = c + W_OFFSET

    return s_apc * 100
