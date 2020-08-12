import io
from pathlib import Path
import plistlib  # we use plistlib since we assume valid plists. ~ nekit
import re

from attr import attrib, dataclass

from gd.colors import Color
from gd.logging import get_logger
from gd.typing import Any, Dict, Iterator, List, Sequence, Tuple, Union, ref
from gd.utils.enums import IconType
from gd.utils.text_tools import JSDict

log = get_logger(__name__)

try:
    from PIL import Image, ImageOps
    from PIL.Image import Image as ImageType
except ImportError:
    ImageType = ref("PIL.Image.Image")
    log.warning("Failed to load Pillow/PIL. Icon Factory will not be supported.")

ALPHA = (0, 0, 0, 0)
COLOR_1 = Color(0x00FF00)
COLOR_2 = Color(0x00FFFF)
DARK = Color(0x808080)

ASSETS = Path(__file__).parent / "assets"

ROB_NAMES = {
    IconType.CUBE: "player",
    IconType.SHIP: "ship",
    IconType.BALL: "player_ball",
    IconType.UFO: "bird",
    IconType.WAVE: "dart",
    IconType.ROBOT: "robot",
    IconType.SPIDER: "spider",
}
ROB_SPRITE_STARTS = tuple(name + "_" for name in ROB_NAMES.values())

TWO = "_2_"
THREE = "_3_"
GLOW = "_glow_"
EXTRA = "_extra_"
ROBOT_LEG = re.compile(r"robot_[0-9]+_(02|03|04)_.*")
SPIDER_LEG = re.compile(r"spider_[0-9]+_02_.*")

PathLike = Union[str, Path]
PlistImageSheetType = ref("gd.icon_factory.PlistImageSheet")
SpriteType = ref("gd.icon_factory.Sprite")
remove_braces = str.maketrans({"{": "", "}": ""})


def dict_merge(*dicts, **fields) -> Dict[Any, Any]:
    result = {}

    for other in dicts:
        result.update(other)

    result.update(fields)

    return result


@dataclass
class Point:
    x: int = attrib()
    y: int = attrib()


@dataclass
class Size:
    width: int = attrib()
    height: int = attrib()


@dataclass
class Rectangle:
    point: Point = attrib()
    size: Size = attrib()

    @property
    def x(self) -> int:
        return self.point.x

    @property
    def y(self) -> int:
        return self.point.y

    @property
    def width(self) -> int:
        return self.size.width

    @property
    def height(self) -> int:
        return self.size.height


def into_name(
    type: str, id: int, *args, last: int = 1, suffix: str = "png", copy_level: int = 0
) -> str:
    # construct image name from type, id, args, last, copy_level and suffix
    if len(args) == 1:
        maybe_args = args[0]
        if isinstance(maybe_args, tuple):
            args = maybe_args

    suffix += "_copy" * copy_level

    if args:
        return f"{type}_{id:02}_{'_'.join(map(str, args))}_{last:03}.{suffix}"

    return f"{type}_{id:02}_{last:03}.{suffix}"


@dataclass
class Icon:
    type: IconType = attrib()
    id: int = attrib()

    def __attrs_post_init__(self) -> None:
        self.type = IconType.from_value(self.type)

    def get_start(self) -> str:
        return f"{self.rob_type}_{self.id:02}_"

    def get_name(self, *args, copy_level: int = 0) -> str:
        return into_name(self.rob_type, self.id, *args, copy_level=copy_level)

    @property
    def rob_type(self) -> str:
        return type_to_rob_name(self.type)


@dataclass
class Sprite:
    name: str = attrib()
    offset: Point = attrib()
    size: Size = attrib()
    source_size: Size = attrib()
    rectangle: Rectangle = attrib()
    rotated: bool = attrib()
    sheet: PlistImageSheetType = attrib()
    copy_level: int = attrib(default=0)

    def get_name(self) -> str:
        return self.name + "_copy" * self.copy_level

    def is_rotated(self) -> bool:
        return self.rotated

    def copy(self) -> SpriteType:
        return self.__class__(
            name=self.name,
            offset=self.offset,
            size=self.size,
            source_size=self.source_size,
            rectangle=self.rectangle,
            rotated=self.rotated,
            sheet=self.sheet,
            copy_level=self.copy_level + 1,
        )


def c_int_array_str_parse(string: str) -> Iterator[int]:
    return map(int, map(float, string.translate(remove_braces).split(",")))


def type_to_rob_name(icon_type: IconType) -> str:
    return ROB_NAMES.get(icon_type, "player")


def is_interesting(string: str) -> bool:
    return string.startswith(ROB_SPRITE_STARTS)


class PlistImageSheet:
    def __init__(self, sheet_location: PathLike) -> None:
        self.sheet_path = Path(sheet_location)
        self.plist_path = self.sheet_path.with_suffix(".plist")

        for path in (self.sheet_path, self.plist_path):
            if not path.exists():
                raise FileNotFoundError(f"{path} was not found.")

        self.cache: List[str] = []

        self.image = Image.open(self.sheet_path)

        self.name = self.sheet_path.stem  # last part, without suffix

        with open(self.plist_path, "rb") as plist_file:
            self.plist = plistlib.load(plist_file, dict_type=JSDict).get("frames", {})

    def load(self) -> None:
        self.image.load()
        self.cache = [name for name in self.plist if is_interesting(name)]

    def get_image_info(self, image_name: str, strict: bool = True) -> Dict[str, Any]:
        try:
            return self.plist[image_name]

        except KeyError:
            if strict:
                raise LookupError(f"Could not find image by name: {image_name!r}.") from None

            return JSDict()

    def get_sprite(self, image_name: str) -> Sprite:
        info = self.get_image_info(image_name)

        x, y, rect_width, rect_height = c_int_array_str_parse(info.get("texture_rect"))
        offset_x, offset_y = c_int_array_str_parse(info.get("sprite_offset"))
        width, height = c_int_array_str_parse(info.get("sprite_size"))
        source_width, source_height = c_int_array_str_parse(info.get("sprite_source_size"))
        is_rotated = info.get("texture_rotated", False)

        return Sprite(
            name=image_name,
            offset=Point(offset_x, offset_y),
            size=Size(width, height),
            source_size=Size(source_width, source_height),
            rectangle=Rectangle(point=Point(x, y), size=Size(rect_width, rect_height)),
            rotated=is_rotated,
            sheet=self,
        )


class IconFactory:
    def __init__(self, icon_sheet_path: PathLike, glow_sheet_path: PathLike) -> None:
        self.icon_sheet = PlistImageSheet(icon_sheet_path)
        self.glow_sheet = PlistImageSheet(glow_sheet_path)
        self.loaded = False

    def load(self) -> None:
        self.icon_sheet.load()
        self.glow_sheet.load()
        self.loaded = True

    def is_loaded(self) -> bool:
        return self.loaded

    def get_sheet(self, image_name: str) -> PlistImageSheet:
        for sheet in (self.icon_sheet, self.glow_sheet):
            if image_name in sheet.cache:
                return sheet
        raise ValueError(f"{image_name!r} not found in cache.")

    @property
    def cache(self) -> List[str]:
        return self.icon_sheet.cache + self.glow_sheet.cache

    def reorder_sprites(self, sprites: List[Sprite], icon: Icon) -> None:
        for sprite in sprites.copy():
            if ROBOT_LEG.match(sprite.name):
                sprites.append(sprite.copy())
            elif SPIDER_LEG.match(sprite.name):
                dupe = sprite.copy()
                sprites.append(dupe)
                sprites.append(dupe.copy())

        names = self.generate_names(icon)
        sprites.sort(key=lambda sprite: names.index(sprite.get_name()))

    def generate(
        self,
        icon_type: Union[int, str, IconType] = IconType.CUBE,
        icon_id: int = 1,
        color_1: Color = COLOR_1,
        color_2: Color = COLOR_2,
        glow_outline: bool = False,
        error_on_not_found: bool = False,
    ) -> ImageType:
        if not self.is_loaded():
            self.load()

        result = Image.new("RGBA", (250, 250), ALPHA)

        icon = Icon(type=icon_type, id=icon_id)
        start = icon.get_start()

        sprites = [
            self.get_sheet(name).get_sprite(name) for name in self.cache if name.startswith(start)
        ]

        if not sprites:  # sprites not found, fall back to ID=1
            if error_on_not_found:
                raise LookupError(f"{icon} does not exist.")

            return self.generate(
                icon_type=icon_type,
                icon_id=1,
                color_1=color_1,
                color_2=color_2,
                glow_outline=glow_outline,
            )

        if not glow_outline:
            sprites = [sprite for sprite in sprites if GLOW not in sprite.name]

        self.reorder_sprites(sprites, icon)

        for sprite in sprites:
            name = sprite.name
            copy_level = sprite.copy_level

            x, y = sprite.rectangle.x, sprite.rectangle.y

            width, height = sprite.size.width, sprite.size.height
            center_x, center_y = width // 2, height // 2

            off_x, off_y = sprite.offset.x, sprite.offset.y

            real_width, real_height = sprite.rectangle.width, sprite.rectangle.height

            is_rotated = sprite.rotated

            if is_rotated:
                real_width, real_height = real_height, real_width

            image = sprite.sheet.image.crop((x, y, x + real_width, y + real_height))

            if is_rotated:
                image = image.rotate(90, resample=Image.BICUBIC, expand=True)

            if copy_level and GLOW not in name:
                image = reduce_brightness(image)

            image, off_x, off_y = self.get_image_and_offset(
                name, icon_id, image, off_x, off_y, copy_level
            )

            if GLOW in name:
                image = apply_color(image, get_glow_color(color_1, color_2).to_rgb())
            elif TWO in name:
                image = apply_color(image, color_2.to_rgb())
            elif EXTRA not in name and THREE not in name:
                image = apply_color(image, color_1.to_rgb())

            draw_x = 100 - center_x + off_x
            draw_y = 100 - center_y - off_y

            draw_off_x, draw_off_y = {
                IconType.ROBOT: (0, -20),
                IconType.SPIDER: (6, -5),
                IconType.UFO: (0, 30),
            }.get(icon.type, (0, 0))

            result.alpha_composite(image, (25 + draw_off_x + draw_x, 25 + draw_off_y + draw_y))

        return result

    # WEIRD AND TOUGH CODE AHEAD (THANKS ROBERT)

    @staticmethod
    def generate_names(icon: Icon) -> List[str]:
        names = []

        if icon.type in {IconType.CUBE, IconType.SHIP, IconType.BALL, IconType.WAVE}:
            names += [icon.get_name(part) for part in ("glow", 2, (), "extra")]

        elif icon.type is IconType.UFO:
            names += [icon.get_name(part) for part in ("glow", 3, 2, (), "extra")]

        elif icon.type is IconType.ROBOT:
            COPY_PARTS = (("03", 2), "03", ("04", 2), "04", ("02", 2), "02")
            NORMAL_PARTS = (
                ("03", 2),
                "03",
                ("04", 2),
                "04",
                ("01", 2),
                "01",
                ("02", 2),
                "02",
                ("01", "extra"),
            )

            for additional in ("glow", ()):
                names += [
                    icon.get_name(extend_part(part, additional), copy_level=1)
                    for part in COPY_PARTS
                ] + [icon.get_name(extend_part(part, additional)) for part in NORMAL_PARTS]

        elif icon.type is IconType.SPIDER:
            PRE_COPY_PARTS = (("04", 2), "04")
            DOUBLE_COPY_PARTS = (("02", 2), "02")
            COPY_PARTS = (("02", 2), "02")
            NORMAL_PARTS = (("01", 2), "01", ("03", 2), "03", ("02", 2), "02", ("01", "extra"))

            for additional in ("glow", ()):
                names += (
                    [icon.get_name(extend_part(part, additional)) for part in PRE_COPY_PARTS]
                    + [
                        icon.get_name(extend_part(part, additional), copy_level=2)
                        for part in DOUBLE_COPY_PARTS
                    ]
                    + [
                        icon.get_name(extend_part(part, additional), copy_level=1)
                        for part in COPY_PARTS
                    ]
                    + [icon.get_name(extend_part(part, additional)) for part in NORMAL_PARTS]
                )

        return names

    @staticmethod
    def get_image_and_offset(
        name: str, id: int, image: ImageType, off_x: int, off_y: int, copy_level: int
    ) -> Tuple[ImageType, int, int]:  # image, off_x, off_y
        # blame rob; honestly, I am done with doing all those exceptions at this point ~ nekit
        if "robot" in name:

            if f"{id}_02_" in name:
                image = image.rotate(-45, resample=Image.BICUBIC, expand=True)
                off_x -= 50 if copy_level else 40
                off_y -= 20

                if TWO in name:

                    if id in {2, 5, 6, 8, 9, 11, 12, 15, 17, 24}:
                        off_x += 15
                        off_y -= 5
                    elif id in {7, 10, 19, 20}:
                        off_x += 7
                    elif id == 13:
                        off_x += 10
                        off_y -= 4
                    elif id == 18:
                        off_x -= 1
                        off_y -= 1
                    elif id in {21, 25}:
                        off_x += 12
                    elif id == 22:
                        off_y -= 5
                    elif id in {3, 26}:
                        off_x += 1
                    elif id == 23:
                        off_x -= 3
                        off_y -= 2

            elif f"{id}_03_" in name:
                image = image.rotate(45, resample=Image.BICUBIC, expand=True)
                off_x -= 40 if copy_level else 30

                if TWO in name and id in {3, 5, 6, 8, 16, 17}:
                    off_x += 10

                off_y -= 52 if id == 21 and TWO not in name else 60

            elif f"{id}_04_" in name:

                if copy_level:
                    off_x -= 10
                off_y -= 70

        elif "spider" in name:

            if f"{id}_02_" in name:

                if copy_level > 1:
                    off_x += 55
                    off_y -= 38

                    image = image.transpose(Image.FLIP_LEFT_RIGHT)

                elif copy_level > 0:
                    off_x += 18
                    off_y -= 38
                else:
                    off_x -= 16
                    off_y -= 38

            elif f"{id}_03_" in name:
                off_x -= 86
                off_y -= 38

                if id == 7:
                    off_x += 15
                    off_y += 13

                elif id == 15:
                    off_x += 5
                    off_y += 3

                if TWO in name:

                    if id == 16:
                        off_y += 5
                    elif id in {1, 8, 9, 11, 13, 14}:
                        off_x += 2
                    elif id in {2, 3}:
                        off_x += 25
                    elif id == 10:
                        off_x += 18
                        off_y -= 5

                if GLOW in name:
                    off_y += 3

                image = image.rotate(-45, resample=Image.BICUBIC, expand=True)

            elif f"{id}_04_" in name:
                off_x -= 30
                off_y -= 20

        return image, off_x, off_y


def extend_part(part: Any, additional: Any) -> Any:
    if additional:
        return (*part, additional) if isinstance(part, tuple) else (part, additional)

    return part


def get_glow_color(color_1: Color, color_2: Color) -> Color:
    if not color_1.value:  # black
        return Color(0xFFFFFF)  # white
    return color_2


def apply_color(image: ImageType, color: Tuple[int, int, int]) -> ImageType:
    # [r, g, b, a][3] -> a
    alpha = image.split()[3]

    colored = ImageOps.colorize(ImageOps.grayscale(image), white=color, black="black")
    colored.putalpha(alpha)

    return colored


def reduce_brightness(image: ImageType) -> ImageType:
    return apply_color(image, DARK.to_rgb())


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


try:
    factory = IconFactory(ASSETS / "icon_sheet.png", ASSETS / "glow_sheet.png")

except Exception as error:  # noqa
    factory = None

    log.warning(f"Could not create initial factory. {error}")


if __name__ == "__main__":  # easter egg?! ~ nekit
    factory.generate(
        icon_type="cube",
        icon_id=98,
        color_1=Color(0x7289DA),
        color_2=Color(0xFFFFFF),
        glow_outline=True,
    ).save("easter_egg.png")
