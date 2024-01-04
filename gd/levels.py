from __future__ import annotations

from io import BufferedReader, BufferedWriter
from typing import TYPE_CHECKING, AsyncIterator, Iterable, Optional, TypeVar

from attrs import define, field
from iters.async_iters import wrap_async_iter
from pendulum import DateTime, Duration, duration

from gd.api.editor import Editor
from gd.binary import Binary
from gd.capacity import Capacity
from gd.constants import (
    COMMENT_PAGE_SIZE,
    DEFAULT_COINS,
    DEFAULT_DOWNLOADS,
    DEFAULT_GET_DATA,
    DEFAULT_ID,
    DEFAULT_LOW_DETAIL,
    DEFAULT_OBJECT_COUNT,
    DEFAULT_PAGE,
    DEFAULT_PAGES,
    DEFAULT_RATING,
    DEFAULT_RECORD,
    DEFAULT_SCORE,
    DEFAULT_TIME_STEPS,
    DEFAULT_TWO_PLAYER,
    DEFAULT_USE_CLIENT,
    DEFAULT_VERIFIED_COINS,
    DEFAULT_VERSION,
    EMPTY,
    UNKNOWN,
)
from gd.converter import CONVERTER, register_unstructure_hook_omit_client
from gd.date_time import (
    duration_milliseconds,
    timestamp_milliseconds,
    utc_from_timestamp_milliseconds,
)
from gd.either_reward import EitherReward
from gd.encoding import compress, decompress, unzip_level_string, zip_level_string
from gd.entity import Entity, EntityData
from gd.enums import (
    CommentStrategy,
    DemonDifficulty,
    Difficulty,
    LevelLeaderboardStrategy,
    LevelLength,
    LevelPrivacy,
    RateType,
    TimelyType,
)
from gd.errors import MissingAccess
from gd.password import Password, PasswordData
from gd.schema import LevelReferenceSchema, LevelSchema
from gd.schema_constants import NONE, SOME
from gd.songs import SongReference
from gd.users import User, UserReference, UserReferenceData
from gd.versions import CURRENT_GAME_VERSION, GameVersion, RobTopVersionData

if TYPE_CHECKING:
    from typing_extensions import Self

    from gd.api.recording import Recording
    from gd.client import Client
    from gd.comments import LevelComment
    from gd.models import LevelModel, TimelyInfoModel
    from gd.schema import (
        LevelBuilder,
        LevelReader,
        LevelReferenceBuilder,
        LevelReferenceReader,
    )
    from gd.songs import SongReferenceData

__all__ = ("Level", "LevelReference")

L = TypeVar("L", bound="Level")

EXPECTED_QUERY = "expected either `id` or `name` query"
CAN_NOT_FIND_LEVEL = "can not find an official level by given query"


OFFICIAL_LEVEL_DESCRIPTION = "Official level: {}"


class LevelReferenceData(EntityData):
    name: str


@define()
class LevelReference(Binary, Entity):
    name: str = field(eq=False)

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

    def __str__(self) -> str:
        return self.name or UNKNOWN

    @classmethod
    def from_data(cls, data: LevelReferenceData) -> Self:  # type: ignore[override]
        return CONVERTER.structure(data, cls)

    def into_data(self) -> LevelReferenceData:
        return CONVERTER.unstructure(self)  # type: ignore[no-any-return]

    @classmethod
    def default(cls, id: int = DEFAULT_ID, name: str = EMPTY) -> Self:
        return cls(id=id, name=name)

    @classmethod
    def from_binary(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(LevelReferenceSchema.read(binary))

    @classmethod
    def from_binary_packed(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(LevelReferenceSchema.read_packed(binary))

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        with LevelReferenceSchema.from_bytes(data) as reader:
            return cls.from_reader(reader)

    @classmethod
    def from_bytes_packed(cls, data: bytes) -> Self:
        return cls.from_reader(LevelReferenceSchema.from_bytes_packed(data))

    def to_binary(self, binary: BufferedWriter) -> None:
        self.to_builder().write(binary)

    def to_binary_packed(self, binary: BufferedWriter) -> None:
        self.to_builder().write_packed(binary)

    def to_bytes(self) -> bytes:
        return self.to_builder().to_bytes()

    def to_bytes_packed(self) -> bytes:
        return self.to_builder().to_bytes_packed()

    @classmethod
    def from_reader(cls, reader: LevelReferenceReader) -> Self:
        return cls(id=reader.id, name=reader.name)

    def to_builder(self) -> LevelReferenceBuilder:
        builder = LevelReferenceSchema.new_message()

        builder.id = self.id
        builder.name = self.name

        return builder

    async def delete(self) -> None:
        await self.client.delete_level(self)

    async def update_description(self, content: str) -> None:
        await self.client.update_level_description(self, content)

    async def rate(self, stars: int) -> None:
        await self.client.rate_level(self, stars)

    async def rate_demon(self, rating: DemonDifficulty) -> None:
        await self.client.rate_demon(self, rating=rating)

    async def suggest_demon(self, rating: DemonDifficulty) -> None:
        await self.client.suggest_demon(self, rating=rating)

    async def suggest(self, stars: int, feature: bool) -> None:
        await self.client.suggest_level(self, stars=stars, feature=feature)

    async def comment(
        self, content: Optional[str] = None, record: int = DEFAULT_RECORD
    ) -> Optional[LevelComment]:
        return await self.client.post_level_comment(self, content, record)

    async def like(self) -> None:
        await self.client.like_level(self)

    async def dislike(self) -> None:
        await self.client.dislike_level(self)

    @wrap_async_iter
    def get_leaderboard(
        self,
        strategy: LevelLeaderboardStrategy = LevelLeaderboardStrategy.DEFAULT,
    ) -> AsyncIterator[User]:
        return self.client.get_level_leaderboard(self, strategy=strategy).unwrap()

    @wrap_async_iter
    def get_comments_on_page(
        self,
        strategy: CommentStrategy = CommentStrategy.DEFAULT,
        page: int = DEFAULT_PAGE,
        count: int = COMMENT_PAGE_SIZE,
    ) -> AsyncIterator[LevelComment]:
        return self.client.get_level_comments_on_page(
            self, page=page, count=count, strategy=strategy
        ).unwrap()

    @wrap_async_iter
    def get_comments(
        self,
        strategy: CommentStrategy = CommentStrategy.DEFAULT,
        count: int = COMMENT_PAGE_SIZE,
        pages: Iterable[int] = DEFAULT_PAGES,
    ) -> AsyncIterator[LevelComment]:
        return self.client.get_level_comments(
            level=self,
            strategy=strategy,
            count=count,
            pages=pages,
        ).unwrap()


class LevelData(LevelReferenceData):
    creator: UserReferenceData
    song: SongReferenceData
    description: str
    unprocessed_data: str
    version: int
    downloads: int
    game_version: RobTopVersionData
    rating: int
    length: int
    difficulty: int
    stars: int
    requested_stars: int
    score: int
    rate_type: int
    password: PasswordData
    original_id: int
    two_player: bool
    coins: int
    verified_coins: bool
    low_detail: bool
    object_count: int
    created_at: str
    updated_at: str
    editor_time: str
    copies_time: str
    timely_type: int
    timely_id: int


NO_DESCRIPTION = "no description"
NO_DATA = "no data"


@register_unstructure_hook_omit_client
@define()
class Level(LevelReference):
    creator: UserReference = field(eq=False)
    song: SongReference = field(eq=False)
    description: str = field(default=EMPTY, eq=False)
    unprocessed_data_unchecked: Optional[str] = field(default=None, eq=False, repr=False)
    version: int = field(default=DEFAULT_VERSION, eq=False)
    downloads: int = field(default=DEFAULT_DOWNLOADS, eq=False)
    game_version: GameVersion = field(default=CURRENT_GAME_VERSION, eq=False)
    rating: int = field(default=DEFAULT_RATING, eq=False)
    length: LevelLength = field(default=LevelLength.DEFAULT, eq=False)
    difficulty: Difficulty = field(default=Difficulty.DEFAULT, eq=False)
    reward: EitherReward = field(factory=EitherReward, eq=False)
    requested_reward: EitherReward = field(factory=EitherReward, eq=False)
    score: int = field(default=DEFAULT_SCORE, eq=False)
    rate_type: RateType = field(default=RateType.DEFAULT, eq=False)
    password: Optional[Password] = field(default=None, eq=False)
    original_id: int = field(default=DEFAULT_ID, eq=False)
    two_player: bool = field(default=DEFAULT_TWO_PLAYER, eq=False)
    capacity: Optional[Capacity] = field(default=None, eq=False)
    coins: int = field(default=DEFAULT_COINS, eq=False)
    verified_coins: bool = field(default=DEFAULT_VERIFIED_COINS, eq=False)
    low_detail: bool = field(default=DEFAULT_LOW_DETAIL, eq=False)
    object_count: int = field(default=DEFAULT_OBJECT_COUNT, eq=False)
    created_at: Optional[DateTime] = field(default=None, eq=False)
    updated_at: Optional[DateTime] = field(default=None, eq=False)
    editor_time: Duration = field(factory=duration, eq=False)
    copies_time: Duration = field(factory=duration, eq=False)
    timely_type: TimelyType = field(default=TimelyType.DEFAULT, eq=False)
    timely_id: int = field(default=DEFAULT_ID, eq=False)
    time_steps: int = field(default=DEFAULT_TIME_STEPS, eq=False)

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

    def has_data(self) -> bool:
        return self.unprocessed_data_unchecked is not None

    @property
    def unprocessed_data(self) -> str:
        return self.unprocessed_data_unchecked or EMPTY

    @unprocessed_data.setter
    def unprocessed_data(self, unprocessed_data: str) -> None:
        self.unprocessed_data_unchecked = unprocessed_data

    @unprocessed_data.deleter
    def unprocessed_data(self) -> None:
        self.unprocessed_data_unchecked = None

    @property
    def processed_data(self) -> str:
        return unzip_level_string(self.unprocessed_data)

    @processed_data.setter
    def processed_data(self, processed_data: str) -> None:
        self.unprocessed_data = zip_level_string(processed_data)

    @property
    def data(self) -> bytes:
        return self.open_editor().to_bytes()

    @data.setter
    def data(self, data: bytes) -> None:
        self.processed_data = Editor.from_bytes(data).to_robtop()

    @classmethod
    def from_data(cls, data: LevelData) -> Self:  # type: ignore
        return CONVERTER.structure(data, cls)

    def into_data(self) -> LevelData:
        return CONVERTER.unstructure(self)  # type: ignore

    @classmethod
    def from_model(cls, model: LevelModel, creator: UserReference, song: SongReference) -> Self:
        rate_type = RateType.NOT_RATED

        reward = model.reward.count

        if reward > 0:
            rate_type = RateType.RATED

        score = model.score

        if score > 0:
            rate_type = RateType.FEATURED

        if model.is_epic():
            rate_type = RateType.EPIC

        if model.is_legendary():
            rate_type = RateType.LEGENDARY

        if model.is_mythic():
            rate_type = RateType.MYTHIC

        return cls(
            id=model.id,
            name=model.name,
            creator=creator,
            song=song,
            description=model.description,
            unprocessed_data_unchecked=model.unprocessed_data or None,
            version=model.version,
            difficulty=model.difficulty,
            downloads=model.downloads,
            game_version=model.game_version,
            rating=model.rating,
            length=model.length,
            reward=model.reward,
            score=model.score,
            rate_type=rate_type,
            password=model.password,
            created_at=model.created_at,
            updated_at=model.updated_at,
            original_id=model.original_id,
            two_player=model.is_two_player(),
            coins=model.coins,
            verified_coins=model.has_verified_coins(),
            requested_reward=model.requested_reward,
            low_detail=model.has_low_detail(),
            timely_id=model.timely_id,
            timely_type=model.timely_type,
            object_count=model.object_count,
            editor_time=model.editor_time,
            copies_time=model.copies_time,
            time_steps=model.time_steps,
        )

    def update_with_timely_model(self, model: TimelyInfoModel) -> Self:
        self.timely_id = model.id
        self.timely_type = model.type

        return self

    @classmethod
    def default(
        cls,
        id: int = DEFAULT_ID,
        name: str = EMPTY,
        creator_id: int = DEFAULT_ID,
        creator_account_id: int = DEFAULT_ID,
        song_id: int = DEFAULT_ID,
    ) -> Self:
        return cls(
            id=id,
            name=name,
            creator=UserReference.default(creator_id, creator_account_id),
            song=SongReference.default(song_id),
        )

    def is_timely(self, timely_type: Optional[TimelyType] = None) -> bool:
        if timely_type is None:
            return self.timely_type.is_timely()

        return self.timely_type is timely_type

    def is_daily(self) -> bool:
        return self.is_timely(TimelyType.DAILY)

    def is_weekly(self) -> bool:
        return self.is_timely(TimelyType.WEEKLY)

    def is_event(self) -> bool:
        return self.is_timely(TimelyType.EVENT)

    def is_rated(self) -> bool:
        return self.rate_type.is_rated()

    def is_featured(self) -> bool:
        return self.rate_type.is_featured()

    def is_epic(self) -> bool:
        return self.rate_type.is_epic()

    def is_legendary(self) -> bool:
        return self.rate_type.is_legendary()

    def is_mythic(self) -> bool:
        return self.rate_type.is_mythic()

    def is_original(self) -> bool:
        return not self.original_id

    def is_two_player(self) -> bool:
        return self.two_player

    def is_demon(self) -> bool:
        return self.difficulty.is_demon()

    def has_low_detail(self) -> bool:
        return self.low_detail

    def has_verified_coins(self) -> bool:
        return self.verified_coins

    def open_editor(self) -> Editor:
        return Editor.from_robtop(self.processed_data)

    async def report(self) -> None:
        await self.client.report_level(self)

    async def upload(
        self,
        name: Optional[str] = None,
        id: Optional[int] = None,
        version: Optional[int] = None,
        length: Optional[LevelLength] = None,
        official_song_id: Optional[int] = None,
        song_id: Optional[int] = None,
        description: Optional[str] = None,
        original_id: Optional[int] = None,
        two_player: Optional[bool] = None,
        privacy: LevelPrivacy = LevelPrivacy.DEFAULT,
        object_count: Optional[int] = None,
        coins: Optional[int] = None,
        reward: Optional[int] = None,
        low_detail: Optional[bool] = None,
        capacity: Optional[Capacity] = None,
        password: Optional[Password] = None,
        recording: Optional[Recording] = None,
        editor_time: Optional[Duration] = None,
        copies_time: Optional[Duration] = None,
        time_steps: Optional[int] = None,
        data: Optional[str] = None,
    ) -> None:
        song = self.song
        default_song_id = song.id

        default_official_song_id, default_song_id = (
            (0, default_song_id) if song.is_custom() else (default_song_id, 0)
        )

        keywords = dict(
            name=switch_none(name, self.name),
            id=switch_none(id, self.id),
            version=switch_none(version, self.version),
            length=switch_none(length, self.length),
            official_song_id=switch_none(official_song_id, default_official_song_id),
            song_id=switch_none(song_id, default_song_id),
            description=switch_none(description, self.description),
            original_id=switch_none(original_id, self.original_id),
            two_player=switch_none(two_player, self.is_two_player()),
            privacy=privacy,
            object_count=switch_none(object_count, self.object_count),
            coins=switch_none(coins, self.coins),
            reward=switch_none(reward, self.reward.count),
            low_detail=switch_none(low_detail, self.has_low_detail()),
            capacity=switch_none(capacity, self.capacity),
            password=switch_none(password, self.password),
            recording=recording,
            editor_time=switch_none(editor_time, self.editor_time),
            copies_time=switch_none(copies_time, self.copies_time),
            time_steps=switch_none(time_steps, self.time_steps),
            data=switch_none(data, self.unprocessed_data),
        )

        uploaded = await self.client.upload_level(**keywords)  # type: ignore

        self.update_from(uploaded)

    async def update(
        self,
        *,
        get_data: bool = DEFAULT_GET_DATA,
        use_client: bool = DEFAULT_USE_CLIENT,
    ) -> Optional[Level]:
        try:
            if self.is_timely():
                level = await self.client.get_timely(self.timely_type)

            else:
                level = await self.client.get_level(self.id, get_data=get_data)

        except MissingAccess:
            return None

        else:
            self.update_from(level)

            return self

    def attach_client_unchecked(self, client: Optional[Client]) -> Self:
        self.creator.attach_client_unchecked(client)
        self.song.attach_client_unchecked(client)

        return super().attach_client_unchecked(client)

    def attach_client(self, client: Client) -> Self:
        self.creator.attach_client(client)
        self.song.attach_client(client)

        return super().attach_client(client)

    def detach_client(self) -> Self:
        self.creator.detach_client()
        self.song.detach_client()

        return super().detach_client()

    @classmethod
    def from_reader(cls, reader: LevelReader) -> Self:  # type: ignore[override]
        password_option = reader.password

        if password_option.which() == NONE:
            password = None

        else:
            password = Password.from_reader(password_option.some)

        capacity_option = reader.capacity

        if capacity_option.which() == NONE:
            capacity = None

        else:
            capacity = Capacity.from_value(capacity_option.some)

        created_at_option = reader.createdAt

        if created_at_option.which() == NONE:
            created_at = None

        else:
            created_at = utc_from_timestamp_milliseconds(created_at_option.some)

        updated_at_option = reader.updatedAt

        if updated_at_option.which() == NONE:
            updated_at = None

        else:
            updated_at = utc_from_timestamp_milliseconds(updated_at_option.some)

        level = cls(
            id=reader.id,
            name=reader.name,
            creator=UserReference.from_reader(reader.creator),
            song=SongReference.from_reader(reader.song),
            description=reader.description,
            version=reader.version,
            downloads=reader.downloads,
            game_version=GameVersion.from_value(reader.gameVersion),
            rating=reader.rating,
            length=LevelLength(reader.length),
            difficulty=Difficulty(reader.difficulty),
            reward=EitherReward.from_reader(reader.reward),
            requested_reward=EitherReward.from_reader(reader.requestedReward),
            score=reader.score,
            rate_type=RateType(reader.rateType),
            password=password,
            original_id=reader.originalId,
            two_player=reader.twoPlayer,
            capacity=capacity,
            coins=reader.coins,
            verified_coins=reader.verifiedCoins,
            low_detail=reader.lowDetail,
            object_count=reader.objectCount,
            created_at=created_at,
            updated_at=updated_at,
            editor_time=duration(milliseconds=reader.editorTime),
            copies_time=duration(milliseconds=reader.copiesTime),
            timely_type=TimelyType(reader.timelyType),
            timely_id=reader.timelyId,
            time_steps=reader.timeSteps,
        )

        data_option = reader.data

        if data_option.which() == SOME:
            level.data = decompress(data_option.some)

        return level

    def to_builder(self) -> LevelBuilder:  # type: ignore[override]
        builder = LevelSchema.new_message()

        builder.id = self.id
        builder.name = self.name
        builder.creator = self.creator.to_builder()
        builder.song = self.song.to_builder()
        builder.description = self.description

        if self.has_data():
            builder.data.some = compress(self.data)

        else:
            builder.data.none = None

        builder.version = self.version
        builder.downloads = self.downloads
        builder.gameVersion = self.game_version.to_value()
        builder.rating = self.rating
        builder.length = self.length.value
        builder.difficulty = self.difficulty.value
        builder.reward = self.reward.to_builder()
        builder.requestedReward = self.requested_reward.to_builder()
        builder.score = self.score
        builder.rateType = self.rate_type.value

        password = self.password

        if password is None:
            builder.password.none = None

        else:
            builder.password.some = password.to_builder()

        builder.originalId = self.original_id
        builder.twoPlayer = self.is_two_player()

        capacity = self.capacity

        if capacity is None:
            builder.capacity.none = None

        else:
            builder.capacity.some = capacity.to_value()

        builder.coins = self.coins
        builder.verifiedCoins = self.has_verified_coins()
        builder.lowDetail = self.has_low_detail()
        builder.objectCount = self.object_count

        created_at = self.created_at

        if created_at is None:
            builder.createdAt.none = None

        else:
            builder.createdAt.some = timestamp_milliseconds(created_at)

        updated_at = self.updated_at

        if updated_at is None:
            builder.updatedAt.none = None

        else:
            builder.updatedAt.some = timestamp_milliseconds(updated_at)

        builder.editorTime = duration_milliseconds(self.editor_time)
        builder.copiesTime = duration_milliseconds(self.copies_time)
        builder.timelyType = self.timely_type.value
        builder.timelyId = self.timely_id
        builder.timeSteps = self.time_steps

        return builder

    def as_reference(self) -> LevelReference:
        return LevelReference(id=self.id, name=self.name)


T = TypeVar("T")


def switch_none(item: Optional[T], default: T) -> T:
    return default if item is None else item
