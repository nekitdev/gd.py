from __future__ import annotations

from typing import TYPE_CHECKING, AsyncIterator, Iterable, Optional, TypeVar

from attrs import define, field
from iters.async_iters import wrap_async_iter
from pendulum import DateTime, Duration, duration

from gd.api.editor import Editor
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
    DEFAULT_STARS,
    DEFAULT_TWO_PLAYER,
    DEFAULT_USE_CLIENT,
    DEFAULT_VERIFIED_COINS,
    DEFAULT_VERSION,
    EMPTY,
    UNKNOWN,
)
from gd.converter import CONVERTER, register_unstructure_hook_omit_client
from gd.date_time import utc_now
from gd.encoding import decompress, unzip_level_string, zip_level_string
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
from gd.users import User, UserReference, UserReferenceData
from gd.versions import CURRENT_GAME_VERSION, GameVersion, RobTopVersionData

if TYPE_CHECKING:
    from typing_extensions import Self

    from gd.api.recording import Recording
    from gd.client import Client
    from gd.comments import LevelComment
    from gd.models import LevelModel, TimelyInfoModel
    from gd.songs import SongReference, SongReferenceData

__all__ = ("Level",)

L = TypeVar("L", bound="Level")

EXPECTED_QUERY = "expected either `id` or `name` query"
CAN_NOT_FIND_LEVEL = "can not find an official level by given query"


OFFICIAL_LEVEL_DESCRIPTION = "Official level: {}"


class LevelReferenceData(EntityData):
    name: str


@define()
class LevelReference(Entity):
    name: str = field(eq=False)


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


@register_unstructure_hook_omit_client
@define()
class Level(LevelReference):
    creator: UserReference = field(eq=False)
    song: SongReference = field(eq=False)
    description: str = field(default=EMPTY, eq=False)
    unprocessed_data: str = field(default=EMPTY, eq=False, repr=False)
    version: int = field(default=DEFAULT_VERSION, eq=False)
    downloads: int = field(default=DEFAULT_DOWNLOADS, eq=False)
    game_version: GameVersion = field(default=CURRENT_GAME_VERSION, eq=False)
    rating: int = field(default=DEFAULT_RATING, eq=False)
    length: LevelLength = field(default=LevelLength.DEFAULT, eq=False)
    difficulty: Difficulty = field(default=Difficulty.DEFAULT, eq=False)
    stars: int = field(default=DEFAULT_STARS, eq=False)
    requested_stars: int = field(default=DEFAULT_STARS, eq=False)
    score: int = field(default=DEFAULT_SCORE, eq=False)
    rate_type: RateType = field(default=RateType.DEFAULT, eq=False)
    password: Password = field(factory=Password, eq=False)
    original_id: int = field(default=DEFAULT_ID, eq=False)
    two_player: bool = field(default=DEFAULT_TWO_PLAYER, eq=False)
    capacity: Capacity = field(factory=Capacity, eq=False)
    coins: int = field(default=DEFAULT_COINS, eq=False)
    verified_coins: bool = field(default=DEFAULT_VERIFIED_COINS, eq=False)
    low_detail: bool = field(default=DEFAULT_LOW_DETAIL, eq=False)
    object_count: int = field(default=DEFAULT_OBJECT_COUNT, eq=False)
    created_at: DateTime = field(factory=utc_now, eq=False)
    updated_at: DateTime = field(factory=utc_now, eq=False)
    editor_time: Duration = field(factory=duration, eq=False)
    copies_time: Duration = field(factory=duration, eq=False)
    timely_type: TimelyType = field(default=TimelyType.DEFAULT, eq=False)
    timely_id: int = field(default=DEFAULT_ID, eq=False)

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

    def __str__(self) -> str:
        return self.name or UNKNOWN

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

        stars = model.stars

        if stars > 0:
            rate_type = RateType.RATED

        score = model.score

        if score > 0:
            rate_type = RateType.FEATURED

        if model.is_epic():
            rate_type = RateType.EPIC

        if model.is_godlike():
            rate_type = RateType.GODLIKE

        return cls(
            id=model.id,
            name=model.name,
            creator=creator,
            song=song,
            description=model.description,
            unprocessed_data=model.unprocessed_data,
            version=model.version,
            difficulty=model.difficulty,
            downloads=model.downloads,
            game_version=model.game_version,
            rating=model.rating,
            length=model.length,
            stars=model.stars,
            score=model.score,
            rate_type=rate_type,
            password=model.password,
            created_at=model.created_at,
            updated_at=model.updated_at,
            original_id=model.original_id,
            two_player=model.is_two_player(),
            coins=model.coins,
            verified_coins=model.has_verified_coins(),
            requested_stars=model.requested_stars,
            low_detail=model.has_low_detail(),
            timely_id=model.timely_id,
            timely_type=model.timely_type,
            object_count=model.object_count,
            editor_time=model.editor_time,
            copies_time=model.copies_time,
        )

    def update_with_timely_model(self, model: TimelyInfoModel) -> Self:
        self.timely_id = model.id
        self.timely_type = model.type

        return self

    @classmethod
    def default(
        cls,
        id: int = DEFAULT_ID,
        creator_id: int = DEFAULT_ID,
        creator_account_id: int = DEFAULT_ID,
        song_id: int = DEFAULT_ID,
    ) -> Self:
        return cls(
            id=id,
            name=EMPTY,
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

    def is_godlike(self) -> bool:
        return self.rate_type.is_godlike()

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
        stars: Optional[int] = None,
        low_detail: Optional[bool] = None,
        capacity: Optional[Capacity] = None,
        password: Optional[Password] = None,
        recording: Optional[Recording] = None,
        editor_time: Optional[Duration] = None,
        copies_time: Optional[Duration] = None,
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
            stars=switch_none(stars, self.stars),
            low_detail=switch_none(low_detail, self.has_low_detail()),
            capacity=switch_none(capacity, self.capacity),
            password=switch_none(password, self.password),
            recording=recording,
            editor_time=switch_none(editor_time, self.editor_time),
            copies_time=switch_none(copies_time, self.copies_time),
            data=switch_none(data, self.unprocessed_data),
        )

        uploaded = await self.client.upload_level(**keywords)  # type: ignore

        self.update_from(uploaded)

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

    async def update(
        self, *, get_data: bool = DEFAULT_GET_DATA, use_client: bool = DEFAULT_USE_CLIENT
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


T = TypeVar("T")


def switch_none(item: Optional[T], default: T) -> T:
    return default if item is None else item
