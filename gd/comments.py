from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Union

from attrs import define, field
from pendulum import DateTime

# from gd.binary import Binary
from gd.color import Color
from gd.constants import (
    DEFAULT_GET_DATA,
    DEFAULT_ID,
    DEFAULT_RATING,
    DEFAULT_RECORD,
    DEFAULT_USE_CLIENT,
    EMPTY,
)
from gd.converter import register_unstructure_hook_omit_client
from gd.date_time import utc_now
from gd.entity import Entity
from gd.levels import Level, LevelReference

# from gd.schema import CommentSchema
from gd.users import User, UserReference

if TYPE_CHECKING:
    from typing_extensions import Self

    from gd.client import Client
    from gd.models import LevelCommentModel, UserCommentModel

    # from gd.schema import CommentBuilder, CommentReader

__all__ = ("LevelCommentReference", "UserCommentReference", "LevelComment", "UserComment")

COMMENT = "{}: {}"
comment = COMMENT.format


@register_unstructure_hook_omit_client
@define()
class UserCommentReference(Entity):
    author: UserReference = field(eq=False)


@register_unstructure_hook_omit_client
@define()
class UserComment(UserCommentReference):
    rating: int = field(default=DEFAULT_RATING, eq=False)
    content: str = field(default=EMPTY, eq=False)

    created_at: DateTime = field(factory=utc_now, eq=False)

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

    def __str__(self) -> str:
        return comment(self.author, self.content)

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
        return cls(id=id, author=User.default(author_id, author_account_id))

    @classmethod
    def from_model(cls, model: UserCommentModel, author: UserReference) -> Self:
        return cls(
            id=model.id,
            author=author,
            rating=model.rating,
            content=model.content,
            created_at=model.created_at,
        )

    def attach_client_unchecked(self, client: Optional[Client]) -> Self:
        self.author.attach_client_unchecked(client)

        return super().attach_client_unchecked(client)

    def attach_client(self, client: Client) -> Self:
        self.author.attach_client(client)

        return super().attach_client(client)

    def detach_client(self) -> Self:
        self.author.detach_client()

        return super().detach_client()


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
        return await self.client.get_level(self.level.id, get_data=get_data, use_client=use_client)

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


@register_unstructure_hook_omit_client
@define()
class LevelComment(LevelCommentReference):
    record: int = field(default=DEFAULT_RECORD, eq=False)

    color: Color = field(factory=Color.default, eq=False)

    rating: int = field(default=DEFAULT_RATING, eq=False)
    content: str = field(default=EMPTY, eq=False)

    created_at: DateTime = field(factory=utc_now, eq=False)

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

    def __str__(self) -> str:
        return comment(self.author, self.content)

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
            id=id, author=User.default(author_id, author_account_id), level=Level.default(level_id)
        )

    @classmethod
    def from_model(cls, model: LevelCommentModel) -> Self:
        inner = model.inner

        level = Level.default(inner.level_id)

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


Comment = Union[UserComment, LevelComment]
