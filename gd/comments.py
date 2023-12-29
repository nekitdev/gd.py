from __future__ import annotations
from io import BufferedReader, BufferedWriter

from typing import TYPE_CHECKING, Optional, Union

from attrs import define, field
from pendulum import DateTime

from gd.binary import Binary
from gd.color import Color
from gd.constants import (
    DEFAULT_GET_DATA,
    DEFAULT_ID,
    DEFAULT_RATING,
    DEFAULT_USE_CLIENT,
    EMPTY,
)
from gd.converter import register_unstructure_hook_omit_client
from gd.date_time import timestamp_milliseconds, utc_from_timestamp_milliseconds, utc_now
from gd.entity import Entity
from gd.levels import Level, LevelReference

from gd.schema import CommentLevelReferenceSchema, CommentSchema
from gd.schema_constants import NONE, SOME
from gd.users import UserReference

if TYPE_CHECKING:
    from typing_extensions import Self

    from gd.client import Client
    from gd.models import LevelCommentModel, UserCommentModel

    from gd.schema import CommentBuilder, CommentReader

__all__ = ("LevelCommentReference", "UserCommentReference", "LevelComment", "UserComment")

COMMENT = "{}: {}"
comment = COMMENT.format


@register_unstructure_hook_omit_client
@define()
class UserCommentReference(Entity):
    author: UserReference = field(eq=False)

    def attach_client_unchecked(self, client: Optional[Client]) -> Self:
        self.author.attach_client_unchecked(client)

        return super().attach_client_unchecked(client)

    def attach_client(self, client: Client) -> Self:
        self.author.attach_client(client)

        return super().attach_client(client)

    def detach_client(self) -> Self:
        self.author.detach_client()

        return super().detach_client()


LEVEL_COMMENT = "reading level comment as user comment"
NO_CONTENT = "no content"


@register_unstructure_hook_omit_client
@define()
class UserComment(Binary, UserCommentReference):
    color: Color = field(factory=Color.default, eq=False)

    rating: int = field(default=DEFAULT_RATING, eq=False)
    content: str = field(default=EMPTY, eq=False)

    created_at: DateTime = field(factory=utc_now, eq=False)

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

    def __str__(self) -> str:
        return comment(self.author, self.content)

    @classmethod
    def from_binary(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(CommentSchema.read(binary))

    @classmethod
    def from_binary_packed(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(CommentSchema.read_packed(binary))

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        with CommentSchema.from_bytes(data) as reader:
            return cls.from_reader(reader)

    @classmethod
    def from_bytes_packed(cls, data: bytes) -> Self:
        return cls.from_reader(CommentSchema.from_bytes_packed(data))

    def to_binary(self, binary: BufferedWriter) -> None:
        self.to_builder().write(binary)

    def to_binary_packed(self, binary: BufferedWriter) -> None:
        self.to_builder().write_packed(binary)

    def to_bytes(self) -> bytes:
        return self.to_builder().to_bytes()

    def to_bytes_packed(self) -> bytes:
        return self.to_builder().to_bytes_packed()

    @classmethod
    def from_reader(cls, reader: CommentReader) -> Self:
        if reader.reference.which() == SOME:
            raise ValueError(LEVEL_COMMENT)

        return cls(
            id=reader.id,
            author=UserReference.from_reader(reader.author),
            color=Color(reader.color),
            rating=reader.rating,
            content=reader.content,
            created_at=utc_from_timestamp_milliseconds(reader.createdAt),
        )

    def to_builder(self) -> CommentBuilder:
        builder = CommentSchema.new_message()

        builder.id = self.id
        builder.author = self.author.to_builder()
        builder.color = self.color.to_value()
        builder.rating = self.rating
        builder.content = self.content
        builder.createdAt = timestamp_milliseconds(self.created_at)

        return builder

    async def like(self) -> None:
        await self.client.like_user_comment(self)

    async def dislike(self) -> None:
        await self.client.dislike_user_comment(self)

    async def delete(self) -> None:
        await self.client.delete_user_comment(self)

    def is_disliked(self) -> bool:
        return self.rating < 0

    @classmethod
    def default(
        cls,
        id: int = DEFAULT_ID,
        author_id: int = DEFAULT_ID,
        author_account_id: int = DEFAULT_ID,
    ) -> Self:
        return cls(id=id, author=UserReference.default(author_id, author_account_id))

    @classmethod
    def from_model(
        cls,
        model: UserCommentModel,
        author: UserReference,
    ) -> Self:
        return cls(
            id=model.id,
            author=author,
            # color=model.color,
            rating=model.rating,
            content=model.content,
            created_at=model.created_at,
        )

    def as_reference(self) -> UserCommentReference:
        return UserCommentReference(id=self.id, author=self.author)


@register_unstructure_hook_omit_client
@define()
class LevelCommentReference(Entity):
    author: UserReference = field(eq=False)
    level: LevelReference = field(eq=False)

    async def like(self) -> None:
        await self.client.like_level_comment(self)

    async def dislike(self) -> None:
        await self.client.dislike_level_comment(self)

    async def delete(self) -> None:
        await self.client.delete_level_comment(self)

    async def get_level(
        self, get_data: bool = DEFAULT_GET_DATA, use_client: bool = DEFAULT_USE_CLIENT
    ) -> Level:
        return await self.client.get_level(
            self.level.id, get_data=get_data, use_client=use_client
        )

    def attach_client_unchecked(self, client: Optional[Client]) -> Self:
        self.author.attach_client_unchecked(client)
        self.level.attach_client_unchecked(client)

        return super().attach_client_unchecked(client)

    def attach_client(self, client: Client) -> Self:
        self.author.attach_client(client)
        self.level.attach_client(client)

        return super().attach_client(client)

    def detach_client(self) -> Self:
        self.author.detach_client()
        self.level.detach_client()

        return super().detach_client()


CommentReference = Union[UserCommentReference, LevelCommentReference]

USER_COMMENT = "reading user comment as level comment"

NO_RECORD = "no record"


@register_unstructure_hook_omit_client
@define()
class LevelComment(Binary, LevelCommentReference):
    record: Optional[int] = field(default=None, eq=False)

    color: Color = field(factory=Color.default, eq=False)

    rating: int = field(default=DEFAULT_RATING, eq=False)
    content: str = field(default=EMPTY, eq=False)

    created_at: DateTime = field(factory=utc_now, eq=False)

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

    def __str__(self) -> str:
        return comment(self.author, self.content)

    @classmethod
    def from_binary(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(CommentSchema.read(binary))

    @classmethod
    def from_binary_packed(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(CommentSchema.read_packed(binary))

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        with CommentSchema.from_bytes(data) as reader:
            return cls.from_reader(reader)

    @classmethod
    def from_bytes_packed(cls, data: bytes) -> Self:
        return cls.from_reader(CommentSchema.from_bytes_packed(data))

    def to_binary(self, binary: BufferedWriter) -> None:
        self.to_builder().write(binary)

    def to_binary_packed(self, binary: BufferedWriter) -> None:
        self.to_builder().write_packed(binary)

    def to_bytes(self) -> bytes:
        return self.to_builder().to_bytes()

    def to_bytes_packed(self) -> bytes:
        return self.to_builder().to_bytes_packed()

    @classmethod
    def from_reader(cls, reader: CommentReader) -> Self:
        option = reader.reference

        if option.which() == NONE:
            raise ValueError(USER_COMMENT)

        reference = option.some

        record_option = reference.record

        if record_option.which() == NONE:
            record = None

        else:
            record = record_option.some

        return cls(
            id=reader.id,
            author=UserReference.from_reader(reader.author),
            level=LevelReference.from_reader(reference.level),
            record=record,
            color=Color(reader.color),
            rating=reader.rating,
            content=reader.content,
            created_at=utc_from_timestamp_milliseconds(reader.createdAt),
        )

    def to_builder(self) -> CommentBuilder:
        builder = CommentSchema.new_message()

        builder.id = self.id
        builder.author = self.author.to_builder()
        builder.color = self.color.to_value()
        builder.rating = self.rating

        builder.createdAt = timestamp_milliseconds(self.created_at)

        reference_builder = CommentLevelReferenceSchema.new_message()

        reference_builder.level = self.level.to_builder()

        record = self.record

        if record is None:
            reference_builder.record.none = None

        else:
            reference_builder.record.some = record

        builder.reference.some = reference_builder

        return builder

    def is_disliked(self) -> bool:
        return self.rating < 0

    @classmethod
    def default(
        cls,
        id: int = DEFAULT_ID,
        author_id: int = DEFAULT_ID,
        author_account_id: int = DEFAULT_ID,
        level_id: int = DEFAULT_ID,
    ) -> Self:
        return cls(
            id=id,
            author=UserReference.default(author_id, author_account_id),
            level=LevelReference.default(level_id),
        )

    @classmethod
    def from_model(cls, model: LevelCommentModel, name: str = EMPTY) -> Self:
        inner = model.inner

        user_model = model.user

        return cls(
            id=inner.id,
            author=UserReference(
                id=inner.user_id, name=user_model.name, account_id=user_model.account_id
            ),
            level=LevelReference(id=inner.level_id, name=name),
            rating=inner.rating,
            content=inner.content,
            created_at=inner.created_at,
            record=inner.record,
            color=inner.color,
        )

    def as_reference(self) -> LevelCommentReference:
        return LevelCommentReference(id=self.id, author=self.author, level=self.level)


Comment = Union[UserComment, LevelComment]
