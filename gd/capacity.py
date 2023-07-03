from collections import UserList as ListType
from typing import List, Type, TypeVar

from iters.iters import iter

from gd.binary import VERSION, Binary, BinaryReader, BinaryWriter
from gd.binary_utils import Reader, Writer
from gd.enums import ByteOrder
from gd.models_constants import CAPACITY_SEPARATOR
from gd.models_utils import concat_capacity, split_capacity
from gd.robtop import RobTop

__all__ = ("Capacity",)

C = TypeVar("C", bound="Capacity")


class Capacity(ListType, List[int], Binary, RobTop):  # type: ignore
    @classmethod
    def from_binary(
        cls: Type[C],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> C:
        reader = Reader(binary, order)

        length = reader.read_u16()

        return iter.repeat_exactly_with(reader.read_u16, length).collect(cls)

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        writer = Writer(binary, order)

        writer.write_u16(len(self))

        iter(self).for_each(writer.write_u16)

    @classmethod
    def from_robtop(cls: Type[C], string: str) -> C:
        return iter(split_capacity(string)).filter(None).map(int).collect(cls)

    def to_robtop(self) -> str:
        return iter(self).map(str).collect(concat_capacity)

    @staticmethod
    def can_be_in(string: str) -> bool:
        return CAPACITY_SEPARATOR in string
