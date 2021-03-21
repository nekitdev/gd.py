import re
from datetime import (
    date as std_date,
    datetime as std_datetime,
    time as std_time,
    timedelta as std_timedelta,
    tzinfo,
)

from gd.typing import (
    Iterator,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    no_type_check,
    overload,
)

__all__ = (
    "date",
    "datetime",
    "time",
    "timedelta",
    "tzinfo",
    "std_date",
    "std_datetime",
    "std_time",
    "std_timedelta",
)

DELIM = ", "
AND_DELIM = " and "

HUMAN_TIME_COMPLEX = re.compile(
    r"(?:(?P<future>in)[ ]+)?"
    r"(?:"
    r"(?P<delta>[0-9]+)[ ]+"
    r"(?P<time>(?:year|month|week|day|hour|minute|second))s?"
    r"(?:(?:,|[ ]+and)[ ]+)?"
    r")+"
    r"(?:[ ]+(?P<past>ago))?"
)

HUMAN_TIME_SIMPLE = re.compile(
    r"(?:(?P<future>in)[ ]+)?"
    r"(?P<delta>[0-9]+)[ ]+"
    r"(?P<time>(?:year|month|week|day|hour|minute|second))s?"
    r"(?:[ ]+(?P<past>ago))?"
)

HUMAN_TIME = re.compile(
    r"(?P<delta>[0-9]+)[ ]+"
    r"(?P<time>(?:year|month|week|day|hour|minute|second))s?"
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

SORTED_SECONDS_TO_TIME_NAME = sorted(SECONDS_TO_TIME_NAME.items(), reverse=True)


D = TypeVar("D", bound="date")
DT = TypeVar("DT", bound="datetime")
TD = TypeVar("TD", bound="timedelta")
T = TypeVar("T", bound="time")


class timedelta(std_timedelta):
    def __json__(self) -> str:
        return str(self)

    def __add__(self: TD, other: std_timedelta) -> TD:
        return self.create_from_instance(super().__add__(other))

    def __radd__(self: TD, other: std_timedelta) -> TD:
        return self.create_from_instance(super().__radd__(other))

    def __sub__(self: TD, other: std_timedelta) -> TD:
        return self.create_from_instance(super().__sub__(other))

    def __rsub__(self: TD, other: std_timedelta) -> TD:
        return self.create_from_instance(super().__rsub__(other))

    def __mul__(self: TD, other: float) -> TD:
        return self.create_from_instance(super().__mul__(other))

    def __rmul__(self: TD, other: float) -> TD:
        return self.create_from_instance(super().__rmul__(other))

    def __mod__(self: TD, other: std_timedelta) -> TD:
        return self.create_from_instance(super().__mod__(other))

    def __divmod__(self: TD, other: std_timedelta) -> Tuple[int, TD]:
        delta, remainder = super().__divmod__(other)

        return (delta, type(self).create_from_instance(remainder))

    def __abs__(self: TD) -> TD:
        return self.create_from_instance(super().__abs__())

    def __pos__(self: TD) -> TD:
        return self.create_from_instance(super().__pos__())

    def __neg__(self: TD) -> TD:
        return self.create_from_instance(super().__neg__())

    @classmethod
    def create_from_instance(cls: Type[TD], instance: std_timedelta) -> TD:
        return cls(days=instance.days, seconds=instance.seconds, microseconds=instance.microseconds)

    @classmethod
    def from_human(cls: Type[TD], string: str, simple: bool = True) -> TD:
        if simple:
            match = HUMAN_TIME_SIMPLE.fullmatch(string)

            if match is None:
                raise ValueError(f"{string!r} does not match {HUMAN_TIME.pattern!r}.")

            matches = [match]

        else:
            match = HUMAN_TIME_COMPLEX.fullmatch(string)

            if match is None:
                raise ValueError(f"{string!r} does not match {HUMAN_TIME_COMPLEX.pattern!r}.")

            matches = list(HUMAN_TIME.finditer(string))

        is_future = match.group("future") is not None
        is_past = match.group("past") is not None

        if is_future:
            if is_past:
                raise ValueError("Attempt to convert time that is both past and future.")

        else:
            is_past = not is_future

        seconds = 0

        for match in matches:
            delta = int(match.group("delta"))

            if is_past:
                delta = -delta

            name = match.group("time")

            seconds += TIME_NAME_TO_SECONDS.get(name, 0) * delta

        return cls(seconds=seconds)

    @no_type_check
    def to_human(self: Optional[TD], distance_only: bool = False, simple: bool = True) -> str:
        if self is None:
            if distance_only:
                return "unknown"

            return "unknown ago"

        seconds = round(self.total_seconds())
        absolute_seconds = abs(seconds)

        if simple:
            for unit_seconds, name in SORTED_SECONDS_TO_TIME_NAME:
                if absolute_seconds >= unit_seconds:
                    break

            delta = absolute_seconds // unit_seconds

            end = "" if delta == 1 else "s"

            if distance_only:
                return f"{delta} {name}{end}"

            if seconds > 0:
                return f"in {delta} {name}{end}"

            return f"{delta} {name}{end} ago"

        return self.get_delta_string(seconds, distance_only=distance_only)

    @classmethod
    def get_delta_string(
        cls,
        seconds: int,
        distance_only: bool = False,
        with_and: bool = True,
    ) -> str:
        string = DELIM.join(cls.get_delta_strings(seconds))

        if with_and:
            string = AND_DELIM.join(string.rsplit(DELIM, 1))

        if distance_only:
            return string

        if seconds > 0:
            return f"in {string}"

        return f"{string} ago"

    @classmethod
    def get_delta_strings(cls, seconds: int) -> Iterator[str]:
        absolute_seconds = abs(seconds)

        for unit_seconds, name in SORTED_SECONDS_TO_TIME_NAME:
            delta = absolute_seconds // unit_seconds
            absolute_seconds %= unit_seconds

            if delta:
                end = "" if delta == 1 else "s"

                yield f"{delta} {name}{end}"

            elif not seconds:
                break


timedelta.min = timedelta.create_from_instance(std_timedelta.min)
timedelta.max = timedelta.create_from_instance(std_timedelta.max)
timedelta.resolution = timedelta.create_from_instance(std_timedelta.resolution)


class date(std_date):
    def __json__(self) -> str:
        return self.isoformat()

    def __add__(self: D, other: std_timedelta) -> D:
        return self.create_from_instance(super().__add__(other))

    def __radd__(self: D, other: std_timedelta) -> D:
        return self.create_from_instance(super().__radd__(other))

    @overload  # type: ignore  # noqa
    def __sub__(self: D, other: std_timedelta) -> D:  # noqa
        ...

    @overload  # noqa
    def __sub__(self: D, other: std_date) -> timedelta:  # noqa
        ...

    def __sub__(self: D, other: Union[std_date, std_timedelta]) -> Union[D, timedelta]:  # noqa
        instance = super().__sub__(other)

        if isinstance(instance, std_date):
            return type(self).create_from_instance(instance)

        if isinstance(instance, std_timedelta):
            return timedelta.create_from_instance(instance)

        return instance

    @classmethod
    def create_from_instance(cls: Type[D], instance: std_date) -> D:
        return cls(year=instance.year, month=instance.month, day=instance.day)


date.min = date.create_from_instance(std_date.min)
date.max = date.create_from_instance(std_date.max)
date.resolution = timedelta.create_from_instance(std_date.resolution)


class time(std_time):
    def __json__(self) -> str:
        return self.isoformat()

    @classmethod
    def create_from_instance(cls: Type[T], instance: std_time) -> T:
        return cls(
            hour=instance.hour,
            minute=instance.minute,
            second=instance.second,
            microsecond=instance.microsecond,
            tzinfo=instance.tzinfo,
        )


time.min = time.create_from_instance(std_time.min)
time.max = time.create_from_instance(std_time.max)
time.resolution = timedelta.create_from_instance(std_time.resolution)


class datetime(std_datetime):
    def __json__(self) -> str:
        return self.isoformat()

    def __add__(self: DT, other: std_timedelta) -> DT:
        return self.create_from_instance(super().__add__(other))

    def __radd__(self: DT, other: std_timedelta) -> DT:
        return self.create_from_instance(super().__radd__(other))

    @overload  # type: ignore  # noqa
    def __sub__(self: DT, other: std_datetime) -> timedelta:
        ...

    @overload  # noqa
    def __sub__(self: DT, other: std_timedelta) -> DT:  # noqa
        ...

    def __sub__(self: DT, other: Union[std_datetime, std_timedelta]) -> Union[DT, timedelta]:  # noqa
        instance = super().__sub__(other)

        if isinstance(instance, std_datetime):
            return type(self).create_from_instance(instance)

        if isinstance(instance, std_timedelta):
            return timedelta.create_from_instance(instance)

        return instance

    @classmethod
    def create_from_instance(cls: Type[DT], instance: std_datetime) -> DT:
        return cls(
            year=instance.year,
            month=instance.month,
            day=instance.day,
            hour=instance.hour,
            minute=instance.minute,
            second=instance.second,
            microsecond=instance.microsecond,
            tzinfo=instance.tzinfo,
            fold=instance.fold,
        )

    @classmethod
    def from_human_delta(cls: Type[DT], string: str, simple: bool = True) -> DT:
        """Convert human time delta to datetime object.

        Parameters
        ----------
        string: :class:`str`
            Human time delta, like ``13 hours ago`` or ``in 42 seconds``.

        simple: :class:`bool`
            Whether to parse simple delta, or complex one.
            Note that complex version can parse simple strings, but not vice-versa.
            See :meth:`~gd.datetime.datetime.to_human_delta`` for more information.

        Returns
        -------
        :class:`gd.datetime.datetime`
            Datetime object from string.
        """
        return cls.utcnow() + timedelta.from_human(string, simple=simple)

    @no_type_check
    def to_human_delta(
        self: Optional[DT], distance_only: bool = False, simple: bool = True
    ) -> str:
        """Convert datetime object to human delta.

        Parameters
        ----------
        self: Optional[:class:`gd.datetime.datetime`]
            Datetime object to convert to string. If ``None``, ``unknown`` is used.

        distance_only: :class:`bool`
            Whether to display distance only.

            +---------------+--------------------+-------------------+
            | distance_only |          past time |       future time |
            +===============+====================+===================+
            | ``False``     | ``30 minutes ago`` | ``in 10 seconds`` |
            +---------------+--------------------+-------------------+
            | ``True``      | ``30 minutes``     | ``10 seconds``    |
            +---------------+--------------------+-------------------+

        simple: :class:`bool`
            Whether to return simple human delta, or complex one.

            +---------------+-----------+---------------------------------------+
            | distance_only |    simple |                                  time |
            +===============+===========+=======================================+
            | ``False``     | ``False`` | ``1 hour, 1 minute and 1 second ago`` |
            +---------------+-----------+---------------------------------------+
            | ``False``     | ``True``  | ``1 hour ago``                        |
            +---------------+-----------+---------------------------------------+
            | ``True``      | ``False`` | ``1 hour, 1 minute and 1 second``     |
            +---------------+-----------+---------------------------------------+
            | ``True``      | ``True``  | ``1 hour``                            |
            +---------------+-----------+---------------------------------------+

        Returns
        -------
        :class:`str`
            Human time delta, like ``13 hours ago`` or ``42 seconds``.
        """
        if self is None:
            return timedelta.to_human(self, distance_only=distance_only, simple=simple)

        self_now = self.utcnow()

        offset = self.utcoffset()

        if offset is not None:
            self_now += offset

        return (self_now - self).to_human(distance_only=distance_only, simple=simple)

    @classmethod
    def combine(
        cls: Type[DT], date: std_date, time: std_time, tz: Optional[tzinfo] = None
    ) -> DT:
        return cls.create_from_instance(super().combine(date, time, tz))

    def date(self) -> date:
        return date.create_from_instance(super().date())

    def timetz(self) -> time:
        return time.create_from_instance(super().timetz())

    def time(self) -> time:
        return time.create_from_instance(super().time())

    @classmethod
    def now(cls: Type[DT], tz: Optional[tzinfo] = None) -> DT:
        return cls.create_from_instance(super().now(tz))

    @classmethod
    def utcnow(cls: Type[DT]) -> DT:
        return cls.create_from_instance(super().utcnow())

    def astimezone(self: DT, tz: Optional[tzinfo] = None) -> DT:
        return self.create_from_instance(super().astimezone(tz))

    @classmethod
    def strptime(cls: Type[DT], date_string: str, format: str) -> DT:
        return cls.create_from_instance(super().strptime(date_string, format))

    parse = strptime

    def utcoffset(self: DT) -> Optional[timedelta]:
        instance = super().utcoffset()

        if isinstance(instance, std_timedelta):
            return timedelta.create_from_instance(instance)

        return instance

    def dst(self: DT) -> Optional[timedelta]:
        instance = super().dst()

        if isinstance(instance, std_timedelta):
            return timedelta.create_from_instance(instance)

        return instance


de_human_delta = datetime.from_human_delta
ser_human_delta = datetime.to_human_delta
