# TODO: consider rewriting several aspects like offset calculation.
# Other than that, I feel that things are generally fine here.
# Perhaps we should not generate all icon names automatically like it is done now;
# Instead, we could create different functions for each icon type, and work in them.

import io
from pathlib import Path

try:
    import PIL.Image  # type: ignore
    import PIL.ImageOps  # type: ignore

except ImportError:
    pass

from gd.async_utils import run_blocking
from gd.color import COLOR_1, COLOR_2, Color
from gd.decorators import cache_by
from gd.enums import IconType
from gd.image.sheet import DEFAULT_IMAGE_SUFFIX, DEFAULT_PLIST_SUFFIX, Sheet
from gd.image.sprite import Sprite
from gd.logging import get_logger
from gd.typing import (
    Dict,
    Iterator,
    List,
    MutableMapping,
    Optional,
    Protocol,
    Sequence,
    Tuple,
    TypeVar,
    Union,
    cast,
)

__all__ = (
    "IconFactory",
    "connect_images",
    "factory",
    "generate_icon_names",
    "get_icon_name",
    "to_bytes",
)


class ToString(Protocol):
    def __str__(self) -> str:
        ...

    def __format__(self, format_spec: str) -> str:
        ...


KT = TypeVar("KT")
VT = TypeVar("VT")

ASSETS = Path(__file__).parent.parent / "assets"

BLACK = Color(0x000000)
DARK = Color(0x808080)
WHITE = Color(0xFFFFFF)

COPY_SUFFIX = "_copy"

DEFAULT_FORMAT = "png"
DEFAULT_TRAIL = "001"

DEFAULT_WIDTH = 250
DEFAULT_HEIGHT = 250

EMPTY = Color(0x000000).to_rgba(0)

RGBA = "RGBA"

TWO = "_2_"
THREE = "_3_"
GLOW = "_glow_"
EXTRA = "_extra_"
ZERO_TWO = "02"
ZERO_THREE = "03"
ZERO_FOUR = "04"

ROBOT = "robot"
SPIDER = "spider"

log = get_logger(__name__)

icon_type_names = {
    IconType.CUBE: "player",
    IconType.SHIP: "ship",
    IconType.BALL: "player_ball",
    IconType.UFO: "bird",
    IconType.WAVE: "dart",
    IconType.ROBOT: "robot",
    IconType.SPIDER: "spider",
}


def get_icon_name(
    icon_type: IconType,
    icon_id: int,
    *extras: ToString,
    trail: Optional[ToString] = DEFAULT_TRAIL,
    format: str = DEFAULT_FORMAT,
    copy_level: int = 0,
) -> str:
    icon_type_name = icon_type_names.get(icon_type)  # type: ignore

    if icon_type_name is None:
        raise LookupError(f"Can not find icon type name for {icon_type}.")

    if trail is None:
        if extras:
            extra = "_".join(map(str, extras))
            name = f"{icon_type_name}_{icon_id:02}_{extra}.{format}"

        else:
            name = f"{icon_type_name}_{icon_id:02}.{format}"

    else:
        if extras:
            extra = "_".join(map(str, extras))
            name = f"{icon_type_name}_{icon_id:02}_{extra}_{trail}.{format}"

        else:
            name = f"{icon_type_name}_{icon_id:02}_{trail}.{format}"

    if copy_level:
        return name + COPY_SUFFIX * copy_level

    return name


def get_icon_name_prefix(icon_type: IconType, icon_id: int, *extras: ToString) -> str:
    icon_type_name = icon_type_names.get(icon_type)  # type: ignore

    if icon_type_name is None:
        raise LookupError(f"Can not find icon type name for {icon_type}.")

    if extras:
        extra = "_".join(map(str, extras))
        return f"{icon_type_name}_{icon_id:02}_{extra}_"

    return f"{icon_type_name}_{icon_id:02}_"


def generate_icon_names(
    icon_type: IconType,
    icon_id: int,
    trail: Optional[ToString] = DEFAULT_TRAIL,
    format: str = DEFAULT_FORMAT,
) -> Iterator[str]:
    for extras, copy_level in ICON_EXTRAS.get(icon_type, ()):
        yield get_icon_name(  # type: ignore
            icon_type, icon_id, *extras, trail=trail, format=format, copy_level=copy_level
        )


def mapping_union(*mappings: MutableMapping[KT, VT], **keywords: VT) -> Dict[KT, VT]:
    result: Dict[KT, VT] = {}

    for mapping in mappings:
        result.update(mapping)

    result.update(cast(MutableMapping[KT, VT], keywords))

    return result


def apply_color(image: "PIL.Image.Image", color: Tuple[int, int, int]) -> "PIL.Image.Image":
    alpha = image.split()[3]  # [r, g, b, a][3] -> a

    colored = PIL.ImageOps.colorize(
        PIL.ImageOps.grayscale(image), black=BLACK.to_rgb(), white=color
    )
    colored.putalpha(alpha)

    return colored


def reduce_brightness(image: "PIL.Image.Image") -> "PIL.Image.Image":
    return apply_color(image, DARK.to_rgb())


def connect_images(images: Sequence["PIL.Image.Image"], mode: str = "RGBA") -> "PIL.Image.Image":
    all_x = [image.size[0] for image in images]  # x
    max_y = max(image.size[1] for image in images)  # y

    width, height = sum(all_x), max_y

    result = PIL.Image.new(mode=mode, size=(width, height))

    offset = 0

    for (to_add, image) in zip(all_x, images):
        result.paste(image, (offset, 0))  # box is upper-left corner
        offset += to_add

    return result


def to_bytes(image: "PIL.Image.Image", image_format: str = "png") -> bytes:
    file = io.BytesIO()
    image.save(file, format=image_format)
    return file.getvalue()


class IconFactory:
    def __init__(self, icon_sheet: Sheet, glow_sheet: Sheet) -> None:
        self.icon_sheet = icon_sheet
        self.glow_sheet = glow_sheet

    @property  # type: ignore
    @cache_by(
        "icon_sheet.image_path",
        "icon_sheet.plist_path",
        "glow_sheet.image_path",
        "glow_sheet.plist_path",
        "icon_sheet.loaded",
        "glow_sheet.loaded",
    )
    def sprites(self) -> Dict[str, Sprite]:
        self.assure_loaded()

        return mapping_union(self.icon_sheet.sprites, self.glow_sheet.sprites)

    def assure_loaded(self) -> None:
        self.icon_sheet.assure_loaded()
        self.glow_sheet.assure_loaded()

    def get_sprites(self, icon_type: IconType, icon_id: int) -> List[Sprite]:
        prefix = get_icon_name_prefix(icon_type, icon_id)

        sprites = [sprite for name, sprite in self.sprites.items() if name.startswith(prefix)]

        robot_prefixes = tuple(
            get_icon_name_prefix(IconType.ROBOT, icon_id, extra)  # type: ignore
            for extra in (ZERO_TWO, ZERO_THREE, ZERO_FOUR)
        )

        spider_prefix = get_icon_name_prefix(IconType.SPIDER, icon_id, ZERO_TWO)  # type: ignore

        for sprite in sprites.copy():
            if sprite.name.startswith(robot_prefixes):
                sprites.append(sprite.copy())

            elif sprite.name.startswith(spider_prefix):
                copy = sprite.copy()
                sprites.append(copy)
                sprites.append(copy.copy())

        icon_name_to_index = {
            name: index for index, name in enumerate(generate_icon_names(icon_type, icon_id))
        }

        sprites.sort(key=lambda sprite: icon_name_to_index[sprite.name_with_copy])

        return sprites

    async def generate_async(
        self,
        icon_type: Union[int, str, IconType] = IconType.CUBE,
        icon_id: int = 1,
        color_1: Color = COLOR_1,
        color_2: Color = COLOR_2,
        extra_color: Optional[Color] = None,
        glow_color: Optional[Color] = None,
        glow_outline: bool = False,
        image_width: int = DEFAULT_WIDTH,
        image_height: int = DEFAULT_HEIGHT,
        error_on_not_found: bool = False,
    ) -> "PIL.Image.Image":
        return await run_blocking(
            self.generate,
            icon_type=icon_type,
            icon_id=icon_id,
            color_1=color_1,
            color_2=color_2,
            extra_color=extra_color,
            glow_color=glow_color,
            glow_outline=glow_outline,
            image_width=image_width,
            image_height=image_height,
        )

    def generate(
        self,
        icon_type: Union[int, str, IconType] = IconType.CUBE,
        icon_id: int = 1,
        color_1: Color = COLOR_1,
        color_2: Color = COLOR_2,
        extra_color: Optional[Color] = None,
        glow_color: Optional[Color] = None,
        glow_outline: bool = False,
        image_width: int = DEFAULT_WIDTH,
        image_height: int = DEFAULT_HEIGHT,
        error_on_not_found: bool = False,
    ) -> "PIL.Image.Image":
        self.assure_loaded()

        result = PIL.Image.new(RGBA, (image_width, image_height), EMPTY)

        real_icon_type = IconType.from_value(icon_type)

        sprites = self.get_sprites(real_icon_type, icon_id)

        if not glow_outline:
            sprites = [sprite for sprite in sprites if GLOW not in sprite.name]

        if not sprites:
            if error_on_not_found:
                raise LookupError(
                    f"Can not find sprites for {real_icon_type.title} with ID {icon_id}."
                )

            else:
                return self.generate(
                    icon_type=icon_type,
                    icon_id=1,
                    color_1=color_1,
                    color_2=color_2,
                    extra_color=extra_color,
                    glow_color=glow_color,
                    glow_outline=glow_outline,
                    image_width=image_width,
                    image_height=image_height,
                    error_on_not_found=True,
                )

        if glow_color is None:
            if color_1 == BLACK:
                glow_color = WHITE

            else:
                glow_color = color_2

        if extra_color is None:
            extra_color = WHITE

        image_center_x, image_center_y = image_width / 2, image_height / 2

        for sprite in sprites:
            name = sprite.name
            copy_level = sprite.copy_level

            center_x, center_y = (sprite.size / 2).as_tuple()
            offset_x, offset_y = sprite.relative_offset.as_tuple()

            image = sprite.get_image()

            if copy_level and GLOW not in name:
                image = reduce_brightness(image)

            if GLOW in name:
                image = apply_color(image, glow_color.to_rgb())

            elif TWO in name:
                image = apply_color(image, color_2.to_rgb())

            elif EXTRA in name:
                image = apply_color(image, extra_color.to_rgb())

            elif THREE not in name:
                image = apply_color(image, color_1.to_rgb())

            image, offset_x, offset_y = get_image_and_offset(
                name, icon_id, offset_x, offset_y, copy_level, image
            )

            draw_offset_x, draw_offset_y = DRAW_OFFSETS.get(real_icon_type, (0, 0))

            draw_x = image_center_x - center_x + offset_x + draw_offset_x
            draw_y = image_center_y - center_y - offset_y + draw_offset_y

            result.alpha_composite(image, (int(draw_x), int(draw_y)))

        return result

    @classmethod
    def from_paths(
        cls,
        icon_path: Union[str, Path],
        glow_path: Union[str, Path],
        image_suffix: str = DEFAULT_IMAGE_SUFFIX,
        plist_suffix: str = DEFAULT_PLIST_SUFFIX,
        load: bool = True,
    ) -> "IconFactory":
        return cls(
            Sheet.from_path(
                icon_path, image_suffix=image_suffix, plist_suffix=plist_suffix, load=load
            ),
            Sheet.from_path(
                glow_path, image_suffix=image_suffix, plist_suffix=plist_suffix, load=load
            ),
        )

    @classmethod
    def default(cls, load: bool = True) -> "IconFactory":
        return cls.from_paths(ASSETS / "icon_sheet", ASSETS / "glow_sheet", load=load)


DRAW_OFFSETS = {
    IconType.ROBOT: (0, -20),
    IconType.SPIDER: (6, -5),
    IconType.UFO: (0, 30),
}


def get_image_and_offset(
    name: str,
    icon_id: int,
    offset_x: float,
    offset_y: float,
    copy_level: int,
    image: "PIL.Image.Image",
) -> Tuple["PIL.Image.Image", float, float]:  # image, offset_x, offset_y
    if ROBOT in name:
        if f"{icon_id:02}_02" in name:
            image = image.rotate(-45, resample=PIL.Image.BICUBIC, expand=True)

            offset_x -= 50 if copy_level else 40
            offset_y -= 20

            if TWO in name:
                if icon_id in {2, 5, 6, 8, 9, 11, 12, 15, 17, 24}:
                    offset_x += 15
                    offset_y -= 5

                elif icon_id in {7, 10, 19, 20}:
                    offset_x += 7

                elif icon_id == 13:
                    offset_x += 10
                    offset_y -= 4

                elif icon_id == 18:
                    offset_x -= 1
                    offset_y -= 1

                elif icon_id in {21, 25}:
                    offset_x += 12

                elif icon_id == 22:
                    offset_y -= 5

                elif icon_id in {3, 26}:
                    offset_x += 1

                elif icon_id == 23:
                    offset_x -= 3
                    offset_y -= 2

        elif f"{icon_id:02}_03" in name:
            image = image.rotate(45, resample=PIL.Image.BICUBIC, expand=True)

            offset_x -= 40 if copy_level else 30

            if TWO in name and icon_id in {3, 5, 6, 8, 16, 17}:
                offset_x += 10

            offset_y -= 52 if icon_id == 21 and TWO not in name else 60

        elif f"{icon_id:02}_04" in name:

            if copy_level:
                offset_x -= 10

            offset_y -= 70

    elif SPIDER in name:
        if f"{icon_id:02}_02" in name:
            if copy_level > 1:
                offset_x += 55
                offset_y -= 38

                image = image.transpose(PIL.Image.FLIP_LEFT_RIGHT)

            elif copy_level:
                offset_x += 18
                offset_y -= 38

            else:
                offset_x -= 16
                offset_y -= 38

        elif f"{icon_id:02}_03" in name:
            offset_x -= 86
            offset_y -= 38

            if icon_id == 7:
                offset_x += 15
                offset_y += 13

            elif icon_id == 15:
                offset_x += 5
                offset_y += 3

            if TWO in name:
                if icon_id == 16:
                    offset_y += 5

                elif icon_id in {1, 8, 9, 11, 13, 14}:
                    offset_x += 2

                elif icon_id in {2, 3}:
                    offset_x += 25

                elif icon_id == 10:
                    offset_x += 18
                    offset_y -= 5

            if GLOW in name:
                offset_y += 3

            image = image.rotate(-45, resample=PIL.Image.BICUBIC, expand=True)

        elif f"{icon_id:02}_04" in name:
            offset_x -= 30
            offset_y -= 20

    return image, offset_x, offset_y


ICON_EXTRAS = {  # icon_type -> (((extra, ...), copy_level), ...)
    IconType.CUBE: ((("glow",), 0), ((2,), 0), ((), 0), (("extra",), 0)),
    IconType.SHIP: ((("glow",), 0), ((2,), 0), ((), 0), (("extra",), 0)),
    IconType.BALL: ((("glow",), 0), ((2,), 0), ((), 0), (("extra",), 0)),
    IconType.UFO: ((("glow",), 0), ((3,), 0), ((2,), 0), ((), 0), (("extra",), 0)),
    IconType.WAVE: ((("glow",), 0), ((2,), 0), ((), 0), (("extra",), 0)),
    IconType.ROBOT: (
        (("03", 2, "glow"), 1),
        (("03", "glow"), 1),
        (("04", 2, "glow"), 1),
        (("04", "glow"), 1),
        (("02", 2, "glow"), 1),
        (("02", "glow"), 1),
        (("03", 2, "glow"), 0),
        (("03", "glow"), 0),
        (("04", 2, "glow"), 0),
        (("04", "glow"), 0),
        (("01", 2, "glow"), 0),
        (("01", "glow"), 0),
        (("02", 2, "glow"), 0),
        (("02", "glow"), 0),
        (("01", "extra", "glow"), 0),
        (("03", 2), 1),
        (("03",), 1),
        (("04", 2), 1),
        (("04",), 1),
        (("02", 2), 1),
        (("02",), 1),
        (("03", 2), 0),
        (("03",), 0),
        (("04", 2), 0),
        (("04",), 0),
        (("01", 2), 0),
        (("01",), 0),
        (("02", 2), 0),
        (("02",), 0),
        (("01", "extra"), 0),
    ),
    IconType.SPIDER: (
        (("04", 2, "glow"), 0),
        (("04", "glow"), 0),
        (("02", 2, "glow"), 2),
        (("02", "glow"), 2),
        (("02", 2, "glow"), 1),
        (("02", "glow"), 1),
        (("01", 2, "glow"), 0),
        (("01", "glow"), 0),
        (("03", 2, "glow"), 0),
        (("03", "glow"), 0),
        (("02", 2, "glow"), 0),
        (("02", "glow"), 0),
        (("01", "extra", "glow"), 0),
        (("04", 2), 0),
        (("04",), 0),
        (("02", 2), 2),
        (("02",), 2),
        (("02", 2), 1),
        (("02",), 1),
        (("01", 2), 0),
        (("01",), 0),
        (("03", 2), 0),
        (("03",), 0),
        (("02", 2), 0),
        (("02",), 0),
        (("01", "extra"), 0),
    ),
}


factory: Optional[IconFactory]

try:
    factory = IconFactory.default(load=False)

except Exception as error:  # noqa
    factory = None

    log.warn(f"Can not create initial factory. {type(error).__name__}: {error}")
