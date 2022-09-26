from __future__ import annotations

from datetime import datetime, timedelta

# from pathlib import Path
from typing import TYPE_CHECKING, Any, AsyncIterator, BinaryIO, Iterable, Optional, Type, TypeVar

from attrs import define, field
from iters.async_iters import wrap_async_iter
from iters.iters import iter

# from gd.api.editor import Editor
from gd.binary import VERSION
from gd.binary_utils import Reader, Writer
from gd.constants import (
    COMMENT_PAGE_SIZE,
    DEFAULT_AS_MOD,
    DEFAULT_COINS,
    DEFAULT_ENCODING,
    DEFAULT_ERRORS,
    DEFAULT_DEMON,
    DEFAULT_DOWNLOADS,
    DEFAULT_EPIC,
    DEFAULT_ID,
    DEFAULT_LOW_DETAIL,
    DEFAULT_OBJECT_COUNT,
    DEFAULT_PAGE,
    DEFAULT_RATING,
    DEFAULT_RECORD,
    DEFAULT_SCORE,
    DEFAULT_STARS,
    DEFAULT_TWO_PLAYER,
    DEFAULT_VERIFIED_COINS,
    DEFAULT_VERSION,
    EMPTY,
    EMPTY_BYTES,
    UNKNOWN,
)
from gd.entity import Entity
from gd.enums import (
    ByteOrder,
    CommentStrategy,
    DemonDifficulty,
    Difficulty,
    LevelLeaderboardStrategy,
    LevelLength,
    Score,
    TimelyType,
)
from gd.models import LevelModel, TimelyInfoModel
from gd.official_levels import OFFICIAL_LEVELS, OfficialLevel
from gd.password import Password
from gd.song import Song
from gd.typing import Predicate
from gd.user import User
from gd.versions import CURRENT_GAME_VERSION, GameVersion

if TYPE_CHECKING:
    from gd.client import Client
    from gd.comments import LevelComment

__all__ = ("Level",)

L = TypeVar("L", bound="Level")

TWO_PLAYER_BIT = 0b00000001
VERIFIED_COINS_BIT = 0b00000010
EPIC_BIT = 0b00000100
LOW_DETAIL_BIT = 0b00001000
DEMON_BIT = 0b00010000

EXPECTED_QUERY = "expected either `id` or `name` query"
CAN_NOT_FIND_LEVEL = "can not find an official level by given query"


def by_name(name: str) -> Predicate[OfficialLevel]:
    def predicate(level: OfficialLevel) -> bool:
        return level.name == name

    return predicate


def by_id(id: int) -> Predicate[OfficialLevel]:
    def predicate(level: OfficialLevel) -> bool:
        return level.id == id

    return predicate


OFFICIAL_LEVEL_DESCRIPTION = "Official Level: {}"


@define(hash=True)
class Level(Entity):
    name: str = field(eq=False)
    creator: User = field(eq=False)
    song: Song = field(eq=False)
    description: str = field(default=EMPTY, eq=False)
    data: bytes = field(default=EMPTY_BYTES, eq=False)
    version: int = field(default=DEFAULT_VERSION, eq=False)
    downloads: int = field(default=DEFAULT_DOWNLOADS, eq=False)
    game_version: GameVersion = field(default=CURRENT_GAME_VERSION, eq=False)
    rating: int = field(default=DEFAULT_RATING, eq=False)
    length: LevelLength = field(default=LevelLength.DEFAULT, eq=False)
    difficulty: Difficulty = field(default=Difficulty.DEFAULT, eq=False)
    demon: bool = field(default=DEFAULT_DEMON, eq=False)
    stars: int = field(default=DEFAULT_STARS, eq=False)
    requested_stars: int = field(default=DEFAULT_STARS, eq=False)
    score: int = field(default=DEFAULT_SCORE, eq=False)
    password_data: Password = field(factory=Password, eq=False)
    original_id: int = field(default=DEFAULT_ID, eq=False)
    two_player: bool = field(default=DEFAULT_TWO_PLAYER, eq=False)
    coins: int = field(default=DEFAULT_COINS, eq=False)
    verified_coins: bool = field(default=DEFAULT_VERIFIED_COINS, eq=False)
    low_detail: bool = field(default=DEFAULT_LOW_DETAIL, eq=False)
    epic: bool = field(default=DEFAULT_EPIC, eq=False)
    object_count: int = field(default=DEFAULT_OBJECT_COUNT, eq=False)
    uploaded_at: datetime = field(factory=datetime.utcnow, eq=False)
    updated_at: datetime = field(factory=datetime.utcnow, eq=False)
    editor_time: timedelta = field(factory=timedelta, eq=False)
    copies_time: timedelta = field(factory=timedelta, eq=False)
    timely_type: TimelyType = field(default=TimelyType.DEFAULT, eq=False)
    timely_id: int = field(default=DEFAULT_ID, eq=False)

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

    def __str__(self) -> str:
        return self.name

    def to_binary(
        self,
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
    ) -> None:
        writer = Writer(binary)

        super().to_binary(binary, order, version)

        data = self.name.encode(encoding, errors)

        writer.write_u8(len(data), order)

        writer.write(data)

        self.creator.to_binary(binary, order, version, encoding, errors)
        self.song.to_binary(binary, order, version, encoding, errors)

        writer.write_f64(self.uploaded_at.timestamp(), order)
        writer.write_f64(self.updated_at.timestamp(), order)

        data = self.description.encode(encoding, errors)

        writer.write_u16(len(data), order)

        writer.write(data)

        data = self.data

        writer.write_u32(len(data), order)

        writer.write(data)

        writer.write_u8(self.version, order)

        writer.write_u32(self.downloads, order)

        self.game_version.to_binary(binary, order, version)

        writer.write_i32(self.rating, order)

        writer.write_u8(self.length.value, order)

        writer.write_u8(self.difficulty.value, order)

        value = 0

        if self.is_two_player():
            value |= TWO_PLAYER_BIT

        if self.has_verified_coins():
            value |= VERIFIED_COINS_BIT

        if self.is_epic():
            value |= EPIC_BIT

        if self.has_low_detail():
            value |= LOW_DETAIL_BIT

        if self.is_demon():
            value |= DEMON_BIT

        writer.write_u8(value, order)

        writer.write_u8(self.stars, order)

        writer.write_u8(self.requested_stars, order)

        writer.write_i32(self.score, order)

        self.password_data.to_binary(binary, order, version)

        writer.write_u32(self.original_id, order)

        writer.write_u8(self.coins, order)

        writer.write_u32(self.object_count, order)

        writer.write_f32(self.editor_time.total_seconds(), order)
        writer.write_f32(self.copies_time.total_seconds(), order)

        writer.write_u8(self.timely_type.value, order)
        writer.write_u32(self.timely_id, order)

    @classmethod
    def from_binary(
        cls: Type[L],
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
    ) -> L:
        two_player_bit = TWO_PLAYER_BIT
        verified_coins_bit = VERIFIED_COINS_BIT
        epic_bit = EPIC_BIT
        low_detail_bit = LOW_DETAIL_BIT
        demon_bit = DEMON_BIT

        reader = Reader(binary)

        id = reader.read_u32(order)

        name_length = reader.read_u8(order)

        name = reader.read(name_length).decode(encoding, errors)

        creator = User.from_binary(binary, order, version, encoding, errors)
        song = Song.from_binary(binary, order, version, encoding, errors)

        uploaded_timestamp = reader.read_f64(order)
        updated_timestamp = reader.read_f64(order)

        uploaded_at = datetime.fromtimestamp(uploaded_timestamp)
        updated_at = datetime.fromtimestamp(updated_timestamp)

        description_length = reader.read_u16(order)

        description = reader.read(description_length).decode(encoding, errors)

        data_length = reader.read_u32(order)

        data = reader.read(data_length)

        version = reader.read_u8(order)

        downloads = reader.read_u32(order)

        game_version = GameVersion.from_binary(binary, order, version)

        rating = reader.read_i32(order)

        length_value = reader.read_u8(order)

        length = LevelLength(length_value)

        difficulty_value = reader.read_u8(order)

        difficulty = Difficulty(difficulty_value)

        value = reader.read_u8(order)

        two_player = value & two_player_bit == two_player_bit
        verified_coins = value & verified_coins_bit == verified_coins_bit
        epic = value & epic_bit == epic_bit
        low_detail = value & low_detail_bit == low_detail_bit
        demon = value & demon_bit == demon_bit

        stars = reader.read_u8(order)

        requested_stars = reader.read_u8(order)

        score = reader.read_i32(order)

        password_data = Password.from_binary(binary, order, version)

        original_id = reader.read_u32(order)

        coins = reader.read_u8(order)

        object_count = reader.read_u32(order)

        editor_seconds = reader.read_f32(order)
        copies_seconds = reader.read_f32(order)

        editor_time = timedelta(seconds=editor_seconds)
        copies_time = timedelta(seconds=copies_seconds)

        timely_type_value = reader.read_u8(order)

        timely_type = TimelyType(timely_type_value)

        timely_id = reader.read_u32(order)

        return cls(
            id=id,
            name=name,
            creator=creator,
            song=song,
            uploaded_at=uploaded_at,
            updated_at=updated_at,
            description=description,
            data=data,
            version=version,
            downloads=downloads,
            game_version=game_version,
            rating=rating,
            length=length,
            difficulty=difficulty,
            demon=demon,
            stars=stars,
            requested_stars=requested_stars,
            score=score,
            password_data=password_data,
            original_id=original_id,
            two_player=two_player,
            coins=coins,
            verified_coins=verified_coins,
            low_detail=low_detail,
            epic=epic,
            object_count=object_count,
            editor_time=editor_time,
            copies_time=copies_time,
            timely_type=timely_type,
            timely_id=timely_id,
        )

    @classmethod
    def from_model(cls: Type[L], model: LevelModel, creator: User, song: Song) -> L:
        return cls(
            id=model.id,
            name=model.name,
            creator=creator,
            song=song,
            description=model.description,
            # data?
            version=model.version,
            difficulty=model.difficulty,
            downloads=model.downloads,
            game_version=model.game_version,
            rating=model.rating,
            length=model.length,
            demon=model.demon,
            stars=model.stars,
            score=model.score,
            password_data=model.password_data,
            uploaded_at=model.uploaded_at,
            updated_at=model.updated_at,
            original_id=model.original_id,
            two_player=model.two_player,
            coins=model.coins,
            verified_coins=model.verified_coins,
            requested_stars=model.requested_stars,
            low_detail=model.low_detail,
            timely_id=model.timely_id,
            timely_type=model.timely_type,
            epic=model.epic,
            object_count=model.object_count,
            editor_time=model.editor_time,
            copies_time=model.copies_time,
        )

    def update_with_timely_model(self: L, model: TimelyInfoModel) -> L:
        self.timely_id = model.id
        self.timely_type = model.type

        return self

    @classmethod
    def default(cls: Type[L]) -> L:
        return cls(id=DEFAULT_ID, name=UNKNOWN, creator=User.default(), song=Song.default())

    @classmethod
    def official(
        cls: Type[L],
        id: Optional[int] = None,
        name: Optional[str] = None,
        get_data: bool = True,
        server_style: bool = False,
    ) -> L:
        official_levels = OFFICIAL_LEVELS

        if id is None:
            if name is None:
                raise ValueError(EXPECTED_QUERY)

            else:
                official_level = iter(official_levels).find_or_none(by_name(name))

        else:
            official_level = iter(official_levels).find_or_none(by_id(id))

        if official_level is None:
            raise LookupError(CAN_NOT_FIND_LEVEL)

        data = EMPTY_BYTES  # TODO

        name = official_level.name

        song_id = official_level.song_id

        if server_style:
            song_id -= 1

        return cls(
            id=official_level.id,
            name=name,
            creator=User.robtop(),
            song=Song.official(id=song_id, server_style=server_style),
            description=OFFICIAL_LEVEL_DESCRIPTION.format(name),
            data=data,
            coins=official_level.coins,
            stars=official_level.stars,
            difficulty=official_level.difficulty,
            demon=official_level.demon,
            game_version=official_level.game_version,
            length=official_level.length,
        )

    @property
    def score_type(self) -> Score:
        return Score(self.score)

    @property
    def password(self) -> Optional[int]:
        return self.password_data.password

    def is_copyable(self) -> bool:
        return self.password_data.is_copyable()

    def is_timely(self, timely_type: Optional[TimelyType] = None) -> bool:
        if timely_type is None:
            return not self.timely_type.is_not_timely()

        return self.timely_type is timely_type

    def is_daily(self) -> bool:
        return self.is_timely(TimelyType.DAILY)

    def is_weekly(self) -> bool:
        return self.is_timely(TimelyType.WEEKLY)

    def is_rated(self) -> bool:
        return self.stars > 0

    def is_unfeatured(self) -> bool:
        return self.score_type.is_unfeatured()

    def is_epic_only(self) -> bool:
        return self.score_type.is_epic_only()

    def is_featured(self) -> bool:
        return self.score_type.is_featured()

    def is_epic(self) -> bool:
        return self.epic

    def is_original(self) -> bool:
        return not self.original_id

    def is_two_player(self) -> bool:
        return self.two_player

    def is_demon(self) -> bool:
        return self.demon

    def has_low_detail(self) -> bool:
        return self.low_detail

    def has_verified_coins(self) -> bool:
        return self.verified_coins

    def open_editor(self) -> Editor:
        ...

    async def report(self) -> None:
        await self.client.report_level(self)

    async def upload(self, **kwargs: Any) -> None:
        song = self.song
        song_id = song.id

        official_song_id, song_id = (0, song_id) if song.is_custom() else (song_id, 0)

        args = dict(
            name=self.name,
            id=self.id,
            version=self.version,
            length=abs(self.length.value),
            official_song_id=official_song_id,
            description=self.description,
            song_id=song_id,
            two_player=self.is_two_player(),
            original=self.original_id,
            object_count=self.object_count,
            coins=self.coins,
            stars=self.stars,
            unlisted=False,
            friends_only=False,
            low_detail=self.has_low_detail(),
            password=self.password,
            copyable=self.is_copyable(),
            editor_seconds=self.editor_seconds,
            copies_seconds=self.copies_seconds,
            data=self.data,
        )

        args.update(kwargs)

        uploaded = await self.client.upload_level(**args)

        self.options.update(uploaded.options)

    async def delete(self) -> None:
        await self.client.delete_level(self)

    async def update_description(self, content: str) -> None:
        await self.client.update_level_description(self, content)

    async def rate(self, stars: int) -> None:
        await self.client.rate_level(self, stars)

    async def rate_demon(
        self, rating: DemonDifficulty = DemonDifficulty.DEFAULT, as_mod: bool = DEFAULT_AS_MOD
    ) -> None:
        await self.client.rate_demon(self, rating=rating, as_mod=as_mod)

    async def suggest(self, stars: int, feature: bool) -> None:
        await self.client.suggest_level(self, stars=stars, feature=feature)

    async def update(self, *, get_data: bool = True) -> Optional[Level]:
        ...

    async def comment(self, content: str, record: int = DEFAULT_RECORD) -> Optional[LevelComment]:
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
        pages: Iterable[int] = DEFAULT_PAGE,
    ) -> AsyncIterator[LevelComment]:
        return self.client.get_level_comments(
            level=self,
            strategy=strategy,
            count=count,
            pages=pages,
        ).unwrap()

    def maybe_attach_client(self: L, client: Optional[Client]) -> L:
        self.creator.maybe_attach_client(client)
        self.song.maybe_attach_client(client)

        return super().maybe_attach_client(client)

    def attach_client(self: L, client: Client) -> L:
        self.creator.attach_client(client)
        self.song.attach_client(client)

        return super().attach_client(client)

    def detach_client(self: L) -> L:
        self.creator.detach_client()
        self.song.detach_client()

        return super().detach_client()
