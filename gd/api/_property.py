"""Automatic object property code generator."""

from .enums import *
from .parser import *
from .hsv import HSV

__all__ = ('_template', '_create', '_object_code', '_color_code', '_header_code')

_template = """
@property
def {name}(self):
    \"\"\":class:`{cls}`: Property ({desc}).\"\"\"
    return self.data.get({enum!r})
@{name}.setter
def {name}(self, value):
    self.data[{enum!r}] = value
""".strip('\n')

_container = '_container = {}'

_ENUMS = {
    _EASING: Easing,
    _PULSE_MODE: PulseMode,
    _PULSE_TYPE: PulseType,
    _PICKUP_MODE: PickupItemMode,
    _TOUCH_TOGGLE: TouchToggleMode,
    _COMP: InstantCountComparison,
    _TARGET_COORDS: TargetPosCoordinates
}


def _get_type(n, ts: str = 'object'):
    t = {
        'object': {
            n in _INT: int,
            n in _BOOL: bool,
            n in _FLOAT: float,
            n in _HSV: HSV,
            n in _ENUMS: _ENUMS.get(n),
            n == _TEXT: str,
            n == _GROUPS: set
        },
        'color': {
            n in _COLOR_INT: int,
            n in _COLOR_BOOL: bool,
            n == _COLOR_PLAYER: PlayerColor,
            n == _COLOR_FLOAT: float,
            n == _COLOR_HSV: HSV
        },
        'header': {
            n in _HEADER_INT: int,
            n in _HEADER_BOOL: bool,
            n == _HEADER_FLOAT: float,
            n in _HEADER_COLORS: 'ColorChannel',
            n == _COLORS: list,
            n == _GUIDELINES: list,
            n in _HEADER_ENUMS: _HEADER_ENUMS.get(n)
        }
    }
    r = t.get(ts, {}).get(1, str)

    try:
        return r.__name__
    except AttributeError:
        return r


def _create(enum, ts: str):
    final = []

    for name, value in enum.as_dict().items():
        desc = enum(value).desc
        cls = _get_type(value, ts=ts)
        final.append(_template.format(name=name, enum=value, desc=desc, cls=cls))

    property_container = {}

    for name, value in enum.as_dict().items():
        if value not in property_container:
            property_container[value] = name

    final.append(_container.format(property_container))

    return ('\n\n').join(final)


_object_code = _create(ObjectDataEnum, 'object')
_color_code = _create(ColorChannelProperties, 'color')
_header_code = _create(LevelHeaderEnum, 'header')
