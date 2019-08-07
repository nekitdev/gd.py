import colorsys

from ..utils.wrap_tools import _make_repr
from ..utils.converter import Converter

class Colour:
    """Represents a Colour. This class is similar
    to a (red, green, blue) :class:`tuple`.

    There is an alias for this called Color.

    Attributes
    ------------
    value: :class:`int`
        The raw integer colour value.
    """

    def __init__(self, value):
        if not isinstance(value, int):
            raise TypeError(f'Expected int parameter, but received {value.__class__.__name__}.')

        self.value = value

    def _get_byte(self, byte):
        return (self.value >> (8 * byte)) & 0xff

    def __eq__(self, other):
        return isinstance(other, Colour) and self.value == other.value

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.to_hex()

    def __repr__(self):
        info = {
            'hex': self.to_hex(),
            'value': self.value,
            'index': Converter.to_ordinal(self.index)
        }
        return _make_repr(self, info)

    def __hash__(self):
        return hash(self.value)

    @property
    def index(self):
        """:class:`int`: Returns index that represents position of the colour in ``colors``.
        ``None`` if the colour is not present in ``colors``.
        """
        try:
            return colors.index(self)
        except IndexError:
            return
    
    @property
    def r(self):
        """:class:`int`: Returns the red component of the colour."""
        return self._get_byte(2)

    @property
    def g(self):
        """:class:`int`: Returns the green component of the colour."""
        return self._get_byte(1)

    @property
    def b(self):
        """:class:`int`: Returns the blue component of the colour."""
        return self._get_byte(0)

    def to_hex(self):
        """:class:`str`: Returns the colour in hex format."""
        return f'#{self.value:0>6x}'

    def to_rgb(self):
        """Tuple[:class:`int`, :class:`int`, :class:`int`]: Returns an (r, g, b) tuple representing the colour."""
        return (self.r, self.g, self.b)

    def to_rgba(self):
        """Tuple[:class:`int`, :class:`int`, :class:`int`, :class:`int`]: Same as ``to_rgb``, but contains alpha component. (always 255)"""
        return (*self.to_rgb(), 255)

    @classmethod
    def from_rgb(cls, r, g, b):
        """Constructs a :class:`Colour` from an RGB tuple."""
        return cls((r << 16) + (g << 8) + b)

    @classmethod
    def from_hsv(cls, h, s, v):
        """Constructs a :class:`Colour` from an HSV tuple."""
        rgb = colorsys.hsv_to_rgb(h, s, v)
        return cls.from_rgb(*(int(x * 255) for x in rgb))

Color = Colour

colors = (
    Colour(0x7dff00), Colour(0x00ff00), Colour(0x00ff7d),
    Colour(0x00ffff), Colour(0x007dff), Colour(0x0000ff),
    Colour(0x7d00ff), Colour(0xff00ff), Colour(0xff007d),
    Colour(0xff0000), Colour(0xff7d00), Colour(0xffff00),
    Colour(0xffffff), Colour(0xb900ff), Colour(0xffb900),
    Colour(0x000000), Colour(0x00c8ff), Colour(0xafafaf),
    Colour(0x5a5a5a), Colour(0xff7d7d), Colour(0x00af4b),
    Colour(0x007d7d), Colour(0x004baf), Colour(0x4b00af),
    Colour(0x7d007d), Colour(0xaf004b), Colour(0xaf4b00),
    Colour(0x7d7d00), Colour(0x4baf00), Colour(0xff4b00),
    Colour(0x963200), Colour(0x966400), Colour(0x649600),
    Colour(0x009664), Colour(0x006496), Colour(0x640096),
    Colour(0x960064), Colour(0x960000), Colour(0x009600),
    Colour(0x000096), Colour(0x7dffaf), Colour(0x7d7daf)
)