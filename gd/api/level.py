from datetime import timedelta
from typing import BinaryIO, Type, TypeVar

from attrs import define, field

from gd.api.recording import Recording
from gd.binary import VERSION, Binary
from gd.binary_utils import UTF_8, Reader, Writer
from gd.constants import (
    DEFAULT_ATTEMPTS,
    DEFAULT_CLICKS,
    DEFAULT_COINS,
    DEFAULT_COMPLETIONS,
    DEFAULT_DEMON,
    DEFAULT_DOWNLOADS,
    DEFAULT_EDITABLE,
    DEFAULT_EPIC,
    DEFAULT_FAVORITE,
    DEFAULT_FIRST_COIN_VERIFIED,
    DEFAULT_GAUNTLET,
    DEFAULT_ID,
    DEFAULT_LOW_DETAIL,
    DEFAULT_LOW_DETAIL_TOGGLED,
    DEFAULT_OBJECT_COUNT,
    DEFAULT_ORDER,
    DEFAULT_PLAYABLE,
    DEFAULT_RATING,
    DEFAULT_RECORD,
    DEFAULT_SECOND_COIN_VERIFIED,
    DEFAULT_SCORE,
    DEFAULT_STARS,
    DEFAULT_THIRD_COIN_VERIFIED,
    DEFAULT_TWO_PLAYER,
    DEFAULT_UNLISTED,
    DEFAULT_UNLOCKED,
    DEFAULT_UPLOADED,
    DEFAULT_VERIFIED,
    DEFAULT_VERIFIED_COINS,
    DEFAULT_VERSION,
    EMPTY,
    EMPTY_BYTES,
)
from gd.enums import ByteOrder, Difficulty, LevelLength, LevelType
from gd.password import Password
from gd.progress import Progress
from gd.song import Song
from gd.user import User
from gd.versions import CURRENT_BINARY_VERSION, CURRENT_GAME_VERSION, GameVersion, Version

EDITABLE_BIT = 0b00000000_00000001
VERIFIED_BIT = 0b00000000_00000010
UPLOADED_BIT = 0b00000000_00000100
PLAYABLE_BIT = 0b00000000_00001000
TWO_PLAYER_BIT = 0b00000000_00010000
LOW_DETAIL_BIT = 0b00000000_00100000
LOW_DETAIL_TOGGLED_BIT = 0b00000000_01000000
FAVORITE_BIT = 0b00000000_10000000

FIRST_COIN_ACQUIRED_BIT = 0b00000001_00000000
SECOND_COIN_ACQUIRED_BIT = 0b00000010_00000000
THIRD_COIN_ACQUIRED_BIT = 0b00000100_00000000
VERIFIED_COINS_BIT = 0b00001000_00000000
EPIC_BIT = 0b00010000_00000000
GAUNTLET_BIT = 0b00100000_00000000
UNLISTED_BIT = 0b01000000_00000000

A = TypeVar("A", bound="LevelAPI")


@define()
class LevelAPI(Binary):
    id: int = field()
    name: str = field()
    creator: User = field()
    song: Song = field()
    description: str = field(default=EMPTY)
    data: bytes = field(default=EMPTY_BYTES)
    difficulty: Difficulty = field(default=Difficulty.DEFAULT)
    demon: bool = field(default=DEFAULT_DEMON)
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
    recording: Recording = field(factory=Recording)
    playable: bool = field(default=DEFAULT_PLAYABLE)
    unlocked: bool = field(default=DEFAULT_UNLOCKED)
    password_data: Password = field(factory=Password)
    original_id: int = field(default=DEFAULT_ID)
    two_player: bool = field(default=DEFAULT_TWO_PLAYER)
    object_count: int = field(default=DEFAULT_OBJECT_COUNT)
    first_coin_acquired: bool = field(default=DEFAULT_FIRST_COIN_VERIFIED)
    second_coin_acquired: bool = field(default=DEFAULT_SECOND_COIN_VERIFIED)
    third_coin_acquired: bool = field(default=DEFAULT_THIRD_COIN_VERIFIED)
    coins: int = field(default=DEFAULT_COINS)
    verified_coins: bool = field(default=DEFAULT_VERIFIED_COINS)
    requested_stars: int = field(default=DEFAULT_STARS)
    low_detail: bool = field(default=DEFAULT_LOW_DETAIL)
    low_detail_toggled: bool = field(default=DEFAULT_LOW_DETAIL_TOGGLED)
    timely_id: int = field(default=DEFAULT_ID)
    epic: bool = field(default=DEFAULT_EPIC)
    gauntlet: bool = field(default=DEFAULT_GAUNTLET)
    unlisted: bool = field(default=DEFAULT_UNLISTED)
    editor_time: timedelta = field(factory=timedelta)
    copies_time: timedelta = field(factory=timedelta)
    favorite: bool = field(default=DEFAULT_FAVORITE)
    order: int = field(default=DEFAULT_ORDER)
    folder_id: int = field(default=DEFAULT_ID)
    best_clicks: int = field(default=DEFAULT_CLICKS)
    best_time: timedelta = field(factory=timedelta)
    progress: Progress = field(factory=Progress)
    leaderboard_record: int = field(default=DEFAULT_RECORD)

    def __hash__(self) -> int:
        return self.id

    @classmethod
    def from_binary(
        cls: Type[A], binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> A:
        reader = Reader(binary)

        ...

        return cls()

    def to_binary(
        self,
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = UTF_8,
    ) -> None:
        writer = Writer(binary)

        writer.write_u64(self.id, order)

        data = self.name.encode(encoding)

        writer.write_u8(len(data), order)

        writer.write(data)

        self.creator.to_binary(binary, order, version)
        self.song.to_binary(binary, order, version)

        data = self.description.encode(encoding)

        writer.write_u16(len(data), order)

        writer.write(data)

        data = self.data

        writer.write_u32(len(data), order)

        writer.write(data)

        writer.write_u8(self.difficulty.value, order)

        value = 0

        ...

        writer.write_u16(value, order)
