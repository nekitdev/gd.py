# DOCUMENT

import gc
import plistlib  # we use plistlib since we assume valid plist files. ~ nekit
from pathlib import Path

try:
    import PIL.Image  # type: ignore
    import PIL.ImageOps  # type: ignore

except ImportError:
    pass

from gd.decorators import cache_by
from gd.image.geometry import Point, Rectangle, Size
from gd.image.metadata import Metadata
from gd.image.sprite import Sprite
from gd.json import NamedDict
from gd.logging import get_logger
from gd.text_utils import make_repr
from gd.typing import Any, Callable, Dict, Iterator, Optional, TypeVar, Union

log = get_logger(__name__)

T = TypeVar("T")

PathLike = Union[Path, str]

DEFAULT_IMAGE_SUFFIX = ".png"
DEFAULT_PLIST_SUFFIX = ".plist"

remove_braces = str.maketrans({"{": "", "}": ""})
delimiter = ","


def simple_array_parse(string: str, function: Callable[[str], T]) -> Iterator[T]:
    yield from map(function, string.translate(remove_braces).split(delimiter))


def get_metadata(metadata_dict: NamedDict[str, Any]) -> Metadata:
    format = metadata_dict.format
    pixel_format = metadata_dict.pixelFormat
    premultiply_alpha = bool(metadata_dict.premultiplyAlpha)
    file_name = metadata_dict.textureFileName
    (width, height) = simple_array_parse(metadata_dict.size, float)

    return Metadata(
        format=format,
        pixel_format=pixel_format,
        premultiply_alpha=premultiply_alpha,
        file_name=file_name,
        size=Size(width, height),
    )


def get_sprite_format_0(sprite_dict: NamedDict[str, Any], name: str) -> Sprite:
    x = float(sprite_dict.x)
    y = float(sprite_dict.y)
    width = float(sprite_dict.width)
    height = float(sprite_dict.height)
    offset_x = float(sprite_dict.offsetX)
    offset_y = float(sprite_dict.offsetY)
    original_width = float(sprite_dict.originalWidth)
    original_height = float(sprite_dict.originalHeight)

    return Sprite(
        name=name,
        relative_offset=Point(offset_x, offset_y),
        size=Size(width, height),
        source_size=Size(original_width, original_height),
        rectangle=Rectangle(Point(x, y), Size(width, height)),
    )


def get_sprite_format_1(sprite_dict: NamedDict[str, Any], name: str) -> Sprite:
    (x, y, width, height) = simple_array_parse(sprite_dict.frame, float)
    (offset_x, offset_y) = simple_array_parse(sprite_dict.offset, float)
    (source_width, source_height) = simple_array_parse(sprite_dict.sourceSize, float)

    return Sprite(
        name=name,
        relative_offset=Point(offset_x, offset_y),
        size=Size(width, height),
        source_size=Size(source_width, source_height),
        rectangle=Rectangle(Point(x, y), Size(width, height)),
    )


def get_sprite_format_2(sprite_dict: NamedDict[str, Any], name: str) -> Sprite:
    (x, y, width, height) = simple_array_parse(sprite_dict.frame, float)
    (offset_x, offset_y) = simple_array_parse(sprite_dict.offset, float)
    (source_width, source_height) = simple_array_parse(sprite_dict.sourceSize, float)
    rotated = bool(sprite_dict.rotated)

    return Sprite(
        name=name,
        relative_offset=Point(offset_x, offset_y),
        size=Size(width, height),
        source_size=Size(source_width, source_height),
        rectangle=Rectangle(Point(x, y), Size(width, height)),
        rotated=rotated,
    )


def get_sprite_format_3(sprite_dict: NamedDict[str, Any], name: str) -> Sprite:
    (width, height) = simple_array_parse(sprite_dict.spriteSize, float)
    (offset_x, offset_y) = simple_array_parse(sprite_dict.spriteOffset, float)
    (source_width, source_height) = simple_array_parse(sprite_dict.spriteSourceSize, float)
    (x, y, real_width, real_height) = simple_array_parse(sprite_dict.textureRect, float)
    rotated = bool(sprite_dict.textureRotated)
    aliases = set(sprite_dict.aliases)

    return Sprite(
        name=name,
        aliases=aliases,
        relative_offset=Point(offset_x, offset_y),
        size=Size(width, height),
        source_size=Size(source_width, source_height),
        rectangle=Rectangle(Point(x, y), Size(real_width, real_height)),
        rotated=rotated,
    )


get_sprite_format: Dict[int, Callable[[NamedDict[str, Any], str], Sprite]] = {
    0: get_sprite_format_0,
    1: get_sprite_format_1,
    2: get_sprite_format_2,
    3: get_sprite_format_3,
}


class Sheet:
    def __init__(self, image_path: PathLike, plist_path: PathLike, load: bool = True) -> None:
        self.image_path = Path(image_path)
        self.plist_path = Path(plist_path)

        self.image_unchecked: Optional["PIL.Image.Image"] = None
        self.plist_unchecked: Optional[Any] = None

        self.loaded = False

        for path in (self.image_path, self.plist_path):
            if not path.exists():
                raise FileNotFoundError(f"{path} was not found.")

        if load:
            self.load()

    def __repr__(self) -> str:
        info = {
            "image_path": repr(self.image_path),
            "plist_path": repr(self.plist_path),
            "loaded": self.loaded,
        }

        return make_repr(self, info)

    @property  # type: ignore
    @cache_by("plist_path", "loaded")
    def metadata(self) -> Metadata:
        self.assure_loaded()

        return get_metadata(self.plist.metadata)

    @property  # type: ignore
    @cache_by("image_path", "plist_path", "loaded")
    def sprites(self) -> Dict[str, Sprite]:
        self.assure_loaded()

        format = self.metadata.format

        get_sprite: Optional[Callable[[NamedDict[str, Any], str], Sprite]] = get_sprite_format.get(
            format
        )

        if get_sprite is None:
            raise LookupError(f"Do not know how to parse sprite plist format {format!r}.")

        return {
            name: get_sprite(sprite_dict, name).attach_sheet(self)
            for name, sprite_dict in self.plist.frames.items()
        }

    def get_image(self) -> "PIL.Image.Image":
        result = self.image_unchecked

        if result is None:
            raise ValueError("Image is not attached to the handler.")

        return result

    def set_image(self, image: "PIL.Image.Image") -> None:
        self.image_unchecked = image

    def delete_image(self) -> None:
        self.image_unchecked = None

    def free_image(self) -> None:
        del self.image
        gc.collect()

    image = property(get_image, set_image, delete_image)

    def get_plist(self) -> Any:
        result = self.plist_unchecked

        if result is None:
            raise ValueError("Plist is not attached to the handler.")

        return result

    def set_plist(self, plist: Any) -> None:
        self.plist_unchecked = plist

    def delete_plist(self) -> None:
        self.plist_unchecked = None

    def free_plist(self) -> None:
        del self.plist
        gc.collect()

    plist = property(get_plist, set_plist, delete_plist)

    def load(self) -> None:
        self.loaded = True

        try:
            self.image = PIL.Image.open(self.image_path)

            with open(self.plist_path, "rb") as plist_file:
                self.plist = plistlib.load(plist_file, dict_type=NamedDict)

            self.image.load()

        except Exception:  # noqa
            self.loaded = False

            raise

    reload = load

    def unload(self) -> None:
        self.free_image()
        self.free_plist()

        self.loaded = False

    def is_loaded(self) -> bool:
        return self.loaded

    def assure_loaded(self) -> None:
        if not self.loaded:
            self.load()

    @classmethod
    def from_path(
        cls,
        path: PathLike,
        image_suffix: str = DEFAULT_IMAGE_SUFFIX,
        plist_suffix: str = DEFAULT_PLIST_SUFFIX,
        load: bool = True,
    ) -> "Sheet":
        path = Path(path)

        return cls(path.with_suffix(image_suffix), path.with_suffix(plist_suffix), load=load)
