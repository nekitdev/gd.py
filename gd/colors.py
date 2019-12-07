import colorsys

from .utils.wrap_tools import make_repr
from .utils.converter import Converter

class Colour:
    """Represents a Colour. This class is similar
    to a (red, green, blue) :class:`tuple`.

    There is an alias for this called Color.

    Attributes
    ------------
    value: :class:`int`
        The raw integer colour value.
    """

    sys_name = __import__('sys').platform

    def __init__(self, value: int):
        if not isinstance(value, int):
            raise TypeError('Expected int parameter, but received {!r}.'.format(value.__class__.__name__))

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
        idx = self.index
        info = {
            'hex': self.to_hex(),
            'value': self.value,
            'index': idx if idx is None else Converter.to_ordinal(idx)
        }
        return make_repr(self, info)

    def __hash__(self):
        return hash(self.value)

    @property
    def index(self):
        """:class:`int`: Returns index that represents position of the colour in ``colors``.
        ``None`` if the colour is not present in ``colors``.
        """
        try:
            return colors.index(self)

        except ValueError:
            pass

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

    def print(self):
        if 'win32' in self.sys_name:
            print(self.to_hex())

        else:
            print(self.ansi_escape())

    def to_hex(self):
        """:class:`str`: Returns the colour in hex format."""
        return '#{:0>6x}'.format(self.value)

    def to_rgb(self):
        """Tuple[:class:`int`, :class:`int`, :class:`int`]: Returns an (r, g, b) tuple representing the colour."""
        return (self.r, self.g, self.b)

    def to_rgba(self):
        """Tuple[:class:`int`, :class:`int`, :class:`int`, :class:`int`]: Same as :meth:`.Colour.to_rgb`, but contains alpha component. (always 255)"""
        return (*self.to_rgb(), 255)

    def ansi_escape(self):
        return '\x1b[38;2;{};{};{}m{}\x1b[0m'.format(*self.to_rgb(), self.to_hex())

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
