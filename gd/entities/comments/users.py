from io import BufferedReader, BufferedWriter
from typing import TYPE_CHECKING

from attrs import define, field
from typing_extensions import Self
from pendulum import DateTime
from wraps.option import Option

from gd.binary.protocols import Binary
from gd.converters import register_unstructure_hook_omit_client
from gd.credentials import DEFAULT_ID
from gd.defaults.entities.comments import DEFAULT_RATING
from gd.entities.users import UserReference, UserReferenceData
from gd.entities.core import Entity, EntityData
from gd.images.factory import EMPTY
from gd.internals.entities.comments.users import InternalUserComment
from gd.primitives.colors import Color
from gd.schema.core import UserCommentSchema
from gd.time.now import utc_now
from gd.time.timestamps import timestamp_milliseconds, utc_from_timestamp_milliseconds

if TYPE_CHECKING:
    from gd.clients import Client
    from gd.schema.core import UserCommentBuilder, UserCommentReader

__all__ = (
    "UserComment",
    "UserCommentData",
    "UserCommentReference",
    "UserCommentReferenceData",
)


class UserCommentReferenceData(EntityData):
    author: UserReferenceData


USER_COMMENT_REFERENCE = "{} comment reference"
user_comment_reference = USER_COMMENT_REFERENCE.format


@register_unstructure_hook_omit_client
@define()
class UserCommentReference(Entity):
    author: UserReference = field(eq=False)

    def __str__(self) -> str:
        return user_comment_reference(self.author)

    def attach_option(self, option: Option[Client]) -> Self:
        self.author.attach_option(option)

        return super().attach_option(option)

    async def like(self) -> None:
        await self.client_expected.like_user_comment(self)

    async def dislike(self) -> None:
        await self.client_expected.dislike_user_comment(self)

    async def delete(self) -> None:
        await self.client_expected.delete_user_comment(self)


class UserCommentData(UserCommentReferenceData):
    color: int
    rating: int
    content: str
    created_at: str


USER_COMMENT = "{}: {}"
user_comment = USER_COMMENT.format

NO_CONTENT = "no content"


@register_unstructure_hook_omit_client
@define()
class UserComment(Binary, UserCommentReference):
    color: Color = field(factory=Color.default, eq=False)

    rating: int = field(default=DEFAULT_RATING, eq=False)
    content: str = field(default=EMPTY, eq=False)

    created_at: DateTime = field(factory=utc_now, eq=False)

    def __str__(self) -> str:
        return user_comment(self.author, self.content or NO_CONTENT)

    @classmethod
    def from_binary(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(UserCommentSchema.read(binary))

    @classmethod
    def from_binary_packed(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(UserCommentSchema.read_packed(binary))

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        with UserCommentSchema.from_bytes(data) as reader:
            return cls.from_reader(reader)

    @classmethod
    def from_bytes_packed(cls, data: bytes) -> Self:
        return cls.from_reader(UserCommentSchema.from_bytes_packed(data))

    def to_binary(self, binary: BufferedWriter) -> None:
        self.to_builder().write(binary)

    def to_binary_packed(self, binary: BufferedWriter) -> None:
        self.to_builder().write_packed(binary)

    def to_bytes(self) -> bytes:
        return self.to_builder().to_bytes()

    def to_bytes_packed(self) -> bytes:
        return self.to_builder().to_bytes_packed()

    @classmethod
    def from_reader(cls, reader: UserCommentReader) -> Self:
        return cls(
            id=reader.id,
            author=UserReference.from_reader(reader.author),
            color=Color(reader.color),
            rating=reader.rating,
            content=reader.content,
            created_at=utc_from_timestamp_milliseconds(reader.createdAt),
        )

    def to_builder(self) -> UserCommentBuilder:
        builder = UserCommentSchema.new_message()

        builder.id = self.id
        builder.author = self.author.to_builder()
        builder.color = self.color.into_value()
        builder.rating = self.rating
        builder.content = self.content
        builder.createdAt = timestamp_milliseconds(self.created_at)

        return builder

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
    def from_internal(cls, internal: InternalUserComment, author: UserReference) -> Self:
        return cls(
            id=internal.id,
            author=author,
            # color=internal.color,
            rating=internal.rating,
            content=internal.content,
            created_at=internal.created_at,
        )

    def as_reference(self) -> UserCommentReference:
        return UserCommentReference(id=self.id, author=self.author)
