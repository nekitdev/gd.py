from __future__ import annotations

import re
from collections import UserList as ListType
from typing import Iterable, Iterator, List, Match, Type, TypeVar

from attrs import define
from funcs.application import partial
from iters.iters import iter, wrap_iter

from gd.binary import VERSION, Binary, BinaryReader, BinaryWriter
from gd.binary_utils import Reader, Writer
from gd.constants import DEFAULT_ROUNDING, EMPTY
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

recording_item_find_iter = RECORDING_ITEM.finditer

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

    @staticmethod
    def can_be_in(string: str) -> bool:
        return RECORDING_ITEM_SEPARATOR in string

    @classmethod
    def from_binary(
        cls: Type[RI],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> RI:
        rounding = DEFAULT_ROUNDING

        previous_bit = PREVIOUS_BIT
        next_bit = NEXT_BIT
        secondary_bit = SECONDARY_BIT

        reader = Reader(binary, order)

        timestamp = round(reader.read_f32(), rounding)

        value = reader.read_u8()

        previous = value & previous_bit == previous_bit
        next = value & next_bit == next_bit
        secondary = value & secondary_bit == secondary_bit

        return cls(timestamp=timestamp, previous=previous, next=next, secondary=secondary)

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        writer = Writer(binary, order)

        writer.write_f32(self.timestamp)

        value = 0

        if self.is_previous():
            value |= PREVIOUS_BIT

        if self.is_next():
            value |= NEXT_BIT

        if self.is_secondary():
            value |= SECONDARY_BIT

        writer.write_u8(value)

    def is_previous(self) -> bool:
        return self.previous

    def is_next(self) -> bool:
        return self.next

    def is_secondary(self) -> bool:
        return self.secondary


def recording_item_to_robtop(item: RecordingItem) -> str:
    return item.to_robtop()


R = TypeVar("R", bound="Recording")


class Recording(ListType, List[RecordingItem], Binary, RobTop):  # type: ignore
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

    @staticmethod
    def can_be_in(string: str) -> bool:
        return RECORDING_ITEM_SEPARATOR in string

    @classmethod
    def from_binary(
        cls: Type[R],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> R:
        reader = Reader(binary, order)

        length = reader.read_u32()

        recording_item_from_binary = partial(RecordingItem.from_binary, binary, order, version)

        return cls(iter.repeat_exactly_with(recording_item_from_binary, length).unwrap())

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        writer = Writer(binary, order)

        writer.write_u32(len(self))

        for item in self:
            item.to_binary(binary, order, version)
