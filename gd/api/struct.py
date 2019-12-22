from ..utils.wrap_tools import make_repr
from ..errors import EditorError

from .parser import *

from .utils import _get_dir, _define_color, get_id
from ._property import _object_code, _color_code, _header_code

__all__ = ('Object', 'ColorChannel', 'Header')


class Struct:
    _dump = _dump
    _convert = _convert
    _convert = _collect
    _base_data = {}
    _existing_properties = []

    def __init__(self, **properties):
        self.data = self._base_data.copy()

        for name, value in properties.items():
            setattr(self, name, value)

    def __repr__(self):
        info = {key: repr(value) for key, value in self.to_dict().items()}
        return make_repr(self, info)

    def __str__(self):
        return self.dump()

    def to_dict(self):
        final = {}
        for name in self._existing_properties:
            value = getattr(self, name)

            if value is not None:
                final[name] = value

        return final

    def dump(self):
        return self.__class__._collect(self.to_map())

    def to_map(self):
        return self.__class__._dump(self.data)

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
            return cls.from_mapping(cls._convert(string))

        except Exception as exc:
            raise EditorError('Failed to process string.') from exc


class Object(Struct):
    _base_data = {1: 1, 2: 0, 3: 0}
    _dump = _object_dump
    _convert = _object_convert
    _collect = _object_collect

    def set_id(self, directive: str):
        """Set ``id`` of ``self`` according to the directive, e.g. ``trigger:move``."""
        self.edit(id=get_id(directive))

    def set_z_layer(self, directive: str):
        """Set ``z_layer`` of ``self`` according to the directive, e.g. ``layer:t1`` or ``b3``."""
        self.edit(z_layer=get_id(_get_dir(directive, 'layer'), ret_enum=True))

    def set_easing(self, directive: str):
        """Set ``easing`` of ``self`` according to the directive, e.g. ``sine_in_out``."""
        self.edit(easing=get_id(_get_dir(directive, 'easing'), ret_enum=True))

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
    _base_data = {
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
    _dump = _color_dump
    _convert = _color_convert
    _collect = _color_collect

    def __init__(self, special_directive: str = None, **properties):
        super().__init__(**properties)

        if special_directive is not None:
            self.set_id(special_directive)

    def set_id(self, directive: str):
        """Set ColorID of ``self`` according to the directive, e.g. ``BG`` or ``color:bg``."""
        self.edit(id=get_id(_get_dir(directive, 'color')))

    def set_color(self, color):
        """Set ``rgb`` of ``self`` to ``color``."""
        self.edit(**dict(zip('rgb', _define_color(color).to_rgb())))

    exec(_color_code)


class Header(Struct):
    _base_data = {}
    _dump = _header_dump
    _convert = _header_convert
    _collect = _header_collect

    exec(_header_code)
