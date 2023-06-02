import re
from typing import Iterable

from iters import iter

from gd.errors import InternalError

__all__ = ("parse_pages",)

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

    if inclusive:
        stop += 1

    return range(start, stop)
