import re
from typing import Iterator, Type

from pendulum import UTC, DateTime, Duration, duration, from_timestamp, now, parse
from typing_aliases import is_instance

from gd.constants import EMPTY
from gd.converter import CONVERTER
from gd.errors import InternalError
from gd.models_constants import TIME_SEPARATOR
from gd.models_utils import concat_time
from gd.string_constants import COLON, COMMA, DOT
from gd.string_utils import clear_whitespace, concat_pipe, tick

__all__ = (
    # human converters
    "duration_from_human",
    "duration_to_human",
    "date_time_from_human",
    "date_time_to_human",
    # parse duration
    "parse_duration",
    # UTC functions
    "utc_from_timestamp",
    "utc_now",
)


def utc_from_timestamp(timestamp: float) -> DateTime:
    return from_timestamp(timestamp, UTC)


def utc_now() -> DateTime:
    return now(UTC)


# month days: Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec
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
DURATION_NAME = "duration"
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
                (?P<{DURATION_NAME}>{DIGIT}+)
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
        (?P<{DURATION_NAME}>{DIGIT}+)
        (?P<{TIME}>{TIME_NAMES}){S}?
        (?P<{PAST}>{AGO})?
    )
"""

HUMAN_TIME = re.compile(HUMAN_TIME_PATTERN, re.VERBOSE)

HUMAN_DURATION_PATTERN = rf"""
    (?P<{DURATION_NAME}>{DIGIT}+)
    (?P<{TIME}>{TIME_NAMES}){S}?
"""

HUMAN_DURATION = re.compile(HUMAN_DURATION_PATTERN, re.VERBOSE)


MILLISECONDS = "milliseconds"
SECONDS = "seconds"
MINUTES = "minutes"
HOURS = "hours"
DAYS = "days"

DURATION_PATTERN = rf"""
   (?:(?P<{DAYS}>{DIGIT}+){DAY}{S}?{COMMA})?
   (?P<{HOURS}>{DIGIT}{{1,2}})
   {COLON}
   (?P<{MINUTES}>{DIGIT}{{2}})
   {COLON}
   (?P<{SECONDS}>{DIGIT}{{2}})
   (?:{re.escape(DOT)}(?P<{MILLISECONDS}>{DIGIT}{{6}}))?
"""

DURATION = re.compile(DURATION_PATTERN, re.VERBOSE)

DOES_NOT_MATCH_DURATION = "{} does not match duration pattern"


def parse_duration(string: str) -> Duration:
    string = clear_whitespace(string)

    match = DURATION.fullmatch(string)

    if match is None:
        raise ValueError(DOES_NOT_MATCH_DURATION.format(tick(string)))

    days_option = match.group(DAYS)

    if days_option is None:
        days = 0

    else:
        days = int(days_option)

    hours_option = match.group(HOURS)

    if hours_option is None:
        raise InternalError  # TODO: message?

    hours = int(hours_option)

    minutes_option = match.group(MINUTES)

    if minutes_option is None:
        raise InternalError  # TODO: message?

    minutes = int(minutes_option)

    seconds_option = match.group(SECONDS)

    if seconds_option is None:
        raise InternalError  # TODO: message?

    seconds = int(seconds_option)

    milliseconds_option = match.group(MILLISECONDS)

    if milliseconds_option is None:
        milliseconds = 0

    else:
        milliseconds = int(milliseconds_option)

    return duration(
        days=days,
        hours=hours,
        minutes=minutes,
        seconds=seconds,
        milliseconds=milliseconds,
    )


def dump_duration(duration: Duration) -> str:
    return str(duration.as_timedelta())  # type: ignore


NOT_DATE_TIME = "{} does not represent date/time"


def parse_date_time(string: str) -> DateTime:
    result = parse(string)

    if is_instance(result, DateTime):
        return result

    raise ValueError(NOT_DATE_TIME.format(tick(string)))


def dump_date_time(date_time: DateTime) -> str:
    return str(date_time)


DOES_NOT_MATCH_HUMAN_TIME = "{} does not match human time pattern"
DOES_NOT_MATCH_HUMAN_TIME_COMPLEX = "{} does not match complex human time pattern"

ATTEMPT_TO_CONVERT_BOTH_PAST_AND_FUTURE = "attempt to convert time that is both past and future"

DEFAULT_SIMPLE = True
DEFAULT_DISTANCE_ONLY = False


def duration_from_human(string: str, simple: bool = DEFAULT_SIMPLE) -> Duration:
    cleared = clear_whitespace(string)

    if simple:
        match = HUMAN_TIME.fullmatch(cleared)

        if match is None:
            raise ValueError(DOES_NOT_MATCH_HUMAN_TIME.format(tick(string)))

        matches = [match]

    else:
        match = HUMAN_TIME_COMPLEX.fullmatch(cleared)

        if match is None:
            raise ValueError(DOES_NOT_MATCH_HUMAN_TIME_COMPLEX.format(tick(string)))

        matches = list(HUMAN_DURATION.finditer(cleared))

    is_now = match.group(NOW) is not None

    if is_now:
        return duration()

    is_future = match.group(FUTURE) is not None
    is_past = match.group(PAST) is not None

    if is_future:
        if is_past:
            raise ValueError(ATTEMPT_TO_CONVERT_BOTH_PAST_AND_FUTURE)

    else:
        is_past = not is_future

    seconds = 0

    duration_name = DURATION_NAME
    time = TIME

    name_to_seconds = TIME_NAME_TO_SECONDS

    for match in matches:
        duration_seconds = int(match.group(duration_name))

        if is_past:
            duration_seconds = -duration_seconds

        name = match.group(time)

        seconds += name_to_seconds[name] * duration_seconds

    return duration(seconds=seconds)


def duration_to_human(
    duration: Duration, distance_only: bool = DEFAULT_DISTANCE_ONLY, simple: bool = DEFAULT_SIMPLE
) -> str:
    seconds = round(duration.total_seconds())  # type: ignore

    return string_duration(seconds, distance_only=distance_only, simple=simple)


HUMAN_TIME_FORMAT = "{} {}"


def string_duration(
    seconds: int, distance_only: bool = DEFAULT_DISTANCE_ONLY, simple: bool = DEFAULT_SIMPLE
) -> str:
    iterator = iter_duration(seconds)

    if simple:
        string = next(iterator)

    else:
        string = concat_time(iterator)

    if distance_only or not seconds:
        return string

    if seconds > 0:
        return HUMAN_TIME_FORMAT.format(IN, string)

    return HUMAN_TIME_FORMAT.format(string, AGO)


HUMAN_DURATION_FORMAT = "{} {}{}"

ONE = 1


def iter_duration(seconds: int) -> Iterator[str]:
    if not seconds:
        yield NOW
        return

    absolute_seconds = abs(seconds)

    human_duration = HUMAN_DURATION_FORMAT

    one = ONE

    empty = EMPTY
    s = S

    for unit_seconds, name in SORTED_SECONDS_TO_TIME_NAME:
        duration, absolute_seconds = divmod(absolute_seconds, unit_seconds)

        if duration:
            end = empty if duration == one else s

            yield human_duration.format(duration, name, end)

        if not absolute_seconds:
            break


def date_time_from_human(string: str, simple: bool = DEFAULT_SIMPLE) -> DateTime:
    return utc_now() + duration_from_human(string, simple=simple)  # type: ignore


def date_time_to_human(
    date_time: DateTime, distance_only: bool = DEFAULT_DISTANCE_ONLY, simple: bool = DEFAULT_SIMPLE
) -> str:
    timezone = date_time.timezone

    if timezone is None:
        timezone = UTC

    now = utc_now().in_timezone(timezone)

    return duration_to_human(date_time - now, distance_only=distance_only, simple=simple)


def parse_date_time_ignore_type(string: str, type: Type[DateTime]) -> DateTime:
    return parse_date_time(string)


def parse_duration_ignore_type(string: str, type: Type[Duration]) -> Duration:
    return parse_duration(string)


CONVERTER.register_unstructure_hook(DateTime, dump_date_time)
CONVERTER.register_structure_hook(DateTime, parse_date_time_ignore_type)
CONVERTER.register_unstructure_hook(Duration, dump_duration)
CONVERTER.register_structure_hook(Duration, parse_duration_ignore_type)
