from __future__ import annotations

from builtins import isinstance as is_instance
from builtins import issubclass as is_subclass
from itertools import chain
from typing import (
    Any,
    Dict,
    Hashable,
    Iterable,
    Iterator,
    List,
    MutableSet,
    Optional,
    Sequence,
    Sized,
    Type,
    TypeVar,
    Union,
    overload,
)

from gd.typing import get_name

__all__ = ("OrderedSet", "ordered_set")

Q = TypeVar("Q", bound=Hashable)

OS = TypeVar("OS", bound="AnyOrderedSet")

SLICE_ALL = slice(None)
LAST = ~0

EMPTY_REPRESENTATION = "{}()"
ITEMS_REPRESENTATION = "{}({})"


def fetch_cls(iterable: Iterable[Q]) -> Type[OrderedSet[Q]]:
    cls = OrderedSet

    maybe_cls = type(iterable)

    if is_subclass(maybe_cls, cls):
        return maybe_cls

    return cls  # type: ignore


ITEM_NOT_IN_ORDERED_SET = "item {!r} is not in the ordered set"


class OrderedSet(MutableSet[Q], Sequence[Q]):
    def __init__(self, iterable: Iterable[Q] = ()) -> None:
        self.items: List[Q] = []
        self.item_to_index: Dict[Q, int] = {}

        self.update(iterable)

    def __len__(self) -> int:
        return len(self.items)

    @overload
    def __getitem__(self, index: int) -> Q:
        ...

    @overload
    def __getitem__(self: OS, index: slice) -> OS:
        ...

    def __getitem__(self: OS, index: Union[int, slice]) -> Union[Q, OS]:
        if is_instance(index, slice):
            if index == SLICE_ALL:
                return self.copy()

            return type(self)(self.items[index])

        return self.items[index]  # type: ignore

    def copy(self: OS) -> OS:
        return type(self)(self)

    def __contains__(self, item: Any) -> bool:
        return item in self.item_to_index

    def add(self, item: Q) -> None:
        item_to_index = self.item_to_index

        if item not in item_to_index:
            items = self.items

            item_to_index[item] = len(items)

            items.append(item)

    append = add

    def update(self, iterable: Iterable[Q]) -> None:
        for item in iterable:
            self.add(item)

    extend = update

    def index(self, item: Q, start: Optional[int] = None, stop: Optional[int] = None) -> int:
        try:
            index = self.item_to_index[item]

        except KeyError:
            raise ValueError(ITEM_NOT_IN_ORDERED_SET.format(item)) from None

        if start is not None:
            if index < start:
                raise ValueError(ITEM_NOT_IN_ORDERED_SET.format(item))

        if stop is not None:
            if index >= stop:
                raise ValueError(ITEM_NOT_IN_ORDERED_SET.format(item))

        return index

    def count(self, item: Q) -> int:
        return int(item in self.item_to_index)

    def pop(self, index: int = LAST) -> Q:
        items = self.items

        item = items[index]

        self.discard(item)

        return item

    def discard(self, item: Q) -> None:
        item_to_index = self.item_to_index

        if item in item_to_index:
            index = item_to_index[item]

            del self.items[index]

            for item_in, index_in in item_to_index.items():
                if index_in >= index:
                    item_to_index[item_in] -= 1

    def remove(self, item: Q) -> None:
        if item in self:
            self.discard(item)

        else:
            raise KeyError(ITEM_NOT_IN_ORDERED_SET.format(item))

    def insert(self, index: int, item: Q) -> None:
        item_to_index = self.item_to_index

        if item in item_to_index:
            return

        items = self.items

        if index < len(items):
            items.insert(index, item)

            for item_in, index_in in item_to_index.items():
                if index_in >= index:
                    item_to_index[item_in] += 1

            item_to_index[item] = index

        else:
            self.append(item)

    def clear(self) -> None:
        self.items.clear()
        self.item_to_index.clear()

    def __iter__(self) -> Iterator[Q]:
        return iter(self.items)

    def __reversed__(self) -> Iterator[Q]:
        return reversed(self.items)

    def __repr__(self) -> str:
        name = get_name(type(self))

        items = self.items

        if not items:
            return EMPTY_REPRESENTATION.format(name)

        return ITEMS_REPRESENTATION.format(name, items)

    def __eq__(self, other: Iterable[Q]) -> bool:
        if is_instance(other, Sequence):
            return self.items == list(other)

        return set(self.item_to_index) == set(other)

    @overload
    def union(self: OS, *iterables: Iterable[Q]) -> OS:
        ...

    @overload
    def union(self: Iterable[Q], *iterables: Iterable[Q]) -> OrderedSet[Q]:
        ...

    def union(self, *iterables: Iterable[Q]) -> OrderedSet[Q]:
        cls = fetch_cls(self)

        if iterables:
            items = chain(self, *iterables)

            return cls(items)

        return cls(self)

    @overload
    def intersection(self: OS, *iterables: Iterable[Q]) -> OS:
        ...

    @overload
    def intersection(self: Iterable[Q], *iterables: Iterable[Q]) -> OrderedSet[Q]:
        ...

    def intersection(self, *iterables: Iterable[Q]) -> OrderedSet[Q]:
        cls = fetch_cls(self)

        if iterables:
            intersection = set.intersection(*map(set, iterables))  # type: ignore
            items = (item for item in self if item in intersection)

            return cls(items)

        return cls(self)

    def intersection_update(self, *iterables: Iterable[Q]) -> None:
        intersection = self.intersection(*iterables)

        self.clear()

        self.update(intersection)

    @overload
    def difference(self: OS, *iterables: Iterable[Q]) -> OS:
        ...

    @overload
    def difference(self: Iterable[Q], *iterables: Iterable[Q]) -> OrderedSet[Q]:
        ...

    def difference(self, *iterables: Iterable[Q]) -> OrderedSet[Q]:
        cls = fetch_cls(self)

        if iterables:
            union = set.union(*map(set, iterables))  # type: ignore
            items = (item for item in self if item not in union)

            return cls(items)

        return cls(self)

    def difference_update(self, *iterables: Iterable[Q]) -> None:
        difference = self.difference(*iterables)

        self.clear()

        self.update(difference)

    @overload
    def symmetric_difference(self: OS, other: Iterable[Q]) -> OS:
        ...

    @overload
    def symmetric_difference(self: Iterable[Q], other: Iterable[Q]) -> OrderedSet[Q]:
        ...

    def symmetric_difference(self, other: Iterable[Q]) -> OrderedSet[Q]:
        cls = fetch_cls(self)

        self_set = cls(self)
        other_set = cls(other)

        return self_set.difference(other_set).union(other_set.difference(self_set))

    def symmetric_difference_update(self, *iterables: Iterable[Q]) -> None:
        symmetric_difference = self.symmetric_difference(*iterables)

        self.clear()

        self.update(symmetric_difference)

    def is_subset(self, other: Iterable[Q]) -> bool:
        other_set = set(other)

        return len(self) <= len(other_set) and all(item in other_set for item in self)

    def is_superset(self, other: Iterable[Q]) -> bool:
        if is_instance(other, Sized):
            return len(self) >= len(other) and all(item in self for item in other)

        return all(item in self for item in other)

    def is_disjoint(self, other: Iterable[Q]) -> bool:
        return not any(item in self for item in other)


AnyOrderedSet = OrderedSet[Any]

ordered_set = OrderedSet
