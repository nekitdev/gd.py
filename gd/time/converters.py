from typing import Type
from pendulum import Duration, DateTime, duration, parse
from typing_aliases import is_instance

from gd.converters import CONVERTER
from gd.time.constants import SECONDS_TO_MILLISECONDS

__all__ = (
    "unstructure_date_time",
    "structure_date_time",
    "unstructure_duration",
    "structure_duration",
)


def unstructure_date_time(date_time: DateTime) -> str:
    """Unstructures the `date_time` to its ISO 8601 string representation.

    Arguments:
        date_time: The date/time to unstructure.

    Returns:
        The ISO 8601 string representation of the `date_time`.
    """
    return date_time.to_iso8601_string()


NOT_DATE_TIME = "`{}` does not represent date/time"
not_date_time = NOT_DATE_TIME.format


def structure_date_time(string: str) -> DateTime:
    """Parses the `string` as date/time.

    Arguments:
        string: The string to parse.

    Returns:
        The parsed date/time.
    """
    result = parse(string)

    if is_instance(result, DateTime):
        return result

    raise ValueError(not_date_time(string))


def structure_date_time_ignore_type(string: str, date_time_type: Type[DateTime]) -> DateTime:
    return structure_date_time(string)


def unstructure_duration(duration: Duration) -> int:
    """Unstructures the `duration` to milliseconds.

    Arguments:
        duration: The duration to unstructure.

    Returns:
        The duration in milliseconds.
    """
    return int(duration.total_seconds() * SECONDS_TO_MILLISECONDS)


def structure_duration(milliseconds: int) -> Duration:
    """Returns the duration created from `milliseconds`.

    Arguments:
        milliseconds: The duration in milliseconds.

    Returns:
        The duration created.
    """
    return duration(milliseconds=milliseconds)


def structure_duration_ignore_type(milliseconds: int, duration_type: Type[Duration]) -> Duration:
    return structure_duration(milliseconds)


CONVERTER.register_unstructure_hook(DateTime, unstructure_date_time)
CONVERTER.register_structure_hook(DateTime, structure_date_time_ignore_type)
CONVERTER.register_unstructure_hook(Duration, unstructure_duration)
CONVERTER.register_structure_hook(Duration, structure_duration_ignore_type)
