from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, AsyncIterator, BinaryIO, Dict, Iterable, Optional, Type, TypeVar

from attrs import define

from gd.async_utils import gather_iterable
from gd.await_iters import wrap_await_iter
from gd.binary_utils import UTF_8, Reader, Writer
from gd.colors import Color
from gd.constants import (
    DEFAULT_COLOR_1_ID,
    DEFAULT_COLOR_2_ID,
    DEFAULT_GLOW,
    DEFAULT_ID,
    DEFAULT_PAGE,
    DEFAULT_PAGES,
    EMPTY,
    UNKNOWN,
)
from gd.entity import Entity
from gd.enums import (  # Orientation,
    ByteOrder,
    CommentState,
    CommentStrategy,
    CommentType,
    FriendRequestState,
    FriendState,
    IconType,
    MessageState,
    Orientation,
    Role,
)
from gd.filters import Filters
from gd.image.factory import FACTORY, connect_images
from gd.image.icon import Icon
from gd.models import CreatorModel

from .binary import VERSION

if TYPE_CHECKING:
    from PIL.Image import Image

    from gd.comments import Comment
    from gd.friend_request import FriendRequest
    from gd.level import Level
    from gd.message import Message

__all__ = ("User",)

U = TypeVar("U", bound="User")

DEFAULT_BANNED = False

BANNED_BIT = 0b10000000
MESSAGE_STATE_MASK = 0b01100000
FRIEND_REQUEST_STATE_MASK = 0b00010000
COMMENT_STATE_MASK = 0b00001100
GLOW_BIT = 0b00000010

MESSAGE_STATE_SHIFT = FRIEND_REQUEST_STATE_MASK.bit_length()
FRIEND_REQUEST_STATE_SHIFT = COMMENT_STATE_MASK.bit_length()
COMMENT_STATE_SHIFT = GLOW_BIT.bit_length()

RECORD_BIT = 0b10000000
RECORD_MASK = 0b01111111


@define()
class User(Entity):
    name: str
    account_id: int
    stars: int = 0
    demons: int = 0
    diamonds: int = 0
    orbs: int = 0
    user_coins: int = 0
    secret_coins: int = 0
    creator_points: int = 0
    rank: int = 0
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
    record: Optional[int] = None
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

    def is_glow(self) -> bool:
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
        return self.client.search_levels(pages=pages, filters=Filters.by_user(), user=self)

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
        return self.client.get_user_comments(user=self, type=CommentType.USER, pages=pages)

    @wrap_await_iter
    def get_level_comments(
        self,
        strategy: CommentStrategy = CommentStrategy.DEFAULT,
        pages: Iterable[int] = DEFAULT_PAGES,
    ) -> AsyncIterator[Comment]:
        return self.client.get_user_comments(user=self, type=CommentType.LEVEL, pages=pages)

    @property
    def icon_id_by_type(self) -> Dict[IconType, int]:
        return {
            IconType.CUBE: self.cube_id,
            IconType.SHIP: self.ship_id,
            IconType.BALL: self.ball_id,
            IconType.UFO: self.ufo_id,
            IconType.WAVE: self.wave_id,
            IconType.ROBOT: self.robot_id,
            IconType.SPIDER: self.spider_id,
            # IconType.SWING_COPTER: self.swing_copter_id,
        }

    def get_icon(self, type: Optional[IconType] = None) -> Icon:
        if type is None:
            return Icon(self.icon_type, self.icon_id, self.color_1, self.color_2, self.glow)

        return Icon(type, self.icon_id_by_type[type], self.color_1, self.color_2, self.glow)

    def generate(self, type: Optional[IconType] = None) -> Image:
        return FACTORY.generate(self.get_icon(type))

    async def generate_async(self, type: Optional[IconType] = None) -> Image:
        return await FACTORY.generate_async(self.get_icon(type))

    def generate_many(
        self, *types: Optional[IconType], orientation: Orientation = Orientation.DEFAULT
    ) -> Image:
        return connect_images((self.generate(type) for type in types), orientation)

    async def generate_many_async(
        self, *types: Optional[IconType], orientation: Orientation = Orientation.DEFAULT
    ) -> Image:
        return connect_images(
            await gather_iterable(self.generate_async(type) for type in types), orientation
        )

    def generate_full(self, orientation: Orientation = Orientation.DEFAULT) -> Image:
        return self.generate_many(*IconType, orientation=orientation)

    async def generate_full_async(self, orientation: Orientation = Orientation.DEFAULT) -> Image:
        return await self.generate_many_async(*IconType, orientation=orientation)

    @classmethod
    def from_binary(
        cls: Type[U],
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = UTF_8,
    ) -> U:
        glow_bit = GLOW_BIT
        banned_bit = BANNED_BIT
        record_bit = RECORD_BIT

        reader = Reader(binary)

        id = reader.read_u32(order)

        name_length = reader.read_u8(order)

        name = reader.read(name_length).decode(encoding)

        account_id = reader.read_u32(order)

        stars = reader.read_u32(order)
        demons = reader.read_u16(order)
        diamonds = reader.read_u32(order)
        orbs = reader.read_u32(order)
        user_coins = reader.read_u32(order)
        secret_coins = reader.read_u8(order)
        creator_points = reader.read_u16(order)

        rank = reader.read_u32(order)

        color_1_id = reader.read_u16(order)
        color_2_id = reader.read_u16(order)

        icon_type_value = reader.read_u8(order)

        icon_type = IconType(icon_type_value)

        icon_id = reader.read_u16(order)
        cube_id = reader.read_u16(order)
        ship_id = reader.read_u16(order)
        ball_id = reader.read_u16(order)
        ufo_id = reader.read_u16(order)
        wave_id = reader.read_u16(order)
        robot_id = reader.read_u16(order)
        spider_id = reader.read_u16(order)
        # swing_copter_id = reader.read_u16(order)

        explosion_id = reader.read_u16(order)

        role_value = reader.read_u8(order)

        role = Role(role_value)

        value = reader.read_u8(order)

        glow = value & glow_bit == glow_bit
        banned = value & banned_bit == banned_bit

        message_state_value = (value & MESSAGE_STATE_MASK) >> MESSAGE_STATE_SHIFT
        friend_request_state_value = (
            value & FRIEND_REQUEST_STATE_MASK
        ) >> FRIEND_REQUEST_STATE_SHIFT
        comment_state_value = (value & COMMENT_STATE_MASK) >> COMMENT_STATE_SHIFT

        message_state = MessageState(message_state_value)
        friend_request_state = FriendRequestState(friend_request_state_value)
        comment_state = CommentState(comment_state_value)

        friend_state_value = reader.read_u8(order)

        friend_state = FriendState(friend_state_value)

        youtube_length = reader.read_u16(order)

        youtube = reader.read(youtube_length).decode(encoding)

        if not youtube:
            youtube = None

        twitter_length = reader.read_u16(order)

        twitter = reader.read(twitter_length).decode(encoding)

        if not twitter:
            twitter = None

        twitch_length = reader.read_u16(order)

        twitch = reader.read(twitch_length).decode(encoding)

        if not twitch:
            twitch = None

        # discord_length = reader.read_u16(order)

        # discord = reader.read(discord_length).decode(encoding)

        # if not discord:
        #     discord = None

        record_value = reader.read_u8(order)

        record = record_value & RECORD_MASK

        record_present = record_value & record_bit == record_bit

        if not record_present:
            record = None

        timestamp = reader.read_f32(order)

        if timestamp:
            recorded_at = datetime.fromtimestamp(timestamp)

        else:
            recorded_at = None

        return cls(
            id=id,
            name=name,
            account_id=account_id,
            stars=stars,
            demons=demons,
            diamonds=diamonds,
            orbs=orbs,
            user_coins=user_coins,
            secret_coins=secret_coins,
            creator_points=creator_points,
            rank=rank,
            color_1_id=color_1_id,
            color_2_id=color_2_id,
            icon_type=icon_type,
            icon_id=icon_id,
            cube_id=cube_id,
            ship_id=ship_id,
            ball_id=ball_id,
            ufo_id=ufo_id,
            wave_id=wave_id,
            robot_id=robot_id,
            spider_id=spider_id,
            # swing_copter_id=swing_copter_id,
            explosion_id=explosion_id,
            glow=glow,
            role=role,
            message_state=message_state,
            friend_request_state=friend_request_state,
            comment_state=comment_state,
            friend_state=friend_state,
            youtube=youtube,
            twitter=twitter,
            twitch=twitch,
            # discord=discord,
            record=record,
            banned=banned,
            recorded_at=recorded_at,
        )

    def to_binary(
        self,
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = UTF_8,
    ) -> None:
        super().to_binary(binary, order)

        writer = Writer(binary)

        data = self.name.encode(encoding)

        writer.write_u8(len(data), order)

        writer.write(data)

        writer.write_u32(self.account_id, order)

        writer.write_u32(self.stars, order)
        writer.write_u16(self.demons, order)
        writer.write_u32(self.diamonds, order)
        writer.write_u32(self.orbs, order)
        writer.write_u32(self.user_coins, order)
        writer.write_u8(self.secret_coins, order)
        writer.write_u16(self.creator_points, order)

        writer.write_u32(self.rank, order)

        writer.write_u16(self.color_1_id, order)
        writer.write_u16(self.color_2_id, order)

        writer.write_u8(self.icon_type.value, order)

        writer.write_u16(self.icon_id, order)
        writer.write_u16(self.cube_id, order)
        writer.write_u16(self.ship_id, order)
        writer.write_u16(self.ball_id, order)
        writer.write_u16(self.ufo_id, order)
        writer.write_u16(self.wave_id, order)
        writer.write_u16(self.robot_id, order)
        writer.write_u16(self.spider_id, order)
        # writer.write_u16(self.swing_copter_id, order)

        writer.write_u16(self.explosion_id, order)

        writer.write_u8(self.role.value, order)

        value = 0

        if self.is_glow():
            value |= GLOW_BIT

        if self.is_banned():
            value |= BANNED_BIT

        value |= self.message_state.value << MESSAGE_STATE_SHIFT
        value |= self.friend_request_state.value << FRIEND_REQUEST_STATE_SHIFT
        value |= self.comment_state.value << COMMENT_STATE_SHIFT

        writer.write_u8(value, order)

        writer.write_u8(self.friend_state.value, order)

        youtube = self.youtube

        if youtube is None:
            youtube = EMPTY

        data = youtube.encode(encoding)

        writer.write_u16(len(data), order)

        writer.write(data)

        twitter = self.twitter

        if twitter is None:
            twitter = EMPTY

        data = twitter.encode(encoding)

        writer.write_u16(len(data), order)

        writer.write(data)

        twitch = self.twitch

        if twitch is None:
            twitch = EMPTY

        data = twitch.encode(encoding)

        writer.write_u16(len(data), order)

        writer.write(data)

        # discord = self.discord

        # if discord is None:
        #     discord = EMPTY

        # data = discord.encode(encoding)

        # writer.write_u16(len(data), order)

        # writer.write(data)

        record = self.record

        if record is None:
            record = 0

        else:
            record |= RECORD_BIT

        writer.write_u8(record, order)

        recorded_at = self.recorded_at

        if recorded_at is None:
            timestamp = 0.0

        else:
            timestamp = recorded_at.timestamp()

        writer.write_f32(timestamp, order)
