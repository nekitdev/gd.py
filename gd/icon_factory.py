from pathlib import Path
import plistlib  # we use plistlib since we assume valid plists. ~ nekit

from attr import attrib, dataclass

from gd.colors import Color
from gd.typing import Any, Dict, Iterator, Tuple, Union, ref
from gd.utils.enums import IconType
from gd.utils.text_tools import JSDict

try:
    from PIL import Image, ImageOps
    from PIL.Image import Image as ImageType
except ImportError:
    ImageType = ref("PIL.Image.Image")
    print("Failed to load Pillow/PIL. Icon Factory will not be supported.")

ALPHA = Color().to_rgba()
COLOR_1 = Color(0x00FF00)
COLOR_2 = Color(0x00FFFF)

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

PathLike = Union[str, Path]
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


def into_name(type: str, id: int, *args, last: int = 1, suffix: str = "png") -> str:
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
        return f"{self.rob_type}_{self.id:02}"

    def get_name(self, *args) -> str:
        return into_name(self.rob_type, self.id, *args)

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

    def is_rotated(self) -> bool:
        return self.rotated


def c_int_array_str_parse(string: str) -> Iterator[int]:
    return map(int, map(float, string.translate(remove_braces).split(",")))


def type_to_rob_name(icon_type: IconType) -> str:
    return ROB_NAMES.get(icon_type, "player")


def is_interesting(string: str) -> bool:
    return string.startswith(ROB_SPRITE_STARTS)


class IconFactory:
    def __init__(self, icon_sheet_path: PathLike, glow_sheet_path: PathLike) -> None:
        self.icon_sheet = PlistImageSheet(icon_sheet_path)
        self.glow_sheet = PlistImageSheet(glow_sheet_path)
        self.loaded = False

    @property
    def cache(self):
        return dict_merge(self.icon_sheet.cache, self.glow_sheet.cache)

    def load(self) -> None:
        self.icon_sheet.load()
        self.glow_sheet.load()
        self.loaded = True

    def unload(self) -> None:
        self.icon_sheet.unload()
        self.glow_sheet.unload()
        self.loaded = False

    def is_loaded(self) -> bool:
        return self.loaded

    def generate(
        self,
        icon_type: Union[int, str, IconType] = IconType.CUBE,
        icon_id: int = 1,
        color_1: Color = COLOR_1,
        color_2: Color = COLOR_2,
        glow_outline: bool = False,
    ) -> ImageType:
        if not self.is_loaded():
            self.load()

        start = Icon(type=icon_type, id=icon_id).get_start()
        sprites = [sprite for sprite in self.cache.values() if sprite.name.startswith(start)]

        print(*(sprite.name for sprite in sprites))
        ...


class PlistImageSheet:
    def __init__(self, sheet_location: PathLike) -> None:
        self.sheet_path = Path(sheet_location)
        self.plist_path = self.sheet_path.with_suffix(".plist")

        for path in (self.sheet_path, self.plist_path):
            if not path.exists():
                raise FileNotFoundError(f"{path} was not found.")

        self.cache: Dict[str, Sprite] = {}

        self.name = self.sheet_path.stem  # last part, without suffix
        self.image = Image.open(self.sheet_path)

        with open(self.plist_path, "rb") as plist_file:
            self.plist = plistlib.load(plist_file, dict_type=JSDict).get("frames", {})

    def load(self) -> None:
        self.cache = {name: self.get_sprite(name) for name in self.plist if is_interesting(name)}

    def unload(self) -> None:
        self.cache.clear()

    def get_image_info(self, image_name: str) -> Dict[str, Any]:
        info = self.plist.get(image_name, JSDict())

        if not info:
            raise LookupError(f"Could not find image by name: {image_name!r}.")

        return info

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
        )


def concat_images(
    image_1: ImageType,
    image_2: ImageType,
    offset_1: Tuple[int, int] = (0, 0),
    offset_2: Tuple[int, int] = (0, 0),
) -> ImageType:
    width_1, height_1 = image_1.size
    width_2, height_2 = image_2.size

    if width_1 > width_2 or height_1 > height_2:
        width, height = width_1, height_1
        mode, size = image_1.mode, image_1.size
    else:
        width, height = width_2, height_2
        mode, size = image_2.mode, image_2.size

    off_x1, off_y1 = offset_1
    off_x2, off_y2 = offset_2

    image_1_offset = (width - image_1.width) // 2 - off_x2, (height - image_1.height) // 2 - off_y2
    image_2_offset = (width - image_2.width) // 2 - off_x1, (height - image_2.height) // 2 - off_y1

    result = Image.new(mode, size, ALPHA)
    result.paste(image_1, image_1_offset)

    other = Image.new(mode, size, ALPHA)
    other.paste(image_2, image_2_offset)

    result.alpha_composite(other)

    return result


def apply_color(image: ImageType, color: Tuple[int, int, int]) -> ImageType:
    # [r, g, b, a][3] -> a
    alpha = image.split()[3]

    colored = ImageOps.colorize(ImageOps.grayscale(image), white=color, black="black")
    colored.putalpha(alpha)

    return colored


if __name__ == "__main__":
    factory = IconFactory(ASSETS / "icon_sheet.png", ASSETS / "glow_sheet.png")
    factory.generate("cube", 2)
