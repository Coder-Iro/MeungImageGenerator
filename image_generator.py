from PIL import Image, ImageDraw, ImageFont
from freetype import Face


def generate_image(char: str, color: tuple) -> bytes | None:
    font_path = "./assets/fonts/NanumGothicExtraBold.otf"

    font_face = Face(font_path)

    if font_face.get_char_index(char) == 0:
        print("The character does not exist in the font")
        return

    size = 512

    font = ImageFont.truetype(font_path, 350)

    image = Image.new("RGBA", (size,) * 2, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle(((0, 0), (size,) * 2), size // 8, color)

    bbox = font.getmask(char, anchor="lt").getbbox()
    offset = (size / 2) - (bbox[0] + bbox[2]) // 2, (size / 2) - (bbox[1] + bbox[3]) // 2

    luminosity = (0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]) / 255
    text_color = (0, 0, 0) if luminosity > 0.5 else (255, 255, 255)
    draw.text(offset, char, font=font, anchor="lt", fill=text_color)

    # 이 부분 지우고 필요한 코드 작성
    image.save("test.png")
