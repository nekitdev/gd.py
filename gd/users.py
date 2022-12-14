from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, AsyncIterator, Dict, Iterable, Optional, Type, TypeVar

from attrs import define, field
from iters.async_iters import wrap_async_iter

from gd.async_utils import gather_iterable
from gd.binary import VERSION, BinaryReader, BinaryWriter
from gd.binary_utils import Reader, Writer
from gd.color import Color
from gd.constants import (
    DEFAULT_BANNED,
    DEFAULT_COINS,
    DEFAULT_COLOR_1_ID,
    DEFAULT_COLOR_2_ID,
    DEFAULT_CREATOR_POINTS,
    DEFAULT_DEMONS,
    DEFAULT_DIAMONDS,
    DEFAULT_ENCODING,
    DEFAULT_ERRORS,
    DEFAULT_FRIEND_STATE,
    DEFAULT_GLOW,
    DEFAULT_ICON_ID,
    DEFAULT_ID,
    DEFAULT_ORBS,
    DEFAULT_PAGE,
    DEFAULT_PAGES,
    DEFAULT_PLACE,
    DEFAULT_RANK,
    DEFAULT_RECORD,
    DEFAULT_SECRET_COINS,
    DEFAULT_SIMPLE,
    DEFAULT_STARS,
    DEFAULT_USER_COINS,
    EMPTY,
    ROBTOP_ACCOUNT_ID,
    ROBTOP_ID,
    ROBTOP_NAME,
    UNKNOWN,
)
from gd.entity import Entity
from gd.enums import (
    ByteOrder,
    CommentState,
    CommentStrategy,
    FriendRequestState,
    FriendState,
    IconType,
    MessageState,
    Orientation,
    RelationshipType,
    Role,
)
from gd.filters import Filters
from gd.image.factory import FACTORY, connect_images
from gd.image.icon import Icon
from gd.models import (
    CreatorModel,
    LeaderboardUserModel,
    LevelCommentUserModel,
    LevelLeaderboardUserModel,
    ProfileModel,
    RelationshipUserModel,
    SearchUserModel,
)
from gd.relationship import Relationship

if TYPE_CHECKING:
    from PIL.Image import Image

    from gd.comments import LevelComment, UserComment
    from gd.friend_request import FriendRequest
    from gd.level import Level
    from gd.message import Message

__all__ = ("User", "LeaderboardUser", "LevelLeaderboardUser")

U = TypeVar("U", bound="User")

BANNED_BIT = 0b10000000
MESSAGE_STATE_MASK = 0b01100000
FRIEND_REQUEST_STATE_MASK = 0b00010000
COMMENT_STATE_MASK = 0b00001100
GLOW_BIT = 0b00000010

MESSAGE_STATE_SHIFT = FRIEND_REQUEST_STATE_MASK.bit_length()
FRIEND_REQUEST_STATE_SHIFT = COMMENT_STATE_MASK.bit_length()
COMMENT_STATE_SHIFT = GLOW_BIT.bit_length()


@define()
class User(Entity):
    name: str = field(eq=False)
    account_id: int = field(eq=False)
    stars: int = field(default=DEFAULT_STARS, eq=False)
    demons: int = field(default=DEFAULT_DEMONS, eq=False)
    diamonds: int = field(default=DEFAULT_DIAMONDS, eq=False)
    orbs: int = field(default=DEFAULT_ORBS, eq=False)
    user_coins: int = field(default=DEFAULT_USER_COINS, eq=False)
    secret_coins: int = field(default=DEFAULT_SECRET_COINS, eq=False)
    creator_points: int = field(default=DEFAULT_CREATOR_POINTS, eq=False)
    rank: int = field(default=DEFAULT_RANK, eq=False)
    color_1_id: int = field(default=DEFAULT_COLOR_1_ID, eq=False)
    color_2_id: int = field(default=DEFAULT_COLOR_2_ID, eq=False)
    icon_type: IconType = field(default=IconType.DEFAULT, eq=False)
    icon_id: int = field(default=DEFAULT_ICON_ID, eq=False)
    cube_id: int = field(default=DEFAULT_ICON_ID, eq=False)
    ship_id: int = field(default=DEFAULT_ICON_ID, eq=False)
    ball_id: int = field(default=DEFAULT_ICON_ID, eq=False)
    ufo_id: int = field(default=DEFAULT_ICON_ID, eq=False)
    wave_id: int = field(default=DEFAULT_ICON_ID, eq=False)
    robot_id: int = field(default=DEFAULT_ICON_ID, eq=False)
    spider_id: int = field(default=DEFAULT_ICON_ID, eq=False)
    # swing_copter_id: int = field(default=DEFAULT_ICON_ID, eq=False)
    explosion_id: int = field(default=DEFAULT_ICON_ID, eq=False)
    glow: bool = field(default=DEFAULT_GLOW, eq=False)
    role: Role = field(default=Role.DEFAULT, eq=False)
    message_state: MessageState = field(default=MessageState.DEFAULT, eq=False)
    friend_request_state: FriendRequestState = field(default=FriendRequestState.DEFAULT, eq=False)
    comment_state: CommentState = field(default=CommentState.DEFAULT, eq=False)
    friend_state: FriendState = field(default=FriendState.DEFAULT, eq=False)
    youtube: Optional[str] = field(default=None, eq=False)
    twitter: Optional[str] = field(default=None, eq=False)
    twitch: Optional[str] = field(default=None, eq=False)
    # discord: Optional[str] = field(default=None, eq=False)
    banned: bool = field(default=DEFAULT_BANNED, eq=False)

    @classmethod
    def default(cls: Type[U]) -> U:
        return cls(id=DEFAULT_ID, name=UNKNOWN, account_id=DEFAULT_ID)

    @classmethod
    def robtop(cls: Type[U]) -> U:
        return cls(id=ROBTOP_ID, name=ROBTOP_NAME, account_id=ROBTOP_ACCOUNT_ID)

    @classmethod
    def from_creator_model(cls: Type[U], model: CreatorModel) -> U:
        return cls(id=model.id, name=model.name, account_id=model.account_id)

    @classmethod
    def from_search_user_model(cls: Type[U], model: SearchUserModel) -> U:
        return cls(
            name=model.name,
            id=model.id,
            stars=model.stars,
            demons=model.demons,
            rank=model.rank,
            creator_points=model.creator_points,
            icon_id=model.icon_id,
            color_1_id=model.color_1_id,
            color_2_id=model.color_2_id,
            secret_coins=model.secret_coins,
            icon_type=model.icon_type,
            glow=model.glow,
            account_id=model.account_id,
            user_coins=model.user_coins,
        )

    @classmethod
    def from_profile_model(cls: Type[U], model: ProfileModel) -> U:
        return cls(
            name=model.name,
            id=model.id,
            stars=model.stars,
            demons=model.demons,
            creator_points=model.creator_points,
            color_1_id=model.color_1_id,
            color_2_id=model.color_2_id,
            secret_coins=model.secret_coins,
            account_id=model.account_id,
            user_coins=model.user_coins,
            message_state=model.message_state,
            friend_request_state=model.friend_request_state,
            youtube=model.youtube,
            cube_id=model.cube_id,
            ship_id=model.ship_id,
            ball_id=model.ball_id,
            ufo_id=model.ufo_id,
            wave_id=model.wave_id,
            robot_id=model.robot_id,
            glow=model.glow,
            banned=model.banned,
            rank=model.rank,
            friend_state=model.friend_state,
            spider_id=model.spider_id,
            twitter=model.twitter,
            twitch=model.twitch,
            diamonds=model.diamonds,
            explosion_id=model.explosion_id,
            role=model.role,
            comment_state=model.comment_state,
        )

    @classmethod
    def from_search_user_and_profile_models(
        cls: Type[U], search_user_model: SearchUserModel, profile_model: ProfileModel
    ) -> U:
        return cls(
            name=profile_model.name,
            id=profile_model.id,
            stars=profile_model.stars,
            demons=profile_model.demons,
            creator_points=profile_model.creator_points,
            color_1_id=profile_model.color_1_id,
            color_2_id=profile_model.color_2_id,
            secret_coins=profile_model.secret_coins,
            account_id=profile_model.account_id,
            user_coins=profile_model.user_coins,
            message_state=profile_model.message_state,
            friend_request_state=profile_model.friend_request_state,
            youtube=profile_model.youtube,
            icon_id=search_user_model.icon_id,
            icon_type=search_user_model.icon_type,
            cube_id=profile_model.cube_id,
            ship_id=profile_model.ship_id,
            ball_id=profile_model.ball_id,
            ufo_id=profile_model.ufo_id,
            wave_id=profile_model.wave_id,
            robot_id=profile_model.robot_id,
            glow=profile_model.glow,
            banned=profile_model.banned,
            rank=profile_model.rank,
            friend_state=profile_model.friend_state,
            spider_id=profile_model.spider_id,
            twitter=profile_model.twitter,
            twitch=profile_model.twitch,
            diamonds=profile_model.diamonds,
            explosion_id=profile_model.explosion_id,
            role=profile_model.role,
            comment_state=profile_model.comment_state,
        )

    @classmethod
    def from_relationship_user_model(cls: Type[U], model: RelationshipUserModel) -> U:
        return cls(
            name=model.name,
            id=model.id,
            icon_id=model.icon_id,
            color_1_id=model.color_1_id,
            color_2_id=model.color_2_id,
            icon_type=model.icon_type,
            glow=model.glow,
            account_id=model.account_id,
            message_state=model.message_state,
        )

    @classmethod
    def from_level_comment_user_model(cls: Type[U], model: LevelCommentUserModel, id: int) -> U:
        return cls(
            id=id,
            name=model.name,
            icon_id=model.icon_id,
            color_1_id=model.color_1_id,
            color_2_id=model.color_2_id,
            icon_type=model.icon_type,
            glow=model.glow,
            account_id=model.account_id,
        )

    def __str__(self) -> str:
        return self.name

    def into_relationship(self, type: RelationshipType) -> Relationship:
        return Relationship(user=self, type=type).attach_client_unchecked(self.client_unchecked)

    def is_glow(self) -> bool:
        return self.glow

    def is_banned(self) -> bool:
        """Indicates whether the user is banned."""
        return self.banned

    def is_registered(self) -> bool:
        """Indicates whether the user is registered."""
        return self.account_id > 0 and self.id > 0

    @property
    def color_1(self) -> Color:
        return Color.with_id(self.color_1_id, Color.default_color_1())

    @property
    def color_2(self) -> Color:
        return Color.with_id(self.color_2_id, Color.default_color_2())

    async def get(
        self, simple: bool = DEFAULT_SIMPLE, friend_state: bool = DEFAULT_FRIEND_STATE
    ) -> User:
        return await self.client.get_user(self.account_id, simple=simple, friend_state=friend_state)

    async def update(self: U, friend_state: bool = DEFAULT_FRIEND_STATE) -> U:
        return self.update_from(await self.get(friend_state=friend_state))

    async def send(
        self, subject: Optional[str] = None, content: Optional[str] = None
    ) -> Optional[Message]:
        return await self.client.send_message(self, subject, content)

    async def block(self) -> None:
        await self.client.block_user(self)

    async def unblock(self) -> None:
        await self.client.unblock_user(self)

    async def unfriend(self) -> None:
        await self.client.unfriend_user(self)

    async def send_friend_request(self, message: Optional[str] = None) -> Optional[FriendRequest]:
        return await self.client.send_friend_request(self, message)

    @wrap_async_iter
    def get_levels_on_page(self, page: int = DEFAULT_PAGE) -> AsyncIterator[Level]:
        return self.client.search_levels_on_page(
            page=page, filters=Filters.by_user(), user=self
        ).unwrap()

    @wrap_async_iter
    def get_levels(self, pages: Iterable[int] = DEFAULT_PAGES) -> AsyncIterator[Level]:
        return self.client.search_levels(pages=pages, filters=Filters.by_user(), user=self).unwrap()

    @wrap_async_iter
    def get_comments_on_page(self, page: int = DEFAULT_PAGE) -> AsyncIterator[UserComment]:
        return self.client.get_user_comments_on_page(user=self, page=page).unwrap()

    @wrap_async_iter
    def get_level_comments_on_page(
        self,
        strategy: CommentStrategy = CommentStrategy.DEFAULT,
        page: int = DEFAULT_PAGE,
    ) -> AsyncIterator[LevelComment]:
        return self.client.get_user_level_comments_on_page(
            user=self, page=page, strategy=strategy
        ).unwrap()

    @wrap_async_iter
    def get_comments(self, pages: Iterable[int] = DEFAULT_PAGES) -> AsyncIterator[UserComment]:
        return self.client.get_user_comments(user=self, pages=pages).unwrap()

    @wrap_async_iter
    def get_level_comments(
        self,
        strategy: CommentStrategy = CommentStrategy.DEFAULT,
        pages: Iterable[int] = DEFAULT_PAGES,
    ) -> AsyncIterator[LevelComment]:
        return self.client.get_user_level_comments(
            user=self, pages=pages, strategy=strategy
        ).unwrap()

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
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
    ) -> U:
        glow_bit = GLOW_BIT
        banned_bit = BANNED_BIT

        reader = Reader(binary)

        id = reader.read_u32(order)

        name_length = reader.read_u8(order)

        name = reader.read(name_length).decode(encoding, errors)

        account_id = reader.read_u32(order)

        stars = reader.read_u32(order)
        demons = reader.read_u16(order)
        diamonds = reader.read_u32(order)
        orbs = reader.read_u32(order)
        user_coins = reader.read_u32(order)
        secret_coins = reader.read_u16(order)
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

        youtube: Optional[str] = reader.read(youtube_length).decode(encoding, errors)

        if not youtube:
            youtube = None

        twitter_length = reader.read_u16(order)

        twitter: Optional[str] = reader.read(twitter_length).decode(encoding, errors)

        if not twitter:
            twitter = None

        twitch_length = reader.read_u16(order)

        twitch: Optional[str] = reader.read(twitch_length).decode(encoding, errors)

        if not twitch:
            twitch = None

        # discord_length = reader.read_u16(order)

        # discord: Optional[str] = reader.read(discord_length).decode(encoding, errors)

        # if not discord:
        #     discord = None

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
            banned=banned,
        )

    def to_binary(
        self,
        binary: BinaryWriter,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        data = self.name.encode(encoding, errors)

        writer.write_u8(len(data), order)

        writer.write(data)

        writer.write_u32(self.account_id, order)

        writer.write_u32(self.stars, order)
        writer.write_u16(self.demons, order)
        writer.write_u32(self.diamonds, order)
        writer.write_u32(self.orbs, order)
        writer.write_u32(self.user_coins, order)
        writer.write_u16(self.secret_coins, order)
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

        data = youtube.encode(encoding, errors)

        writer.write_u16(len(data), order)

        writer.write(data)

        twitter = self.twitter

        if twitter is None:
            twitter = EMPTY

        data = twitter.encode(encoding, errors)

        writer.write_u16(len(data), order)

        writer.write(data)

        twitch = self.twitch

        if twitch is None:
            twitch = EMPTY

        data = twitch.encode(encoding, errors)

        writer.write_u16(len(data), order)

        writer.write(data)

        # discord = self.discord

        # if discord is None:
        #     discord = EMPTY

        # data = discord.encode(encoding, errors)

        # writer.write_u16(len(data), order)

        # writer.write(data)


LU = TypeVar("LU", bound="LeaderboardUser")


@define()
class LeaderboardUser(User):
    place: int = field(default=DEFAULT_PLACE, eq=False)

    @classmethod
    def from_leaderboard_user_model(cls: Type[LU], model: LeaderboardUserModel) -> LU:
        return cls(
            name=model.name,
            id=model.id,
            stars=model.stars,
            demons=model.demons,
            place=model.place,
            creator_points=model.creator_points,
            icon_id=model.icon_id,
            color_1_id=model.color_1_id,
            color_2_id=model.color_2_id,
            secret_coins=model.secret_coins,
            icon_type=model.icon_type,
            glow=model.glow,
            account_id=model.account_id,
            user_coins=model.user_coins,
            diamonds=model.diamonds,
        )

    @classmethod
    def from_binary(
        cls: Type[LU],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
    ) -> LU:
        leaderboard_user = super().from_binary(binary, order, version, encoding, errors)

        reader = Reader(binary)

        place = reader.read_u32(order)

        leaderboard_user.place = place

        return leaderboard_user

    def to_binary(
        self,
        binary: BinaryWriter,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
    ) -> None:
        super().to_binary(binary, order, version, encoding, errors)

        writer = Writer(binary)

        writer.write_u32(self.place, order)


LLU = TypeVar("LLU", bound="LevelLeaderboardUser")


@define()
class LevelLeaderboardUser(LeaderboardUser):
    coins: int = field(default=DEFAULT_COINS, eq=False)
    record: int = field(default=DEFAULT_RECORD, eq=False)

    recorded_at: Optional[datetime] = None

    @classmethod
    def from_level_leaderboard_user_model(cls: Type[LLU], model: LevelLeaderboardUserModel) -> LLU:
        return cls(
            name=model.name,
            id=model.id,
            record=model.record,
            place=model.place,
            icon_id=model.icon_id,
            color_1_id=model.color_1_id,
            color_2_id=model.color_2_id,
            coins=model.coins,
            icon_type=model.icon_type,
            glow=model.glow,
            account_id=model.account_id,
            recorded_at=model.recorded_at,
        )

    @classmethod
    def from_binary(
        cls: Type[LLU],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
    ) -> LLU:
        level_leaderboard_user = super().from_binary(binary, order, version, encoding, errors)

        reader = Reader(binary)

        coins = reader.read_u8(order)

        record = reader.read_u8(order)

        timestamp = reader.read_f64(order)

        if timestamp:
            recorded_at = datetime.fromtimestamp(timestamp)

        else:
            recorded_at = None

        level_leaderboard_user.coins = coins
        level_leaderboard_user.record = record
        level_leaderboard_user.recorded_at = recorded_at

        return level_leaderboard_user

    def to_binary(
        self,
        binary: BinaryWriter,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
    ) -> None:
        super().to_binary(binary, order, version, encoding, errors)

        writer = Writer(binary)

        writer.write_u8(self.coins, order)

        writer.write_u8(self.record, order)

        recorded_at = self.recorded_at

        if recorded_at is None:
            timestamp = 0.0

        else:
            timestamp = recorded_at.timestamp()

        writer.write_f64(timestamp, order)
