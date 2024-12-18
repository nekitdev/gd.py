from enum import Enum

__all__ = ("TimelyType",)


class TimelyType(Enum):
    """Represents timely types."""

    NOT_TIMELY = 0
    """Non-timely level."""

    DAILY = 1
    """Daily level."""

    WEEKLY = 2
    """Weekly level."""

    EVENT = 3
    """Event level."""

    DEFAULT = NOT_TIMELY
    """The default timely type."""

    def is_not_timely(self) -> bool:
        """Checks if the timely type is [`NOT_TIMELY`][gd.enums.timely.TimelyType.NOT_TIMELY].

        Returns:
            Whether the timely type is [`NOT_TIMELY`][gd.enums.timely.TimelyType.NOT_TIMELY].
        """
        return self is type(self).NOT_TIMELY

    def is_timely(self) -> bool:
        """The inverse of [`is_not_timely`][gd.enums.timely.TimelyType.is_not_timely].

        This is equivalent to:

        ```python
        not timely.is_not_timely()
        ```

        Returns:
            Whether the timely type is, in fact, timely.
        """
        return not self.is_not_timely()

    def is_daily(self) -> bool:
        """Checks if the timely type is [`DAILY`][gd.enums.timely.TimelyType.DAILY].

        Returns:
            Whether the timely type is [`DAILY`][gd.enums.timely.TimelyType.DAILY].
        """
        return self is type(self).DAILY

    def is_weekly(self) -> bool:
        """Checks if the timely type is [`WEEKLY`][gd.enums.timely.TimelyType.WEEKLY].

        Returns:
            Whether the timely type is [`WEEKLY`][gd.enums.timely.TimelyType.WEEKLY].
        """
        return self is type(self).WEEKLY

    def is_event(self) -> bool:
        """Checks if the timely type is [`EVENT`][gd.enums.timely.TimelyType.EVENT].

        Returns:
            Whether the timely type is [`EVENT`][gd.enums.timely.TimelyType.EVENT].
        """
        return self is type(self).EVENT

    def is_default(self) -> bool:
        """Checks if the timely type is [`DEFAULT`][gd.enums.timely.TimelyType.DEFAULT].

        Returns:
            Whether the timely type is [`DEFAULT`][gd.enums.timely.TimelyType.DEFAULT].
        """
        return self is type(self).DEFAULT

    @property
    def id(self) -> int:
        """Returns the special ID used to fetch the timely level.

        This is equivalent to:

        ```python
        id = -timely.value
        ```

        Returns:
            The special ID used to fetch the timely level.
        """
        return -self.value
