from __future__ import annotations

import re
from collections import UserList as ListType
from typing import Iterable, Iterator, List, Match, Type, TypeVar, overload

from attrs import define

from gd.constants import EMPTY
from gd.errors import InternalError
from gd.models_constants import ONE, RECORDING_SEPARATOR
from gd.models_utils import concat_recording, float_str, int_bool
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

# [1;]t[.d];[1];[;]

RECORDING_ITEM_PATTERN = rf"""
    (?:(?P<{PREVIOUS}>{ONE}){RECORDING_SEPARATOR})?
    (?P<{TIMESTAMP}>{DIGIT}(?:{re.escape(DOT)}{DIGIT}*)?){RECORDING_SEPARATOR}
    (?P<{NEXT}>{ONE})?{RECORDING_SEPARATOR}
    (?:(?P<{SECONDARY}>);)?
"""

RECORDING_ITEM = re.compile(RECORDING_ITEM_PATTERN, re.VERBOSE)

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

        if self.previous:
            yield one

        yield float_str(self.timestamp)

        yield one if self.next else empty

        yield empty

        if self.secondary:
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
        return concat_recording(self.to_robtop_iterator())

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return RECORDING_SEPARATOR in string


R = TypeVar("R", bound="Recording")


class Recording(RobTop, ListType, List[RecordingItem]):  # type: ignore
    @overload
    @staticmethod
    def iter_robtop(string: str) -> Iterator[RecordingItem]:
        ...

    @overload
    @staticmethod
    def iter_robtop(string: str, item_type: Type[RI]) -> Iterator[RI]:
        ...

    @staticmethod
    def iter_robtop(
        string: str, item_type: Type[RecordingItem] = RecordingItem
    ) -> Iterator[RecordingItem]:
        matches = RECORDING_ITEM.finditer(string)

        return map(item_type.from_robtop_match, matches)

    @staticmethod
    def collect_robtop(recording: Iterable[RecordingItem]) -> str:
        return concat_empty(item.to_robtop() for item in recording)

    @classmethod
    def from_robtop(
        cls: Type[R],
        string: str,
        item_type: Type[RecordingItem] = RecordingItem,
    ) -> R:
        return cls(cls.iter_robtop(string, item_type))

    def to_robtop(self) -> str:
        return self.collect_robtop(self)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return RECORDING_SEPARATOR in string
