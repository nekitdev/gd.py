from typing import Type, TypeVar
from attrs import frozen

from gd.binary import VERSION, Binary, BinaryReader, BinaryWriter
from gd.binary_utils import Reader, Writer
from gd.constants import DEFAULT_ID
from gd.enums import ByteOrder, LikeType
from gd.models_utils import concat_like, int_bool, split_like
from gd.robtop import RobTop

__all__ = ("Like",)

LIKE = "like"

L = TypeVar("L", bound="Like")

DEFAULT_LIKED = True

TYPE_MASK = 0b00000011
LIKED_BIT = 0b00000100


@frozen()
class Like(Binary, RobTop):
    type: LikeType
    id: int
    other_id: int = DEFAULT_ID
    liked: bool = DEFAULT_LIKED

    @classmethod
    def from_robtop(cls: Type[L], string: str) -> L:
        _, type_string, id_string, liked_string, other_id_string = split_like(string)

        return cls(
            type=LikeType(int(type_string)),
            id=int(id_string),
            other_id=int(other_id_string),
            liked=int_bool(liked_string),
        )

    def to_robtop(self) -> str:
        values = (LIKE, str(self.type.value), str(self.id), str(int(self.liked)), str(self.other_id))

        return concat_like(values)

    @classmethod
    def from_binary(
        cls: Type[L],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> L:
        liked_bit = LIKED_BIT

        reader = Reader(binary)

        value = reader.read_u8(order)

        type = LikeType(value & TYPE_MASK)

        liked = value & liked_bit == liked_bit

        id = reader.read_u32(order)

        other_id = reader.read_u32(order)

        return cls(type=type, id=id, other_id=other_id, liked=liked)

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        writer = Writer(binary)

        value = self.type.value

        if self.is_liked():
            value |= LIKED_BIT

        writer.write_u8(value, order)

        writer.write_u32(self.id, order)

        writer.write_u32(self.other_id, order)

    def is_liked(self) -> bool:
        return self.liked
