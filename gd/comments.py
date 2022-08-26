from __future__ import annotations

from datetime import datetime
from typing import BinaryIO, Type, TypeVar

from attrs import define, field

from gd.binary import VERSION
from gd.binary_utils import BITS, UTF_8, Reader, Writer
from gd.color import Color
from gd.constants import BYTE, DEFAULT_GET_DATA, DEFAULT_ID, DEFAULT_RATING, DEFAULT_RECORD, DEFAULT_USE_CLIENT, EMPTY
from gd.entity import Entity
from gd.enums import ByteOrder
from gd.level import Level
from gd.models import LevelCommentModel, UserCommentModel
from gd.user import User

__all__ = ("Comment", "LevelComment", "UserComment")


@define()
class Comment(Entity):
    author: User
    rating: int
    content: str

    created_at: datetime

    def __str__(self) -> str:
        return self.content

    def is_disliked(self) -> bool:
        return self.rating < 0


UC = TypeVar("UC", bound="UserComment")


@define()
class UserComment(Comment):
    rating: int = field(default=DEFAULT_RATING)
    content: str = field(default=EMPTY)

    created_at: datetime = field(factory=datetime.utcnow)

    async def like(self) -> None:
        await self.client.like_user_comment(self)

    async def dislike(self) -> None:
        await self.client.dislike_user_comment(self)

    async def delete(self) -> None:
        await self.client.delete_user_comment(self)

    @classmethod
    def default(cls: Type[UC]) -> UC:
        return cls(id=DEFAULT_ID, author=User.default())

    @classmethod
    def from_model(cls: Type[UC], model: UserCommentModel, author: User) -> UC:
        return cls(
            id=model.id,
            author=author,
            rating=model.rating,
            content=model.content,
            created_at=model.created_at,
        )

    @classmethod
    def from_binary(
        cls: Type[UC],
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = UTF_8,
    ) -> UC:
        reader = Reader(binary)

        id = reader.read_u32(order)

        author = User.from_binary(binary, order, version, encoding)

        rating = reader.read_i32(order)

        content_length = reader.read_u16(order)

        content = reader.read(content_length).decode(encoding)

        timestamp = reader.read_f64(order)

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
        super().to_binary(binary, order, version)

        self.author.to_binary(binary, order, version, encoding)

        writer = Writer(binary)

        writer.write_i32(self.rating, order)

        data = self.content.encode(encoding)

        writer.write_u16(len(data), order)

        writer.write(data)

        writer.write_f64(self.created_at.timestamp(), order)


LC = TypeVar("LC", bound="LevelComment")


@define()
class LevelComment(Comment):
    level: Level = field()

    record: int = field(default=DEFAULT_RECORD)

    color: Color = field(factory=Color.default)

    rating: int = field(default=DEFAULT_RATING)
    content: str = field(default=EMPTY)

    created_at: datetime = field(factory=datetime.utcnow)

    @classmethod
    def default(cls: Type[LC]) -> LC:
        return cls(id=DEFAULT_ID, author=User.default(), level=Level.default())

    @classmethod
    def from_model(cls: Type[LC], model: LevelCommentModel) -> LC:
        level = Level.default()

        inner = model.inner

        level.id = inner.level_id

        return cls(
            id=inner.id,
            author=User.from_level_comment_user_model(model.user, inner.user_id),
            rating=inner.rating,
            content=inner.content,
            created_at=inner.created_at,
            level=level,
            record=inner.record,
            color=inner.color,
        )

    async def like(self) -> None:
        await self.client.like_level_comment(self)

    async def dislike(self) -> None:
        await self.client.dislike_level_comment(self)

    async def delete(self) -> None:
        await self.client.delete_level_comment(self)

    async def get_level(
        self, get_data: bool = DEFAULT_GET_DATA, use_client: bool = DEFAULT_USE_CLIENT
    ) -> Level:
        return await self.client.get_level(self.level.id, get_data=get_data, use_client=use_client)

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

        author = User.from_binary(binary, order, version, encoding)

        rating = reader.read_i32(order)

        content_length = reader.read_u16(order)

        content = reader.read(content_length).decode(encoding)

        timestamp = reader.read_f64(order)

        created_at = datetime.fromtimestamp(timestamp)

        level = Level.from_binary(binary, order, version, encoding)

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
        super().to_binary(binary, order, version, encoding)

        self.level.to_binary(binary, order, version, encoding)

        writer = Writer(binary)

        value = (self.color.value << BITS) | self.record

        writer.write_u32(value, order)
