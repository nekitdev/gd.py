from itertools import chain

from enums import Enum

from gd.typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Set,
    Type,
    TypeVar,
    Tuple,
    Union,
)

from gd.utils.enums import LevelLength
from gd.utils.crypto.coders import Coder

from gd.api.guidelines import Guidelines
from gd.api.hsv import HSV
from gd.api.enums import (
    ZLayer,
    Easing,
    PulseMode,
    PulseType,
    PickupItemMode,
    TouchToggleMode,
    InstantCountComparison,
    TargetPosCoordinates,
    PlayerColor,
    Gamemode,
    LevelType,
    Speed,
)

T = TypeVar("T")
U = TypeVar("U")

# MAIN HELPERS


def _identity(any_object: T) -> T:
    return any_object


def _try_convert(py_object: T, cls: Type[U] = int) -> Union[T, U]:
    try:
        return cls(py_object)
    except Exception:
        return py_object


def _prepare(string: str, delim: str) -> Iterator[Tuple[str, str]]:
    str_iter = iter(string.split(delim))
    return zip(str_iter, str_iter)


def _convert(
    string: str, delim: str = "_", *, func: Optional[Callable[[str], T]] = None
) -> Dict[str, Union[str, T]]:
    prepared = _prepare(string, delim)

    if func is None:
        # case: no convert func
        return dict(prepared)

    return {key: func(key, value) for key, value in prepared}


def _dump(
    some_dict: Dict[str, T], additional: Optional[Dict[str, Callable[[T], U]]] = None
) -> Dict[str, Union[T, U]]:
    if additional is None:
        return {key: _convert_type(value) for key, value in some_dict.items()}

    else:
        return {
            key: additional.get(key, _identity)(_convert_type(value))
            for key, value in some_dict.items()
        }


def _collect(some_dict: Dict[T, U], char: str = "_"):
    return char.join(map(str, chain.from_iterable(some_dict.items())))


def _maybefloat(string: str) -> Union[float, int]:
    if "." in string:
        return float(string)
    return int(string)


def _bool(string: str) -> bool:
    return string == "1"


def _ints_from_str(string: str, split: str = ".") -> Set[int]:
    if not string:
        return set()

    return set(map(int, string.split(split)))


def _iter_to_str(some_iter: Iterable[Any]) -> str:
    char = "."

    try:
        first_type = type(next(iter(some_iter)))

    except StopIteration:
        pass

    else:
        if first_type is dict:
            char = "|"
            some_iter = (_collect(_dump(elem)) for elem in some_iter)

    return char.join(map(str, some_iter))


def _b64_failsafe(string: str, encode: bool = True) -> str:
    try:
        return Coder.do_base64(string, encode=encode)
    except Exception:
        return string


# OBJECT PARSING

_INT = {
    "1",
    "7",
    "8",
    "9",
    "12",
    "20",
    "21",
    "22",
    "23",
    "24",
    "25",
    "50",
    "51",
    "61",
    "71",
    "76",
    "77",
    "80",
    "95",
    "108",
}

_BOOL = {
    "4",
    "5",
    "11",
    "13",
    "14",
    "15",
    "16",
    "17",
    "34",
    "36",
    "41",
    "42",
    "56",
    "58",
    "59",
    "60",
    "62",
    "64",
    "65",
    "66",
    "67",
    "70",
    "78",
    "81",
    "86",
    "87",
    "89",
    "93",
    "94",
    "96",
    "98",
    "99",
    "100",
    "102",
    "103",
    "106",
}

_FLOAT = {
    "2",
    "3",
    "6",
    "10",
    "28",
    "29",
    "32",
    "35",
    "45",
    "46",
    "47",
    "54",
    "63",
    "68",
    "69",
    "72",
    "73",
    "75",
    "84",
    "85",
    "90",
    "91",
    "92",
    "97",
    "105",
    "107",
}

_HSV = {"43", "44", "49"}

_TEXT = "31"
_GROUPS = "57"

_Z_LAYER = "24"
_EASING = "30"
_PULSE_MODE = "48"
_PULSE_TYPE = "52"
_PICKUP_MODE = "79"
_TOUCH_TOGGLE = "82"
_COMP = "88"
_TARGET_COORDS = "101"

_ENUMS = {
    _Z_LAYER: ZLayer,
    _EASING: Easing,
    _PULSE_MODE: PulseMode,
    _PULSE_TYPE: PulseType,
    _PICKUP_MODE: PickupItemMode,
    _TOUCH_TOGGLE: TouchToggleMode,
    _COMP: InstantCountComparison,
    _TARGET_COORDS: TargetPosCoordinates,
}

_OBJECT_ADDITIONAL = {_TEXT: lambda text: _b64_failsafe(text, encode=True)}


def _object_convert(string: str) -> Dict[str, Any]:
    return _convert(string, delim=",", func=_from_str)


def _object_dump(some_dict: Dict[str, T]) -> Dict[str, Union[T, U]]:
    return _dump(some_dict, _OBJECT_ADDITIONAL)


def _object_collect(some_dict: Dict[T, U]) -> str:
    return _collect(some_dict, ",")


def _from_str(key: str, value: str) -> Any:
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


_MAPPING = {
    bool: int,
    list: _iter_to_str,
    tuple: _iter_to_str,
    set: _iter_to_str,
    dict: _iter_to_str,
    Guidelines: Guidelines.dump,
    HSV: HSV.dump,
}


def _convert_type(some_object: T) -> Union[T, U]:
    some_type = some_object.__class__
    if some_type in _MAPPING:
        return _MAPPING[some_type](some_object)
    elif Enum in some_type.__mro__:
        return some_object.value
    return some_object


# COLOR PARSING

_COLOR_INT = {"1", "2", "3", "6", "9", "11", "12", "13"}
_COLOR_BOOL = {"5", "8", "15", "17", "18"}
_COLOR_PLAYER = "4"
_COLOR_FLOAT = "7"
_COLOR_HSV = "10"


def _parse_color(key: str, value: str) -> Any:
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


def _color_convert(string: str) -> Dict[str, Any]:
    return _convert(string, delim="_", func=_parse_color)


def _color_dump(some_dict: Dict[str, T]) -> Dict[str, Union[T, U]]:
    return _dump(some_dict)


def _color_collect(some_dict: Dict[T, U]) -> str:
    return _collect(some_dict, "_")


# HEADER PARSING

_HEADER_INT = {
    "kA1",
    "kA6",
    "kA7",
    "kA18",  # TODO: add related enums
    "kS1",
    "kS2",
    "kS3",
    "kS4",
    "kS5",
    "kS6",
    "kS7",
    "kS8",
    "kS9",
    "kS10",
    "kS11",
    "kS12",
    "kS13",
    "kS14",
    "kS15",
    "kS16",
    "kS17",
    "kS18",
    "kS19",
    "kS20",
    "kS39",
}
_HEADER_BOOL = {"kA3", "kA5", "kA8", "kA9", "kA10", "kA11", "kA15", "kA16", "kA17"}
_HEADER_FLOAT = "kA13"
_HEADER_COLORS = {"kS29", "kS30", "kS31", "kS32", "kS33", "kS34", "kS35", "kS36", "kS37"}

_COLORS = "kS38"
_GUIDELINES = "kA14"

_GAMEMODE = "kA2"
_SPEED = "kA4"

_HEADER_ENUMS = {
    _GAMEMODE: Gamemode,
    _SPEED: Speed,
}


def _parse_header(key: str, value: str) -> Any:
    if key in _HEADER_INT:
        return int(value)
    if key in _HEADER_BOOL:
        return _bool(value)
    if key in _HEADER_ENUMS:
        return _HEADER_ENUMS[key](int(value))
    if key == _COLORS:
        return _parse_colors(value)
    if key == _HEADER_FLOAT:
        return _maybefloat(value)
    if key in _HEADER_COLORS:
        from gd.api.struct import ColorChannel  # HACK: circular imports

        return ColorChannel.from_mapping(_color_convert(value))
    if key == _GUIDELINES:
        return _parse_guidelines(value)
    return value


def _dump_header_part(key: str, value: Any) -> Any:
    if key in _HEADER_COLORS:
        try:
            return value.dump()
        except AttributeError:
            return value
    return value


def _parse_colors(string: str, delim: str = "|") -> List[Any]:
    return list(filter(bool, map(_color_convert, string.split(delim))))


def _parse_guidelines(string: str, delim: str = "~"):
    float_iter = map(float, filter(bool, string.split(delim)))
    return Guidelines.new(zip(float_iter, float_iter))


def _header_convert(string: str) -> Dict[str, Any]:
    return _convert(string, delim=",", func=_parse_header)


def _header_dump(some_dict: Dict[str, T]) -> Dict[str, Union[T, U]]:
    return _dump({key: _dump_header_part(key, value) for key, value in some_dict.items()})


def _header_collect(some_dict: Dict[T, U]) -> str:
    return _collect(some_dict, ",")


# LEVEL API

_DESC = "k3"
_SPECIAL = "k67"
_CRYPTED = {"k4", "k34"}
_TAB = "kI6"
_LEVEL_TYPE = "k21"
_LEVEL_LENGTH = "k23"
_LEVEL_ENUMS = {
    _LEVEL_TYPE: LevelType,
    _LEVEL_LENGTH: LevelLength,
}


def _parse_into_array(string: str, delim: str = "_") -> List[int]:
    return list(map(int, filter(bool, string.split(delim))))


def _join_into_string(array: List[int], delim: str = "_") -> str:
    return delim.join(map(str, array))


def _attempt_zip(string: str) -> str:
    unzip = all(char not in string for char in "|;,.")  # O(m*n)

    try:
        if unzip:
            return Coder.unzip(string)

        return Coder.zip(string)

    except Exception:
        return string


def _level_dump(some_dict: Dict[str, T]) -> Dict[str, U]:
    return {key: _dump_entry(key, value) for key, value in some_dict.items()}


def _dump_entry(key: str, value: Any) -> Union[str, Dict[str, str]]:
    if key == _SPECIAL:
        return _join_into_string(value)
    if key in _CRYPTED:
        return _attempt_zip(value)
    if key == _DESC:
        return _b64_failsafe(value, encode=True)
    if key == _TAB:
        return {str(key): str(other_value) for key, other_value in value.items()}
    if key in _LEVEL_ENUMS:
        try:
            return value.value
        except AttributeError:
            pass
    return value


def _process_entry(key: str, value: str) -> Any:
    if key == _SPECIAL:
        return _parse_into_array(value)
    if key in _CRYPTED:
        return _attempt_zip(value)
    if key == _DESC:
        return _b64_failsafe(value, encode=False)
    if key == _TAB:
        return {int(key): int(other_value) for key, other_value in value.items()}
    if key in _LEVEL_ENUMS:
        return _LEVEL_ENUMS[key](int(value))
    return value


def _process_level(some_dict: Dict[str, T]) -> Dict[str, U]:
    return {key: _process_entry(key, value) for key, value in some_dict.items()}


# LOAD ACCELERATOR

try:
    import _gdc

    locals().update(_gdc.__dict__)  # hacky insertion yay
except ImportError:
    pass  # can not import? kden

# add all _private_stuff
__all__ = tuple(key for key in locals().keys() if key.startswith("_") and "__" not in key)
