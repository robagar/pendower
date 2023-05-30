import numpy as np
from PIL import Image, ImageDraw, ImageColor


def draw_vertical_gradient_polygon(image, poly, bottom, top):
    color1 = ImageColor.getrgb(bottom)
    color2 = ImageColor.getrgb(top)

    gradient_1d = np.linspace(color1, color2, image.height, True).astype(np.uint8)
    gradient_2d = np.tile(gradient_1d, [image.width, 1, 1])
    gradient_2d = np.rot90(gradient_2d)
    
    gradient_image = Image.fromarray(gradient_2d)

    mask = Image.new('RGBA', image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(mask)
    draw.polygon(poly, fill=(0, 0, 0, 255), outline=None)

    image.paste(gradient_image, mask=mask)


if __name__ == '__main__':
    image = Image.new('RGB', (640, 400))

    poly = [(300, 100), (500, 300), (100, 300)]
    draw_vertical_gradient_polygon(image, poly, 'navy', 'aquamarine')

    image.show()
