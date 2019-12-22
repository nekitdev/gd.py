# distutils: language=c++
# cython: language_level=3

from gd.utils.crypto.coders import Coder
from gd.utils.enums import NEnum
from gd.api.hsv import HSV
from gd.api.enums import *

from itertools import chain

from libcpp cimport bool

# MAIN HELPERS

cdef _try_convert(object obj, type cls = int):
    try:
        return cls(obj)
    except Exception:
        return obj


cdef _prepare(str s, str delim):
    split = s.split(delim)
    return zip(split[::2], split[1::2])


cpdef dict _convert(str s, str delim = '_', bool attempt_conversion = True, object f = None):
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


cpdef _dump(dict d, dict additional = None):
    final = {}

    for n, value in d.items():
        to_add = _convert_type(value)

        if additional and n in additional:
            to_add = additional[n](to_add)

        final[n] = to_add

    return final


cpdef _collect(dict d, str char = '_'):
    return char.join(map(str, chain.from_iterable(d.items())))


cdef _maybefloat(str s):
    if '.' in s:
        return float(s)
    return int(s)


cdef bool _bool(str s):
    return s == '1'


cdef set _ints_from_str(str string, str split = '.'):
    if not string:
        return set()

    return set(map(int, string.split(split)))


cpdef _iter_to_str(x):
    cdef str char = '.'

    try:
        elem = next(iter(x))
    except StopIteration:
        pass

    else:
        t = type(elem)

        if t is float:
            char = '~0~'

        elif t is dict:
            char = '|'

            s = []
            for d in x:
                s.append(_collect(_dump(d)))
            x = s

    return char.join(map(str, x))


cdef str _b64_failsafe(str string, bool encode = True):
    try:
        return Coder.do_base64(string, encode=encode)
    except Exception:
        return string

# OBJECT PARSING

cdef set _INT = {
    1, 7, 8, 9, 12, 20, 21, 22, 23, 24, 25, 50, 51, 61, 71, 
    76, 77, 80, 95, 108
}

cdef set _BOOL = {
    4, 5, 11, 13, 14, 15, 16, 17, 34, 36, 41, 42, 56, 58, 59, 60, 62, 64, 65,
    66, 67, 70, 78, 81, 86, 87, 89, 93, 94, 96, 98, 99, 100, 102, 103, 106
}

cdef set _FLOAT = {
    2, 3, 6, 10, 28, 29, 32, 35, 45, 46, 47, 54, 63, 68, 69, 72, 73, 75,
    84, 85, 90, 91, 92, 97, 105, 107
}

cdef set _HSV = {43, 44, 49}

cdef int _TEXT = 31
cdef int _GROUPS = 57

cdef int _Z_LAYER = 24
cdef int _EASING = 30
cdef int _PULSE_MODE = 48
cdef int _PULSE_TYPE = 52
cdef int _PICKUP_MODE = 79
cdef int _TOUCH_TOGGLE = 82
cdef int _COMP = 88
cdef int _TARGET_COORDS = 101

cdef dict _ENUMS = {
    _Z_LAYER: ZLayer,
    _EASING: Easing,
    _PULSE_MODE: PulseMode,
    _PULSE_TYPE: PulseType,
    _PICKUP_MODE: PickupItemMode,
    _TOUCH_TOGGLE: TouchToggleMode,
    _COMP: InstantCountComparison,
    _TARGET_COORDS: TargetPosCoordinates
}

cdef dict _OBJECT_ADDITIONAL = {
    _TEXT: lambda x: _b64_failsafe(x, encode=True)
}

cpdef dict _object_convert(str s):
    return _convert(s, delim=',', attempt_conversion=True, f=_from_str)

cpdef dict _object_dump(dict d):
    return _dump(d, _OBJECT_ADDITIONAL)

cpdef str _object_collect(dict d):
    return _collect(d, ',')


cdef _from_str(int n, str v):
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
        return _ENUMS[n](int(v))
    if n == _TEXT:
        return _b64_failsafe(v, encode=False)
    return v


cdef dict _MAPPING = {
    type(True): int,
    list: _iter_to_str,
    tuple: _iter_to_str,
    set: _iter_to_str,
    HSV: HSV.dump
}

cdef set _KEYS = {k for k in _MAPPING}

cdef _convert_type(object x):
    t = x.__class__
    if t in _KEYS:
        return _MAPPING[t](x)
    elif NEnum in t.__mro__:
        return x.value
    return x

# COLOR PARSING

cdef set _COLOR_INT = {1, 2, 3, 6, 9, 11, 12, 13}
cdef set _COLOR_BOOL = {5, 8, 15, 17, 18}
cdef int _COLOR_PLAYER = 4
cdef int _COLOR_FLOAT = 7
cdef int _COLOR_HSV = 10

cdef _parse_color(int n, str v):
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

cpdef dict _color_convert(str s):
    return _convert(s, delim='_', attempt_conversion=True, f=_parse_color)

cpdef dict _color_dump(dict d):
    return _dump(d)

cpdef str _color_collect(dict d):
    return _collect(d, '_')
