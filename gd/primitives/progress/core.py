from typing import Iterable, Type, TypeVar

from attrs import frozen
from iters.iters import iter
from typing_aliases import DynamicTuple
from typing_extensions import Self

from gd.converters import CONVERTER
from gd.primitives.progress.robtop import PROGRESS_SEPARATOR, concat_progress, split_progress
from gd.internals.robtop.protocols import RobTop

__all__ = ("Progress", "ProgressItems")

ProgressItems = DynamicTuple[int]


@frozen()
class Progress(RobTop):
    items: ProgressItems = ()

    @classmethod
    def from_iterable(cls, iterable: Iterable[int]) -> Self:
        return cls.from_items(tuple(iterable))

    @classmethod
    def of(cls, *items: int) -> Self:
        return cls.from_items(items)

    @classmethod
    def from_items(cls, items: ProgressItems) -> Self:
        return cls(items)

    def into_items(self) -> ProgressItems:
        return self.items

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        return iter(split_progress(string)).filter(None).map(int).collect(cls.from_iterable)

    def to_robtop(self) -> str:
        return iter(self.items).map(str).collect(concat_progress)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return PROGRESS_SEPARATOR in string


def unstructure_progress(progress: Progress) -> ProgressItems:
    return progress.into_items()


P = TypeVar("P", bound=Progress)


def structure_progress(items: ProgressItems, progress_type: Type[P]) -> P:
    return progress_type.from_items(items)


CONVERTER.register_structure_hook(Progress, structure_progress)
CONVERTER.register_unstructure_hook(Progress, unstructure_progress)
