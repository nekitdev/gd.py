from pendulum import UTC, DateTime, from_timestamp

from gd.time.constants import SECONDS_TO_MILLISECONDS

__all__ = (
    "utc_from_timestamp",
    "utc_from_timestamp_milliseconds",
    "timestamp_milliseconds",
)


def utc_from_timestamp(timestamp: float) -> DateTime:
    """Returns UTC date/time corresponding to the `timestamp`.

    Arguments:
        timestamp: The timestamp in seconds.

    Returns:
        The UTC date/time created.
    """
    return from_timestamp(timestamp, UTC)


def utc_from_timestamp_milliseconds(timestamp: int) -> DateTime:
    """Similar to [`utc_from_timestamp`][gd.time.timestamps.utc_from_timestamp],
    but for timestamps in milliseconds.

    Arguments:
        timestamp: The timestamp in milliseconds.

    Returns:
        The UTC date/time created.
    """
    return utc_from_timestamp(timestamp / SECONDS_TO_MILLISECONDS)


def timestamp_milliseconds(date_time: DateTime) -> int:
    """Returns the timestamp in milliseconds corresponding to the `date_time`.

    Arguments:
        date_time: The date/time to convert.

    Returns:
        The timestamp in milliseconds.
    """
    return int(date_time.timestamp() * SECONDS_TO_MILLISECONDS)
