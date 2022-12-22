from __future__ import annotations

from typing import TYPE_CHECKING, AsyncIterator, Iterable, Optional, Type, TypeVar

from attrs import define, field
from iters.async_iters import wrap_async_iter
from iters.iters import iter

from gd.api.editor import DEFAULT_DATA, Editor
from gd.api.recording import Recording
from gd.binary import VERSION, BinaryReader, BinaryWriter
from gd.binary_utils import Reader, Writer
from gd.constants import (
    COMMENT_PAGE_SIZE,
    DEFAULT_COINS,
    DEFAULT_DOWNLOADS,
    DEFAULT_ENCODING,
    DEFAULT_ERRORS,
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
    DEFAULT_VERIFIED_COINS,
    DEFAULT_VERSION,
    EMPTY,
    UNKNOWN,
)
from gd.date_time import DateTime, Duration, utc_from_timestamp, utc_now
from gd.entity import Entity
from gd.enums import (
    ByteOrder,
    CommentStrategy,
    DemonDifficulty,
    Difficulty,
    LevelLeaderboardStrategy,
    LevelLength,
    LevelPrivacy,
    RateType,
    TimelyType,
)
from gd.errors import InternalError, MissingAccess
from gd.models import LevelModel, TimelyInfoModel
from gd.official_levels import OFFICIAL_LEVELS, OfficialLevel
from gd.password import Password
from gd.song import Song
from gd.typing import Predicate
from gd.users import User
from gd.versions import CURRENT_GAME_VERSION, GameVersion

if TYPE_CHECKING:
    from gd.client import Client
    from gd.comments import LevelComment

__all__ = ("Level",)

L = TypeVar("L", bound="Level")

RATE_TYPE_MASK = 0b00011111
TWO_PLAYER_BIT = 0b00100000
VERIFIED_COINS_BIT = 0b01000000
LOW_DETAIL_BIT = 0b10000000

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
    data: bytes = field(default=DEFAULT_DATA, eq=False, repr=False)
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
    password_data: Password = field(factory=Password, eq=False)
    original_id: int = field(default=DEFAULT_ID, eq=False)
    two_player: bool = field(default=DEFAULT_TWO_PLAYER, eq=False)
    coins: int = field(default=DEFAULT_COINS, eq=False)
    verified_coins: bool = field(default=DEFAULT_VERIFIED_COINS, eq=False)
    low_detail: bool = field(default=DEFAULT_LOW_DETAIL, eq=False)
    object_count: int = field(default=DEFAULT_OBJECT_COUNT, eq=False)
    created_at: DateTime = field(factory=utc_now, eq=False)
    updated_at: DateTime = field(factory=utc_now, eq=False)
    editor_time: Duration = field(factory=Duration, eq=False)
    copies_time: Duration = field(factory=Duration, eq=False)
    timely_type: TimelyType = field(default=TimelyType.DEFAULT, eq=False)
    timely_id: int = field(default=DEFAULT_ID, eq=False)

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

    def __str__(self) -> str:
        return self.name

    def to_binary(
        self,
        binary: BinaryWriter,
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

        writer.write_f64(self.created_at.timestamp(), order)
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

        value = self.rate_type.value

        if self.is_two_player():
            value |= TWO_PLAYER_BIT

        if self.has_verified_coins():
            value |= VERIFIED_COINS_BIT

        if self.has_low_detail():
            value |= LOW_DETAIL_BIT

        writer.write_u8(value, order)

        writer.write_u8(self.stars, order)

        writer.write_u8(self.requested_stars, order)

        writer.write_u32(self.score, order)

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
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
    ) -> L:
        two_player_bit = TWO_PLAYER_BIT
        verified_coins_bit = VERIFIED_COINS_BIT
        low_detail_bit = LOW_DETAIL_BIT
        rate_type_mask = RATE_TYPE_MASK

        reader = Reader(binary)

        id = reader.read_u32(order)

        name_length = reader.read_u8(order)

        name = reader.read(name_length).decode(encoding, errors)

        creator = User.from_binary(binary, order, version, encoding, errors)
        song = Song.from_binary(binary, order, version, encoding, errors)

        uploaded_timestamp = reader.read_f64(order)
        updated_timestamp = reader.read_f64(order)

        created_at = utc_from_timestamp(uploaded_timestamp)
        updated_at = utc_from_timestamp(updated_timestamp)

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
        low_detail = value & low_detail_bit == low_detail_bit

        rate_type_value = value & rate_type_mask

        rate_type = RateType(rate_type_value)

        stars = reader.read_u8(order)

        requested_stars = reader.read_u8(order)

        score = reader.read_u32(order)

        password_data = Password.from_binary(binary, order, version)

        original_id = reader.read_u32(order)

        coins = reader.read_u8(order)

        object_count = reader.read_u32(order)

        editor_seconds = reader.read_f32(order)
        copies_seconds = reader.read_f32(order)

        editor_time = Duration(seconds=editor_seconds)
        copies_time = Duration(seconds=copies_seconds)

        timely_type_value = reader.read_u8(order)

        timely_type = TimelyType(timely_type_value)

        timely_id = reader.read_u32(order)

        return cls(
            id=id,
            name=name,
            creator=creator,
            song=song,
            created_at=created_at,
            updated_at=updated_at,
            description=description,
            data=data,
            version=version,
            downloads=downloads,
            game_version=game_version,
            rating=rating,
            length=length,
            difficulty=difficulty,
            stars=stars,
            requested_stars=requested_stars,
            score=score,
            rate_type=rate_type,
            password_data=password_data,
            original_id=original_id,
            two_player=two_player,
            coins=coins,
            verified_coins=verified_coins,
            low_detail=low_detail,
            object_count=object_count,
            editor_time=editor_time,
            copies_time=copies_time,
            timely_type=timely_type,
            timely_id=timely_id,
        )

    @classmethod
    def from_model(cls: Type[L], model: LevelModel, creator: User, song: Song) -> L:
        rate_type = RateType.NOT_RATED

        stars = model.stars

        if stars > 0:
            rate_type = RateType.RATED

        score = model.score

        if score > 0:
            rate_type = RateType.FEATURED

        epic = model.is_epic()

        if epic:
            rate_type = RateType.EPIC

        # godlike = model.is_godlike()

        # if godlike:
        #    rate_type = RateType.GODLIKE

        return cls(
            id=model.id,
            name=model.name,
            creator=creator,
            song=song,
            description=model.description,
            # this might take some time, but it should be worth it
            data=Editor.from_robtop(model.data).to_bytes(),
            version=model.version,
            difficulty=model.difficulty,
            downloads=model.downloads,
            game_version=model.game_version,
            rating=model.rating,
            length=model.length,
            stars=model.stars,
            score=model.score,
            rate_type=rate_type,
            password_data=model.password_data,
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

        if get_data:
            data = DEFAULT_DATA  # TODO

        else:
            data = DEFAULT_DATA

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
            game_version=official_level.game_version,
            length=official_level.length,
        )

    @property
    def password(self) -> Optional[int]:
        return self.password_data.password

    def is_copyable(self) -> bool:
        return self.password_data.is_copyable()

    def is_timely(self, timely_type: Optional[TimelyType] = None) -> bool:
        if timely_type is None:
            return self.timely_type.is_timely()

        return self.timely_type is timely_type

    def is_daily(self) -> bool:
        return self.is_timely(TimelyType.DAILY)

    def is_weekly(self) -> bool:
        return self.is_timely(TimelyType.WEEKLY)

    # def is_event(self) -> bool:
    #     return self.is_timely(TimelyType.EVENT)

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
        return Editor.from_bytes(self.data)

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
        password: Optional[Password] = None,
        recording: Optional[Recording] = None,
        editor_time: Optional[Duration] = None,
        copies_time: Optional[Duration] = None,
        data: Optional[bytes] = None,
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
            password=switch_none(password, self.password_data),
            recording=recording,
            editor_time=switch_none(editor_time, self.editor_time),
            copies_time=switch_none(copies_time, self.copies_time),
            data=switch_none(data, self.data),
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

    async def update(self, *, get_data: bool = DEFAULT_GET_DATA) -> Optional[Level]:
        try:
            if self.is_timely():
                if self.is_daily():
                    level = await self.client.get_daily()

                elif self.is_weekly():
                    level = await self.client.get_weekly()

                # elif self.is_event():
                #     level = await self.client.get_event()

                else:
                    raise InternalError  # TODO: message?

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

    def attach_client_unchecked(self: L, client: Optional[Client]) -> L:
        self.creator.attach_client_unchecked(client)
        self.song.attach_client_unchecked(client)

        return super().attach_client_unchecked(client)

    def attach_client(self: L, client: Client) -> L:
        self.creator.attach_client(client)
        self.song.attach_client(client)

        return super().attach_client(client)

    def detach_client(self: L) -> L:
        self.creator.detach_client()
        self.song.detach_client()

        return super().detach_client()


T = TypeVar("T")


def switch_none(item: Optional[T], default: T) -> T:
    return default if item is None else item
