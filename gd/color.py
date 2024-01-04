from __future__ import annotations

from typing import ClassVar, Dict, Iterator, List, Optional, Type, TypeVar

from attrs import frozen
from colors import Color as ColorCore
from iters.iters import iter, wrap_iter
from typing_extensions import Self

from gd.constants import DEFAULT_COLOR_1_ID, DEFAULT_COLOR_2_ID, DEFAULT_COLOR_3_ID
from gd.converter import CONVERTER
from gd.models_constants import COLOR_SEPARATOR
from gd.models_utils import concat_color, split_color
from gd.robtop import RobTop
from gd.simple import Simple

__all__ = ("Color",)

C = TypeVar("C", bound="Color")

ID_NOT_PRESENT = "color with ID `{}` is not present"
id_not_present = ID_NOT_PRESENT.format


@frozen(order=True)
class Color(RobTop, ColorCore, Simple[int]):
    ID_TO_VALUE: ClassVar[Dict[int, int]] = {
        0: 0x7DFF00,
        1: 0x00FF00,
        2: 0x00FF7D,
        3: 0x00FFFF,
        4: 0x007DFF,
        5: 0x0000FF,
        6: 0x7D00FF,
        7: 0xFF00FF,
        8: 0xFF007D,
        9: 0xFF0000,
        10: 0xFF7D00,
        11: 0xFFFF00,
        12: 0xFFFFFF,
        13: 0xB900FF,
        14: 0xFFB900,
        15: 0x000000,
        16: 0x00C8FF,
        17: 0xAFAFAF,
        18: 0x5A5A5A,
        19: 0xFF7D7D,
        20: 0x00AF4B,
        21: 0x007D7D,
        22: 0x004BAF,
        23: 0x4B00AF,
        24: 0x7D007D,
        25: 0xAF004B,
        26: 0xAF4B00,
        27: 0x7D7D00,
        28: 0x4BAF00,
        29: 0xFF4B00,
        30: 0x963200,
        31: 0x966400,
        32: 0x649600,
        33: 0x009664,
        34: 0x006496,
        35: 0x640096,
        36: 0x960064,
        37: 0x960000,
        38: 0x009600,
        39: 0x000096,
        40: 0x7DFFAF,
        41: 0x7D7DFF,
        42: 0xFFFA7F,
        43: 0xFA7FFF,
        44: 0x00FFC0,
        45: 0x50320E,
        46: 0xCDA576,
        47: 0xB680FF,
        48: 0xFF3A3A,
        49: 0x4D4D8F,
        50: 0x000A4C,
        51: 0xFDD4CE,
        52: 0xBEB5FF,
        53: 0x700000,
        54: 0x520200,
        55: 0x380106,
        56: 0x804F4F,
        57: 0x7A3535,
        58: 0x512424,
        59: 0xA36246,
        60: 0x754936,
        61: 0x563528,
        62: 0xFFB972,
        63: 0xFFA040,
        64: 0x66311E,
        65: 0x5B2700,
        66: 0x472000,
        67: 0xA77B4D,
        68: 0x6D5339,
        69: 0x513E2A,
        70: 0xFFFFC0,
        71: 0xFDE0A0,
        72: 0xC0FFA0,
        73: 0xB1FF6D,
        74: 0xC0FFE0,
        75: 0x94FFE4,
        76: 0x43A18A,
        77: 0x316D5F,
        78: 0x265449,
        79: 0x006000,
        80: 0x004000,
        81: 0x006060,
        82: 0x004040,
        83: 0xA0FFFF,
        84: 0x010770,
        85: 0x00496D,
        86: 0x00324C,
        87: 0x002638,
        88: 0x5080AD,
        89: 0x335375,
        90: 0x233C56,
        91: 0xE0E0E0,
        92: 0x3D068C,
        93: 0x370860,
        94: 0x404040,
        95: 0x6F49A4,
        96: 0x54367F,
        97: 0x422A63,
        98: 0xFCB5FF,
        99: 0xAF57AF,
        100: 0x824382,
        101: 0x5E315E,
        102: 0x808080,
        103: 0x66033E,
        104: 0x470134,
        105: 0xD2FF32,
        106: 0x76BDFF,
    }

    VALUE_TO_ID: ClassVar[Dict[int, int]] = {value: id for id, value in ID_TO_VALUE.items()}

    @classmethod
    def from_value(cls, value: int) -> Self:
        return cls(value)

    def to_value(self) -> int:
        return self.value

    @property
    def id(self) -> Optional[int]:
        """The in-game ID of the color (if present)."""
        return self.VALUE_TO_ID.get(self.value)

    @classmethod
    def default(cls) -> Self:
        return cls.white()

    @classmethod
    def default_color_1(cls) -> Self:
        return cls.with_id(DEFAULT_COLOR_1_ID)

    @classmethod
    def default_color_2(cls) -> Self:
        return cls.with_id(DEFAULT_COLOR_2_ID)

    @classmethod
    def default_color_3(cls) -> Self:
        return cls.with_id(DEFAULT_COLOR_3_ID)

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        r, g, b = iter(split_color(string)).map(float).map(round).tuple()

        return cls.from_rgb(r, g, b)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return COLOR_SEPARATOR in string

    def to_robtop(self) -> str:
        return iter.of(self.red, self.green, self.blue).map(str).collect(concat_color)

    @classmethod
    def with_id(cls, id: int, default: Optional[Self] = None) -> Self:
        """Creates a [`Color`][gd.color.Color] with an in-game ID of `id`.

        Arguments:
            id: The in-game ID of the color.
            default: The default color to use. If not given, [`ValueError`][ValueError] is raised.

        Raises:
            ValueError: The color ID is not present and `default` is not provided.

        Returns:
            The [`Color`][gd.color.Color] matching the `id`.
        """
        value = cls.ID_TO_VALUE.get(id)

        if value is None:
            if default is None:
                raise ValueError(id_not_present(id))

            return default

        return cls.from_value(value)

    @classmethod
    @wrap_iter
    def iter_colors(cls) -> Iterator[Self]:
        """Returns an iterator over all in-game colors.

        Returns:
            An iterator over in-game colors.
        """
        return iter(cls.VALUE_TO_ID).map(cls.from_value).unwrap()

    @classmethod
    def list_colors(cls) -> List[Self]:
        """Same as [`iter_colors`][gd.color.Color.iter_colors], but returns a list.

        Returns:
            The list of in-game colors.
        """
        return cls.iter_colors().list()


def dump_color(color: Color) -> int:
    return color.to_value()


def load_color(value: int, color_type: Type[C]) -> C:
    return color_type.from_value(value)


CONVERTER.register_structure_hook(Color, load_color)
CONVERTER.register_unstructure_hook(Color, dump_color)
