from io import BytesIO

from fastapi import FastAPI, Path, Query
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

    rgb_color = (*[int(x, 16) for x in (color[1:3], color[3:5], color[5:7])],)
    
    contrast = abs(calculate_contrast((0,0,0),rgb_color)), abs(calculate_contrast((255,255,255),rgb_color))

    text_color = "black" if contrast[0] > contrast[1] else "white"

    draw.text(offset, char, font=FONT, anchor="lt", fill=text_color)
    image_bytes = BytesIO()
    image.save(image_bytes, "png")
    return image_bytes

def srgb_to_y(srgb):
    """Converts sRGB color components to luminance (Y).

    Args:
        srgb: A tuple of (R, G, B) color components, each in the range 0-255.

    Returns:
        The luminance (Y) value.
    """
    r_linear = (srgb[0] / 255) ** 2.4
    g_linear = (srgb[1] / 255) ** 2.4
    b_linear = (srgb[2] / 255) ** 2.4

    y = 0.2126729 * r_linear + 0.7151522 * g_linear + 0.0721750 * b_linear

    if y < 0.022:
        y += (0.022 - y) ** 1.414  # Threshold adjustment

    return y

def calculate_contrast(foreground, background):
    """Calculates the contrast ratio between foreground and background colors.

    Args:
        foreground: A tuple of (R, G, B) color components, each in the range 0-255.
        background: A tuple of (R, G, B) color components, each in the range 0-255.

    Returns:
        The contrast ratio as a value between -100 and 100.
    """
    y_fg = srgb_to_y(foreground)
    y_bg = srgb_to_y(background)

    # Contrast calculation with adjustments
    c = 1.14

    if y_bg > y_fg:
        c *= y_bg ** 0.56 - y_fg ** 0.57
    else:
        c *= y_bg ** 0.65 - y_fg ** 0.62

    if abs(c) < 0.1:
        return 0
    else:
        if c > 0:
            c -= 0.027
        else:
            c += 0.027

    return c * 100