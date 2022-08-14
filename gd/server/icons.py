from typing import List

from aiohttp.web import FileResponse, Request

from gd.async_utils import gather_iterable
from gd.colors import Color
from gd.enums import IconType
from gd.image.factory import FACTORY, connect_images
from gd.image.icon import Icon
from gd.server.assets import ASSETS, IMAGE_SUFFIX
from gd.server.handler import request_handler
from gd.server.routes import get
from gd.server.utils import parse_bool

ICONS = "/icons"
ICONS_NAME = "icons"

ICONS_PATH = ASSETS / ICONS_NAME

ICONS_PATH.mkdir(parents=True, exist_ok=True)

COLOR_1 = "color_1"
COLOR_2 = "color_2"

GLOW = "glow"

DEFAULT_COLOR_1 = Color.default_color_1().to_hex()
DEFAULT_COLOR_2 = Color.default_color_2().to_hex()

DEFAULT_GLOW = "false"


@get(ICONS, version=1)
@request_handler()
async def get_icons(request: Request) -> FileResponse:
    path = (ASSETS / ICONS_NAME / request.query_string).with_suffix(IMAGE_SUFFIX)

    if path.exists():
        return FileResponse(path)

    factory = FACTORY

    query = request.query

    icons: List[Icon] = []

    color_1_hex = query.get(COLOR_1, DEFAULT_COLOR_1)

    color_1 = Color.from_hex(color_1_hex)

    color_2_hex = query.get(COLOR_2, DEFAULT_COLOR_2)

    color_2 = Color.from_hex(color_2_hex)

    glow_string = query.get(GLOW, DEFAULT_GLOW)

    glow = parse_bool(glow_string)

    for name, value in query.items():
        try:
            type = IconType.from_name(name)
            id = int(value)

        except (KeyError, ValueError):
            pass

        else:
            icons.append(Icon(type, id, color_1, color_2, glow))

    images = await gather_iterable(factory.generate_async(icon) for icon in icons)

    image = connect_images(images)

    image.save(path)

    return FileResponse(path)
