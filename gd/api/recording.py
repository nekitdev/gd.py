from __future__ import annotations

import re
from collections import UserList as ListType
from typing import Iterable, Iterator, List, Match, Type, TypeVar

from attrs import define
from iters.iters import iter, wrap_iter

from gd.constants import EMPTY
from gd.errors import InternalError
from gd.models_constants import RECORDING_ITEM_SEPARATOR
from gd.models_utils import concat_recording_item, float_str, int_bool
from gd.robtop import RobTop
from gd.string_constants import DOT
from gd.string_utils import concat_empty

__all__ = ("RecordingItem", "Recording")

DEFAULT_TIMESTAMP = 0.0
DEFAULT_PREVIOUS = False
DEFAULT_NEXT = False
DEFAULT_SECONDARY = False

TIMESTAMP = "timestamp"
PREVIOUS = "previous"
NEXT = "next"
SECONDARY = "secondary"

DIGIT = r"[0-9]"

ONE = str(1)

# [1;]t[.d];[1];[;]

RECORDING_ITEM_PATTERN = rf"""
    (?:(?P<{PREVIOUS}>{ONE}){RECORDING_ITEM_SEPARATOR})?
    (?P<{TIMESTAMP}>{DIGIT}(?:{re.escape(DOT)}{DIGIT}*)?){RECORDING_ITEM_SEPARATOR}
    (?P<{NEXT}>{ONE})?{RECORDING_ITEM_SEPARATOR}
    (?:(?P<{SECONDARY}>);)?
"""

RECORDING_ITEM = re.compile(RECORDING_ITEM_PATTERN, re.VERBOSE)

recording_item_find_iter = RECORDING_ITEM.finditer

RI = TypeVar("RI", bound="RecordingItem")


@define()
class RecordingItem(RobTop):
    timestamp: float = DEFAULT_TIMESTAMP
    previous: bool = DEFAULT_PREVIOUS
    next: bool = DEFAULT_NEXT
    secondary: bool = DEFAULT_SECONDARY

    def to_robtop_iterator(self) -> Iterator[str]:
        one = ONE
        empty = EMPTY

        if self.is_previous():
            yield one

        yield float_str(self.timestamp)

        yield one if self.is_next() else empty

        yield empty

        if self.is_secondary():
            yield empty

    @classmethod
    def from_robtop_match(cls: Type[RI], match: Match[str]) -> RI:
        previous_group = match.group(PREVIOUS)

        previous = False if previous_group is None else int_bool(previous_group)

        timestamp_group = match.group(TIMESTAMP)

        if timestamp_group is None:
            raise InternalError  # TODO: message?

        timestamp = float(timestamp_group)

        next_group = match.group(NEXT)

        next = False if next_group is None else int_bool(next_group)

        secondary_group = match.group(SECONDARY)

        secondary = secondary_group is not None

        return cls(timestamp, previous, next, secondary)

    @classmethod
    def from_robtop(cls: Type[RI], string: str) -> RI:
        match = RECORDING_ITEM.fullmatch(string)

        if match is None:
            raise ValueError  # TODO: message?

        return cls.from_robtop_match(match)

    def to_robtop(self) -> str:
        return concat_recording_item(self.to_robtop_iterator())

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return RECORDING_ITEM_SEPARATOR in string

    def is_previous(self) -> bool:
        return self.previous

    def is_next(self) -> bool:
        return self.next

    def is_secondary(self) -> bool:
        return self.secondary


def recording_item_to_robtop(item: RecordingItem) -> str:
    return item.to_robtop()


R = TypeVar("R", bound="Recording")


class Recording(ListType, List[RecordingItem], RobTop):  # type: ignore
    @staticmethod
    @wrap_iter
    def iter_robtop(string: str) -> Iterator[RecordingItem]:
        return iter(recording_item_find_iter(string)).map(RecordingItem.from_robtop_match).unwrap()

    @staticmethod
    def collect_robtop(recording: Iterable[RecordingItem]) -> str:
        return iter(recording).map(recording_item_to_robtop).collect(concat_empty)

    @classmethod
    def from_robtop(cls: Type[R], string: str) -> R:
        return cls.iter_robtop(string).collect(cls)

    def to_robtop(self) -> str:
        return self.collect_robtop(self)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return RECORDING_ITEM_SEPARATOR in string
