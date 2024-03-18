from io import BytesIO

from fastapi import FastAPI, Path, Query
from fastapi.responses import Response
from freetype import Face
from PIL import Image, ImageDraw, ImageFont

SIZE = 512
FONT_PATH = "./assets/fonts/NanumGothicExtraBold.otf"
FONT_FACE = Face(FONT_PATH)
FONT = ImageFont.truetype(FONT_PATH, 350)

app: FastAPI = FastAPI()


@app.get("/{char}")
async def get_meung_image(
    char: str = Path(min_length=1, max_length=1),
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
    text_color = ["white", "black"][
        round((299 * rgb_color[0] + 587 * rgb_color[1] + 114 * rgb_color[2]) / 255000)
    ]
    draw.text(offset, char, font=FONT, anchor="lt", fill=text_color)
    image_bytes = BytesIO()
    image.save(image_bytes, "png")
    return image_bytes
