from ..utils.crypto.coders import Coder
from ..utils.enums import NEnum

from .hsv import HSV
from .enums import *

# MAIN HELPERS

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
        for pair in d.items():
            yield from map(str, pair)
    return char.join(generator())


def _maybefloat(s: str):
    if '.' in s:
        return float(s)
    return int(s)


def _bool(s: str):
    return s == '1'


def _ints_from_str(string: str, split: str = '.'):
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

# OBJECT PARSING

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

def _object_collect(d):
    return _collect(d, ',')


def _from_str(n: int, v: str):
    if n in _INT:
        return int(v)
    if n in _BOOL:
        return _bool(v)
    if n in _FLOAT:
        return _maybefloat(v)
    if n == _GROUPS:
        return _ints_from_str(v)
    if n in _HSV:
        return HSV.from_string(v)
    if n in _ENUMS:
        return _ENUMS.get(n)(v)
    if n == _TEXT:
        return _b64_failsafe(v, encode=False)
    return v


_MAPPING = {
    list: _iter_to_str,
    tuple: _iter_to_str,
    set: _iter_to_str,
    HSV: HSV.dump,
    NEnum: lambda enum: enum.value
}

_KEYS = set(_MAPPING)

def _convert_type(x: object):
    t = type(x)
    if t in _KEYS:
        return _MAPPING[t](x)
    return x

# COLOR PARSING

_COLOR_INT = {1, 2, 3, 6, 9, 11, 12, 13}
_COLOR_BOOL = {5, 8, 15, 17, 18}
_COLOR_PLAYER = 4
_COLOR_FLOAT = 7
_COLOR_HSV = 10

def _parse_color(n: int, v: str):
    if n in _COLOR_INT:
        return int(v)
    if n in _COLOR_BOOL:
        return _bool(v)
    if n == _COLOR_FLOAT:
        return _maybefloat(v)
    if n == _COLOR_HSV:
        return HSV.from_string(v)
    if n == _COLOR_PLAYER:
        return PlayerColor(int(v))
    return v

def _color_convert(s):
    return _convert(s, delim=('_'), attempt_conversion=True, f=_parse_color)

def _color_dump(d):
    return _dump(d)

def _color_collect(d):
    return _collect(d, '_')

# HEADER PARSING

def _process_header_colors(d):
    pass

def _convert_header(s):
    return _convert(s, delim=(','), attempt_conversion=False)

# LOAD ACCELERATOR

try:
    # attempt to load all functions from acceleator module
    import _gd
    locals().update(_gd.__dict__)  # hacky insertion

except ImportError:
    pass


__all__ = tuple(key for key in locals().keys() if key.startswith('_') and '__' not in key)
