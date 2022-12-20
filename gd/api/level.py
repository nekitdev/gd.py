from typing import Type, TypeVar

from attrs import define, field

from gd.api.editor import DEFAULT_DATA
from gd.api.recording import Recording
from gd.binary import VERSION, Binary, BinaryReader, BinaryWriter
from gd.binary_utils import Reader, Writer
from gd.constants import (
    DEFAULT_ATTEMPTS,
    DEFAULT_CLICKS,
    DEFAULT_COINS,
    DEFAULT_COMPLETIONS,
    DEFAULT_DOWNLOADS,
    DEFAULT_EDITABLE,
    DEFAULT_ENCODING,
    DEFAULT_ERRORS,
    DEFAULT_FAVORITE,
    DEFAULT_GAUNTLET,
    DEFAULT_ID,
    DEFAULT_LEVEL_ORDER,
    DEFAULT_LOW_DETAIL,
    DEFAULT_LOW_DETAIL_TOGGLED,
    DEFAULT_OBJECT_COUNT,
    DEFAULT_PLAYABLE,
    DEFAULT_RATING,
    DEFAULT_RECORD,
    DEFAULT_SCORE,
    DEFAULT_STARS,
    DEFAULT_TWO_PLAYER,
    DEFAULT_UNLISTED,
    DEFAULT_UNLOCKED,
    DEFAULT_UPLOADED,
    DEFAULT_VERIFIED,
    DEFAULT_VERIFIED_COINS,
    DEFAULT_VERSION,
    EMPTY,
    UNKNOWN,
)
from gd.date_time import Duration
from gd.enums import ByteOrder, CollectedCoins, Difficulty, LevelLength, LevelType, RateType
from gd.password import Password
from gd.progress import Progress
from gd.robtop import RobTop
from gd.song import Song
from gd.users import User
from gd.versions import CURRENT_BINARY_VERSION, CURRENT_GAME_VERSION, GameVersion, Version

EDITABLE_BIT = 0b00000001
VERIFIED_BIT = 0b00000010
UPLOADED_BIT = 0b00000100
PLAYABLE_BIT = 0b00001000
TWO_PLAYER_BIT = 0b00010000
LOW_DETAIL_BIT = 0b00100000
LOW_DETAIL_TOGGLED_BIT = 0b01000000
FAVORITE_BIT = 0b10000000

COLLECTED_COINS_MASK = 0b00000111
VERIFIED_COINS_BIT = 0b00001000
GAUNTLET_BIT = 0b00010000
UNLISTED_BIT = 0b00100000
UNLOCKED_BIT = 0b01000000

TYPE_MASK = 0b00000111
RATE_TYPE_MASK = 0b11111000

RATE_TYPE_SHIFT = TYPE_MASK.bit_length()

A = TypeVar("A", bound="LevelAPI")


@define()
class LevelAPI(Binary, RobTop):
    id: int = field()
    name: str = field()
    creator: User = field()
    song: Song = field()
    description: str = field(default=EMPTY)
    data: bytes = field(default=DEFAULT_DATA, repr=False)
    difficulty: Difficulty = field(default=Difficulty.DEFAULT)
    downloads: int = field(default=DEFAULT_DOWNLOADS)
    editable: bool = field(default=DEFAULT_EDITABLE)
    completions: int = field(default=DEFAULT_COMPLETIONS)
    verified: bool = field(default=DEFAULT_VERIFIED)
    uploaded: bool = field(default=DEFAULT_UPLOADED)
    version: int = field(default=DEFAULT_VERSION)
    game_version: GameVersion = field(default=CURRENT_GAME_VERSION)
    binary_version: Version = field(default=CURRENT_BINARY_VERSION)
    attempts: int = field(default=DEFAULT_ATTEMPTS)
    normal_record: int = field(default=DEFAULT_RECORD)
    practice_record: int = field(default=DEFAULT_RECORD)
    type: LevelType = field(default=LevelType.DEFAULT)
    rating: int = field(default=DEFAULT_RATING)
    length: LevelLength = field(default=LevelLength.DEFAULT)
    stars: int = field(default=DEFAULT_STARS)
    score: int = field(default=DEFAULT_SCORE)
    rate_type: RateType = field(default=RateType.DEFAULT)
    recording: Recording = field(factory=Recording)
    playable: bool = field(default=DEFAULT_PLAYABLE)
    unlocked: bool = field(default=DEFAULT_UNLOCKED)
    password_data: Password = field(factory=Password)
    original_id: int = field(default=DEFAULT_ID)
    two_player: bool = field(default=DEFAULT_TWO_PLAYER)
    object_count: int = field(default=DEFAULT_OBJECT_COUNT)
    collected_coins: CollectedCoins = field(default=CollectedCoins.DEFAULT)
    coins: int = field(default=DEFAULT_COINS)
    verified_coins: bool = field(default=DEFAULT_VERIFIED_COINS)
    requested_stars: int = field(default=DEFAULT_STARS)
    low_detail: bool = field(default=DEFAULT_LOW_DETAIL)
    low_detail_toggled: bool = field(default=DEFAULT_LOW_DETAIL_TOGGLED)
    timely_id: int = field(default=DEFAULT_ID)
    gauntlet: bool = field(default=DEFAULT_GAUNTLET)
    unlisted: bool = field(default=DEFAULT_UNLISTED)
    editor_time: Duration = field(factory=Duration)
    copies_time: Duration = field(factory=Duration)
    favorite: bool = field(default=DEFAULT_FAVORITE)
    level_order: int = field(default=DEFAULT_LEVEL_ORDER)
    folder_id: int = field(default=DEFAULT_ID)
    best_clicks: int = field(default=DEFAULT_CLICKS)
    best_time: Duration = field(factory=Duration)
    progress: Progress = field(factory=Progress)
    leaderboard_record: int = field(default=DEFAULT_RECORD)

    @classmethod
    def default(cls: Type[A]) -> A:
        return cls(id=DEFAULT_ID, name=UNKNOWN, creator=User.default(), song=Song.default())

    def __hash__(self) -> int:
        return self.id ^ hash(type(self))

    @classmethod
    def from_binary(
        cls: Type[A],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
    ) -> A:
        editable_bit = EDITABLE_BIT
        verified_bit = VERIFIED_BIT
        uploaded_bit = UPLOADED_BIT
        playable_bit = PLAYABLE_BIT
        two_player_bit = TWO_PLAYER_BIT
        low_detail_bit = LOW_DETAIL_BIT
        low_detail_toggled_bit = LOW_DETAIL_TOGGLED_BIT
        favorite_bit = FAVORITE_BIT

        verified_coins_bit = VERIFIED_COINS_BIT
        gauntlet_bit = GAUNTLET_BIT
        unlisted_bit = UNLISTED_BIT
        unlocked_bit = UNLOCKED_BIT

        reader = Reader(binary)

        id = reader.read_u32(order)

        name_length = reader.read_u8(order)

        name = reader.read(name_length).decode(encoding, errors)

        creator = User.from_binary(binary, order, version, encoding, errors)

        song = Song.from_binary(binary, order, version, encoding, errors)

        description_length = reader.read_u16(order)

        description = reader.read(description_length).decode(encoding, errors)

        data_length = reader.read_u32(order)

        data = reader.read(data_length)

        difficulty_value = reader.read_u8(order)

        difficulty = Difficulty(difficulty_value)

        value = reader.read_u8(order)

        editable = value & editable_bit == editable_bit
        verified = value & verified_bit == verified_bit
        uploaded = value & uploaded_bit == uploaded_bit
        playable = value & playable_bit == playable_bit
        two_player = value & two_player_bit == two_player_bit
        low_detail = value & low_detail_bit == low_detail_bit
        low_detail_toggled = value & low_detail_toggled_bit == low_detail_toggled_bit
        favorite = value & favorite_bit == favorite_bit

        value = reader.read_u8(order)

        collected_coins_value = value & COLLECTED_COINS_MASK

        collected_coins = CollectedCoins(collected_coins_value)

        verified_coins = value & verified_coins_bit == verified_coins_bit
        gauntlet = value & gauntlet_bit == gauntlet_bit
        unlisted = value & unlisted_bit == unlisted_bit
        unlocked = value & unlocked_bit == unlocked_bit

        downloads = reader.read_u32(order)

        completions = reader.read_u16(order)

        version = reader.read_u8(order)

        game_version = GameVersion.from_binary(binary, order, version)
        binary_version = Version.from_binary(binary, order, version)

        attempts = reader.read_u32(order)

        normal_record = reader.read_u8(order)
        practice_record = reader.read_u8(order)

        value = reader.read_u8(order)

        type_value = value & TYPE_MASK

        type = LevelType(type_value)

        rate_type_value = (value & RATE_TYPE_MASK) >> RATE_TYPE_SHIFT

        rate_type = RateType(rate_type_value)

        rating = reader.read_i32(order)

        length_value = reader.read_u8(order)

        length = LevelLength(length_value)

        stars = reader.read_u8(order)

        score = reader.read_u32(order)

        recording = Recording.from_binary(binary, order, version)

        password_data = Password.from_binary(binary, order, version)

        original_id = reader.read_u32(order)

        object_count = reader.read_u32(order)

        coins = reader.read_u8(order)

        requested_stars = reader.read_u8(order)

        timely_id = reader.read_u32(order)

        editor_seconds = reader.read_f32(order)
        copies_seconds = reader.read_f32(order)

        editor_time = Duration(seconds=editor_seconds)
        copies_time = Duration(seconds=copies_seconds)

        level_order = reader.read_u16(order)

        folder_id = reader.read_u8(order)

        best_clicks = reader.read_u16(order)

        best_seconds = reader.read_f32(order)

        best_time = Duration(seconds=best_seconds)

        progress = Progress.from_binary(binary, order, version)

        leaderboard_record = reader.read_u8(order)

        return cls(
            id=id,
            name=name,
            creator=creator,
            song=song,
            description=description,
            data=data,
            difficulty=difficulty,
            downloads=downloads,
            editable=editable,
            completions=completions,
            verified=verified,
            uploaded=uploaded,
            version=version,
            game_version=game_version,
            binary_version=binary_version,
            attempts=attempts,
            normal_record=normal_record,
            practice_record=practice_record,
            type=type,
            rating=rating,
            length=length,
            stars=stars,
            score=score,
            rate_type=rate_type,
            recording=recording,
            playable=playable,
            unlocked=unlocked,
            password_data=password_data,
            original_id=original_id,
            two_player=two_player,
            object_count=object_count,
            collected_coins=collected_coins,
            coins=coins,
            verified_coins=verified_coins,
            requested_stars=requested_stars,
            low_detail=low_detail,
            low_detail_toggled=low_detail_toggled,
            timely_id=timely_id,
            gauntlet=gauntlet,
            unlisted=unlisted,
            editor_time=editor_time,
            copies_time=copies_time,
            favorite=favorite,
            level_order=level_order,
            folder_id=folder_id,
            best_clicks=best_clicks,
            best_time=best_time,
            progress=progress,
            leaderboard_record=leaderboard_record,
        )

    def to_binary(
        self,
        binary: BinaryWriter,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
    ) -> None:
        writer = Writer(binary)

        writer.write_u32(self.id, order)

        data = self.name.encode(encoding, errors)

        writer.write_u8(len(data), order)

        writer.write(data)

        self.creator.to_binary(binary, order, version, encoding, errors)
        self.song.to_binary(binary, order, version, encoding, errors)

        data = self.description.encode(encoding, errors)

        writer.write_u16(len(data), order)

        writer.write(data)

        data = self.data

        writer.write_u32(len(data), order)

        writer.write(data)

        writer.write_u8(self.difficulty.value, order)

        value = 0

        if self.is_editable():
            value |= EDITABLE_BIT

        if self.is_verified():
            value |= VERIFIED_BIT

        if self.is_uploaded():
            value |= UPLOADED_BIT

        if self.is_playable():
            value |= PLAYABLE_BIT

        if self.is_two_player():
            value |= TWO_PLAYER_BIT

        if self.has_low_detail():
            value |= LOW_DETAIL_BIT

        if self.is_low_detail_toggled():
            value |= LOW_DETAIL_TOGGLED_BIT

        if self.is_favorite():
            value |= FAVORITE_BIT

        writer.write_u8(value, order)

        value = self.collected_coins.value

        if self.has_verified_coins():
            value |= VERIFIED_COINS_BIT

        if self.is_gauntlet():
            value |= GAUNTLET_BIT

        if self.is_unlisted():
            value |= UNLISTED_BIT

        if self.is_unlocked():
            value |= UNLOCKED_BIT

        writer.write_u8(value, order)

        writer.write_u32(self.downloads, order)

        writer.write_u16(self.completions, order)

        writer.write_u8(self.version, order)

        self.game_version.to_binary(binary, order, version)
        self.binary_version.to_binary(binary, order, version)

        writer.write_u32(self.attempts, order)

        writer.write_u8(self.normal_record, order)
        writer.write_u8(self.practice_record, order)

        value = self.type.value

        value |= self.rate_type.value << RATE_TYPE_SHIFT

        writer.write_u8(value, order)

        writer.write_i32(self.rating, order)

        writer.write_u8(self.length.value, order)

        writer.write_u8(self.stars, order)

        writer.write_u32(self.score, order)

        self.recording.to_binary(binary, order, version)

        self.password_data.to_binary(binary, order, version)

        writer.write_u32(self.original_id, order)

        writer.write_u32(self.object_count, order)

        writer.write_u8(self.coins, order)

        writer.write_u8(self.requested_stars, order)

        writer.write_u32(self.timely_id, order)

        writer.write_f32(self.editor_time.total_seconds(), order)
        writer.write_f32(self.copies_time.total_seconds(), order)

        writer.write_u16(self.level_order, order)

        writer.write_u8(self.folder_id, order)

        writer.write_u16(self.best_clicks, order)
        writer.write_f32(self.best_time.total_seconds(), order)

        self.progress.to_binary(binary, order, version)

        writer.write_u8(self.leaderboard_record, order)

    def is_demon(self) -> bool:
        return self.difficulty.is_demon()

    def is_editable(self) -> bool:
        return self.editable

    def is_verified(self) -> bool:
        return self.verified

    def is_uploaded(self) -> bool:
        return self.uploaded

    def is_playable(self) -> bool:
        return self.playable

    def is_unlocked(self) -> bool:
        return self.unlocked

    def is_two_player(self) -> bool:
        return self.two_player

    def has_low_detail(self) -> bool:
        return self.low_detail

    def is_low_detail_toggled(self) -> bool:
        return self.low_detail_toggled

    def is_favorite(self) -> bool:
        return self.favorite

    def has_verified_coins(self) -> bool:
        return self.verified_coins

    def is_gauntlet(self) -> bool:
        return self.gauntlet

    def is_unlisted(self) -> bool:
        return self.unlisted

    @classmethod
    def from_robtop(cls: Type[A], string: str) -> A:
        ...

    def to_robtop(self) -> str:
        ...

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        ...
