from typing import Iterable, Type, TypeVar

from attrs import define
from iters.iters import iter
from typing_aliases import DynamicTuple
from typing_extensions import Self

from gd.converters import CONVERTER
from gd.primitives.capacity.robtop import (
    CAPACITY_SEPARATOR,
    concat_capacity,
    migrate_capacity,
    split_capacity,
)
from gd.internals.robtop.protocols import RobTop

__all__ = ("Capacity", "CapacityItems")

CapacityItems = DynamicTuple[int]


@define()
class Capacity(RobTop):
    items: CapacityItems = ()

    @classmethod
    def from_iterable(cls, iterable: Iterable[int]) -> Self:
        return cls.from_items(tuple(iterable))

    @classmethod
    def of(cls, *items: int) -> Self:
        return cls.from_items(items)

    @classmethod
    def from_items(cls, items: CapacityItems) -> Self:
        return cls(items)

    def into_items(self) -> CapacityItems:
        return self.items

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return CAPACITY_SEPARATOR in string

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        return (
            iter(split_capacity(migrate_capacity(string)))
            .filter(None)
            .map(int)
            .collect(cls.from_iterable)
        )

    def to_robtop(self) -> str:
        return iter(self.into_items()).map(str).collect(concat_capacity)


def unstructure_capacity(capacity: Capacity) -> CapacityItems:
    return capacity.into_items()


C = TypeVar("C", bound=Capacity)


def structure_capacity(items: CapacityItems, capacity_type: Type[C]) -> C:
    return capacity_type.from_items(items)


CONVERTER.register_structure_hook(Capacity, structure_capacity)
CONVERTER.register_unstructure_hook(Capacity, unstructure_capacity)
