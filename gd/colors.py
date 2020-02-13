import colorsys
from sys import platform

from .typing import Color, Optional, Tuple

from .utils.converter import Converter
from .utils.text_tools import make_repr


class Color:
    """Represents a Color. This class is similar
    to a (red, green, blue) :class:`tuple`.

    There is an alias for this called Colour.

    Attributes
    ------------
    value: :class:`int`
        The raw integer colour value.
    """
    def __init__(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError(
                'Expected int parameter, but received {!r}.'.format(value.__class__.__name__)
            )
        self.value = value

    def _get_byte(self, byte: int) -> int:
        return (self.value >> (8 * byte)) & 0xff

    @property
    def _ord_index(self) -> str:
        if self.index is not None:
            return Converter.to_ordinal(self.index)

    def __eq__(self, other: Color) -> bool:
        return isinstance(other, Color) and self.value == other.value

    def __ne__(self, other: Color) -> bool:
        return not self.__eq__(other)

    def __str__(self) -> str:
        return self.to_hex()

    def __repr__(self) -> str:
        info = {
            'hex': self.to_hex(),
            'value': self.value,
            'index': self._ord_index,
        }
        return make_repr(self, info)

    def __hash__(self) -> int:
        return hash(self.value)

    def _json(self) -> dict:
        return dict(
            rgb=self.to_rgb(),
            hex=self.to_hex(),
            value=self.value,
            index=self.index
        )

    @property
    def index(self) -> Optional[int]:
        """Optional[:class:`int`]: Returns index that represents position of the colour in ``colors``.
        ``None`` if the colour is not present in ``colors``.
        """
        try:
            return colors.index(self)
        except ValueError:
            pass

    @property
    def r(self) -> int:
        """:class:`int`: Returns the red component of the colour."""
        return self._get_byte(2)

    @property
    def g(self) -> int:
        """:class:`int`: Returns the green component of the colour."""
        return self._get_byte(1)

    @property
    def b(self) -> int:
        """:class:`int`: Returns the blue component of the colour."""
        return self._get_byte(0)

    def print(self) -> None:
        if platform in ('win32', 'cygwin'):
            print(self.to_hex())
        else:
            print(self.ansi_escape())

    def to_hex(self) -> str:
        """:class:`str`: Returns the colour in hex format."""
        return '#{:0>6x}'.format(self.value)

    def to_rgb(self) -> Tuple[int, int, int]:
        """Tuple[:class:`int`, :class:`int`, :class:`int`]: Returns an (r, g, b) tuple representing the colour."""
        return (self.r, self.g, self.b)

    def to_rgba(self) -> Tuple[int, int, int, int]:
        """Tuple[:class:`int`, :class:`int`, :class:`int`, :class:`int`]: Same as :meth:`.Color.to_rgb`,
        but contains alpha component (always ``255``).
        """
        return (*self.to_rgb(), 255)

    def ansi_escape(self) -> str:
        return '\x1b[38;2;{};{};{}m{}\x1b[0m'.format(*self.to_rgb(), self.to_hex())

    @classmethod
    def from_rgb(cls, r: int, g: int, b: int) -> Color:
        """Constructs a :class:`Color` from an RGB tuple."""
        return cls((r << 16) + (g << 8) + b)

    @classmethod
    def from_hsv(cls, h: float, s: float, v: float) -> Color:
        """Constructs a :class:`Color` from an HSV (HSB) tuple."""
        rgb = colorsys.hsv_to_rgb(h, s, v)
        return cls.from_rgb(*(int(x * 255) for x in rgb))


values = (
    0x7dff00, 0x00ff00, 0x00ff7d,
    0x00ffff, 0x007dff, 0x0000ff,
    0x7d00ff, 0xff00ff, 0xff007d,
    0xff0000, 0xff7d00, 0xffff00,
    0xffffff, 0xb900ff, 0xffb900,
    0x000000, 0x00c8ff, 0xafafaf,
    0x5a5a5a, 0xff7d7d, 0x00af4b,
    0x007d7d, 0x004baf, 0x4b00af,
    0x7d007d, 0xaf004b, 0xaf4b00,
    0x7d7d00, 0x4baf00, 0xff4b00,
    0x963200, 0x966400, 0x649600,
    0x009664, 0x006496, 0x640096,
    0x960064, 0x960000, 0x009600,
    0x000096, 0x7dffaf, 0x7d7daf
)
colors = tuple(Color(value) for value in values)

Colour = Color
