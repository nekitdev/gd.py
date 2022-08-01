from __future__ import annotations

from bisect import insort_left
from typing import BinaryIO, Dict, Iterator, List, Optional, Tuple, Type, TypeVar

from attrs import define, field, frozen

from gd.binary_utils import Reader, Writer
from gd.colors import Color
from gd.enums import ByteOrder
from gd.string_utils import maps
from gd.typing import IntoMapping, Pairs, is_mapping

__all__ = ("Guidelines", "Guideline")

G = TypeVar("G", bound="Guideline")


@define()
class Guideline:
    _timestamp: float = field()
    _color: Color = field()
    _alpha: int = field()

    _guidelines: Guidelines = field(repr=False)

    def get_timestamp(self) -> float:
        return self._timestamp

    def set_timestamp(self, timestamp: float) -> None:
        self._timestamp = timestamp

        self.unsync()
        self.sync()

    timestamp = property(get_timestamp, set_timestamp)

    def get_color(self) -> Color:
        return self._color

    def set_color(self, color: Color) -> None:
        self._color = color

        self.sync()

    color = property(get_color, set_color)

    def unsync(self) -> None:
        self._guidelines.remove(self._timestamp)

    def sync(self) -> None:
        self._guidelines.set(self._timestamp, self._color)

    def resync(self) -> None:
        self._color = self._guidelines.get(self._timestamp, self._color)

    @classmethod
    def from_binary(cls: Type[G], binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT) -> G:
        reader = Reader()

        timestamp = reader.read_f32(order)

        value = reader.read_u32(order)


IntoGuidelines = IntoMapping[float, Tuple[Color, int]]
GuidelinePairs = Pairs[float, Tuple[Color, int]]


@frozen()
class Guidelines(Dict[float, Tuple[Color, int]]):
    guideline_type: Type[Guideline] = field(default=Guideline)

    _timestamps: List[float] = field(repr=False, init=False)

    @_timestamps.default
    def default_timestamps(self) -> List[float]:
        return sorted(self)

    def __init__(
        self, guidelines: IntoGuidelines, guideline_type: Type[Guideline] = Guideline
    ) -> None:
        super().__init__(guidelines)

        self.__attrs_init__(guideline_type)

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

    def _clear_timestamps(self) -> None:
        self._timestamps.clear()

    def __setitem__(self, timestamp: float, color: Tuple[Color, int]) -> None:
        super().__setitem__(self._insert_timestamp(timestamp), color)

    def __delitem__(self, timestamp: float) -> None:
        super().__delitem__(self._remove_timestamp(timestamp))

    def pop(self, timestamp: float, default: Optional[Color] = None) -> Color:
        self._remove_timestamp(timestamp)

        if default is None:
            return super().pop(timestamp)

        return super().pop(timestamp, default)

    def popitem(self) -> Tuple[float, Color]:
        timestamp, color = super().popitem()

        self._remove_timestamp(timestamp)

        return (timestamp, color)

    def clear(self) -> None:
        self._clear_timestamps()

        super().clear()

    def setdefault(self, timestamp: float, color: Color) -> float:
        return super().setdefault(self._insert_timestamp(timestamp), color)

    def update(self, guidelines: IntoGuidelines = ()) -> None:
        guideline_pairs: GuidelinePairs

        if is_mapping(guidelines):
            guideline_pairs = guidelines.items()

        else:
            guideline_pairs = guidelines  # type: ignore

        super().update(
            (self._insert_timestamp(timestamp), color) for timestamp, color in guideline_pairs
        )

    def remove(self, timestamp: float) -> None:
        if timestamp in self:
            del self[timestamp]

    def set(self, timestamp: float, color: Color) -> None:
        self[timestamp] = color
