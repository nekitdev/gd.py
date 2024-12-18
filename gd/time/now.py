from pendulum import UTC, Date, DateTime, now

__all__ = ("utc_now", "utc_today")


def utc_now() -> DateTime:
    """Returns the current UTC date/time.

    Returns:
        The current UTC date/time.
    """
    return now(UTC)


def utc_today() -> Date:
    """Returns the current UTC date.

    Returns:
        The current UTC date.
    """
    return utc_now().date()
