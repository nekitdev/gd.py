import re
from datetime import (
    date as std_date,
    datetime as std_datetime,
    time as std_time,
    timedelta as std_timedelta,
    tzinfo,
)
from functools import wraps

from gd.typing import (
    Callable,
    Iterator,
    Optional,
    Protocol,
    Tuple,
    Type,
    TypeVar,
    Union,
    no_type_check,
    overload,
    runtime_checkable,
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
    r"(?P<delta>-?[0-9]+)[ ]+"
    r"(?P<time>(?:year|month|week|day|hour|minute|second))s?"
    r"(?:(?:,|[ ]+and)[ ]+)?"
    r")+"
    r"(?:[ ]+(?P<past>ago))?"
)

HUMAN_TIME_SIMPLE = re.compile(
    r"(?:(?P<future>in)[ ]+)?"
    r"(?P<delta>-?[0-9]+)[ ]+"
    r"(?P<time>(?:year|month|week|day|hour|minute|second))s?"
    r"(?:[ ]+(?P<past>ago))?"
)

HUMAN_TIME = re.compile(
    r"(?P<delta>-?[0-9]+)[ ]+"
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


T_co = TypeVar("T_co", covariant=True)
U_contra = TypeVar("U_contra", contravariant=True)


@runtime_checkable
class instance_cast(Protocol[T_co, U_contra]):
    @classmethod
    def create_from_instance(cls: Type[T_co], instance: U_contra) -> T_co:
        raise NotImplementedError(
            "Derived classes should implement create_from_instance(instance)."
        )


R = TypeVar("R")
S = TypeVar("S")


def hook_method(
    function: Callable[..., R], hook: Optional[Type[instance_cast[S, R]]] = None
) -> Callable[..., S]:
    @wraps(function)
    def wrapper(self: instance_cast[S, R], *args, **kwargs) -> S:
        cls = type(self)

        instance = function(self, *args, **kwargs)

        return cls.create_from_instance(instance)

    return wrapper


def hook_class_method(
    function: Callable[..., R], hook: Optional[Type[instance_cast[S, R]]] = None
) -> Callable[..., S]:
    @wraps(function)
    def wrapper(cls: Type[instance_cast[S, R]], *args, **kwargs) -> S:
        instance = function(cls, *args, **kwargs)

        return cls.create_from_instance(instance)

    return wrapper


D = TypeVar("D", bound="date")
DT = TypeVar("DT", bound="datetime")
TD = TypeVar("TD", bound="timedelta")
T = TypeVar("T", bound="time")


class timedelta(std_timedelta, instance_cast):
    def __json__(self) -> str:
        return str(self)

    __add__: Callable[[TD, std_timedelta], TD] = hook_method(std_timedelta.__add__)
    __radd__: Callable[[TD, std_timedelta], TD] = hook_method(std_timedelta.__radd__)

    __sub__: Callable[[TD, std_timedelta], TD] = hook_method(std_timedelta.__sub__)
    __rsub__: Callable[[TD, std_timedelta], TD] = hook_method(std_timedelta.__rsub__)

    __mul__: Callable[[TD, float], TD] = hook_method(std_timedelta.__mul__)
    __rmul__: Callable[[TD, float], TD] = hook_method(std_timedelta.__rmul__)

    __mod__: Callable[[TD, std_timedelta], TD] = hook_method(std_timedelta.__mod__)

    def __divmod__(self: TD, other: std_timedelta) -> Tuple[int, TD]:
        delta, remainder = super().__divmod__(other)

        return (delta, type(self).create_from_instance(remainder))

    __abs__: Callable[[TD], TD] = hook_method(std_timedelta.__abs__)

    __pos__: Callable[[TD], TD] = hook_method(std_timedelta.__pos__)

    __neg__: Callable[[TD], TD] = hook_method(std_timedelta.__neg__)

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

        if is_future and is_past:
            raise ValueError("Attempt to convert time that is both past and future.")

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
        abs_seconds = abs(seconds)

        if simple:
            for unit_seconds, name in SORTED_SECONDS_TO_TIME_NAME:
                if abs_seconds >= unit_seconds:
                    break

            delta = abs_seconds // unit_seconds

            end = "" if delta == 1 else "s"

            if distance_only:
                if seconds < 0:
                    delta = -delta

                return f"{delta} {name}{end}"

            if seconds > 0:
                return f"in {delta} {name}{end}"

            return f"{delta} {name}{end} ago"

        return self.get_delta_string(abs_seconds, seconds, distance_only=distance_only)

    @classmethod
    def get_delta_string(
        cls,
        abs_seconds: int,
        seconds: int,
        distance_only: bool = False,
        with_and: bool = True,
    ) -> str:
        string = DELIM.join(
            cls.get_delta_strings(abs_seconds, seconds, distance_only=distance_only)
        )

        if with_and:
            string = AND_DELIM.join(string.rsplit(DELIM, 1))

        if distance_only:
            return string

        if seconds > 0:
            return f"in {string}"

        return f"{string} ago"

    @classmethod
    def get_delta_strings(
        cls, abs_seconds: int, seconds: int, distance_only: bool = False
    ) -> Iterator[str]:
        negate_delta = seconds < 0 and distance_only

        for unit_seconds, name in SORTED_SECONDS_TO_TIME_NAME:
            delta = abs_seconds // unit_seconds
            abs_seconds %= unit_seconds

            if delta:
                end = "" if delta == 1 else "s"

                if negate_delta:
                    delta = -delta

                yield f"{delta} {name}{end}"

            elif not abs_seconds:
                break


timedelta.min = timedelta.create_from_instance(std_timedelta.min)
timedelta.max = timedelta.create_from_instance(std_timedelta.max)
timedelta.resolution = timedelta.create_from_instance(std_timedelta.resolution)


class date(std_date, instance_cast):
    def __json__(self) -> str:
        return self.isoformat()

    __add__: Callable[[D, std_timedelta], D] = hook_method(std_date.__add__)
    __radd__: Callable[[D, std_timedelta], D] = hook_method(std_date.__radd__)

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


class time(std_time, instance_cast):
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


class datetime(std_datetime, instance_cast):
    def __json__(self) -> str:
        return self.isoformat()

    __add__: Callable[[DT, std_timedelta], DT] = hook_method(std_datetime.__add__)
    __radd__: Callable[[DT, std_timedelta], DT] = hook_method(std_datetime.__radd__)

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
            | ``True``      | ``-30 minutes``    | ``10 seconds``    |
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
            | ``True``      | ``False`` | ``-1 hour, -1 minute and -1 second``  |
            +---------------+-----------+---------------------------------------+
            | ``True``      | ``True``  | ``-1 hour``                           |
            +---------------+-----------+---------------------------------------+

        Returns
        -------
        :class:`str`
            Human time delta, like ``13 hours ago`` or ``42 seconds``.
        """
        if self is None:
            return timedelta.to_human(self, distance_only=distance_only, simple=simple)

        return timedelta.to_human(self.utcnow() - self, distance_only=distance_only, simple=simple)

    combine: Callable[
        [Type[DT], date, time, Optional[tzinfo]], DT
    ] = hook_class_method(std_datetime.combine)  # type: ignore

    date: Callable[[DT], date] = hook_method(std_datetime.date, date)

    timetz: Callable[[DT], time] = hook_method(std_datetime.timetz, time)
    time: Callable[[DT], time] = hook_method(std_datetime.time, time)

    now: Callable[[Type[DT]], DT] = hook_class_method(std_datetime.now)  # type: ignore

    astimezone: Callable[
        [DT, Optional[tzinfo]], DT
    ] = hook_method(std_datetime.astimezone)  # type: ignore

    strptime: Callable[
        [Type[DT], str, str], DT
    ] = hook_class_method(std_datetime.strptime)  # type: ignore

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
