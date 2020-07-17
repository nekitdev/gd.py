import colorsys

from gd.typing import Color, Dict, Optional, Tuple, Union

from gd.utils.converter import Converter
from gd.utils.text_tools import make_repr


class Color:
    """Represents a Color. This class is similar
    to a (red, green, blue) :class:`tuple`.

    There is an alias for this called Colour.

    Attributes
    ------------
    value: :class:`int`
        The raw integer colour value.
    """

    def __init__(self, value: int = 0) -> None:
        if not isinstance(value, int):
            raise TypeError(f"Expected int parameter, but received {self.__class__.__name__!r}.")
        self.value = value

    def _get_byte(self, byte: int) -> int:
        return (self.value >> (8 * byte)) & 0xFF

    @property
    def _ord_index(self) -> Optional[str]:
        if self.index is not None:
            return Converter.to_ordinal(self.index)

    def __eq__(self, other: Color) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.value == other.value

    def __ne__(self, other: Color) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.value != other.value

    def __str__(self) -> str:
        return self.to_hex()

    def __repr__(self) -> str:
        info = {
            "hex": self.to_hex(),
            "value": self.value,
            "index": self._ord_index,
        }
        return make_repr(self, info)

    def __hash__(self) -> int:
        return hash(self.value)

    def __json__(self) -> Dict[str, Optional[Union[Tuple[int, int, int], int, str]]]:
        return dict(rgb=self.to_rgb(), hex=self.to_hex(), value=self.value, index=self.index)

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

    def show(self) -> None:
        print(self.ansi_escape())

    def to_hex(self) -> str:
        """:class:`str`: Returns the colour in hex format."""
        return f"#{self.value:0>6x}"

    def to_rgb(self) -> Tuple[int, int, int]:
        """Tuple[:class:`int`, :class:`int`, :class:`int`]: Returns an (r, g, b) tuple representing the colour."""
        return (self.r, self.g, self.b)

    def to_rgba(self) -> Tuple[int, int, int, int]:
        """Tuple[:class:`int`, :class:`int`, :class:`int`, :class:`int`]: Same as :meth:`.Color.to_rgb`,
        but contains alpha component (always ``255``).
        """
        return (*self.to_rgb(), 255)

    def ansi_escape(self) -> str:
        return f"\x1b[38;2;{self.r};{self.g};{self.b}m{self.to_hex()}\x1b[0m"

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
    0x7DFF00,
    0x00FF00,
    0x00FF7D,
    0x00FFFF,
    0x007DFF,
    0x0000FF,
    0x7D00FF,
    0xFF00FF,
    0xFF007D,
    0xFF0000,
    0xFF7D00,
    0xFFFF00,
    0xFFFFFF,
    0xB900FF,
    0xFFB900,
    0x000000,
    0x00C8FF,
    0xAFAFAF,
    0x5A5A5A,
    0xFF7D7D,
    0x00AF4B,
    0x007D7D,
    0x004BAF,
    0x4B00AF,
    0x7D007D,
    0xAF004B,
    0xAF4B00,
    0x7D7D00,
    0x4BAF00,
    0xFF4B00,
    0x963200,
    0x966400,
    0x649600,
    0x009664,
    0x006496,
    0x640096,
    0x960064,
    0x960000,
    0x009600,
    0x000096,
    0x7DFFAF,
    0x7D7DAF,
)
colors = tuple(Color(value) for value in values)

Colour = Color  # create alias
