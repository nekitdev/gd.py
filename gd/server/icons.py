from aiohttp.web import FileResponse, Request

from gd.enums import IconType
from gd.image.factory import FACTORY
from gd.image.icon import Icon
from gd.server.handler import request_handler
from gd.server.routes import get

ICONS = "/icons"


@get(ICONS, version=1)
@request_handler()
async def get_icons(request: Request) -> FileResponse:
    factory = FACTORY

    icons = []

    for name, value in request.query.items():
        try:
            type = IconType.from_name(name)
            id = int(value)

        except (KeyError, ValueError):
            pass

        else:
            icons.append(Icon(type, id))
