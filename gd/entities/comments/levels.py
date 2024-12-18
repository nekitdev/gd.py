from io import BufferedReader, BufferedWriter
from typing import TYPE_CHECKING, Optional

from attrs import define, field
from typing_extensions import Self
from pendulum import DateTime
from wraps.option import Option

from gd.binary.protocols import Binary
from gd.converters import register_unstructure_hook_omit_client
from gd.credentials import DEFAULT_ID
from gd.defaults.entities.comments import DEFAULT_RATING
from gd.entities.core import Entity, EntityData
from gd.entities.levels import LevelReference, LevelReferenceData
from gd.entities.users import UserReference, UserReferenceData
from gd.primitives.colors.core import Color
from gd.schema.core import LevelCommentSchema
from gd.strings.constants import EMPTY
from gd.time.now import utc_now
from gd.time.timestamps import timestamp_milliseconds

if TYPE_CHECKING:
    from gd.clients import Client
    from gd.schema.core import LevelCommentBuilder, LevelCommentReader

__all__ = (
    "LevelComment",
    "LevelCommentData",
    "LevelCommentReference",
    "LevelCommentReferenceData",
)


class LevelCommentReferenceData(EntityData):
    author: UserReferenceData
    level: LevelReferenceData


LEVEL_COMMENT_REFERENCE = "{} on {} comment reference"
level_comment_reference = LEVEL_COMMENT_REFERENCE.format


@register_unstructure_hook_omit_client
@define()
class LevelCommentReference(Entity):
    author: UserReference = field(eq=False)
    level: LevelReference = field(eq=False)

    def __str__(self) -> str:
        return level_comment_reference(self.author, self.level)

    async def like(self) -> None:
        await self.client_expected.like_level_comment(self)

    async def dislike(self) -> None:
        await self.client_expected.dislike_level_comment(self)

    async def delete(self) -> None:
        await self.client_expected.delete_level_comment(self)

    def attach_option(self, option: Option[Client]) -> Self:
        self.author.attach_option(option)
        self.level.attach_option(option)

        return super().attach_option(option)


class LevelCommentData(LevelCommentReferenceData):
    record: Optional[int]
    color: int
    rating: int
    content: str
    created_at: str


LEVEL_COMMENT = "{} on {}: {}"
level_comment = LEVEL_COMMENT.format

NO_CONTENT = "no content"


@register_unstructure_hook_omit_client
@define()
class LevelComment(Binary, LevelCommentReference):
    record: Optional[int] = field(default=None, eq=False)

    color: Color = field(factory=Color.default, eq=False)

    rating: int = field(default=DEFAULT_RATING, eq=False)
    content: str = field(default=EMPTY, eq=False)

    created_at: DateTime = field(factory=utc_now, eq=False)

    def __str__(self) -> str:
        return level_comment(self.author, self.level, self.content or NO_CONTENT)

    @classmethod
    def from_binary(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(LevelCommentSchema.read(binary))

    @classmethod
    def from_binary_packed(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(LevelCommentSchema.read_packed(binary))

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        with LevelCommentSchema.from_bytes(data) as reader:
            return cls.from_reader(reader)

    @classmethod
    def from_bytes_packed(cls, data: bytes) -> Self:
        return cls.from_reader(LevelCommentSchema.from_bytes_packed(data))

    def to_binary(self, binary: BufferedWriter) -> None:
        self.to_builder().write(binary)

    def to_binary_packed(self, binary: BufferedWriter) -> None:
        self.to_builder().write_packed(binary)

    def to_bytes(self) -> bytes:
        return self.to_builder().to_bytes()

    def to_bytes_packed(self) -> bytes:
        return self.to_builder().to_bytes_packed()

    @classmethod
    def from_reader(cls, reader: LevelCommentReader) -> Self:
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

    def to_builder(self) -> LevelCommentBuilder:
        builder = LevelCommentSchema.new_message()

        builder.id = self.id
        builder.author = self.author.to_builder()
        builder.content = self.content
        builder.color = self.color.into_value()
        builder.rating = self.rating
        builder.createdAt = timestamp_milliseconds(self.created_at)
        builder.level = self.level.to_builder()

        record = self.record

        if record is None:
            builder.record.none = None

        else:
            builder.record.some = record

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
