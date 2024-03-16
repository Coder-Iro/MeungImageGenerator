from email.mime import image

from fastapi import FastAPI
from fastapi.responses import Response

from image_generator import generate_image

app: FastAPI = FastAPI()


@app.get("/{char}")
async def get_meung_image(char: str, color: str):

    rgb_color = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    generated_image = generate_image(char, rgb_color)

    return Response()
