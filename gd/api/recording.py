from __future__ import annotations

import re
from collections import UserList as ListType
from functools import partial
from typing import Iterable, Iterator, List, Match, Type, TypeVar

from attrs import define
from iters import Iter, iter

from gd.binary import VERSION, Binary, BinaryReader, BinaryWriter
from gd.binary_utils import Reader, Writer
from gd.constants import EMPTY
from gd.enums import ByteOrder
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
        return concat_recording_item(self.to_robtop_iterator())

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return RECORDING_ITEM_SEPARATOR in string

    @classmethod
    def from_binary(
        cls: Type[RI],
        binary: BinaryReader,
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
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
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
    @staticmethod
    def iter_robtop(string: str) -> Iter[RecordingItem]:
        return iter(RECORDING_ITEM.finditer(string)).map(RecordingItem.from_robtop_match)

    @staticmethod
    def collect_robtop(recording: Iterable[RecordingItem]) -> str:
        return concat_empty(item.to_robtop() for item in recording)

    @classmethod
    def from_robtop(cls: Type[R], string: str) -> R:
        return cls.iter_robtop(string).collect(cls)

    def to_robtop(self) -> str:
        return self.collect_robtop(self)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return RECORDING_ITEM_SEPARATOR in string

    @classmethod
    def from_binary(
        cls: Type[R],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> R:
        reader = Reader(binary)

        length = reader.read_u32(order)

        recording_item_from_binary = partial(RecordingItem.from_binary, binary, order, version)

        return cls(iter.repeat_exactly_with(recording_item_from_binary, length).unwrap())

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        writer = Writer(binary)

        writer.write_u32(len(self), order)

        for item in self:
            item.to_binary(binary, order, version)
