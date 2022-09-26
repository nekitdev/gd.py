from __future__ import annotations

from colorsys import hsv_to_rgb, rgb_to_hsv
from typing import ClassVar, Dict, Iterator, List, Optional, Tuple, Type, TypeVar

from attrs import Attribute, field, frozen

from gd.binary_constants import BITS, BYTE, DOUBLE_BITS
from gd.constants import DEFAULT_COLOR_1_ID, DEFAULT_COLOR_2_ID, EMPTY
from gd.json import JSON
from gd.models_constants import COLOR_SEPARATOR
from gd.models_utils import concat_color, split_color
from gd.robtop import RobTop
from gd.string_utils import tick

__all__ = ("Color",)

C = TypeVar("C", bound="Color")

BLACK = 0x000000
WHITE = 0xFFFFFF


def float_to_byte(value: float) -> int:
    return int(value * BYTE)


def byte_to_float(value: int) -> float:
    return value / BYTE


HEX_BASE = 16
HEX_PREFIX = "0x"
HEX_VALUE_PREFIX = "#"

HEX_FORMAT = "{:0>6X}"

HEX = HEX_VALUE_PREFIX + HEX_FORMAT
HEX_VALUE = HEX_PREFIX + HEX_FORMAT

hex_string = HEX.format
hex_value = HEX_VALUE.format

ANSI_RGB = "\x1b[38;2;{};{};{}m"
ANSI_RESET = "\x1b[0m"

ID_NOT_PRESENT = "color ID not present: {}"

VALUE_TOO_LARGE = "color value too large: {}"
VALUE_TOO_SMALL = "color value too small: {}"


@frozen(order=True)
class Color(JSON[int], RobTop):
    value: int = field(default=BLACK, repr=hex_value)

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
        41: 0x7D7DAF,
    }

    VALUE_TO_ID: ClassVar[Dict[int, int]] = {color: id for id, color in ID_TO_VALUE.items()}

    @value.validator
    def check_value(self, attribute: Attribute[int], value: int) -> None:
        if value > WHITE:
            raise ValueError(VALUE_TOO_LARGE.format(tick(hex(value))))

        if value < BLACK:
            raise ValueError(VALUE_TOO_SMALL.format(tick(hex(value))))

    def get_byte(self, index: int) -> int:
        """Gets the byte at `index`.

        Arguments:
            index: The index to get the byte at.

        Returns:
            The byte at `index`.
        """
        return (self.value >> (BITS * index)) & BYTE

    def __str__(self) -> str:
        return self.to_hex()

    def __hash__(self) -> int:
        return self.value

    @property
    def id(self) -> Optional[int]:
        """An in-game ID of the color (if present)."""
        return self.VALUE_TO_ID.get(self.value)

    @property
    def red(self) -> int:
        """The red component of the color."""
        return self.get_byte(2)

    @property
    def green(self) -> int:
        """The green component of the color."""
        return self.get_byte(1)

    @property
    def blue(self) -> int:
        """The blue component of the color."""
        return self.get_byte(0)

    r, g, b = red, green, blue

    def to_hex(self) -> str:
        """Returns the color in hex format.

        Returns:
            The string representing the color.
        """
        return hex_string(self.value)

    def to_hex_value(self) -> str:
        """Returns the color in hex value format.

        Returns:
            The string representing the color.
        """
        return hex_value(self.value)

    def to_rgb(self) -> Tuple[int, int, int]:
        """Returns the `(r, g, b)` tuple representing the color.

        Returns:
            The `(r, g, b)` tuple.
        """
        return (self.red, self.green, self.blue)

    def to_rgba(self, alpha: Optional[int] = None) -> Tuple[int, int, int, int]:
        """Returns the `(r, g, b, a)` tuple representing the color.

        Arguments:
            alpha: The alpha component of the color to use.

        Returns:
            The `(r, g, b, a)` tuple.
        """
        byte = BYTE

        if alpha is None:
            alpha = byte

        return (self.red, self.green, self.blue, alpha & byte)

    def to_hsv(self) -> Tuple[float, float, float]:
        """Returns the `(h, s, v)` tuple representing the color.

        Returns:
            The `(h, s, v)` tuple.
        """
        r, g, b = map(byte_to_float, self.to_rgb())

        return rgb_to_hsv(r, g, b)

    def ansi_escape(self, string: Optional[str] = None) -> str:
        """Colors the `string` (or [`self.to_hex()`][gd.color.Color.to_hex]) using ANSI escapes.

        Returns:
            The colored `string` (or [`self.to_hex()`][gd.color.Color.to_hex]).
        """
        if string is None:
            string = self.to_hex()

        color = ANSI_RGB.format(self.red, self.green, self.blue)
        reset = ANSI_RESET

        return color + string + reset

    paint = ansi_escape

    @classmethod
    def from_json(cls: Type[C], data: int) -> C:
        return cls(data)

    def to_json(self) -> int:
        return self.value

    @classmethod
    def default(cls: Type[C]) -> C:
        return cls.white()

    @classmethod
    def black(cls: Type[C]) -> C:
        return cls(BLACK)

    @classmethod
    def white(cls: Type[C]) -> C:
        return cls(WHITE)

    def is_black(self) -> bool:
        return self.value == BLACK

    def is_white(self) -> bool:
        return self.value == WHITE

    @classmethod
    def default_color_1(cls: Type[C]) -> C:
        return cls.with_id(DEFAULT_COLOR_1_ID)

    @classmethod
    def default_color_2(cls: Type[C]) -> C:
        return cls.with_id(DEFAULT_COLOR_2_ID)

    @classmethod
    def from_hex(cls: Type[C], hex_string: str) -> C:
        """Converts a `hex_string` to [`Color`][gd.color.Color].

        Returns:
            The converted [`Color`][gd.color.Color].
        """
        return cls(int(hex_string.replace(HEX_VALUE_PREFIX, EMPTY), HEX_BASE))

    @classmethod
    def from_rgb(cls: Type[C], r: int, g: int, b: int) -> C:
        """Converts an `(r, g, b)` tuple to [`Color`][gd.color.Color].

        Returns:
            The converted [`Color`][gd.color.Color].
        """
        return cls((r << DOUBLE_BITS) + (g << BITS) + b)

    @classmethod
    def from_rgba(cls: Type[C], r: int, g: int, b: int, a: int) -> C:
        """Converts an `(r, g, b, a)` tuple to [`Color`][gd.color.Color].

        The alpha component is ignored.

        Returns:
            The converted [`Color`][gd.color.Color].
        """
        return cls.from_rgb(r, g, b)

    @classmethod
    def from_hsv(cls: Type[C], h: float, s: float, v: float) -> C:
        """Converts an `(h, s, v)` tuple to [`Color`][gd.color.Color].

        Returns:
            The converted [`Color`][gd.color.Color].
        """
        r, g, b = map(float_to_byte, hsv_to_rgb(h, s, v))

        return cls.from_rgb(r, g, b)

    @classmethod
    def from_robtop(cls: Type[C], string: str) -> C:
        r, g, b = map(int, split_color(string))

        return cls.from_rgb(r, g, b)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return COLOR_SEPARATOR in string

    def to_robtop(self) -> str:
        return concat_color(map(str, self.to_rgb()))

    @classmethod
    def with_id(cls: Type[C], id: int, default: Optional[C] = None) -> C:
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
                raise ValueError(ID_NOT_PRESENT.format(id))

            return default

        return cls(value)

    @classmethod
    def iter_color(cls: Type[C]) -> Iterator[C]:
        """Returns an iterator over all in-game colors.

        Returns:
            An iterator over in-game colors.
        """
        for value in cls.VALUE_TO_ID:
            yield cls(value)

    @classmethod
    def list_color(cls: Type[C]) -> List[C]:
        """Same as [`iter_color`][gd.color.Color.iter_color], but returns a list.

        Returns:
            The list of in-game colors.
        """
        return list(cls.iter_color())
