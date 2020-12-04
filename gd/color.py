import colorsys

from gd.text_utils import make_repr
from gd.typing import Any, Dict, Iterator, List, Optional, Tuple, Union

__all__ = ("COLOR_1", "COLOR_2", "Color")

BYTE = 0xFF
SIZE = BYTE.bit_length()
DOUBLE_SIZE = SIZE * 2


def float_to_byte_channel(value: float) -> int:
    return int(value * BYTE)


class Color:
    """Represents a Color.

    .. container:: operations

        .. describe:: x == y

            Check if two colors are equal.

        .. describe:: x != y

            Check if two colors are not equal.

        .. describe:: str(x)

            Return hex of the color, e.g. ``#ffffff``.

        .. describe:: repr(x)

            Return representation of the color, useful for debugging.

        .. describe:: hash(x)

            Returns ``hash(self.value)``.

    Attributes
    ----------
    value: :class:`int`
        The raw integer colour value.
    """

    ID_TO_COLOR = {
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

    COLOR_TO_ID = {color: id for id, color in ID_TO_COLOR.items()}

    def __init__(self, value: int = 0) -> None:
        if not isinstance(value, int):
            raise TypeError(f"Expected int value, received {self.__class__.__name__!r}.")

        self.value = value

    def get_byte(self, byte_index: int) -> int:
        return (self.value >> (SIZE * byte_index)) & BYTE

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self.value == other.value

    def __ne__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self.value != other.value

    def __str__(self) -> str:
        return self.to_hex()

    def __repr__(self) -> str:
        info = {
            "hex": self.to_hex(),
            "value": self.value,
            "id": self.id,
        }
        return make_repr(self, info)

    def __hash__(self) -> int:
        return hash(self.value)

    def __json__(self) -> Dict[str, Optional[Union[Tuple[int, int, int], int, str]]]:
        return dict(rgb=self.to_rgb(), hex=self.to_hex(), value=self.value, id=self.id)

    @property
    def id(self) -> Optional[int]:
        """Optional[:class:`int`]: Returns ID that represents position of the color.
        ``None`` if not a default one.
        """
        return self.COLOR_TO_ID.get(self.value)

    @property
    def r(self) -> int:
        """:class:`int`: Returns the red component of the colour."""
        return self.get_byte(2)

    @property
    def g(self) -> int:
        """:class:`int`: Returns the green component of the colour."""
        return self.get_byte(1)

    @property
    def b(self) -> int:
        """:class:`int`: Returns the blue component of the colour."""
        return self.get_byte(0)

    def to_hex(self) -> str:
        """:class:`str`: Returns the colour in hex format."""
        return f"#{self.value:0>6x}"

    def to_rgb(self) -> Tuple[int, int, int]:
        """Return a :class:`tuple` representing the color.

        Returns
        -------
        Tuple[:class:`int`, :class:`int`, :class:`int`]
            ``(r, g, b)`` :class:`tuple` representing the color.
        """
        return (self.r, self.g, self.b)

    def to_rgba(self, alpha: int = BYTE) -> Tuple[int, int, int, int]:
        """Same as :meth:`gd.Color.to_rgb`, but contains ``alpha`` component.

        Parameters
        ----------
        alpha: :class:`int`
            Value of an alpha channel to use. Defaults to ``255``, meaning full value.

        Returns
        ------
        Tuple[:class:`int`, :class:`int`, :class:`int`, :class:`int`]
            ``(r, g, b, a)`` :class:`tuple` representing the color.
        """
        return (self.r, self.g, self.b, alpha & BYTE)

    def get_ansi_start(self) -> str:
        return f"\x1b[38;2;{self.r};{self.g};{self.b}m"

    def get_ansi_end(self) -> str:
        return "\x1b[0m"

    def ansi_escape(self, string: Optional[str] = None) -> str:
        """Color ``string`` using ANSI representation of the color.
        If not given, :meth:`~gd.Color.to_hex` is used.
        """
        if string is None:
            string = self.to_hex()

        return f"{self.get_ansi_start()}{string}{self.get_ansi_end()}"

    paint = ansi_escape

    @classmethod
    def from_hex(cls, hex_str: str) -> "Color":
        """Constructs :class:`~gd.Color` from hex string, e.g. ``0x7289da`` or ``#000000``."""
        return cls(int(hex_str.replace("#", ""), 16))

    @classmethod
    def from_rgb(cls, r: int, g: int, b: int) -> "Color":
        """Constructs a :class:`~gd.Color` from an RGB tuple."""
        return cls((r << DOUBLE_SIZE) + (g << SIZE) + b)

    @classmethod
    def from_hsv(cls, h: float, s: float, v: float) -> "Color":
        """Constructs a :class:`~gd.Color` from an HSV (HSB) tuple."""
        rgb = colorsys.hsv_to_rgb(h, s, v)
        return cls.from_rgb(*map(float_to_byte_channel, rgb))

    @classmethod
    def from_rgb_string(cls, string: str, delim: str = ",") -> "Color":
        """Constructs a :class:`~gd.Color` from RGB string, e.g. ``255,255,255``."""
        return cls.from_rgb(*map(int, string.split(delim)))

    @classmethod
    def with_id(cls, id: int, default: Optional["Color"] = None) -> "Color":
        """Creates a :class:`~gd.Color` with in-game ID of ``id``."""
        color = cls.ID_TO_COLOR.get(id)

        if color is None:
            if default is None:
                raise ValueError(f"ID is not present: {id}.")

            return default

        return Color(color)

    @classmethod
    def iter_colors(cls) -> Iterator["Color"]:
        """Returns an iterator over all in-game colors."""
        for value in cls.COLOR_TO_ID:
            yield cls(value)

    @classmethod
    def list_colors(cls) -> List["Color"]:
        """Same as :meth:`~gd.Color.iter_colors`, but returns a list."""
        return list(cls.iter_colors())


COLOR_1 = Color.with_id(0)
COLOR_2 = Color.with_id(3)
