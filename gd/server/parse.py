import re
from typing import AbstractSet, Any, Iterable, Optional, Type, TypeVar

from gd.enums import Enum
from gd.errors import InternalError
from gd.string_constants import COMMA
from gd.string_utils import tick
from gd.typing import Parse

__all__ = ("parse_bool", "parse_enum", "parse_pages")


TRUE = frozenset(("yes", "y", "true", "t", "1"))
FALSE = frozenset(("no", "n", "false", "f", "0"))

CAN_NOT_CONVERT = "can not convert {} to bool"


def parse_bool(string: str, true: AbstractSet[str] = TRUE, false: AbstractSet[str] = FALSE) -> bool:
    string = string.casefold()

    if string in true:
        return True

    if string in false:
        return False

    raise ValueError(CAN_NOT_CONVERT.format(tick(string)))


E = TypeVar("E", bound=Enum)


def parse_enum(string: str, enum: Type[E], parse: Optional[Parse[Any]] = None) -> E:
    if parse is None:
        return enum.from_data(string)

    try:
        return enum.from_data(parse(string))

    except Exception:
        return enum.from_data(string)


START = "start"
STOP = "stop"
INCLUSIVE = "inclusive"

DIGIT = r"[0-9]"
EQUAL = "="
DOTS = re.escape("..")

RANGE_PATTERN = rf"(?P<{START}>{DIGIT}+){DOTS}(?P<{INCLUSIVE}>{EQUAL})?(?P<{STOP}>{DIGIT}+)"

RANGE = re.compile(RANGE_PATTERN)


def parse_pages(string: str) -> Iterable[int]:
    match = RANGE.fullmatch(string)

    if match is None:
        return map(int, string.split(COMMA))

    start_string = match.group(START)

    if start_string is None:
        raise InternalError  # TODO: message?

    start = int(start_string)

    stop_string = match.group(STOP)

    if stop_string is None:
        raise InternalError  # TODO: message?

    stop = int(stop_string)

    if match.group(INCLUSIVE) is not None:
        stop += 1

    return range(start, stop)
