from collections import UserList as ListType
from functools import partial
from typing import List, Type, TypeVar

from iters import iter

from gd.binary import VERSION, Binary, BinaryReader, BinaryWriter
from gd.binary_utils import Reader, Writer
from gd.enums import ByteOrder
from gd.models import Model
from gd.models_constants import PROGRESS_SEPARATOR
from gd.models_utils import concat_progress, split_progress

__all__ = ("Progress",)

P = TypeVar("P", bound="Progress")


class Progress(Binary, Model, ListType, List[int]):  # type: ignore
    @classmethod
    def from_binary(
        cls: Type[P],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> P:
        reader = Reader(binary)

        length = reader.read_u8(order)

        read_i8 = partial(reader.read_i8, order)

        return iter.repeat_exactly_with(read_i8, length).collect(cls)

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        writer = Writer(binary)

        writer.write_u8(len(self), order)

        for part in self:
            writer.write_i8(part, order)

    @classmethod
    def from_robtop(cls: Type[P], string: str) -> P:
        return iter(split_progress(string)).map(int).collect(cls)

    def to_robtop(self) -> str:
        return iter(self).map(str).collect(concat_progress)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return PROGRESS_SEPARATOR in string
