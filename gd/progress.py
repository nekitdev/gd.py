from typing import List, Type, TypeVar

from attrs import define, field

from gd.binary import VERSION, Binary, BinaryReader, BinaryWriter
from gd.binary_utils import Reader, Writer
from gd.enums import ByteOrder
from gd.models import Model
from gd.models_constants import PROGRESS_SEPARATOR
from gd.models_utils import concat_progress, split_progress

__all__ = ("Progress",)

P = TypeVar("P", bound="Progress")


@define()
class Progress(Binary, Model):
    array: List[int] = field(factory=list)

    @classmethod
    def from_binary(
        cls: Type[P],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> P:
        reader = Reader(binary)

        length = reader.read_u8(order)

        array = [reader.read_i8(order) for _ in range(length)]

        return cls(array)

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        writer = Writer(binary)

        array = self.array

        writer.write_u8(len(array), order)

        for item in array:
            writer.write_i8(item, order)

    @classmethod
    def from_robtop(cls: Type[P], string: str) -> P:
        array = list(map(int, split_progress(string)))

        return cls(array)

    def to_robtop(self) -> str:
        return concat_progress(map(str, self.array))

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return PROGRESS_SEPARATOR in string
