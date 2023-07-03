import re
from math import copysign as copy_sign
from typing import AbstractSet as AnySet
from typing import Iterable

from iters.iters import iter
from iters.ordered_set import ordered_set_unchecked
from typing_extensions import Final

from gd.errors import InternalError
from gd.string_utils import tick

__all__ = ("parse_bool", "parse_pages")

# SAFETY: we ensure that items are unique

FALSE_TUPLE: Final = ("false", "f", "no", "n", "0", "off")
TRUE_TUPLE: Final = ("true", "t", "yes", "y", "1", "on")

FALSE: Final = ordered_set_unchecked(FALSE_TUPLE)
TRUE: Final = ordered_set_unchecked(TRUE_TUPLE)

CAN_NOT_PARSE_BOOL = "can not parse {} to `bool`"


def parse_bool(string: str, false: AnySet[str] = FALSE, true: AnySet[str] = TRUE) -> bool:
    if string in false:
        return False

    if string in true:
        return True

    raise ValueError(CAN_NOT_PARSE_BOOL.format(tick(string)))


START = "start"
STOP = "stop"
INCLUSIVE = "inclusive"

DIGIT = r"[0-9]"

RANGE_SEPARATOR = ".."
INCLUSIVE_MARKER = "="

RANGE_PATTERN = rf"""
    (?P<{START}>{DIGIT}+)
    {re.escape(RANGE_SEPARATOR)}
    (?P<{INCLUSIVE}>{INCLUSIVE_MARKER})?
    (?P<{STOP}>{DIGIT}+)
"""

RANGE = re.compile(RANGE_PATTERN, re.VERBOSE)

PAGES_SEPARATOR = ","


def inclusive_range(item: range) -> range:
    step = item.step

    shift = int(copy_sign(1, step))

    return range(item.start, item.stop + shift, step)


def split_pages(string: str) -> Iterable[str]:
    return string.split(PAGES_SEPARATOR)


def parse_pages(string: str) -> Iterable[int]:
    match = RANGE.fullmatch(string)

    if match is None:
        return iter(split_pages(string)).map(int).unwrap()

    start_option = match.group(START)

    if start_option is None:
        raise InternalError  # TODO: message?

    start = int(start_option)

    stop_option = match.group(STOP)

    if stop_option is None:
        raise InternalError  # TODO: message?

    stop = int(stop_option)

    inclusive = match.group(INCLUSIVE) is not None

    return range(start, stop + inclusive)
