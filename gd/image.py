import io

from .typing import Sequence, ref

try:
    from PIL import Image
    from PIL.Image import Image as ImageType

except ImportError:
    ImageType = ref("PIL.Image.Image")
    print("Failed to load Pillow/PIL. Image creating will not be supported.")

DEFAULT_SIZE = 200


def to_image(data: bytes) -> ImageType:
    return Image.open(io.BytesIO(data))


def resize(image: ImageType, mode: str = "RGBA", size: int = DEFAULT_SIZE) -> ImageType:
    result = Image.new(mode=mode, size=(size, size))
    w, h = image.size
    # up-left corner
    x, y = size // 2 - w // 2, size // 2 - h // 2

    result.alpha_composite(image, (x, y))

    return result


def connect_images(images: Sequence[ImageType], mode: str = "RGBA") -> ImageType:
    all_x = [image.size[0] for image in images]  # x
    max_y = max(image.size[1] for image in images)  # y

    w, h = sum(all_x), max_y

    result = Image.new(mode=mode, size=(w, h))

    offset = 0

    for (to_add, image) in zip(all_x, images):
        result.paste(image, box=(offset, 0))  # box is upper-left corner
        offset += to_add

    return result


def to_bytes(image: ImageType, image_format: str = "png") -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, format=image_format)
    return buffer.getvalue()
