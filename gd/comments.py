from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, BinaryIO, Type, TypeVar

from attrs import define

from gd.binary import VERSION
from gd.binary_utils import BITS, UTF_8, Reader, Writer
from gd.colors import Color
from gd.constants import BYTE, DEFAULT_GET_DATA, DEFAULT_USE_CLIENT
from gd.entity import Entity
from gd.enums import ByteOrder

# from gd.models import LevelCommentModel, UserCommentModel

__all__ = ("Comment", "LevelComment", "UserComment")

if TYPE_CHECKING:
    from gd.level import Level
    from gd.user import User


C = TypeVar("C", bound="Comment")


@define()
class Comment(Entity):
    author: User
    rating: int
    content: str

    created_at: datetime

    def is_disliked(self) -> bool:
        return self.rating < 0

    @classmethod
    def from_binary(
        cls: Type[C],
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = UTF_8,
    ) -> C:
        reader = Reader(binary)

        id = reader.read_u32(order)

        author = User.from_binary(binary, order, encoding)

        rating = reader.read_i32(order)

        content_length = reader.read_u16(order)

        content = reader.read(content_length).decode(encoding)

        timestamp = reader.read_f32(order)

        created_at = datetime.fromtimestamp(timestamp)

        return cls(
            id=id,
            author=author,
            content=content,
            rating=rating,
            created_at=created_at,
        )

    def to_binary(
        self,
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = UTF_8,
    ) -> None:
        super().to_binary(binary, order)

        self.author.to_binary(binary, order, encoding)

        writer = Writer(binary)

        writer.write_i32(self.rating, order)

        data = self.content.encode(encoding)

        writer.write_u16(len(data), order)

        writer.write(data)

        writer.write_f32(self.created_at.timestamp(), order)

    async def like(self) -> None:
        await self.client.like_comment(self)

    async def dislike(self) -> None:
        await self.client.dislike_comment(self)

    async def delete(self) -> None:
        await self.client.delete_comment(self)


@define()
class UserComment(Comment):
    pass


LC = TypeVar("LC", bound="LevelComment")


@define()
class LevelComment(Comment):
    level: Level
    record: int

    color: Color

    @classmethod
    def from_binary(
        cls: Type[LC],
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = UTF_8,
    ) -> LC:
        reader = Reader(binary)

        id = reader.read_u32(order)

        author = User.from_binary(binary, order, encoding)

        rating = reader.read_i32(order)

        content_length = reader.read_u16(order)

        content = reader.read(content_length).decode(encoding)

        timestamp = reader.read_f32(order)

        created_at = datetime.fromtimestamp(timestamp)

        level = Level.from_binary(binary, order, encoding)

        value = reader.read_u32()

        record = value & BYTE

        value >>= BITS

        color = Color(value)

        return cls(
            id=id,
            author=author,
            content=content,
            rating=rating,
            created_at=created_at,
            level=level,
            record=record,
            color=color,
        )

    def to_binary(
        self,
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = UTF_8,
    ) -> None:
        super().to_binary(binary, order, encoding)

        self.level.to_binary(binary, order, encoding)

        writer = Writer(binary)

        value = (self.color.value << BITS) | self.record

        writer.write_u32(value, order)

    async def get_level(
        self, get_data: bool = DEFAULT_GET_DATA, use_client: bool = DEFAULT_USE_CLIENT
    ) -> Level:
        return await self.client.get_level(self.level.id, get_data=get_data)
