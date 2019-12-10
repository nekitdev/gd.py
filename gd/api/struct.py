from ..utils.wrap_tools import make_repr
from ..colors import Color
from ..errors import EditorError

from .hsv import HSV
from .parser import *
from ._property import _object_code, _color_code

__all__ = ('Object', 'ColorChannel')

class Struct:
    dumper = _dump
    convert = _convert
    collect = _collect
    base_data = {}

    def __init__(self, **properties):
        self.data = self.base_data.copy()

        for name, value in properties.items():
            setattr(self, name, value)

    def __repr__(self):
        info = {key: repr(value) for key, value in self.to_dict().items()}
        return make_repr(self, info)

    def to_dict(self):
        final = {}
        for name in self.existing_properties:
            value = getattr(self, name)

            if value is not None:
                final[name] = value

        return final

    def dump(self):
        return self.__class__.collect(self.to_map())

    def to_map(self):
        return self.__class__.dumper(self.data)

    def copy(self):
        self_copy = self.__class__()
        self_copy.data = self.data.copy()
        return self_copy

    def edit(self, **fields):
        for field, value in fields.items():
            setattr(self, field, value)

    @classmethod
    def from_mapping(cls, mapping: dict):
        self = cls()
        self.data = mapping
        return self

    @classmethod
    def from_string(cls, string: str):
        try:
            return cls.from_mapping(cls.convert(string))

        except Exception as exc:
            raise EditorError('Failed to process string.') from exc


def _define_color(color):
    if hasattr(color, '__iter__'):
        return Color.from_rgb(*color)

    if hasattr(color, 'value'):
        return Color(color.value)

    return Color(color)


class Object(Struct):
    base_data = {1: 1, 2: 0, 3: 0}
    dumper = _object_dump
    convert = _object_convert
    collect = _object_collect

    def set_color(self, color):
        """Set ``rgb`` of ``self`` to ``color``."""
        self.edit(**dict(zip('rgb', _define_color(color).to_rgb())))

    def add_groups(self, *groups: int):
        """Add ``groups`` to ``self.groups``."""
        if not hasattr(self, 'groups'):
            self.groups = set(groups)

        else:
            self.groups.update(groups)

    def get_pos(self):
        """Tuple[:class:`int`, :class:`int`]: ``x`` and ``y`` of ``self``."""
        return (self.x, self.y)

    def set_pos(self, x: float, y: float):
        """Set ``x`` and ``y`` position of ``self`` to given values."""
        self.x, self.y = x, y

    def move(self, x: float = 0, y: float = 0):
        """Add ``x`` and ``y`` to coordinates of ``self``."""
        self.x += x
        self.y += y

    def rotate(self, deg: float = 0):
        """Add ``deg`` to ``rotation`` of ``self``."""
        if not self.rotation:
            self.rotation = deg
        else:
            self.rotation += deg

    exec(_object_code)

class ColorChannel(Struct):
    base_data = {
        1: 255, 2: 255, 3: 255,
        4: -1,
        5: False,
        6: 0,
        7: 1,
        8: True,
        11: 255, 12: 255, 13: 255,
        15: True,
        18: False
    }
    dumper = _color_dump
    convert = _color_convert
    collect = _color_collect

    def set_color(self, color):
        """Set ``rgb`` of ``self`` to ``color``."""
        self.edit(**dict(zip('rgb', _define_color(color).to_rgb())))

    exec(_color_code)


class Header:
    pass
