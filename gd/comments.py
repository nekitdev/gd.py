from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from attrs import define

from gd.colors import Color
from gd.constants import DEFAULT_GET_DATA, DEFAULT_USE_CLIENT
from gd.entity import Entity
from gd.enums import CommentType

# from gd.models import LevelCommentModel, UserCommentModel

__all__ = ("Comment", "LevelComment", "UserComment")

if TYPE_CHECKING:
    from gd.level import Level
    from gd.user import User


@define()
class Comment(Entity):
    author: User
    rating: int
    content: str

    type: CommentType

    created_at: datetime

    def is_disliked(self) -> bool:
        return self.rating < 0

    async def like(self) -> None:
        await self.client.like_comment(self)

    async def dislike(self) -> None:
        await self.client.dislike_comment(self)

    async def delete(self) -> None:
        await self.client.delete_comment(self)


class UserComment(Comment):
    pass


class LevelComment(Comment):
    level: Level
    record: int

    color: Color

    async def get_level(
        self, get_data: bool = DEFAULT_GET_DATA, use_client: bool = DEFAULT_USE_CLIENT
    ) -> Level:
        return await self.client.get_level(self.level.id, get_data=get_data)
