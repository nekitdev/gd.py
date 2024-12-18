from typing import Iterator
from pendulum import UTC, DateTime, Duration, duration
from typing_aliases import is_not_none
from wraps.wraps import wrap_option

from gd.errors import InternalError
from gd.strings.constants import EMPTY
from gd.strings.removing import remove_whitespace
from gd.time.constants import (
    AGO,
    IN,
    MILLISECONDS_TO_NAME_SEARCH,
    NAME_TO_MILLISECONDS,
    NOW,
    S_LITERAL,
    SECONDS_TO_MILLISECONDS,
    SEPARATOR_SPACE,
)
from gd.time.formats import human_duration_format, human_format
from gd.time.now import utc_now
from gd.time.patterns import DURATION, DURATIONS, FUTURE, HUMAN, HUMAN_DURATION, NAME, PAST

CAN_NOT_PARSE = "can not parse `{}` as human duration"
can_not_parse = CAN_NOT_PARSE.format

BOTH_PAST_AND_FUTURE = "human duration is both past and future"

MATCH_BUT_GROUP_NOT_FOUND = "human duration matched but group not found"


def duration_from_human(string: str) -> Duration:
    match = HUMAN.match(remove_whitespace(string))

    if match is None:
        raise ValueError(can_not_parse(string))

    is_now = is_not_none(match.group(NOW))

    if is_now:
        return duration()

    is_future = is_not_none(match.group(FUTURE))
    is_past = is_not_none(match.group(PAST))

    if is_future:
        if is_past:
            raise ValueError(BOTH_PAST_AND_FUTURE)

    else:
        is_past = not is_future

    milliseconds = 0

    durations = match.group(DURATIONS)

    if durations is None:
        raise InternalError(MATCH_BUT_GROUP_NOT_FOUND)

    for match in HUMAN_DURATION.finditer(durations):
        part = match.group(DURATION)

        if part is None:
            raise InternalError(MATCH_BUT_GROUP_NOT_FOUND)

        value = int(part)

        name = match.group(NAME)

        if name is None:
            raise InternalError(MATCH_BUT_GROUP_NOT_FOUND)

        milliseconds += NAME_TO_MILLISECONDS[name] * value

    if is_past:
        milliseconds = -milliseconds

    return duration(milliseconds=milliseconds)


option_duration_from_human = wrap_option(duration_from_human)


def date_time_from_human(string: str) -> DateTime:
    return utc_now() + duration_from_human(string)


option_date_time_from_human = wrap_option(date_time_from_human)


DEFAULT_PRECISE = False
"""Whether to return precise human duration."""


concat_separator = SEPARATOR_SPACE.join


def duration_to_human(duration: Duration, precise: bool = DEFAULT_PRECISE) -> str:
    milliseconds = int(duration.total_seconds() * SECONDS_TO_MILLISECONDS)

    absolute_milliseconds = abs(milliseconds)

    string = concat_separator(duration_iter_format(absolute_milliseconds))

    if not string:
        return NOW

    if absolute_milliseconds == milliseconds:
        return human_format(IN, string)

    return human_format(string, AGO)


def get_end(value: int) -> str:
    return EMPTY if value == 1 else S_LITERAL


def duration_iter_format(absolute_milliseconds: int) -> Iterator[str]:
    for unit_milliseconds, name in MILLISECONDS_TO_NAME_SEARCH:
        value, absolute_milliseconds = divmod(absolute_milliseconds, unit_milliseconds)

        if value:
            yield human_duration_format(value=value, name=name, end=get_end(value))

        if not absolute_milliseconds:
            break


def date_time_to_human(date_time: DateTime, precise: bool = DEFAULT_PRECISE) -> str:
    timezone = date_time.timezone

    if timezone is None:
        timezone = UTC

    now = utc_now().in_timezone(timezone)

    return duration_to_human(date_time - now, precise=precise)
