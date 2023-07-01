from __future__ import annotations

from enum import Flag
from typing import TYPE_CHECKING, AsyncIterator, Dict, Iterable, Optional, Type, TypeVar

from attrs import define, field
from iters.async_iters import wrap_async_iter
from iters.iters import iter
from pendulum import DateTime
from typing_extensions import TypedDict as Data

from gd.binary import VERSION, Binary, BinaryReader, BinaryWriter
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
    DEFAULT_PAGE,
    DEFAULT_PAGES,
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
from gd.converter import CONVERTER, register_unstructure_hook_omit_client
from gd.date_time import utc_from_timestamp, utc_now
from gd.entity import Entity, EntityData
from gd.enums import (
    ByteOrder,
    CommentState,
    CommentStrategy,
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
from gd.models import (
    CreatorModel,
    LeaderboardUserModel,
    LevelCommentUserModel,
    LevelLeaderboardUserModel,
    ProfileModel,
    RelationshipUserModel,
    SearchUserModel,
)

if TYPE_CHECKING:
    from PIL.Image import Image

    from gd.comments import LevelComment, UserComment
    from gd.friend_request import FriendRequest
    from gd.level import Level
    from gd.message import Message

__all__ = (
    "User",
    "UserStatistics",
    "UserCosmetics",
    "UserStates",
    "UserSocials",
    "UserLeaderboard",
)

U = TypeVar("U", bound="User")

UStatistics = TypeVar("UStatistics", bound="UserStatistics")
UCosmetics = TypeVar("UCosmetics", bound="UserCosmetics")
UStates = TypeVar("UStates", bound="UserStates")
USocials = TypeVar("USocials", bound="UserSocials")
ULeaderboard = TypeVar("ULeaderboard", bound="UserLeaderboard")

MESSAGE_STATE_MASK = 0b00000011
FRIEND_REQUEST_STATE_MASK = 0b00000100
COMMENT_STATE_MASK = 0b00011000
FRIEND_STATE_MASK = 0b11100000

FRIEND_REQUEST_STATE_SHIFT = MESSAGE_STATE_MASK.bit_length()
COMMENT_STATE_SHIFT = FRIEND_REQUEST_STATE_MASK.bit_length()
FRIEND_STATE_SHIFT = COMMENT_STATE_MASK.bit_length()

BANNED_BIT = 0b00000001

USER_FLAG_SHIFT = BANNED_BIT.bit_length()

GLOW_BIT = 0b00000001

ICON_TYPE_SHIFT = GLOW_BIT.bit_length()


class UserStatisticsData(Data):
    stars: int
    demons: int
    diamonds: int
    user_coins: int
    secret_coins: int
    creator_points: int
    rank: int


@define()
class UserStatistics(Binary):
    stars: int = DEFAULT_STARS
    demons: int = DEFAULT_DEMONS
    diamonds: int = DEFAULT_DIAMONDS
    user_coins: int = DEFAULT_USER_COINS
    secret_coins: int = DEFAULT_SECRET_COINS
    creator_points: int = DEFAULT_CREATOR_POINTS
    rank: int = DEFAULT_RANK

    @classmethod
    def from_data(cls: Type[UStatistics], data: UserStatisticsData) -> UStatistics:
        return CONVERTER.structure(data, cls)

    def into_data(self) -> UserStatisticsData:
        return CONVERTER.unstructure(self)  # type: ignore

    @classmethod
    def from_binary(
        cls: Type[UStatistics],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> UStatistics:
        reader = Reader(binary, order)

        stars = reader.read_u32()
        demons = reader.read_u16()
        diamonds = reader.read_u32()
        user_coins = reader.read_u32()
        secret_coins = reader.read_u16()
        creator_points = reader.read_u16()

        rank = reader.read_u32()

        return cls(
            stars=stars,
            demons=demons,
            diamonds=diamonds,
            user_coins=user_coins,
            secret_coins=secret_coins,
            creator_points=creator_points,
            rank=rank,
        )

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        writer = Writer(binary, order)

        writer.write_u32(self.stars)
        writer.write_u16(self.demons)
        writer.write_u32(self.diamonds)
        writer.write_u32(self.user_coins)
        writer.write_u16(self.secret_coins)
        writer.write_u16(self.creator_points)

        writer.write_u32(self.rank)


class UserCosmeticsData(Data):
    color_1_id: int
    color_2_id: int
    icon_type: int
    icon_id: int
    cube_id: int
    ship_id: int
    ball_id: int
    ufo_id: int
    wave_id: int
    robot_id: int
    spider_id: int
    swing_copter_id: int
    explosion_id: int
    glow: bool


@define()
class UserCosmetics(Binary):
    color_1_id: int = DEFAULT_COLOR_1_ID
    color_2_id: int = DEFAULT_COLOR_2_ID
    icon_type: IconType = IconType.DEFAULT
    icon_id: int = DEFAULT_ICON_ID
    cube_id: int = DEFAULT_ICON_ID
    ship_id: int = DEFAULT_ICON_ID
    ball_id: int = DEFAULT_ICON_ID
    ufo_id: int = DEFAULT_ICON_ID
    wave_id: int = DEFAULT_ICON_ID
    robot_id: int = DEFAULT_ICON_ID
    spider_id: int = DEFAULT_ICON_ID
    # swing_copter_id: int = DEFAULT_ICON_ID
    explosion_id: int = DEFAULT_ICON_ID
    glow: bool = DEFAULT_GLOW

    @classmethod
    def from_data(cls: Type[UCosmetics], data: UserCosmeticsData) -> UCosmetics:
        return CONVERTER.structure(data, cls)

    def into_data(self) -> UserCosmeticsData:
        return CONVERTER.unstructure(self)  # type: ignore

    @classmethod
    def from_binary(
        cls: Type[UCosmetics],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> UCosmetics:
        glow_bit = GLOW_BIT

        reader = Reader(binary, order)

        color_1_id = reader.read_u8()
        color_2_id = reader.read_u8()

        value = reader.read_u8()

        glow = value & glow_bit == glow_bit

        value >>= ICON_TYPE_SHIFT

        icon_type = IconType(value)

        icon_id = reader.read_u16()
        cube_id = reader.read_u16()
        ship_id = reader.read_u8()
        ball_id = reader.read_u8()
        ufo_id = reader.read_u8()
        wave_id = reader.read_u8()
        robot_id = reader.read_u8()
        spider_id = reader.read_u8()
        # swing_copter_id = reader.read_u8()

        explosion_id = reader.read_u8()

        return cls(
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
        )

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        writer = Writer(binary, order)

        writer.write_u8(self.color_1_id)
        writer.write_u8(self.color_2_id)

        value = 0

        if self.has_glow():
            value |= GLOW_BIT

        value |= self.icon_type.value << ICON_TYPE_SHIFT

        writer.write_u8(value)

        writer.write_u16(self.icon_id)
        writer.write_u16(self.cube_id)
        writer.write_u8(self.ship_id)
        writer.write_u8(self.ball_id)
        writer.write_u8(self.ufo_id)
        writer.write_u8(self.wave_id)
        writer.write_u8(self.robot_id)
        writer.write_u8(self.spider_id)
        # writer.write_u8(self.swing_copter_id)

        writer.write_u8(self.explosion_id)

    @property
    def color_1(self) -> Color:
        return Color.with_id(self.color_1_id, Color.default_color_1())

    @property
    def color_2(self) -> Color:
        return Color.with_id(self.color_2_id, Color.default_color_2())

    def has_glow(self) -> bool:
        return self.glow

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
        return connect_images(iter(types).map(self.generate).unwrap(), orientation)

    async def generate_many_async(
        self, *types: Optional[IconType], orientation: Orientation = Orientation.DEFAULT
    ) -> Image:
        return connect_images(
            await iter(types)
            .map(self.generate_async)
            .into_async_iter()
            .wait_concurrent()
            .extract(),
            orientation,
        )

    def generate_full(self, orientation: Orientation = Orientation.DEFAULT) -> Image:
        return self.generate_many(*IconType, orientation=orientation)

    async def generate_full_async(self, orientation: Orientation = Orientation.DEFAULT) -> Image:
        return await self.generate_many_async(*IconType, orientation=orientation)


class UserStatesData(Data):
    message_state: int
    friend_request_state: int
    comment_state: int
    friend_state: int


@define()
class UserStates(Binary):
    message_state: MessageState = MessageState.DEFAULT
    friend_request_state: FriendRequestState = FriendRequestState.DEFAULT
    comment_state: CommentState = CommentState.DEFAULT
    friend_state: FriendState = FriendState.DEFAULT

    @classmethod
    def from_data(cls: Type[UStates], data: UserStatesData) -> UStates:
        return CONVERTER.structure(data, cls)

    def into_data(self) -> UserStatesData:
        return CONVERTER.unstructure(self)  # type: ignore

    @classmethod
    def from_binary(
        cls: Type[UStates],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> UStates:
        reader = Reader(binary, order)

        value = reader.read_u8()

        message_state_value = value & MESSAGE_STATE_MASK
        friend_request_state_value = (
            value & FRIEND_REQUEST_STATE_MASK
        ) >> FRIEND_REQUEST_STATE_SHIFT
        comment_state_value = (value & COMMENT_STATE_MASK) >> COMMENT_STATE_SHIFT
        friend_state_value = (value & FRIEND_STATE_MASK) >> FRIEND_STATE_SHIFT

        message_state = MessageState(message_state_value)
        friend_request_state = FriendRequestState(friend_request_state_value)
        comment_state = CommentState(comment_state_value)
        friend_state = FriendState(friend_state_value)

        return cls(
            message_state=message_state,
            friend_request_state=friend_request_state,
            comment_state=comment_state,
            friend_state=friend_state,
        )

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        writer = Writer(binary, order)

        value = self.message_state.value

        value |= self.friend_request_state.value << FRIEND_REQUEST_STATE_SHIFT
        value |= self.comment_state.value << COMMENT_STATE_SHIFT
        value |= self.friend_state.value << FRIEND_STATE_SHIFT

        writer.write_u8(value)


class UserSocialsData(Data):
    youtube: Optional[str]
    twitter: Optional[str]
    twitch: Optional[str]
    # discord: Optional[str]


@define()
class UserSocials(Binary):
    youtube: Optional[str] = None
    twitter: Optional[str] = None
    twitch: Optional[str] = None
    # discord: Optional[str] = None

    @classmethod
    def from_data(cls: Type[USocials], data: UserSocialsData) -> USocials:
        return CONVERTER.structure(data, cls)

    def into_data(self) -> UserSocialsData:
        return CONVERTER.unstructure(self)  # type: ignore

    @classmethod
    def from_binary(
        cls: Type[USocials],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
    ) -> USocials:
        reader = Reader(binary, order)

        youtube_length = reader.read_u8()

        if youtube_length:
            youtube = reader.read(youtube_length).decode(encoding, errors)

        else:
            youtube = None

        twitter_length = reader.read_u8()

        if twitter_length:
            twitter = reader.read(twitter_length).decode(encoding, errors)

        else:
            twitter = None

        twitch_length = reader.read_u8()

        if twitch_length:
            twitch = reader.read(twitch_length).decode(encoding, errors)

        else:
            twitch = None

        # discord_length = reader.read_u8()

        # if discord_length:
        #     discord = reader.read(discord_length).decode(encoding, errors)

        # else:
        #     discord = None

        return cls(
            youtube=youtube,
            twitter=twitter,
            twitch=twitch,
            # discord=discord,
        )

    def to_binary(
        self,
        binary: BinaryWriter,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
    ) -> None:
        writer = Writer(binary, order)

        youtube = self.youtube

        if youtube is None:
            writer.write_u8(0)

        else:
            data = youtube.encode(encoding, errors)

            writer.write_u8(len(data))

            writer.write(data)

        twitter = self.twitter

        if twitter is None:
            writer.write_u8(0)

        else:
            data = twitter.encode(encoding, errors)

            writer.write_u8(len(data))

            writer.write(data)

        twitch = self.twitch

        if twitch is None:
            writer.write_u8(0)

        else:
            data = twitch.encode(encoding, errors)

            writer.write_u8(len(data))

            writer.write(data)

        # discord = self.discord

        # if discord is None:
        #     writer.write_u8(0)

        # else:
        #     data = discord.encode(encoding, errors)

        #     writer.write_u8(len(data))

        #     writer.write(data)


class UserLeaderboardData(Data):
    record: int
    coins: int

    recorded_at: str


@define()
class UserLeaderboard(Binary):
    record: int = field(default=DEFAULT_RECORD)
    coins: int = field(default=DEFAULT_COINS)

    recorded_at: DateTime = field(factory=utc_now)

    @classmethod
    def from_data(cls: Type[ULeaderboard], data: UserLeaderboardData) -> ULeaderboard:
        return CONVERTER.structure(data, cls)

    def into_data(self) -> UserLeaderboardData:
        return CONVERTER.unstructure(self)  # type: ignore

    @classmethod
    def from_binary(
        cls: Type[ULeaderboard],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> ULeaderboard:
        reader = Reader(binary, order)

        record = reader.read_u8()

        coins = reader.read_u8()

        timestamp = reader.read_f64()

        recorded_at = utc_from_timestamp(timestamp)

        return cls(record=record, coins=coins, recorded_at=recorded_at)

    def to_binary(
        self,
        binary: BinaryWriter,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> None:
        writer = Writer(binary, order)

        writer.write_u8(self.record)

        writer.write_u8(self.coins)

        timestamp = self.recorded_at.timestamp()  # type: ignore

        writer.write_f64(timestamp)


class UserData(EntityData):
    name: str
    account_id: int
    role_id: int
    banned: bool
    statistics: Optional[UserStatisticsData]
    cosmetics: Optional[UserCosmeticsData]
    states: Optional[UserStatesData]
    socials: Optional[UserSocialsData]
    place: Optional[int]
    leaderboard: Optional[UserLeaderboardData]


class UserFlag(Flag):
    SIMPLE = 0

    STATISTICS = 1 << 0
    COSMETICS = 1 << 1
    STATES = 1 << 2
    SOCIALS = 1 << 3
    PLACE = 1 << 4
    LEADERBOARD = 1 << 5

    def has_statistics(self) -> bool:
        return type(self).STATISTICS in self

    def has_cosmetics(self) -> bool:
        return type(self).COSMETICS in self

    def has_states(self) -> bool:
        return type(self).STATES in self

    def has_socials(self) -> bool:
        return type(self).SOCIALS in self

    def has_place(self) -> bool:
        return type(self).PLACE in self

    def has_leaderboard(self) -> bool:
        return type(self).LEADERBOARD in self


@register_unstructure_hook_omit_client
@define()
class User(Entity):
    name: str = field(eq=False)
    account_id: int = field(eq=False)
    role_id: int = field(default=DEFAULT_ID, eq=False)
    banned: bool = field(default=DEFAULT_BANNED, eq=False)
    statistics: Optional[UserStatistics] = field(default=None, eq=False)
    cosmetics: Optional[UserCosmetics] = field(default=None, eq=False)
    states: Optional[UserStates] = field(default=None, eq=False)
    socials: Optional[UserSocials] = field(default=None, eq=False)
    place: Optional[int] = field(default=None, eq=False)
    leaderboard: Optional[UserLeaderboard] = field(default=None, eq=False)

    @classmethod
    def from_data(cls: Type[U], data: UserData) -> U:  # type: ignore
        return CONVERTER.structure(data, cls)

    def into_data(self) -> UserData:
        return CONVERTER.unstructure(self)  # type: ignore

    @classmethod
    def from_binary(
        cls: Type[U],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
    ) -> U:
        banned_bit = BANNED_BIT

        reader = Reader(binary, order)

        value = reader.read_u8()

        banned = value & banned_bit == banned_bit

        value >>= USER_FLAG_SHIFT

        user_flag = UserFlag(value)

        id = reader.read_u32()

        name_length = reader.read_u8()

        name = reader.read(name_length).decode(encoding, errors)

        account_id = reader.read_u32()

        role_id = reader.read_u8()

        if user_flag.has_statistics():
            statistics = UserStatistics.from_binary(binary, order, version)

        else:
            statistics = None

        if user_flag.has_cosmetics():
            cosmetics = UserCosmetics.from_binary(binary, order, version)

        else:
            cosmetics = None

        if user_flag.has_states():
            states = UserStates.from_binary(binary, order, version)

        else:
            states = None

        if user_flag.has_socials():
            socials = UserSocials.from_binary(binary, order, version, encoding, errors)

        else:
            socials = None

        if user_flag.has_place():
            place = reader.read_u32()

        else:
            place = None

        if user_flag.has_leaderboard():
            leaderboard = UserLeaderboard.from_binary(binary, order, version)

        else:
            leaderboard = None

        return cls(
            id=id,
            name=name,
            account_id=account_id,
            role_id=role_id,
            banned=banned,
            statistics=statistics,
            cosmetics=cosmetics,
            states=states,
            socials=socials,
            place=place,
            leaderboard=leaderboard,
        )

    def to_binary(
        self,
        binary: BinaryWriter,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
    ) -> None:
        writer = Writer(binary, order)

        value = 0

        if self.is_banned():
            value |= BANNED_BIT

        user_flag = UserFlag.SIMPLE

        statistics = self.statistics

        if statistics is not None:
            user_flag |= UserFlag.STATISTICS

        cosmetics = self.cosmetics

        if cosmetics is not None:
            user_flag |= UserFlag.COSMETICS

        states = self.states

        if states is not None:
            user_flag |= UserFlag.STATES

        socials = self.socials

        if socials is not None:
            user_flag |= UserFlag.SOCIALS

        place = self.place

        if place is not None:
            user_flag |= UserFlag.PLACE

        leaderboard = self.leaderboard

        if leaderboard is not None:
            user_flag |= UserFlag.LEADERBOARD

        value |= user_flag.value << USER_FLAG_SHIFT

        writer.write_u8(value)

        writer.write_u32(self.id)

        data = self.name.encode(encoding, errors)

        writer.write_u8(len(data))

        writer.write(data)

        writer.write_u32(self.account_id)

        writer.write_u8(self.role_id)

        if statistics is not None:
            statistics.to_binary(binary, order, version)

        if cosmetics is not None:
            cosmetics.to_binary(binary, order, version)

        if states is not None:
            states.to_binary(binary, order, version)

        if socials is not None:
            socials.to_binary(binary, order, version, encoding, errors)

        if place is not None:
            writer.write_u32(place)

        if leaderboard is not None:
            leaderboard.to_binary(binary, order, version)

    @classmethod
    def default(cls: Type[U], id: int = DEFAULT_ID, account_id: int = DEFAULT_ID) -> U:
        return cls(id=id, name=EMPTY, account_id=account_id)

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
            account_id=model.account_id,
            statistics=UserStatistics(
                stars=model.stars,
                demons=model.demons,
                creator_points=model.creator_points,
                secret_coins=model.secret_coins,
                user_coins=model.user_coins,
                rank=model.rank,
            ),
            cosmetics=UserCosmetics(
                color_1_id=model.color_1_id,
                color_2_id=model.color_2_id,
                icon_type=model.icon_type,
                icon_id=model.icon_id,
                glow=model.glow,
            ),
        )

    @classmethod
    def from_profile_model(cls: Type[U], model: ProfileModel) -> U:
        return cls(
            name=model.name,
            id=model.id,
            account_id=model.account_id,
            role_id=model.role_id,
            banned=model.banned,
            statistics=UserStatistics(
                stars=model.stars,
                demons=model.demons,
                diamonds=model.diamonds,
                user_coins=model.user_coins,
                secret_coins=model.secret_coins,
                creator_points=model.creator_points,
                rank=model.rank,
            ),
            cosmetics=UserCosmetics(
                color_1_id=model.color_1_id,
                color_2_id=model.color_2_id,
                cube_id=model.cube_id,
                ship_id=model.ship_id,
                ball_id=model.ball_id,
                ufo_id=model.ufo_id,
                wave_id=model.wave_id,
                robot_id=model.robot_id,
                spider_id=model.spider_id,
                # swing_copter_id=model.swing_copter_id,
                explosion_id=model.explosion_id,
                glow=model.glow,
            ),
            states=UserStates(
                message_state=model.message_state,
                friend_request_state=model.friend_request_state,
                comment_state=model.comment_state,
                friend_state=model.friend_state,
            ),
            socials=UserSocials(
                youtube=model.youtube,
                twitter=model.twitter,
                twitch=model.twitch,
                # discord=model.discord,
            ),
        )

    @classmethod
    def from_search_user_and_profile_models(
        cls: Type[U], search_user_model: SearchUserModel, profile_model: ProfileModel
    ) -> U:
        return cls(
            name=profile_model.name,
            id=profile_model.id,
            account_id=profile_model.account_id,
            role_id=profile_model.role_id,
            banned=profile_model.banned,
            statistics=UserStatistics(
                stars=profile_model.stars,
                demons=profile_model.demons,
                diamonds=profile_model.diamonds,
                user_coins=profile_model.user_coins,
                secret_coins=profile_model.secret_coins,
                creator_points=profile_model.creator_points,
                rank=profile_model.rank,
            ),
            cosmetics=UserCosmetics(
                color_1_id=profile_model.color_1_id,
                color_2_id=profile_model.color_2_id,
                icon_type=search_user_model.icon_type,
                icon_id=search_user_model.icon_id,
                cube_id=profile_model.cube_id,
                ship_id=profile_model.ship_id,
                ball_id=profile_model.ball_id,
                ufo_id=profile_model.ufo_id,
                wave_id=profile_model.wave_id,
                robot_id=profile_model.robot_id,
                spider_id=profile_model.spider_id,
                # swing_copter_id=profile_model.swing_copter_id,
                explosion_id=profile_model.explosion_id,
                glow=profile_model.glow,
            ),
            states=UserStates(
                message_state=profile_model.message_state,
                friend_request_state=profile_model.friend_request_state,
                comment_state=profile_model.comment_state,
                friend_state=profile_model.friend_state,
            ),
            socials=UserSocials(
                youtube=profile_model.youtube,
                twitter=profile_model.twitter,
                twitch=profile_model.twitch,
                # discord=profile_model.discord,
            ),
        )

    @classmethod
    def from_relationship_user_model(cls: Type[U], model: RelationshipUserModel) -> U:
        return cls(
            name=model.name,
            id=model.id,
            account_id=model.account_id,
            cosmetics=UserCosmetics(
                color_1_id=model.color_1_id,
                color_2_id=model.color_2_id,
                icon_type=model.icon_type,
                icon_id=model.icon_id,
                glow=model.glow,
            ),
            states=UserStates(message_state=model.message_state),
        )

    @classmethod
    def from_level_comment_user_model(cls: Type[U], model: LevelCommentUserModel, id: int) -> U:
        return cls(
            id=id,
            name=model.name,
            account_id=model.account_id,
            cosmetics=UserCosmetics(
                color_1_id=model.color_1_id,
                color_2_id=model.color_2_id,
                icon_type=model.icon_type,
                icon_id=model.icon_id,
                glow=model.glow,
            ),
        )

    @classmethod
    def from_leaderboard_user_model(cls: Type[U], model: LeaderboardUserModel) -> U:
        return cls(
            name=model.name,
            id=model.id,
            account_id=model.account_id,
            place=model.place,
            statistics=UserStatistics(
                stars=model.stars,
                demons=model.demons,
                diamonds=model.diamonds,
                user_coins=model.user_coins,
                secret_coins=model.secret_coins,
                creator_points=model.creator_points,
            ),
            cosmetics=UserCosmetics(
                color_1_id=model.color_1_id,
                color_2_id=model.color_2_id,
                icon_type=model.icon_type,
                icon_id=model.icon_id,
                glow=model.glow,
            ),
        )

    @classmethod
    def from_level_leaderboard_user_model(cls: Type[U], model: LevelLeaderboardUserModel) -> U:
        return cls(
            name=model.name,
            id=model.id,
            account_id=model.account_id,
            place=model.place,
            cosmetics=UserCosmetics(
                color_1_id=model.color_1_id,
                color_2_id=model.color_2_id,
                icon_type=model.icon_type,
                icon_id=model.icon_id,
                glow=model.glow,
            ),
            leaderboard=UserLeaderboard(
                record=model.record,
                coins=model.coins,
                recorded_at=model.recorded_at,
            ),
        )

    def __str__(self) -> str:
        return self.name or UNKNOWN

    @property
    def role(self) -> Role:
        return Role(self.role_id)

    def is_banned(self) -> bool:
        """Indicates whether the user is banned."""
        return self.banned

    def is_registered(self) -> bool:
        """Indicates whether the user is registered."""
        return self.account_id > 0 and self.id > 0

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
