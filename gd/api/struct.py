from ..utils.wrap_tools import make_repr
from ..errors import EditorError

from ..utils import search_utils as search

from .parser import *

from .utils import _get_dir, _define_color, get_id
from ._property import *

__all__ = ('Object', 'ColorChannel', 'Header', 'ColorCollection')


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

    def to_dict(self):
        final = {}
        for key, value in self.data.items():
            key = self._container.get(key)

            if key is not None:
                final[key] = value

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

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.data == other.data

    def set_id(self, directive: str):
        """Set ColorID of ``self`` according to the directive, e.g. ``BG`` or ``color:bg``."""
        self.edit(id=get_id(_get_dir(directive, 'color')))

    def set_color(self, color):
        """Set ``rgb`` of ``self`` to ``color``."""
        self.edit(**dict(zip('rgb', _define_color(color).to_rgb())))

    exec(_color_code)


def _process_color(color):
    if isinstance(color, ColorChannel):
        return color
    elif isinstance(color, dict):
        return ColorChannel.from_mapping(color)
    elif isinstance(color, str):
        return ColorChannel.from_string(color)


class ColorCollection(set):
    @classmethod
    def create(cls, colors: list):
        if isinstance(colors, cls):
            return colors.copy()

        self = cls()
        self.update(colors)

        return self

    def get(self, directive_or_id):
        final = directive_or_id
        if isinstance(final, str):
            final = get_id(_get_dir(final, 'color'))
        return search.get(self, id=final)

    def copy(self):
        return self.__class__(self)

    def update(self, colors):
        super().update(
            color for color in map(_process_color, colors)
            if color is not None)

    def add(self, color):
        color = _process_color(color)
        if color is not None:
            super().add(color)

    def __getitem__(self, c_id: int):
        return self.get(c_id)

    def dump(self):
        return [cc.data for cc in self]


class Header(Struct):
    _base_data = {
        'kA2': 0,
        'kA3': False,
        'kA4': 0,
        'kA6': 0,
        'kA7': 0,
        'kA8': False,
        'kA9': False,
        'kA10': False,
        'kA11': False,
        'kA13': 0,
        'kA14': [],
        'kA15': False,
        'kA16': False,
        'kA17': False,
        'kA18': 0,
        'kS38': ColorCollection(),
        'kS39': 0,
    }
    _dump = _header_dump
    _convert = _header_convert
    _collect = _header_collect

    def __init__(self, **properties):
        super().__init__(**properties)
        self.colorhook()

    def copy(self):
        header = super().copy()
        header.edit(colors=self.copy_colors())
        return header

    def copy_colors(self):
        return ColorCollection(color.copy() for color in (self.colors or list()))

    def colorhook(self):
        self.edit(colors=ColorCollection.create(self.colors or list()))

    @classmethod
    def from_mapping(cls, mapping):
        self = super().from_mapping(mapping)
        self.colorhook()
        return self

    def dump(self):
        header = self.copy()
        header.edit(colors=header.colors.dump())
        return super(type(header), header).dump()

    exec(_header_code)
