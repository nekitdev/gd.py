from typing import List

from attrs import define, field
from iters.iters import iter
from typing_extensions import Self

from gd.models_constants import PROGRESS_SEPARATOR
from gd.models_utils import concat_progress, split_progress
from gd.robtop import RobTop
from gd.simple import Simple

__all__ = ("Progress",)

ProgressItem = int
ProgressItems = List[ProgressItem]


@define()
class Progress(RobTop, Simple[ProgressItems]):
    items: ProgressItems = field(factory=list)

    @classmethod
    def from_value(cls, value: ProgressItems) -> Self:
        return cls(value)

    def to_value(self) -> ProgressItems:
        return self.items

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        value = iter(split_progress(string)).filter(None).map(int).list()

        return cls.from_value(value)

    def to_robtop(self) -> str:
        return iter(self.items).map(str).collect(concat_progress)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return PROGRESS_SEPARATOR in string
