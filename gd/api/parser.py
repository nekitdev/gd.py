from ..utils.crypto.coders import Coder
from ..utils.enums import NEnum

from .hsv import HSV
from .enums import *

# MAIN HELPERS

def _get_name(n, mapping: dict = None):
    try:
        return mapping[n]

    except Exception:
        return ('unknown_' + str(n).replace('-', '_'))


def _load(d, mapping: dict = None):
    return {_get_name(n, mapping): value for n, value in d.items()}


def _try_convert(obj, cls: type = int):
    try:
        return cls(obj)
    except Exception:
        return obj


def _prepare(s, delim: str):
    s = s.split(delim)
    return zip(s[::2], s[1::2])


def _convert(s, delim: str = '_', attempt_conversion: bool = True, *, f=None):
    prepared = _prepare(s, delim)

    if f is None:
        # case: no convert func
        if attempt_conversion:
            return {_try_convert(key): value for key, value in prepared}

        return dict(prepared)

    if not attempt_conversion:
        # leave the keys untouched
        return {key: f(key, value) for key, value in prepared}

    final = {}

    for key, value in prepared:
        key = _try_convert(key)
        final[key] = f(key, value)

    return final


def _get_id(name: str, mapping: dict = None, return_name_on_fail: bool = False):
    try:
        if name.startswith('_'):
            name = name[1:]

        return mapping[name]

    except KeyError:
        if name.startswith('unknown'):
            name = name[7:]

            if name.startswith('_'):
                name = name[1:]

        try:
            return int(name.replace('_', '-'))

        except ValueError:
            if return_name_on_fail:
                return name


def _dump(d, additional: dict = None):
    final = {}

    for n, value in d.items():
        to_add = _convert_type(value)

        if additional and n in additional:
            to_add = additional[n](to_add)

        final[n] = to_add

    return final


def _collect(d, char: str = '_'):
    def generator():
        for key, value in d.items():
            yield from map(str, (key, value))

    return char.join(generator())


def _maybefloat(s: str):
    if '.' in s:
        return float(s)
    return int(s)


def _bool(s: str):
    return s == '1'


def _ints_from_str(string: str, split: str = '.'):
    string = str(string)  # just in case

    if not string:
        return set()

    return set(map(int, string.split(split)))


def _iter_to_str(x):
    return ('.').join(map(str, x))


def _b64_failsafe(string: str, encode: bool = True):
    try:
        return Coder.do_base64(string, encode=encode)
    except Exception:
        return string

# ENUM HELPER

def _make_dicts(enum: NEnum):
    name_to_value = enum.as_dict()
    value_to_name = {v: k for k, v in name_to_value.items()}
    return value_to_name, name_to_value

# OBJECT PARSING

_MAP_ID, _MAP_NAME = _make_dicts(ObjectDataEnum)

_INT = {
    1, 7, 8, 9, 12, 20, 21, 22, 23, 24, 25, 50, 51, 61, 71, 
    76, 77, 80, 95, 108
}

_BOOL = {
    4, 5, 11, 13, 14, 15, 16, 17, 34, 36, 41, 42, 56, 58, 59, 60, 62, 64, 65,
    66, 67, 70, 78, 81, 86, 87, 89, 93, 94, 96, 98, 99, 100, 102, 103, 106
}

_FLOAT = {
    2, 3, 6, 10, 28, 29, 32, 35, 45, 46, 47, 54, 63, 68, 69, 72, 73, 75,
    84, 85, 90, 91, 92, 97, 105, 107
}

_HSV = {43, 44, 49}

_TEXT = 31
_GROUPS = 57

_EASING = 30
_PULSE_MODE = 48
_PULSE_TYPE = 52
_PICKUP_MODE = 79
_TOUCH_TOGGLE = 82
_COMP = 88
_TARGET_COORDS = 101

_ENUMS = {
    _EASING: lambda n: Easing(int(n)),
    _PULSE_MODE: lambda n: PulseMode(int(n)),
    _PULSE_TYPE: lambda n: PulseType(int(n)),
    _PICKUP_MODE: lambda n: PickupItemMode(int(n)),
    _TOUCH_TOGGLE: lambda n: TouchToggleMode(int(n)),
    _COMP: lambda n: InstantCountComparison(int(n)),
    _TARGET_COORDS: lambda n: TargetPosCoordinates(int(n))
}

_OBJECT_ADDITIONAL = {
    _TEXT: lambda x: _b64_failsafe(x, encode=True)
}

def _object_convert(s):
    return _convert(s, delim=(','), attempt_conversion=True, f=_from_str)

def _object_dump(d):
    return _dump(d, _OBJECT_ADDITIONAL)

def _object_get_name(n: int):
    return _get_name(n, _MAP_ID)

def _object_get_id(name: str):
    return _get_id(name, _MAP_NAME)

def _object_load(d):
    return _load(d, _MAP_ID)

def _object_collect(d):
    return _collect(d, ',')

def _from_str(n: int, v: str):
    return {
        n in _INT: int,
        n in _BOOL: _bool,
        n in _FLOAT: _maybefloat,
        n == _GROUPS: _ints_from_str,
        n in _HSV: HSV.from_string,
        n in _ENUMS: _ENUMS.get(n),
        n == _TEXT: lambda string: _b64_failsafe(string, encode=False)
    }.get(1, str)(v)


_MAPPING = {
    int: int,
    float: float,
    list: _iter_to_str,
    tuple: _iter_to_str,
    set: _iter_to_str,
    HSV: HSV.dump,
    NEnum: lambda enum: enum.value,
    str: str
}


def _convert_type(x: type):
    for type_1, type_2 in _MAPPING.items():
        if isinstance(x, type_1):
            return type_2(x)
    return str(x)

# COLOR PARSING

_MAP_COLOR_PROPERTY, _MAP_COLOR_NAME = _make_dicts(ColorChannelProperties)

_COLOR_INT = {1, 2, 3, 9, 11, 12, 13}
_COLOR_BOOL = {5, 8, 15, 17, 18}
_COLOR_PLAYER = 4
_COLOR_FLOAT = 7
_COLOR_HSV = 10

def _parse_color(n: int, v: str):
    return {
        n in _COLOR_INT: int,
        n in _COLOR_BOOL: _bool,
        n == _COLOR_FLOAT: _maybefloat,
        n == _COLOR_HSV: HSV.from_string,
        n == _COLOR_PLAYER: lambda s: PlayerColor(int(s)),
    }.get(1, str)(v)

def _color_convert(s):
    return _convert(s, delim=('_'), attempt_conversion=True, f=_parse_color)

def _color_dump(d):
    return _dump(d)

def _color_get_name(n: int):
    return _get_name(n, _MAP_COLOR_PROPERTY)

def _color_get_id(name: str):
    return _get_id(name, _MAP_COLOR_NAME)

def _color_load(d):
    return _load(d, _MAP_COLOR_PROPERTY)

def _color_collect(d):
    return _collect(d, '_')

# HEADER PARSING

_MAP_LEVEL_PROPERTY, _MAP_LEVEL_NAME = _make_dicts(LevelDataEnum)

def _convert_header(s):
    return _convert(s, delim=(','), attempt_conversion=False)


__all__ = tuple(key for key in locals().keys() if key.startswith('_') and '__' not in key)
