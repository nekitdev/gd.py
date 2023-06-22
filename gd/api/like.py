from typing import Type, TypeVar

from attrs import frozen
from iters.iters import iter

from gd.binary import VERSION, Binary, BinaryReader, BinaryWriter
from gd.binary_utils import Reader, Writer
from gd.constants import DEFAULT_ID
from gd.enums import ByteOrder, LikeType
from gd.models_constants import LIKE_SEPARATOR
from gd.models_utils import concat_like, split_like
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
        type_value, id, liked_value, other_id = iter(split_like(string)).skip(1).map(int).unwrap()

        return cls(type=LikeType(type_value), id=id, other_id=other_id, liked=bool(liked_value))

    def to_robtop(self) -> str:
        return iter.of(
            LIKE, str(self.type.value), str(self.id), str(int(self.liked)), str(self.other_id)
        ).collect(concat_like)

    @staticmethod
    def can_be_in(string: str) -> bool:
        return LIKE_SEPARATOR in string

    @classmethod
    def from_binary(
        cls: Type[L],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> L:
        liked_bit = LIKED_BIT

        reader = Reader(binary, order)

        value = reader.read_u8()

        type = LikeType(value & TYPE_MASK)

        liked = value & liked_bit == liked_bit

        id = reader.read_u32()

        other_id = reader.read_u32()

        return cls(type=type, id=id, other_id=other_id, liked=liked)

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        writer = Writer(binary, order)

        value = self.type.value

        if self.is_liked():
            value |= LIKED_BIT

        writer.write_u8(value)

        writer.write_u32(self.id)

        writer.write_u32(self.other_id)

    def is_liked(self) -> bool:
        return self.liked
