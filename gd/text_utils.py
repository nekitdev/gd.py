import re

from gd.typing import AnyStr, Dict, Match, Optional, TypeVar

__all__ = (
    "make_repr",
    "object_count",
    "is_level_probably_decoded",
    "is_save_probably_decoded",
    "concat",
    "camel_to_snake",
    "snake_to_camel",
    "is_snake",
    "is_camel",
    "to_ordinal",
)

CAMEL_TO_SNAKE = re.compile(r"(?!^)([A-Z])")
SNAKE_TO_CAMEL = re.compile(r"(?!^)_([a-z])")
TEST_CAMEL = re.compile(r"(?:_*)[a-z]+(?:[A-Z][a-z0-9]+)*(?:_*)")
TEST_SNAKE = re.compile(r"(?:_*)(?:[a-z0-9]+_*)+(?:_*)")

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")

concat = "".join

_BYTE_LEVEL_DELIM = b";"

_LEVEL_DELIM = ";"

_HEADER_DELIM = ","


def is_level_probably_decoded(string: str) -> bool:
    return _LEVEL_DELIM in string or _HEADER_DELIM in string


_XML_OPEN_TAG = "<"
_XML_CLOSE_TAG = ">"


def is_save_probably_decoded(string: str) -> bool:
    return _XML_OPEN_TAG in string and _XML_CLOSE_TAG in string


def make_repr(some_object: T, info: Optional[Dict[K, V]] = None, delim: str = " ") -> str:
    """Create a nice representation of an object."""
    if info is None:
        info = {}

    name = some_object.__class__.__name__

    if not info:
        return f"<{name}>"

    formatted_info = delim.join(f"{key}={value}" for key, value in info.items())

    return f"<{name} {formatted_info}>"


def upper_first_group(match: Match) -> str:
    return match.group(1).upper()


def lower_first_group(match: Match) -> str:
    return "_" + match.group(1).lower()


def camel_to_snake(string: str) -> str:
    return CAMEL_TO_SNAKE.sub(lower_first_group, string).lower()


def snake_to_camel(string: str) -> str:
    return SNAKE_TO_CAMEL.sub(upper_first_group, string)


def is_camel(string: str) -> bool:
    return TEST_CAMEL.fullmatch(string) is not None


def is_snake(string: str) -> bool:
    return TEST_SNAKE.fullmatch(string) is not None


def object_count(string: AnyStr, has_header: bool = True) -> int:
    delim = _LEVEL_DELIM if isinstance(string, str) else _BYTE_LEVEL_DELIM
    count = string.strip(delim).count(delim) - has_header
    return 0 if count < 0 else count


ORDINAL_SUFFIXES = ("th", "st", "nd", "rd", "th")


def to_ordinal(number: int) -> str:
    suffix = ORDINAL_SUFFIXES[min(number % 10, 4)]

    if 11 <= (number % 100) <= 13:
        suffix = "th"

    return f"{number}{suffix}"
