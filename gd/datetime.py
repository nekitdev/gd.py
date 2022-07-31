from datetime import datetime, timedelta
from typing import Iterator
import re

from gd.constants import EMPTY
from gd.models_utils import TIME_SEPARATOR, concat_time
from gd.string_utils import clear_whitespace, concat_pipe

__all__ = (
    "timedelta_from_human",
    "timedelta_to_human",
    "datetime_from_human",
    "datetime_to_human",
)

MONTH_DAYS = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

AVERAGE_MONTH_DAYS = sum(MONTH_DAYS) / len(MONTH_DAYS)

SECOND_SECONDS = 1
MINUTE_SECONDS = SECOND_SECONDS * 60
HOUR_SECONDS = MINUTE_SECONDS * 60
DAY_SECONDS = HOUR_SECONDS * 24
WEEK_SECONDS = DAY_SECONDS * 7
MONTH_SECONDS = int(DAY_SECONDS * AVERAGE_MONTH_DAYS)
YEAR_SECONDS = DAY_SECONDS * 365

SECOND = "second"
MINUTE = "minute"
HOUR = "hour"
DAY = "day"
WEEK = "week"
MONTH = "month"
YEAR = "year"

TIME_NAME_TO_SECONDS = {
    SECOND: SECOND_SECONDS,
    MINUTE: MINUTE_SECONDS,
    HOUR: HOUR_SECONDS,
    DAY: DAY_SECONDS,
    WEEK: WEEK_SECONDS,
    MONTH: MONTH_SECONDS,
    YEAR: YEAR_SECONDS,
}

SECONDS_TO_TIME_NAME = {seconds: time_name for time_name, seconds in TIME_NAME_TO_SECONDS.items()}

SORTED_SECONDS_TO_TIME_NAME = sorted(SECONDS_TO_TIME_NAME.items(), reverse=True)

S = "s"

DIGIT = r"[0-9]"

IN = "in"
AGO = "ago"
NOW = "now"

FUTURE = "future"
TIMES = "times"
DELTA = "delta"
TIME = "time"
PAST = "past"

TIME_NAMES = concat_pipe(TIME_NAME_TO_SECONDS)

HUMAN_TIME_COMPLEX_PATTERN = rf"""
    (?P<{NOW}>{NOW})
    |
    (?:
        (?P<{FUTURE}>{IN})?
        (?P<{TIMES}>
            (?:
                (?P<{DELTA}>{DIGIT}+)
                (?P<{TIME}>{TIME_NAMES}){S}?
                (?:{TIME_SEPARATOR})?
            )+
        )
        (?P<{PAST}>{AGO})?
    )
"""

HUMAN_TIME_COMPLEX = re.compile(HUMAN_TIME_COMPLEX_PATTERN, re.VERBOSE)

HUMAN_TIME_PATTERN = rf"""
    (?P<{NOW}>{NOW})
    |
    (?:
        (?P<{FUTURE}>{IN})?
        (?P<{DELTA}>{DIGIT}+)
        (?P<{TIME}>{TIME_NAMES}){S}?
        (?P<{PAST}>{AGO})?
    )
"""

HUMAN_TIME = re.compile(HUMAN_TIME_PATTERN, re.VERBOSE)

HUMAN_DELTA_PATTERN = rf"""
    (?P<{DELTA}>{DIGIT}+)
    (?P<{TIME}>{TIME_NAMES}){S}?
"""

HUMAN_DELTA = re.compile(HUMAN_DELTA_PATTERN, re.VERBOSE)

DOES_NOT_MATCH_HUMAN_TIME = "{} does not match human time pattern"
DOES_NOT_MATCH_HUMAN_TIME_COMPLEX = "{} does not match human time complex pattern"

ATTEMPT_TO_CONVERT_BOTH_PAST_AND_FUTURE = "attempt to convert time that is both past and future"


def timedelta_from_human(string: str, simple: bool = True) -> timedelta:
    cleared = clear_whitespace(string)

    if simple:
        match = HUMAN_TIME.fullmatch(cleared)

        if match is None:
            raise ValueError(DOES_NOT_MATCH_HUMAN_TIME.format(repr(string)))

        matches = [match]

    else:
        match = HUMAN_TIME_COMPLEX.fullmatch(cleared)

        if match is None:
            raise ValueError(DOES_NOT_MATCH_HUMAN_TIME_COMPLEX.format(repr(string)))

        matches = list(HUMAN_DELTA.finditer(cleared))

    is_now = match.group(NOW) is not None

    if is_now:
        return timedelta()

    is_future = match.group(FUTURE) is not None
    is_past = match.group(PAST) is not None

    if is_future:
        if is_past:
            raise ValueError(ATTEMPT_TO_CONVERT_BOTH_PAST_AND_FUTURE)

    else:
        is_past = not is_future

    seconds = 0

    delta = DELTA
    time = TIME

    name_to_seconds = TIME_NAME_TO_SECONDS

    for match in matches:
        delta_seconds = int(match.group(delta))

        if is_past:
            delta_seconds = -delta_seconds

        name = match.group(time)

        seconds += name_to_seconds[name] * delta_seconds

    return timedelta(seconds=seconds)


def timedelta_to_human(
    timedelta: timedelta, distance_only: bool = False, simple: bool = True
) -> str:
    seconds = round(timedelta.total_seconds())

    return string_delta(seconds, distance_only=distance_only, simple=simple)


HUMAN_TIME_FORMAT = "{} {}"


def string_delta(seconds: int, distance_only: bool = False, simple: bool = True) -> str:
    iterator = iter_delta(seconds)

    if simple:
        string = next(iterator)

    else:
        string = concat_time(iterator)

    if distance_only or not seconds:
        return string

    if seconds > 0:
        return HUMAN_TIME_FORMAT.format(IN, string)

    return HUMAN_TIME_FORMAT.format(string, AGO)


HUMAN_DELTA_FORMAT = "{} {}{}"


def iter_delta(seconds: int) -> Iterator[str]:
    if not seconds:
        yield NOW
        return

    absolute_seconds = abs(seconds)

    human_delta = HUMAN_DELTA_FORMAT

    empty = EMPTY
    s = S

    for unit_seconds, name in SORTED_SECONDS_TO_TIME_NAME:
        delta, absolute_seconds = divmod(absolute_seconds, unit_seconds)

        if delta:
            end = empty if delta == 1 else s

            yield human_delta.format(delta, name, end)

        if not absolute_seconds:
            break


def datetime_from_human(string: str, simple: bool = True) -> datetime:
    return datetime.utcnow() + timedelta_from_human(string, simple=simple)


def datetime_to_human(datetime: datetime, distance_only: bool = False, simple: bool = True) -> str:
    now = datetime.utcnow()

    offset = datetime.utcoffset()

    if offset is not None:
        now += offset

    return timedelta_to_human(now - datetime, distance_only=distance_only, simple=simple)
