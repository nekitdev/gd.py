# DOCUMENT

from bisect import bisect_left, bisect_right, insort_left

from gd.decorators import cache_by
from gd.enums import GuidelineColor
from gd.text_utils import make_repr
from gd.typing import (
    Dict, Iterable, Iterator, Mapping, Optional, Sequence, Tuple, Type, TypeVar, Union
)

__all__ = ("Guideline", "Guidelines")

K = TypeVar("K")
V = TypeVar("V")

Pairs = Iterable[Tuple[K, V]]
IntoColor = Union[float, int, str, GuidelineColor]
IntoMapping = Union[Mapping[K, V], Pairs[K, V]]

GuidelineT = TypeVar("GuidelineT", bound="Guideline")

T = TypeVar("T")


def find_before(array: Sequence[T], element: T, strict: bool = True) -> T:
    bisect = bisect_left if strict else bisect_right

    index = bisect(array, element)

    if index:
        return array[index - 1]

    raise ValueError(f"Can not find value before {element!r}.")


def find_after(array: Sequence[T], element: T, strict: bool = True) -> T:
    bisect = bisect_right if strict else bisect_left

    index = bisect(array, element)

    if index != len(array):
        return array[index]

    raise ValueError(f"Can not find value after {element!r}.")


class Guideline:
    def __init__(self, timestamp: float, value: float, guidelines: "Guidelines") -> None:
        self._timestamp = timestamp
        self._value = value
        self._guidelines = guidelines

    def __repr__(self) -> str:
        info = {"timestamp": self.timestamp, "value": self.value, "color": self.color}

        return make_repr(self, info)

    @cache_by("_value")
    def _get_color(self) -> GuidelineColor:
        return GuidelineColor.from_value(self._value)

    def _set_color(self, color: IntoColor) -> None:
        self._value = GuidelineColor.from_value(color).value

    _color = property(_get_color, _set_color)

    def unsync(self) -> None:
        self._guidelines.remove(self._timestamp)

    def sync(self) -> None:
        self._guidelines.set(self._timestamp, self._value)

    def resync(self) -> None:
        self._value = self._guidelines.get(self._timestamp, self._value)

    def get_timestamp(self) -> float:
        return self._timestamp

    def set_timestamp(self, timestamp: float) -> None:
        self._timestamp = timestamp

        self.sync()

    timestamp = property(get_timestamp, set_timestamp)

    def get_value(self) -> float:
        return self._value

    def set_value(self, value: float) -> None:
        self._value = value

        self.sync()

    value = property(get_value, set_value)

    def get_color(self) -> GuidelineColor:
        return self._color

    def set_color(self, color: IntoColor) -> None:
        self._color = color

        self.sync()

    color = property(get_color, set_color)


_default_sentinel = object()


class Guidelines(Dict[float, float]):
    def __init__(self, guidelines: IntoMapping[float, float] = (), **ignore_kwargs) -> None:
        super().__init__(guidelines)

        self._init_timestamps()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._timestamp_string})"

    @property
    def _timestamp_string(self) -> str:
        _casefold = str.casefold

        _color = GuidelineColor

        return ", ".join(
            f"{_timestamp} -> {_casefold(_color(_value).name)}"
            for _timestamp, _value in self.items()
        )

    def _init_timestamps(self) -> None:
        self._timestamps = sorted(self.keys())

    def _insert_timestamp(self, timestamp: float) -> float:
        if timestamp not in self:
            insort_left(self._timestamps, timestamp)

        return timestamp

    def _remove_timestamp(self, timestamp: float) -> float:
        try:
            self._timestamps.remove(timestamp)

        except ValueError:  # not present
            pass

        return timestamp

    def __setitem__(self, timestamp: float, value: float) -> None:
        self._insert_timestamp(timestamp)

        super().__setitem__(timestamp, value)

    def __delitem__(self, timestamp: float) -> None:
        self._remove_timestamp(timestamp)

        super().__delitem__(timestamp)

    def create_ref(
        self,
        timestamp: float,
        value: float = 0.0,
        cls: Type[GuidelineT] = Guideline,  # type: ignore
    ) -> GuidelineT:
        return cls(timestamp, value, self)

    def get_ref(
        self, timestamp: float, cls: Type[GuidelineT] = Guideline  # type: ignore
    ) -> GuidelineT:
        return cls(timestamp, self[timestamp], self)

    def remove(self, timestamp: float) -> None:
        if timestamp in self:
            del self[timestamp]

    def set(self, timestamp: float, value: float) -> None:
        self[timestamp] = value

    def pop(self, timestamp: float, default: float = _default_sentinel) -> None:  # type: ignore
        self._remove_timestamp(timestamp)

        if default is _default_sentinel:
            super().pop(timestamp)

        super().pop(timestamp, default)

    def popitem(self) -> Tuple[float, float]:
        timestamp, value = super().popitem()

        self._remove_timestamp(timestamp)

        return (timestamp, value)

    def clear(self) -> None:
        self._timestamps.clear()

        super().clear()

    def setdefault(self, timestamp: float, value: float) -> float:  # type: ignore
        self._insert_timestamp(timestamp)

        return super().setdefault(timestamp, value)

    def update(  # type: ignore
        self, guidelines: IntoMapping[float, float] = (), **ignore_kwargs
    ) -> None:
        guideline_pairs: Pairs[float, float]

        if isinstance(guidelines, Mapping):
            guideline_pairs = guidelines.items()

        else:
            guideline_pairs = guidelines

        super().update(
            (self._insert_timestamp(timestamp), value) for timestamp, value in guideline_pairs
        )

    @property
    def timestamps(self) -> Iterator[float]:
        yield from self._timestamps

    @property
    def raw_guidelines_ordered(self) -> Iterator[float]:
        for timestamp in self.timestamps:
            yield self[timestamp]

    @property
    def guidelines_ordered(self) -> Iterator[GuidelineT]:
        for timestamp in self.timestamps:
            yield self.get_ref(timestamp)

    @property
    def raw_guidelines(self) -> Iterator[float]:
        yield from self.values()

    @property
    def guidelines(self) -> Iterator[GuidelineT]:
        for timestamp, value in self.items():
            yield self.create_ref(timestamp, value)

    def at(self, timestamp: float) -> float:
        return self[timestamp]

    def at_or(
        self, timestamp: float, default: Optional[float] = None
    ) -> Optional[float]:
        if timestamp in self:
            return self[timestamp]

        return default

    def timestamp_before(self, timestamp: float, strict: bool = True) -> float:
        return find_before(self._timestamps, timestamp, strict=strict)

    def timestamp_after(self, timestamp: float, strict: bool = True) -> float:
        return find_after(self._timestamps, timestamp, strict=strict)

    def before(self, timestamp: float, strict: bool = True) -> float:
        return self[self.timestamp_before(timestamp, strict=strict)]

    def after(self, timestamp: float, strict: bool = True) -> float:
        return self[self.timestamp_after(timestamp, strict=strict)]

    def before_or(
        self, timestamp: float, default: Optional[float], strict: bool = True
    ) -> Optional[float]:
        try:
            return self.before(timestamp)

        except (LookupError, ValueError):
            return default

    def after_or(
        self, timestamp: float, default: Optional[float], strict: bool = True
    ) -> Optional[float]:
        try:
            return self.after(timestamp)

        except (LookupError, ValueError):
            return default
