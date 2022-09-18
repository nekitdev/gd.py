from typing import Optional, TypeVar, Union

from fastapi.responses import FileResponse

from gd.async_utils import gather_iterable, run_blocking
from gd.color import Color
from gd.enums import IconType
from gd.image.factory import FACTORY, connect_images
from gd.image.icon import Icon
from gd.server.assets import ASSETS, IMAGE_SUFFIX
from gd.server.core import app
from gd.server.parse import parse_bool

__all__ = ()

GENERATE_ICONS = "/icons"
ICONS_NAME = "icons"

ICONS_PATH = ASSETS / ICONS_NAME

ICONS_PATH.mkdir(parents=True, exist_ok=True)

DEFAULT_COLOR_1 = Color.default_color_1().to_hex()
DEFAULT_COLOR_2 = Color.default_color_2().to_hex()

DEFAULT_GLOW = "false"

NULL = "null"

QUERY = """
{color_1}_{color_2}_{glow}_{cube_id}_{ship_id}_{ball_id}_{ufo_id}_{wave_id}_{robot_id}_{spider_id}
""".strip()


T = TypeVar("T")
U = TypeVar("U")


def switch_none(option: Optional[T], default: U) -> Union[T, U]:
    return default if option is None else option


@app.get(GENERATE_ICONS)
async def generate_icons(
    color_1: str = DEFAULT_COLOR_1,
    color_2: str = DEFAULT_COLOR_2,
    glow: str = DEFAULT_GLOW,
    cube_id: Optional[int] = None,
    ship_id: Optional[int] = None,
    ball_id: Optional[int] = None,
    ufo_id: Optional[int] = None,
    wave_id: Optional[int] = None,
    robot_id: Optional[int] = None,
    spider_id: Optional[int] = None,
    # swing_copter_id: Optional[int] = None,
) -> FileResponse:
    null = NULL

    query = QUERY.format(
        color_1=color_1,
        color_2=color_2,
        glow=glow,
        cube_id=switch_none(cube_id, null),
        ship_id=switch_none(ship_id, null),
        ball_id=switch_none(ball_id, null),
        ufo_id=switch_none(ufo_id, null),
        wave_id=switch_none(wave_id, null),
        robot_id=switch_none(robot_id, null),
        spider_id=switch_none(spider_id, null),
        # swing_copter_id=switch_none(swing_copter_id, null),
    )

    mapping = {
        IconType.CUBE: cube_id,
        IconType.SHIP: ship_id,
        IconType.BALL: ball_id,
        IconType.UFO: ufo_id,
        IconType.WAVE: wave_id,
        IconType.ROBOT: robot_id,
        IconType.SPIDER: spider_id,
        # IconType.SWING_COPTER: swing_copter_id,
    }

    icon_color_1 = Color.from_hex(color_1)
    icon_color_2 = Color.from_hex(color_2)

    icon_glow = parse_bool(glow)

    icons = []

    for icon_type, icon_id in mapping.items():
        if icon_id is not None:
            icons.append(Icon(icon_type, icon_id, icon_color_1, icon_color_2, icon_glow))

    path = (ASSETS / ICONS_NAME / query).with_suffix(IMAGE_SUFFIX)

    if path.exists():
        return FileResponse(path)

    factory = FACTORY

    images = await gather_iterable(factory.generate_async(icon) for icon in icons)

    image = await run_blocking(connect_images, images)

    await run_blocking(image.save, path)

    return FileResponse(path)
