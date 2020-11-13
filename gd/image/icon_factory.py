from pathlib import Path

try:
    # import PIL.Image  # type: ignore
    # import PIL.ImageOps  # type: ignore
    pass

except ImportError:
    pass

# from gd.color import Color, COLOR_1, COLOR_2
from gd.enums import IconType
from gd.typing import Iterator, Optional, Protocol, TypeVar, Union

from gd.image.sheet import Sheet, DEFAULT_IMAGE_SUFFIX, DEFAULT_PLIST_SUFFIX

__all__ = ("generate_icon_names", "get_icon_name")

T_co = TypeVar("T_co", covariant=True)


class FormatOrStr(Protocol[T_co]):
    def __str__(self: T_co) -> str:
        ...

    def __format__(self: T_co, format_spec: str) -> str:
        ...


COPY_SUFFIX = "_copy"

DEFAULT_FORMAT = "png"
DEFAULT_TRAIL = "001"

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
    *extras: FormatOrStr,
    trail: Optional[FormatOrStr] = DEFAULT_TRAIL,
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


def generate_icon_names(
    icon_type: IconType,
    icon_id: int,
    trail: Optional[FormatOrStr] = DEFAULT_TRAIL,
    format: str = DEFAULT_FORMAT,
) -> Iterator[str]:
    for extras, copy_level in ICON_EXTRAS.get(icon_type, ()):
        yield get_icon_name(  # type: ignore
            icon_type, icon_id, *extras, trail=trail, format=format, copy_level=copy_level
        )


class IconFactory:
    def __init__(self, icon_sheet: Sheet, glow_sheet: Sheet) -> None:
        self.icon_sheet = icon_sheet
        self.glow_sheet = glow_sheet

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


ICON_EXTRAS = {  # icon_type -> (((extra, ...), copy_level), ...)
    IconType.CUBE: (
        (("glow",), 0),
        ((2,), 0),
        ((), 0),
        (("extra",), 0),
    ),
    IconType.SHIP: (
        (("glow",), 0),
        ((2,), 0),
        ((), 0),
        (("extra",), 0),
    ),
    IconType.BALL: (
        (("glow",), 0),
        ((2,), 0),
        ((), 0),
        (("extra",), 0),
    ),
    IconType.UFO: (
        (("glow",), 0),
        ((3,), 0),
        ((2,), 0),
        ((), 0),
        (("extra",), 0),
    ),
    IconType.WAVE: (
        (("glow",), 0),
        ((2,), 0),
        ((), 0),
        (("extra",), 0),
    ),
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
