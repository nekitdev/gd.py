from typing import List

from attrs import define, field
from iters.iters import iter
from typing_extensions import Self

from gd.models_constants import CAPACITY_SEPARATOR
from gd.models_utils import concat_capacity, migrate_capactiy, split_capacity
from gd.robtop import RobTop
from gd.simple import Simple

__all__ = ("Capacity", "CapacityItem", "CapacityItems")

CapacityItem = int
CapacityItems = List[CapacityItem]


@define()
class Capacity(RobTop, Simple[CapacityItems]):
    items: CapacityItems = field(factory=list)

    @classmethod
    def from_value(cls, value: CapacityItems) -> Self:
        return cls(value)

    def to_value(self) -> CapacityItems:
        return self.items

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return CAPACITY_SEPARATOR in string

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        value = iter(split_capacity(migrate_capactiy(string))).filter(None).map(int).list()

        return cls.from_value(value)

    def to_robtop(self) -> str:
        return iter(self.to_value()).map(str).collect(concat_capacity)
