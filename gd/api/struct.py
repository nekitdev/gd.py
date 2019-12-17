from ..utils.wrap_tools import make_repr
from ..colors import Color
from ..errors import EditorError

from .hsv import HSV
from .parser import *
from ._property import _object_code, _color_code

__all__ = ('Object', 'ColorChannel', 'Header', 'supported', 'get_id')

mapping = {
    'special': SpecialBlockType,
    'trigger': TriggerType,
    'portal': PortalType,
    'orb': OrbType,
    'pad': PadType,
    'easing': Easing,
    'layer': ZLayer
}

supported = {name: enum.as_dict() for name, enum in mapping.items()}

d = supported.get('portal')
for i, s in zip(range(5), ('slow', 'normal', 'fast', 'faster', 'fastest')):
    d.update({'speed:x{}'.format(i): 'portal:{}speed'.format(s)})
del i, s, d


def _get_dir(directive: str, cls: str, delim: str = ':'):
    return delim.join((cls, directive.split(delim).pop()))


def get_id(x: str, ret_enum: bool = False, delim: str = ':'):
    """Calculate required value from the given directive ``x``.

    The format is, as follows: ``class:name``, e.g. ``special:h``.

    Parameters
    ----------
    x: :class:`str`
        Directive to get value from.

    ret_enum: :class:`bool`
        Whether to convert found value to enum. By default, ``False``.

    delim: :class:`str`
        Character to split given directive string with.
        It is not recommended to pass this argument to the function.

    Returns
    -------
    `Any`
        The value found, if any.

    Raises
    ------
    :exc:`.EditorError`
        Failed to convert directive to the value.
    """
    typeof, name = (
        string.strip().replace('_', '').lower()
        for string in x.split(delim, maxsplit=1)
    )

    try:
        found = supported[typeof][name]

        if isinstance(found, str) and delim in found:
            # inner directive
            return get_id(found)

        elif ret_enum:
            return mapping[typeof](found)

        return found

    except Exception:
        raise EditorError('ID by directive {!r} was not found.'.format(x)) from None


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

    def set_id(self, directive: str):
        """Set ``id`` of ``self`` according to the directive, e.g. ``trigger:move``.""
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
