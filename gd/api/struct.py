from ..utils.wrap_tools import make_repr
from ..colors import Color
from ..errors import EditorError

from .hsv import HSV
from .parser import *

__all__ = ('Object', 'ColorChannel')

class Struct:
    get_id = _get_id
    loader = _load
    dumper = _dump
    convert = _convert
    collect = _collect
    base_data = {}

    def __init__(self, **properties):
        self.data = {}

        for name, value in properties.items():
            n = self.__class__.get_id(name)
            if n:
                self.data[n] = value

    def __repr__(self):
        info = {key: repr(value) for key, value in self.to_dict().items()}
        return make_repr(self, info)

    def __getattr__(self, name):
        try:
            return self.data[self.__class__.get_id(name)]
        except KeyError:
            raise AttributeError(
                '{0.__class__.__name__!r} object '
                'has no attribute {1!r}.'.format(self, name)
            ) from None

    def __setattr__(self, name, value):
        n = self.__class__.get_id(name)

        if n:
            self.data[n] = value

        else:
            self.__dict__[name] = value

    def to_dict(self):
        return self.__class__.loader(self.data)

    def dump(self):
        return self.__class__.collect(self.to_map())

    def to_map(self):
        data = self.base_data.copy()
        data.update(self.data)
        return self.__class__.dumper(data)

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
    get_id = _object_get_id
    loader = _object_load
    dumper = _object_dump
    convert = _object_convert
    collect = _object_collect

    def set_color(self, color):
        self.edit(**dict(zip('rgb', _define_color(color).to_rgb())))

    def add_groups(self, *groups: int):
        if not hasattr(self, 'groups'):
            self.groups = set(groups)
        else:
            self.groups = {*self.groups, *groups}


class ColorChannel(Struct):
    base_data = {
        1: 255, 2: 255, 3: 255,
        4: -1,
        5: False,
        7: 1,
        8: True,
        11: 255, 12: 255, 13: 255,
        15: True,
        18: False
    }
    get_id = _color_get_id
    loader = _color_load
    dumper = _color_dump
    convert = _color_convert
    collect = _color_collect

    def set_color(self, color):
        self.edit(**dict(zip('rgb', _define_color(color).to_rgb())))


class LevelAPI:
    pass


class Header:
    pass
