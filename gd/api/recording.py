from __future__ import annotations

import re
from collections import UserList as ListType
from typing import BinaryIO, Iterable, Iterator, List, Match, Type, TypeVar, overload

from attrs import define

from gd.binary import VERSION, Binary
from gd.binary_utils import Reader, Writer
from gd.constants import EMPTY
from gd.enums import ByteOrder
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

PREVIOUS_BIT = 0b00000001
NEXT_BIT = 0b00000010
SECONDARY_BIT = 0b00000100


@define()
class RecordingItem(Binary, RobTop):
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

    @classmethod
    def from_binary(
        cls: Type[RI],
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> RI:
        previous_bit = PREVIOUS_BIT
        next_bit = NEXT_BIT
        secondary_bit = SECONDARY_BIT

        reader = Reader(binary)

        timestamp = reader.read_f32(order)

        value = reader.read_u8(order)

        previous = value & previous_bit == previous_bit
        next = value & next_bit == next_bit
        secondary = value & secondary_bit == secondary_bit

        return cls(timestamp=timestamp, previous=previous, next=next, secondary=secondary)

    def to_binary(
        self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        writer = Writer(binary)

        writer.write_f32(self.timestamp, order)

        value = 0

        if self.is_previous():
            value |= PREVIOUS_BIT

        if self.is_next():
            value |= NEXT_BIT

        if self.is_secondary():
            value |= SECONDARY_BIT

        writer.write_u8(value, order)

    def is_previous(self) -> bool:
        return self.previous

    def is_next(self) -> bool:
        return self.next

    def is_secondary(self) -> bool:
        return self.secondary


R = TypeVar("R", bound="Recording")


class Recording(Binary, RobTop, ListType, List[RecordingItem]):  # type: ignore
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

    @classmethod
    def from_binary(
        cls: Type[R],
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        item_type: Type[RecordingItem] = RecordingItem
    ) -> R:
        reader = Reader(binary)

        length = reader.read_u32(order)

        return cls(
            item_type.from_binary(binary, order, version) for _ in range(length)
        )

    def to_binary(
        self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        writer = Writer(binary)

        writer.write_u32(len(self), order)

        for item in self:
            item.to_binary(binary, order, version)
