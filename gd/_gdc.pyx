# distutils: language=c++
# cython: language_level=3

from gd.utils.crypto.coders import Coder
from gd.api.guidelines import Guidelines
from gd.api.hsv import HSV
from gd.api.enums import *

from itertools import chain

from enums import Enum

from libcpp cimport bool


# MAIN HELPERS

cdef object _identity(object some_object):
    return some_object


cdef object _try_convert(object some_object, type some_class = int):
    try:
        return some_class(some_object)
    except Exception:
        return some_object


cdef object _prepare(str string, str delim):
    some_iter = iter(string.split(delim))
    return zip(some_iter, some_iter)


cpdef dict _convert(str string, str delim = "_", object func = None):
    prepared = _prepare(string, delim)

    if func is None:
        return dict(prepared)

    return {key: func(key, value) for key, value in prepared}


cpdef dict _dump(dict some_dict, dict additional = {}):
    return {
        key: additional.get(key, _identity)(_convert_type(value))
        for key, value in some_dict.items()
    }


cpdef str _collect(dict some_dict, str char = "_"):
    return char.join(map(str, chain.from_iterable(some_dict.items())))


cdef object _maybefloat(str string):
    if "." in string:
        return float(string)
    return int(string)


cdef bool _bool(str string):
    return string == "1"


cdef set _ints_from_str(str string, str split = "."):
    if not string:
        return set()

    return set(map(int, string.split(split)))


cpdef str _iter_to_str(object some_iter):
    cdef str char = "."

    try:
        first_type = type(next(iter(some_iter)))

    except StopIteration:
        pass

    else:
        if first_type is dict:
            char = "|"

            some_iter = [_collect(_dump(elem)) for elem in some_iter]

    return char.join(map(str, some_iter))


cdef str _b64_failsafe(str string, bool encode = True):
    try:
        return Coder.do_base64(string, encode=encode)
    except Exception:
        return string


# OBJECT PARSING

cdef set _INT = {
    "1", "7", "8", "9", "12", "20", "21", "22", "23", "24", "25", "50", "51", "61", "71",
    "76", "77", "80", "95", "108"
}

cdef set _BOOL = {
    "4", "5", "11", "13", "14", "15", "16", "17", "34", "36", "41", "42", "56", "58", "59", "60", "62", "64", "65",
    "66", "67", "70", "78", "81", "86", "87", "89", "93", "94", "96", "98", "99", "100", "102", "103", "106"
}

cdef set _FLOAT = {
    "2", "3", "6", "10", "28", "29", "32", "35", "45", "46", "47", "54", "63", "68", "69", "72", "73", "75",
    "84", "85", "90", "91", "92", "97", "105", "107"
}

cdef set _HSV = {"43", "44", "49"}

cdef str _TEXT = "31"
cdef str _GROUPS = "57"

cdef str _Z_LAYER = "24"
cdef str _EASING = "30"
cdef str _PULSE_MODE = "48"
cdef str _PULSE_TYPE = "52"
cdef str _PICKUP_MODE = "79"
cdef str _TOUCH_TOGGLE = "82"
cdef str _COMP = "88"
cdef str _TARGET_COORDS = "101"

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
    _TEXT: lambda text: _b64_failsafe(text, encode=True)
}

cpdef dict _object_convert(str string):
    return _convert(string, delim=",", func=_from_str)

cpdef dict _object_dump(dict some_dict):
    return _dump(some_dict, _OBJECT_ADDITIONAL)

cpdef str _object_collect(dict some_dict):
    return _collect(some_dict, ",")


cdef object _from_str(str key, str value):
    if key in _INT:
        return int(value)
    if key in _BOOL:
        return _bool(value)
    if key in _FLOAT:
        return _maybefloat(value)
    if key == _GROUPS:
        return _ints_from_str(value)
    if key in _HSV:
        return HSV.from_string(value)
    if key in _ENUMS:
        return _ENUMS[key](int(value))
    if key == _TEXT:
        return _b64_failsafe(value, encode=False)
    return value


cdef dict _MAPPING = {
    type(True): int,
    list: _iter_to_str,
    tuple: _iter_to_str,
    set: _iter_to_str,
    dict: _iter_to_str,
    Guidelines: Guidelines.dump,
    HSV: HSV.dump
}

cdef object _convert_type(object some_object):
    some_type = some_object.__class__
    if some_type in _MAPPING:
        return _MAPPING[some_type](some_object)
    elif Enum in some_type.__mro__:
        return some_object.value
    return some_object


# COLOR PARSING

cdef set _COLOR_INT = {"1", "2", "3", "6", "9", "11", "12", "13"}
cdef set _COLOR_BOOL = {"5", "8", "15", "17", "18"}
cdef str _COLOR_PLAYER = "4"
cdef str _COLOR_FLOAT = "7"
cdef str _COLOR_HSV = "10"


cdef object _parse_color(str key, str value):
    if key in _COLOR_INT:
        return int(value)
    if key in _COLOR_BOOL:
        return _bool(value)
    if key == _COLOR_FLOAT:
        return _maybefloat(value)
    if key == _COLOR_HSV:
        return HSV.from_string(value)
    if key == _COLOR_PLAYER:
        return PlayerColor(int(value))
    return value


cpdef dict _color_convert(str string):
    return _convert(string, delim="_", func=_parse_color)


cpdef dict _color_dump(dict some_dict):
    return _dump(some_dict)


cpdef str _color_collect(dict some_dict):
    return _collect(some_dict, "_")


cdef str _byte_xor(char* stream, char key):
    return bytes(byte ^ key for byte in stream).decode(errors="ignore")


cpdef str byte_xor(bytes stream, int key):
    return _byte_xor(stream, key)


Coder.byte_xor = staticmethod(byte_xor)
