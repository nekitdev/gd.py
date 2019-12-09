"""Automatic object property code generator."""

from .enums import *
from .parser import *
from .hsv import HSV

__all__ = ('_template', '_create', '_object_code', '_color_code')

_template = """
@property
def {name}(self):
    \"\"\":class:`{cls}`: Property -> {desc}.\"\"\"
    return self.data.get({enum})
@{name}.setter
def {name}(self, value):
    self.data[{enum}] = value
""".strip('\n')

_properties = "existing_properties = {}"


def _get_type(n, as_string: bool = True, _type: str = 'object'):
    t = {
        'object': {
            n in _INT: int,
            n in _BOOL: bool,
            n in _FLOAT: float,
            n in _HSV: HSV,
            n in _ENUMS: _ENUMS.get(n),
            n in (_GROUPS, _TEXT): str
        },
        'color': {
            n in _COLOR_INT: int,
            n in _COLOR_BOOL: bool,
            n == _COLOR_PLAYER: PlayerColor,
            n == _COLOR_FLOAT: float,
            n == _COLOR_HSV: HSV
        },
        'header': {}
    }
    r = t.get(_type, {}).get(1, str)
    return r.__name__ if as_string else r


def _create(enum, _type: str):
    final = []

    for name, value in enum.as_dict().items():
        desc = enum(value).desc
        cls = _get_type(value, _type=_type)
        final.append(_template.format(name=name, enum=value, desc=desc, cls=cls))

    property_container = {}

    for name, value in enum.as_dict().items():
        if value not in property_container:
            property_container[value] = name

    properties = list(property_container.values())
    final.append(_properties.format(properties))

    return ('\n'*2).join(final)

_object_code = _create(ObjectDataEnum, 'object')
_color_code = _create(ColorChannelProperties, 'color')
