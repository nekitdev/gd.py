import re
from datetime import date, datetime, time, timedelta  # re-export these

from gd.typing import Optional

__all__ = (
    "date",
    "datetime",
    "time",
    "timedelta",
    "from_human_delta",
    "to_human_delta",
)

HUMAN_TIME = re.compile(
    r"(?:(?P<future>in) )?"
    r"(?P<delta>-?[0-9]+)[ ]+"
    r"(?P<time>(?:year|month|week|day|hour|minute|second))s?[ ]*"
    r"(?P<past>ago)?"
)

MONTH_DAYS = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)  # 1 -> 12

AVERAGE_MONTH_DAYS = sum(MONTH_DAYS) / len(MONTH_DAYS)

SECOND_SECONDS = 1
MINUTE_SECONDS = SECOND_SECONDS * 60
HOUR_SECONDS = MINUTE_SECONDS * 60
DAY_SECONDS = HOUR_SECONDS * 24
WEEK_SECONDS = DAY_SECONDS * 7
MONTH_SECONDS = round(DAY_SECONDS * AVERAGE_MONTH_DAYS)
YEAR_SECONDS = DAY_SECONDS * 365

TIME_NAME_TO_SECONDS = {
    "second": SECOND_SECONDS,
    "minute": MINUTE_SECONDS,
    "hour": HOUR_SECONDS,
    "day": DAY_SECONDS,
    "week": WEEK_SECONDS,
    "month": MONTH_SECONDS,
    "year": YEAR_SECONDS,
}

SECONDS_TO_TIME_NAME = {seconds: time_name for time_name, seconds in TIME_NAME_TO_SECONDS.items()}


def de_human_delta(string: str) -> datetime:
    """Convert human time delta to datetime object.

    Parameters
    ----------
    string: :class:`str`
        Human time delta, like ``13 hours ago`` or ``in 42 seconds``.

    Returns
    -------
    :class:`datetime.datetime`
        Datetime object from string.
    """
    match = HUMAN_TIME.match(string)

    if match is None:
        raise ValueError(f"{string!r} does not match {HUMAN_TIME.pattern!r}.")

    delta = int(match.group("delta"))

    is_future = match.group("future") is not None
    is_past = match.group("past") is not None

    if is_future:
        if is_past:
            raise ValueError("Attempt to convert time that is both past and future.")

        delta = -delta

    name = match.group("time")

    time_delta = timedelta(seconds=TIME_NAME_TO_SECONDS.get(name, 0) * delta)

    return datetime.utcnow() - time_delta


def ser_human_delta(datetime_object: Optional[datetime], distance_only: bool = True) -> str:
    """Convert datetime object to human delta.

    Parameters
    ----------
    datetime_object: Optional[:class:`datetime.datetime`]
        Datetime object to convert to string. If ``None``, ``unknown`` is used.

    distance_only: :class:`bool`
        Whether to display distance only.

        +---------------+--------------------+-------------------+
        | distance_only |          past time |       future time |
        +===============+====================+===================+
        | ``False``     | ``30 minutes ago`` | ``in 10 seconds`` |
        +---------------+--------------------+-------------------+
        | ``True``      | ``-30 minutes``    | ``10 seconds``    |
        +---------------+--------------------+-------------------+

    Returns
    -------
    :class:`str`
        Human time delta, like ``13 hours ago`` or ``42 seconds``.
    """
    if datetime_object is None:
        if distance_only:
            return "unknown"

        return "unknown ago"

    time_delta = datetime.utcnow() - datetime_object

    seconds = round(time_delta.total_seconds())
    abs_seconds = abs(seconds)

    for time_seconds, time_name in sorted(SECONDS_TO_TIME_NAME.items(), reverse=True):
        if abs_seconds >= time_seconds:
            break

    delta = abs_seconds // time_seconds
    name = time_name

    end = "s" if delta != 1 else ""

    if distance_only:
        if seconds < 0:
            delta = -delta

        return f"{delta} {name}{end}"

    if seconds < 0:
        return f"in {delta} {name}{end}"

    return f"{delta} {name}{end} ago"


from_human_delta = de_human_delta
to_human_delta = ser_human_delta
