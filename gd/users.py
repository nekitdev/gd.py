from __future__ import annotations

from typing import TYPE_CHECKING, AsyncIterator, Dict, Iterable, Optional

from attrs import define, field
from iters.async_iters import wrap_async_iter
from iters.iters import iter
from typing_extensions import Self

from gd.binary import Binary
from gd.color import Color
from gd.constants import (
    DEFAULT_BANNED,
    DEFAULT_COINS,
    DEFAULT_COLOR_1_ID,
    DEFAULT_COLOR_2_ID,
    DEFAULT_COLOR_3_ID,
    DEFAULT_CREATOR_POINTS,
    DEFAULT_DEMONS,
    DEFAULT_DIAMONDS,
    DEFAULT_FRIEND_STATE,
    DEFAULT_GLOW,
    DEFAULT_ICON_ID,
    DEFAULT_ID,
    DEFAULT_MOONS,
    DEFAULT_PAGE,
    DEFAULT_PAGES,
    DEFAULT_RANK,
    DEFAULT_SECRET_COINS,
    DEFAULT_SIMPLE,
    DEFAULT_STARS,
    DEFAULT_USER_COINS,
    EMPTY,
    UNKNOWN,
)
from gd.converter import CONVERTER, register_unstructure_hook_omit_client
from gd.date_time import timestamp_milliseconds, utc_from_timestamp_milliseconds, utc_now
from gd.either_record import EitherRecord, EitherRecordData
from gd.entity import Entity, EntityData
from gd.enums import (
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
from gd.models import CreatorModel
from gd.schema import (
    UserCosmeticsSchema,
    UserLeaderboardSchema,
    UserReferenceSchema,
    UserSchema,
    UserSocialsSchema,
    UserStatesSchema,
    UserStatisticsSchema,
)
from gd.schema_constants import NONE
from gd.typing import Data

if TYPE_CHECKING:
    from io import BufferedReader, BufferedWriter

    from pendulum import DateTime
    from PIL.Image import Image

    from gd.comments import LevelComment, UserComment
    from gd.friend_request import FriendRequest
    from gd.levels import Level
    from gd.message import Message
    from gd.models import (
        LeaderboardUserModel,
        LevelCommentUserModel,
        LevelLeaderboardUserModel,
        ProfileModel,
        RelationshipUserModel,
        SearchUserModel,
    )
    from gd.schema import (
        UserBuilder,
        UserCosmeticsBuilder,
        UserCosmeticsReader,
        UserLeaderboardBuilder,
        UserLeaderboardReader,
        UserReader,
        UserReferenceBuilder,
        UserReferenceReader,
        UserSocialsBuilder,
        UserSocialsReader,
        UserStatesBuilder,
        UserStatesReader,
        UserStatisticsBuilder,
        UserStatisticsReader,
    )

__all__ = (
    "User",
    "UserStatistics",
    "UserCosmetics",
    "UserStates",
    "UserSocials",
)


class UserReferenceData(EntityData):
    name: str
    account_id: int


@define()
class UserReference(Entity, Binary):
    name: str = field(eq=False)
    account_id: int = field(eq=False)

    @classmethod
    def default(cls, id: int = DEFAULT_ID, account_id: int = DEFAULT_ID, name: str = EMPTY) -> Self:
        return cls(id=id, account_id=account_id, name=name)

    def is_registered(self) -> bool:
        return self.account_id > 0 and self.id > 0

    @classmethod
    def from_creator_model(cls, model: CreatorModel) -> Self:
        return cls(id=model.id, name=model.name, account_id=model.account_id)

    @classmethod
    def from_binary(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(UserReferenceSchema.read(binary))

    @classmethod
    def from_binary_packed(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(UserReferenceSchema.read_packed(binary))

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        with UserReferenceSchema.from_bytes(data) as reader:
            return cls.from_reader(reader)

    @classmethod
    def from_bytes_packed(cls, data: bytes) -> Self:
        return cls.from_reader(UserReferenceSchema.from_bytes_packed(data))

    def to_binary(self, binary: BufferedWriter) -> None:
        self.to_builder().write(binary)

    def to_binary_packed(self, binary: BufferedWriter) -> None:
        self.to_builder().write_packed(binary)

    def to_bytes(self) -> bytes:
        return self.to_builder().to_bytes()

    def to_bytes_packed(self) -> bytes:
        return self.to_builder().to_bytes_packed()

    @classmethod
    def from_reader(cls, reader: UserReferenceReader) -> Self:
        return cls(id=reader.id, name=reader.name, account_id=reader.accountId)

    def to_builder(self) -> UserReferenceBuilder:
        builder = UserReferenceSchema.new_message()

        builder.id = self.id
        builder.name = self.name
        builder.accountId = self.account_id

        return builder

    async def get(
        self, simple: bool = DEFAULT_SIMPLE, friend_state: bool = DEFAULT_FRIEND_STATE
    ) -> User:
        return await self.client.get_user(self.account_id, simple=simple, friend_state=friend_state)

    async def update(self, friend_state: bool = DEFAULT_FRIEND_STATE) -> Self:
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


class UserStatisticsData(Data):
    stars: int
    moons: int
    demons: int
    diamonds: int
    user_coins: int
    secret_coins: int
    creator_points: int
    rank: int


@define()
class UserStatistics(Binary):
    stars: int = DEFAULT_STARS
    moons: int = DEFAULT_MOONS
    demons: int = DEFAULT_DEMONS
    diamonds: int = DEFAULT_DIAMONDS
    user_coins: int = DEFAULT_USER_COINS
    secret_coins: int = DEFAULT_SECRET_COINS
    creator_points: int = DEFAULT_CREATOR_POINTS
    rank: int = DEFAULT_RANK

    @classmethod
    def from_data(cls, data: UserStatisticsData) -> Self:
        return CONVERTER.structure(data, cls)

    def into_data(self) -> UserStatisticsData:
        return CONVERTER.unstructure(self)  # type: ignore

    @classmethod
    def from_binary(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(UserStatisticsSchema.read(binary))

    @classmethod
    def from_binary_packed(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(UserStatisticsSchema.read_packed(binary))

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        with UserStatisticsSchema.from_bytes(data) as reader:
            return cls.from_reader(reader)

    @classmethod
    def from_bytes_packed(cls, data: bytes) -> Self:
        return cls.from_reader(UserStatisticsSchema.from_bytes_packed(data))

    def to_binary(self, binary: BufferedWriter) -> None:
        self.to_builder().write(binary)

    def to_binary_packed(self, binary: BufferedWriter) -> None:
        self.to_builder().write_packed(binary)

    def to_bytes(self) -> bytes:
        return self.to_builder().to_bytes()

    def to_bytes_packed(self) -> bytes:
        return self.to_builder().to_bytes_packed()

    @classmethod
    def from_reader(cls, reader: UserStatisticsReader) -> Self:
        return cls(
            stars=reader.stars,
            moons=reader.moons,
            demons=reader.demons,
            diamonds=reader.diamonds,
            user_coins=reader.userCoins,
            secret_coins=reader.secretCoins,
            creator_points=reader.creatorPoints,
            rank=reader.rank,
        )

    def to_builder(self) -> UserStatisticsBuilder:
        builder = UserStatisticsSchema.new_message()

        builder.stars = self.stars
        builder.moons = self.moons
        builder.demons = self.demons
        builder.diamonds = self.diamonds
        builder.userCoins = self.user_coins
        builder.secretCoins = self.secret_coins
        builder.creatorPoints = self.creator_points
        builder.rank = self.rank

        return builder


class UserCosmeticsData(Data):
    color_1_id: int
    color_2_id: int
    color_3_id: int
    glow: bool
    icon_type: int
    icon_id: int
    cube_id: int
    ship_id: int
    ball_id: int
    ufo_id: int
    wave_id: int
    robot_id: int
    spider_id: int
    swing_id: int
    jetpack_id: int
    explosion_id: int
    streak_id: int


@define()
class UserCosmetics(Binary):
    color_1_id: int = DEFAULT_COLOR_1_ID
    color_2_id: int = DEFAULT_COLOR_2_ID
    color_3_id: int = DEFAULT_COLOR_3_ID
    glow: bool = DEFAULT_GLOW
    icon_type: IconType = IconType.DEFAULT
    icon_id: int = DEFAULT_ICON_ID
    cube_id: int = DEFAULT_ICON_ID
    ship_id: int = DEFAULT_ICON_ID
    ball_id: int = DEFAULT_ICON_ID
    ufo_id: int = DEFAULT_ICON_ID
    wave_id: int = DEFAULT_ICON_ID
    robot_id: int = DEFAULT_ICON_ID
    spider_id: int = DEFAULT_ICON_ID
    swing_id: int = DEFAULT_ICON_ID
    jetpack_id: int = DEFAULT_ICON_ID
    explosion_id: int = DEFAULT_ICON_ID
    streak_id: int = DEFAULT_ICON_ID

    @classmethod
    def from_data(cls, data: UserCosmeticsData) -> Self:
        return CONVERTER.structure(data, cls)

    def into_data(self) -> UserCosmeticsData:
        return CONVERTER.unstructure(self)  # type: ignore

    @classmethod
    def from_binary(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(UserCosmeticsSchema.read(binary))

    @classmethod
    def from_binary_packed(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(UserCosmeticsSchema.read_packed(binary))

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        with UserCosmeticsSchema.from_bytes(data) as reader:
            return cls.from_reader(reader)

    @classmethod
    def from_bytes_packed(cls, data: bytes) -> Self:
        return cls.from_reader(UserCosmeticsSchema.from_bytes_packed(data))

    def to_binary(self, binary: BufferedWriter) -> None:
        self.to_builder().write(binary)

    def to_binary_packed(self, binary: BufferedWriter) -> None:
        self.to_builder().write_packed(binary)

    def to_bytes(self) -> bytes:
        return self.to_builder().to_bytes()

    def to_bytes_packed(self) -> bytes:
        return self.to_builder().to_bytes_packed()

    @classmethod
    def from_reader(cls, reader: UserCosmeticsReader) -> Self:
        return cls(
            color_1_id=reader.color1Id,
            color_2_id=reader.color2Id,
            color_3_id=reader.color3Id,
            glow=reader.glow,
            icon_type=IconType(reader.iconType),
            icon_id=reader.iconId,
            cube_id=reader.cubeId,
            ship_id=reader.shipId,
            ball_id=reader.ballId,
            ufo_id=reader.ufoId,
            wave_id=reader.waveId,
            robot_id=reader.robotId,
            spider_id=reader.spiderId,
            swing_id=reader.swingId,
            jetpack_id=reader.jetpackId,
            explosion_id=reader.explosionId,
            streak_id=reader.streakId,
        )

    def to_builder(self) -> UserCosmeticsBuilder:
        builder = UserCosmeticsSchema.new_message()

        builder.color1Id = self.color_1_id
        builder.color2Id = self.color_2_id
        builder.color3Id = self.color_3_id
        builder.glow = self.has_glow()
        builder.iconType = self.icon_type.value
        builder.iconId = self.icon_id
        builder.cubeId = self.cube_id
        builder.shipId = self.ship_id
        builder.ballId = self.ball_id
        builder.ufoId = self.ufo_id
        builder.waveId = self.wave_id
        builder.robotId = self.robot_id
        builder.spiderId = self.spider_id
        builder.swingId = self.swing_id
        builder.jetpackId = self.jetpack_id
        builder.explosionId = self.explosion_id
        builder.streakId = self.streak_id

        return builder

    @property
    def color_1(self) -> Color:
        return Color.with_id(self.color_1_id, Color.default_color_1())

    @property
    def color_2(self) -> Color:
        return Color.with_id(self.color_2_id, Color.default_color_2())

    @property
    def color_3(self) -> Color:
        return Color.with_id(self.color_3_id, Color.default_color_3())

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
            IconType.SWING: self.swing_id,
            IconType.JETPACK: self.jetpack_id,
        }

    def get_icon(self, type: Optional[IconType] = None) -> Icon:
        if type is None:
            return Icon(
                self.icon_type, self.icon_id, self.color_1, self.color_2, self.color_3, self.glow
            )

        return Icon(
            type, self.icon_id_by_type[type], self.color_1, self.color_2, self.color_3, self.glow
        )

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
    def from_data(cls, data: UserStatesData) -> Self:
        return CONVERTER.structure(data, cls)

    def into_data(self) -> UserStatesData:
        return CONVERTER.unstructure(self)  # type: ignore

    @classmethod
    def from_binary(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(UserStatesSchema.read(binary))

    @classmethod
    def from_binary_packed(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(UserStatesSchema.read_packed(binary))

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        with UserStatesSchema.from_bytes(data) as reader:
            return cls.from_reader(reader)

    @classmethod
    def from_bytes_packed(cls, data: bytes) -> Self:
        return cls.from_reader(UserStatesSchema.from_bytes_packed(data))

    def to_binary(self, binary: BufferedWriter) -> None:
        self.to_builder().write(binary)

    def to_binary_packed(self, binary: BufferedWriter) -> None:
        self.to_builder().write_packed(binary)

    def to_bytes(self) -> bytes:
        return self.to_builder().to_bytes()

    def to_bytes_packed(self) -> bytes:
        return self.to_builder().to_bytes_packed()

    @classmethod
    def from_reader(cls, reader: UserStatesReader) -> Self:
        return cls(
            message_state=MessageState(reader.messageState),
            friend_request_state=FriendRequestState(reader.friendRequestState),
            comment_state=CommentState(reader.commentState),
            friend_state=FriendState(reader.friendState),
        )

    def to_builder(self) -> UserStatesBuilder:
        builder = UserStatesSchema.new_message()

        builder.messageState = self.message_state.value
        builder.friendRequestState = self.friend_request_state.value
        builder.commentState = self.comment_state.value
        builder.friendState = self.friend_state.value

        return builder


class UserSocialsData(Data):
    youtube: Optional[str]
    x: Optional[str]
    twitch: Optional[str]
    discord: Optional[str]


@define()
class UserSocials(Binary):
    youtube: Optional[str] = None
    x: Optional[str] = None
    twitch: Optional[str] = None
    discord: Optional[str] = None

    @classmethod
    def from_data(cls, data: UserSocialsData) -> Self:
        return CONVERTER.structure(data, cls)

    def into_data(self) -> UserSocialsData:
        return CONVERTER.unstructure(self)  # type: ignore

    @classmethod
    def from_binary(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(UserSocialsSchema.read(binary))

    @classmethod
    def from_binary_packed(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(UserSocialsSchema.read_packed(binary))

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        with UserSocialsSchema.from_bytes(data) as reader:
            return cls.from_reader(reader)

    @classmethod
    def from_bytes_packed(cls, data: bytes) -> Self:
        return cls.from_reader(UserSocialsSchema.from_bytes_packed(data))

    def to_binary(self, binary: BufferedWriter) -> None:
        self.to_builder().write(binary)

    def to_binary_packed(self, binary: BufferedWriter) -> None:
        self.to_builder().write_packed(binary)

    def to_bytes(self) -> bytes:
        return self.to_builder().to_bytes()

    def to_bytes_packed(self) -> bytes:
        return self.to_builder().to_bytes_packed()

    @classmethod
    def from_reader(cls, reader: UserSocialsReader) -> Self:
        youtube_option = reader.youtube

        if youtube_option.which() == NONE:
            youtube = None

        else:
            youtube = youtube_option.some

        x_option = reader.x

        if x_option.which() == NONE:
            x = None

        else:
            x = x_option.some

        twitch_option = reader.twitch

        if twitch_option.which() == NONE:
            twitch = None

        else:
            twitch = twitch_option.some

        discord_option = reader.discord

        if discord_option.which() == NONE:
            discord = None

        else:
            discord = discord_option.some

        return cls(youtube=youtube, x=x, twitch=twitch, discord=discord)

    def to_builder(self) -> UserSocialsBuilder:
        builder = UserSocialsSchema.new_message()

        youtube = self.youtube

        if youtube is None:
            builder.youtube.none = None

        else:
            builder.youtube.some = youtube

        x = self.x

        if x is None:
            builder.x.none = None

        else:
            builder.x.some = x

        twitch = self.twitch

        if twitch is None:
            builder.twitch.none = None

        else:
            builder.twitch.some = twitch

        discord = self.discord

        if discord is None:
            builder.discord.none = None

        else:
            builder.discord.some = discord

        return builder


class UserLeaderboardData(Data):
    record: EitherRecordData
    coins: int
    recorded_at: str


class UserLeaderboard(Binary):
    record: EitherRecord = field(factory=EitherRecord)
    coins: int = field(default=DEFAULT_COINS)
    recorded_at: DateTime = field(factory=utc_now)

    @classmethod
    def from_data(cls, data: UserLeaderboardData) -> Self:
        return CONVERTER.structure(data, cls)

    def into_data(self) -> UserLeaderboardData:
        return CONVERTER.unstructure(self)  # type: ignore

    @classmethod
    def from_binary(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(UserLeaderboardSchema.read(binary))

    @classmethod
    def from_binary_packed(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(UserLeaderboardSchema.read_packed(binary))

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        with UserLeaderboardSchema.from_bytes(data) as reader:
            return cls.from_reader(reader)

    @classmethod
    def from_bytes_packed(cls, data: bytes) -> Self:
        return cls.from_reader(UserLeaderboardSchema.from_bytes_packed(data))

    def to_binary(self, binary: BufferedWriter) -> None:
        self.to_builder().write(binary)

    def to_binary_packed(self, binary: BufferedWriter) -> None:
        self.to_builder().write_packed(binary)

    def to_bytes(self) -> bytes:
        return self.to_builder().to_bytes()

    def to_bytes_packed(self) -> bytes:
        return self.to_builder().to_bytes_packed()

    @classmethod
    def from_reader(cls, reader: UserLeaderboardReader) -> Self:
        return cls(
            record=EitherRecord.from_reader(reader.record),
            coins=reader.coins,
            recorded_at=utc_from_timestamp_milliseconds(reader.recordedAt),
        )

    def to_builder(self) -> UserLeaderboardBuilder:
        builder = UserLeaderboardSchema.new_message()

        builder.record = self.record.to_builder()
        builder.coins = self.coins
        builder.recordedAt = timestamp_milliseconds(self.recorded_at)

        return builder


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


@register_unstructure_hook_omit_client
@define()
class User(UserReference, Binary):
    role_id: int = field(default=DEFAULT_ID, eq=False)
    banned: bool = field(default=DEFAULT_BANNED, eq=False)
    statistics: Optional[UserStatistics] = field(default=None, eq=False)
    cosmetics: Optional[UserCosmetics] = field(default=None, eq=False)
    states: Optional[UserStates] = field(default=None, eq=False)
    socials: Optional[UserSocials] = field(default=None, eq=False)
    place: Optional[int] = field(default=None, eq=False)
    leaderboard: Optional[UserLeaderboard] = field(default=None, eq=False)

    @classmethod
    def from_data(cls, data: UserData) -> Self:  # type: ignore
        return CONVERTER.structure(data, cls)

    def into_data(self) -> UserData:
        return CONVERTER.unstructure(self)  # type: ignore

    @classmethod
    def from_binary(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(UserSchema.read(binary))

    @classmethod
    def from_binary_packed(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(UserSchema.read_packed(binary))

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        with UserSchema.from_bytes(data) as reader:
            return cls.from_reader(reader)

    @classmethod
    def from_bytes_packed(cls, data: bytes) -> Self:
        return cls.from_reader(UserSchema.from_bytes_packed(data))

    def to_binary(self, binary: BufferedWriter) -> None:
        self.to_builder().write(binary)

    def to_binary_packed(self, binary: BufferedWriter) -> None:
        self.to_builder().write_packed(binary)

    def to_bytes(self) -> bytes:
        return self.to_builder().to_bytes()

    def to_bytes_packed(self) -> bytes:
        return self.to_builder().to_bytes_packed()

    @classmethod
    def from_reader(cls, reader: UserReader) -> Self:
        statistics_option = reader.statistics

        if statistics_option.which() == NONE:
            statistics = None

        else:
            statistics = UserStatistics.from_reader(statistics_option.some)

        cosmetics_option = reader.cosmetics

        if cosmetics_option.which() == NONE:
            cosmetics = None

        else:
            cosmetics = UserCosmetics.from_reader(cosmetics_option.some)

        states_option = reader.states

        if states_option.which() == NONE:
            states = None

        else:
            states = UserStates.from_reader(states_option.some)

        socials_option = reader.socials

        if socials_option.which() == NONE:
            socials = None

        else:
            socials = UserSocials.from_reader(socials_option.some)

        place_option = reader.place

        if place_option.which() == NONE:
            place = None

        else:
            place = place_option.some

        leaderboard_option = reader.leaderboard

        if leaderboard_option.which() == NONE:
            leaderboard = None

        else:
            leaderboard = UserLeaderboard.from_reader(leaderboard_option.some)

        return cls(
            id=reader.id,
            name=reader.name,
            account_id=reader.accountId,
            role_id=reader.roleId,
            banned=reader.banned,
            statistics=statistics,
            cosmetics=cosmetics,
            states=states,
            socials=socials,
            place=place,
            leaderboard=leaderboard,
        )

    def to_builder(self) -> UserBuilder:
        builder = UserSchema.new_message()

        builder.id = self.id
        builder.name = self.name
        builder.accountId = self.account_id
        builder.roleId = self.role_id
        builder.banned = self.banned

        statistics = self.statistics

        if statistics is None:
            builder.statistics.none = None

        else:
            builder.statistics.some = statistics.to_builder()

        cosmetics = self.cosmetics

        if cosmetics is None:
            builder.cosmetics.none = None

        else:
            builder.cosmetics.some = cosmetics.to_builder()

        states = self.states

        if states is None:
            builder.states.none = None

        else:
            builder.states.some = states.to_builder()

        socials = self.socials

        if socials is None:
            builder.socials.none = None

        else:
            builder.socials.some = socials.to_builder()

        place = self.place

        if place is None:
            builder.place.none = None

        else:
            builder.place.some = place

        leaderboard = self.leaderboard

        if leaderboard is None:
            builder.leaderboard.none = None

        else:
            builder.leaderboard.some = leaderboard.to_builder()

        return builder

    @classmethod
    def default(cls, id: int = DEFAULT_ID, account_id: int = DEFAULT_ID) -> Self:
        return cls(id=id, name=EMPTY, account_id=account_id)

    @classmethod
    def from_search_user_model(cls, model: SearchUserModel) -> Self:
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
    def from_profile_model(cls, model: ProfileModel) -> Self:
        return cls(
            name=model.name,
            id=model.id,
            account_id=model.account_id,
            role_id=model.role_id,
            banned=model.banned,
            statistics=UserStatistics(
                stars=model.stars,
                moons=model.moons,
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
                color_3_id=model.color_3_id,
                glow=model.has_glow(),
                cube_id=model.cube_id,
                ship_id=model.ship_id,
                ball_id=model.ball_id,
                ufo_id=model.ufo_id,
                wave_id=model.wave_id,
                robot_id=model.robot_id,
                spider_id=model.spider_id,
                swing_id=model.swing_id,
                jetpack_id=model.jetpack_id,
                explosion_id=model.explosion_id,
                # streak_id=model.streak_id,
            ),
            states=UserStates(
                message_state=model.message_state,
                friend_request_state=model.friend_request_state,
                comment_state=model.comment_state,
                friend_state=model.friend_state,
            ),
            socials=UserSocials(
                youtube=model.youtube,
                x=model.x,
                twitch=model.twitch,
                # discord=model.discord,
            ),
        )

    @classmethod
    def from_search_user_and_profile_models(
        cls, search_user_model: SearchUserModel, profile_model: ProfileModel
    ) -> Self:
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
                # swing_id=profile_model.swing_id,
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
    def from_relationship_user_model(cls, model: RelationshipUserModel) -> Self:
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
    def from_level_comment_user_model(cls, model: LevelCommentUserModel, id: int) -> Self:
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
    def from_leaderboard_user_model(cls, model: LeaderboardUserModel) -> Self:
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
    def from_level_leaderboard_user_model(cls, model: LevelLeaderboardUserModel) -> Self:
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
        return self.banned

    def is_registered(self) -> bool:
        return self.account_id > 0 and self.id > 0
