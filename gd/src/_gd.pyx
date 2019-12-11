# cython: language_level=3

from ..utils.crypto.coders import Coder
from ..utils.enums import NEnum
from ..api.hsv import HSV
from ..api.enums import *

from libcpp cimport bool

# MAIN HELPERS

cpdef object _try_convert(object obj, type cls = int):
    try:
        return cls(obj)
    except Exception:
        return obj


def _prepare(str s, str delim):
    cdef list sp = s.split(delim)
    return zip(sp[::2], sp[1::2])


cpdef dict _convert(str s, str delim = '_',bool attempt_conversion = True, f = None):
    cdef prepared = _prepare(s, delim)

    if f is None:
        # case: no convert func
        if attempt_conversion:
            return {_try_convert(key): value for key, value in prepared}

        return dict(prepared)

    if not attempt_conversion:
        # leave the keys untouched
        return {key: f(key, value) for key, value in prepared}

    cdef dict final = {}

    cdef str k
    cdef str v
    cdef object key
    for k, v in prepared:
        key = _try_convert(k)
        value = f(key, v)
        final[key] = value

    return final


cpdef dict _dump(dict d, dict additional = {}):
    cdef dict final = {}
    cdef str n
    cdef str value
    cdef object to_add 
    for n, value in d.items():
        to_add = _convert_type(value)

        if additional and n in additional:
            to_add = additional[n](to_add)

        final[n] = to_add

    return final


def _collect(dict d, str char = '_'):
    return char.join(char.join(map(str, pair)) for pair in d.items())


def _maybefloat(str s):
    if '.' in s:
        return float(s)
    return int(s)


cpdef bool _bool(str s):
    return s == '1'


cpdef set _ints_from_str(s, str split = '.'):
    if not string:
        return set()

    return set(map(int, string.split(split)))


cpdef str _iter_to_str(x):
    return ('.').join(map(str, x))


cpdef str _b64_failsafe(str string, bool encode = True):
    try:
        return Coder.do_base64(string, encode=encode)
    except Exception:
        return string

# OBJECT PARSING

cpdef set _INT = {
    1, 7, 8, 9, 12, 20, 21, 22, 23, 24, 25, 50, 51, 61, 71, 
    76, 77, 80, 95, 108
}

cpdef set _BOOL = {
    4, 5, 11, 13, 14, 15, 16, 17, 34, 36, 41, 42, 56, 58, 59, 60, 62, 64, 65,
    66, 67, 70, 78, 81, 86, 87, 89, 93, 94, 96, 98, 99, 100, 102, 103, 106
}

cpdef set _FLOAT = {
    2, 3, 6, 10, 28, 29, 32, 35, 45, 46, 47, 54, 63, 68, 69, 72, 73, 75,
    84, 85, 90, 91, 92, 97, 105, 107
}

cpdef set _HSV = {43, 44, 49}

cpdef int _TEXT = 31
cpdef int _GROUPS = 57

cpdef int _EASING = 30
cpdef int _PULSE_MODE = 48
cpdef int _PULSE_TYPE = 52
cpdef int _PICKUP_MODE = 79
cpdef int _TOUCH_TOGGLE = 82
cpdef int _COMP = 88
cpdef int _TARGET_COORDS = 101

cpdef dict _ENUMS = {
    _EASING: lambda n: Easing(int(n)),
    _PULSE_MODE: lambda n: PulseMode(int(n)),
    _PULSE_TYPE: lambda n: PulseType(int(n)),
    _PICKUP_MODE: lambda n: PickupItemMode(int(n)),
    _TOUCH_TOGGLE: lambda n: TouchToggleMode(int(n)),
    _COMP: lambda n: InstantCountComparison(int(n)),
    _TARGET_COORDS: lambda n: TargetPosCoordinates(int(n))
}

cpdef dict _OBJECT_ADDITIONAL = {
    _TEXT: lambda x: _b64_failsafe(x, encode=True)
}

cpdef object _object_convert(str s):
    return _convert(s, delim=',', attempt_conversion=True, f=_from_str)

cpdef dict _object_dump(dict d):
    return _dump(d, _OBJECT_ADDITIONAL)

cpdef str _object_collect(dict d):
    return _collect(d, ',')

def _from_str(int n, str v):
    return {
        n in _INT: int,
        n in _BOOL: _bool,
        n in _FLOAT: _maybefloat,
        n == _GROUPS: _ints_from_str,
        n in _HSV: HSV.from_string,
        n in _ENUMS: _ENUMS.get(n),
        n == _TEXT: lambda string: _b64_failsafe(string, encode=False)
    }.get(1, str)(v)


cpdef dict _MAPPING = {
    int: int,
    float: float,
    list: _iter_to_str,
    tuple: _iter_to_str,
    set: _iter_to_str,
    HSV: HSV.dump,
    NEnum: lambda enum: enum.value,
    str: str
}


def _convert_type(x):
    cdef type type_1
    cdef type type_2

    for type_1, type_2 in _MAPPING.items():
        if isinstance(x, type_1):
            return type_2(x)
    return str(x)

# COLOR PARSING

cpdef set _COLOR_INT = {1, 2, 3, 6, 9, 11, 12, 13}
cpdef set _COLOR_BOOL = {5, 8, 15, 17, 18}
cpdef int _COLOR_PLAYER = 4
cpdef int _COLOR_FLOAT = 7
cpdef int _COLOR_HSV = 10

def _parse_color(int n, str v):
    return {
        n in _COLOR_INT: int,
        n in _COLOR_BOOL: _bool,
        n == _COLOR_FLOAT: _maybefloat,
        n == _COLOR_HSV: HSV.from_string,
        n == _COLOR_PLAYER: lambda s: PlayerColor(int(s)),
    }.get(1, str)(v)

cpdef object _color_convert(str s):
    return _convert(s, delim='_', attempt_conversion=True, f=_parse_color)

cpdef dict _color_dump(dict d):
    return _dump(d)

cpdef str _color_collect(dict d):
    return _collect(d, '_')

# HEADER PARSING

def _process_header_colors(dict d):
    pass

cpdef object _convert_header(str s):
    return _convert(s, delim=',', attempt_conversion=False)


cpdef tuple __all__ = tuple(key for key in locals().keys() if key.startswith('_') and '__' not in key)
