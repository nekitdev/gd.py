from __future__ import annotations
from datetime import datetime

from typing import TYPE_CHECKING, AsyncIterator, Dict, Iterable, Optional, Type, TypeVar
from attrs import define

from gd.await_iters import wrap_await_iter
from gd.colors import Color
from gd.constants import DEFAULT_COLOR_1_ID, DEFAULT_COLOR_2_ID, DEFAULT_GLOW, DEFAULT_ID, DEFAULT_PAGE, DEFAULT_PAGES, UNKNOWN
from gd.entity import Entity
from gd.enums import (
    CommentState,
    CommentStrategy,
    CommentType,
    FriendRequestState,
    FriendState,
    IconType,
    MessageState,
    # Orientation,
    Role,
)
from gd.filters import Filters
# from gd.image.factory import FACTORY
from gd.image.icon import Icon
from gd.models import CreatorModel

if TYPE_CHECKING:
    # from PIL.Image import Image

    from gd.comments import Comment
    from gd.friend_request import FriendRequest
    from gd.level import Level
    from gd.message import Message

__all__ = ("User",)

U = TypeVar("U", bound="User")

DEFAULT_BANNED = False


@define()
class User(Entity):
    name: str
    account_id: int
    stars: int = 0
    demons: int = 0
    diamonds: int = 0
    orbs: int = 0
    user_coins: int = 0
    coins: int = 0
    creator_points: int = 0
    rank: Optional[int] = None
    color_1_id: int = DEFAULT_COLOR_1_ID
    color_2_id: int = DEFAULT_COLOR_2_ID
    icon_type: IconType = IconType.DEFAULT
    icon_id: int = 1
    cube_id: int = 1
    ship_id: int = 1
    ball_id: int = 1
    ufo_id: int = 1
    wave_id: int = 1
    robot_id: int = 1
    spider_id: int = 1
    # swing_copter_id: int = 1
    explosion_id: int = 1
    glow: bool = DEFAULT_GLOW
    role: Role = Role.DEFAULT
    message_state: MessageState = MessageState.DEFAULT
    friend_request_state: FriendRequestState = FriendRequestState.DEFAULT
    comment_state: CommentState = CommentState.DEFAULT
    friend_state: FriendState = FriendState.DEFAULT
    youtube: Optional[str] = None
    twitter: Optional[str] = None
    twitch: Optional[str] = None
    # discord: Optional[str] = None
    record: int = -1
    banned: bool = DEFAULT_BANNED

    recorded_at: Optional[datetime] = None

    @classmethod
    def default(cls: Type[U]) -> U:
        return cls(id=DEFAULT_ID, name=UNKNOWN, account_id=DEFAULT_ID)

    @classmethod
    def from_creator_model(cls: Type[U], model: CreatorModel) -> U:
        return cls(id=model.id, name=model.name, account_id=model.account_id)

    def __str__(self) -> str:
        return self.name

    def has_glow(self) -> bool:
        return self.glow

    def is_banned(self) -> bool:
        """Indicates whether the user is banned."""
        return self.banned

    @property
    def color_1(self) -> Color:
        return Color.with_id(self.color_1_id, Color.default_color_1())

    @property
    def color_2(self) -> Color:
        return Color.with_id(self.color_2_id, Color.default_color_2())

    async def get_user(self) -> User:
        return await self.client.get_user(self.account_id)

    async def update(self: U) -> U:
        return self.update_from(await self.get_user())

    async def send(
        self, subject: Optional[str] = None, body: Optional[str] = None
    ) -> Optional[Message]:
        return await self.client.send_message(self, subject, body)

    async def block(self) -> None:
        await self.client.block(self)

    async def unblock(self) -> None:
        await self.client.unblock(self)

    async def unfriend(self) -> None:
        await self.client.unfriend(self)

    async def send_friend_request(self, message: Optional[str] = None) -> Optional[FriendRequest]:
        return await self.client.send_friend_request(self, message)

    @wrap_await_iter
    def get_levels_on_page(self, page: int = DEFAULT_PAGE) -> AsyncIterator[Level]:
        return self.client.search_levels_on_page(page=page, filters=Filters.by_user(), user=self)

    @wrap_await_iter
    def get_levels(self, pages: Iterable[int] = DEFAULT_PAGES) -> AsyncIterator[Level]:
        return self.client.search_levels(
            pages=pages, filters=Filters.by_user(), user=self
        )

    @wrap_await_iter
    def get_comments_on_page(self, page: int = DEFAULT_PAGE) -> AsyncIterator[Comment]:
        return self.client.get_user_comments_on_page(user=self, type=CommentType.USER, page=page)

    @wrap_await_iter
    def get_level_comments_on_page(
        self,
        strategy: CommentStrategy = CommentStrategy.DEFAULT,
        page: int = DEFAULT_PAGE,
    ) -> AsyncIterator[Comment]:
        return self.client.get_user_comments_on_page(user=self, type=CommentType.LEVEL, page=page)

    @wrap_await_iter
    def get_comments(self, pages: Iterable[int] = DEFAULT_PAGES) -> AsyncIterator[Comment]:
        return self.client.get_user_comments(
            user=self, type=CommentType.USER, pages=pages
        )

    @wrap_await_iter
    def get_level_comments(
        self,
        strategy: CommentStrategy = CommentStrategy.DEFAULT,
        pages: Iterable[int] = DEFAULT_PAGES,
    ) -> AsyncIterator[Comment]:
        return self.client.get_user_comments(
            user=self, type=CommentType.LEVEL, pages=pages
        )

    @property
    def icon_id_by_type(self) -> Dict[IconType, int]:
        return {
            IconType.CUBE: self.cube_id,
            IconType.SHIP: self.ship_id,
            IconType.BALL: self.ball_id,
            IconType.UFO: self.ufo_id,
            IconType.WAVE: self.wave_id,
            IconType.ROBOT: self.spider_id,
            # IconType.SWING_COPTER: self.swing_copter_id,
        }

    def get_icon(self, type: Optional[IconType] = None) -> Icon:
        if type is None:
            return Icon(self.icon_type, self.icon_id, self.color_1, self.color_2, self.glow)

        return Icon(type, self.icon_id_by_type[type], self.color_1, self.color_2, self.glow)

    # generate
    # generate_async
    # generate_many
    # generate_many_async

    # def generate_full(self, orientation: Orientation = Orientation.DEFAULT) -> Image:
    #     return self.generate_many(*IconType, orientation=orientation)

    # async def generate_full_async(self, orientation: Orientation = Orientation.DEFAULT) -> Image:
    #     return await self.generate_many_async(*IconType, orientation=orientation)
