from gd.enums import IconType
from gd.typing import Optional, Protocol, TypeVar, Union

__all__ = ("get_icon_name",)

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
    icon_type: Union[int, str, IconType],
    icon_id: int,
    extra: Optional[FormatOrStr] = None,
    trail: Optional[FormatOrStr] = DEFAULT_TRAIL,
    format: str = DEFAULT_FORMAT,
    copy_level: int = 0,
) -> str:
    icon_type = IconType.from_value(icon_type)
    icon_type_name = icon_type_names.get(icon_type)  # type: ignore

    if icon_type_name is None:
        raise LookupError(f"Can not find icon type name for {icon_type}.")

    if trail is None:
        if extra is None:
            name = f"{icon_type_name}_{icon_id:02}.{format}"

        else:
            name = f"{icon_type_name}_{icon_id:02}_{extra}.{format}"

    else:
        if extra is None:
            name = f"{icon_type_name}_{icon_id:02}_{trail}.{format}"

        else:
            name = f"{icon_type_name}_{icon_id:02}_{extra}_{trail}.{format}"

    if copy_level:
        return name + COPY_SUFFIX * copy_level

    return name
