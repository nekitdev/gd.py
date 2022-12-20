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
    DEFAULT_DEMON,
    DEFAULT_DOWNLOADS,
    DEFAULT_EDITABLE,
    DEFAULT_ENCODING,
    DEFAULT_EPIC,
    DEFAULT_ERRORS,
    DEFAULT_FAVORITE,
    DEFAULT_GAUNTLET,
    DEFAULT_ID,
    DEFAULT_LOW_DETAIL,
    DEFAULT_LOW_DETAIL_TOGGLED,
    DEFAULT_OBJECT_COUNT,
    DEFAULT_ORDER,
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
)
from gd.date_time import Duration
from gd.enums import ByteOrder, CollectedCoins, Difficulty, LevelLength, LevelType
from gd.password import Password
from gd.progress import Progress
from gd.song import Song
from gd.users import User
from gd.versions import CURRENT_BINARY_VERSION, CURRENT_GAME_VERSION, GameVersion, Version

EDITABLE_BIT = 0b00000000_00000001
VERIFIED_BIT = 0b00000000_00000010
UPLOADED_BIT = 0b00000000_00000100
PLAYABLE_BIT = 0b00000000_00001000
TWO_PLAYER_BIT = 0b00000000_00010000
LOW_DETAIL_BIT = 0b00000000_00100000
LOW_DETAIL_TOGGLED_BIT = 0b00000000_01000000
FAVORITE_BIT = 0b00000000_10000000

COLLECTED_COINS_SHIFT = FAVORITE_BIT.bit_length()

COLLECTED_COINS_MASK = 0b00000111_00000000
VERIFIED_COINS_BIT = 0b00001000_00000000
EPIC_BIT = 0b00010000_00000000
GAUNTLET_BIT = 0b00100000_00000000
UNLISTED_BIT = 0b01000000_00000000
DEMON_BIT = 0b10000000_00000000

A = TypeVar("A", bound="LevelAPI")


@define()
class LevelAPI(Binary):
    id: int = field()
    name: str = field()
    creator: User = field()
    song: Song = field()
    description: str = field(default=EMPTY)
    data: bytes = field(default=DEFAULT_DATA)
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
    # HERE
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
    collected_coins: CollectedCoins = field(default=CollectedCoins.DEFAULT)
    coins: int = field(default=DEFAULT_COINS)
    verified_coins: bool = field(default=DEFAULT_VERIFIED_COINS)
    requested_stars: int = field(default=DEFAULT_STARS)
    low_detail: bool = field(default=DEFAULT_LOW_DETAIL)
    low_detail_toggled: bool = field(default=DEFAULT_LOW_DETAIL_TOGGLED)
    timely_id: int = field(default=DEFAULT_ID)
    epic: bool = field(default=DEFAULT_EPIC)
    gauntlet: bool = field(default=DEFAULT_GAUNTLET)
    unlisted: bool = field(default=DEFAULT_UNLISTED)
    editor_time: Duration = field(factory=Duration)
    copies_time: Duration = field(factory=Duration)
    favorite: bool = field(default=DEFAULT_FAVORITE)
    order: int = field(default=DEFAULT_ORDER)
    folder_id: int = field(default=DEFAULT_ID)
    best_clicks: int = field(default=DEFAULT_CLICKS)
    best_time: Duration = field(factory=Duration)
    progress: Progress = field(factory=Progress)
    leaderboard_record: int = field(default=DEFAULT_RECORD)

    def __hash__(self) -> int:
        return self.id

    @classmethod
    def from_binary(
        cls: Type[A],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
    ) -> A:
        reader = Reader(binary)

        ...

        return cls()

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

        self.creator.to_binary(binary, order, version)
        self.song.to_binary(binary, order, version)

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

        value |= self.collected_coins.value << COLLECTED_COINS_SHIFT

        if self.has_verified_coins():
            value |= VERIFIED_COINS_BIT

        if self.is_epic():
            value |= EPIC_BIT

        if self.is_gauntlet():
            value |= GAUNTLET_BIT

        if self.is_unlisted():
            value |= UNLISTED_BIT

        if self.is_demon():
            value |= DEMON_BIT

        writer.write_u16(value, order)

        writer.write_u32(self.downloads, order)

        writer.write_u16(self.completions, order)

        writer.write_u8(self.version, order)

        self.game_version.to_binary(binary, order, version)
        self.binary_version.to_binary(binary, order, version)

        writer.write_u32(self.attempts, order)

        writer.write_u8(self.normal_record, order)
        writer.write_u8(self.practice_record, order)

    def is_editable(self) -> bool:
        return self.editable

    def is_verified(self) -> bool:
        return self.verified

    def is_uploaded(self) -> bool:
        return self.uploaded

    def is_playable(self) -> bool:
        return self.playable

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

    def is_epic(self) -> bool:
        return self.epic

    def is_gauntlet(self) -> bool:
        return self.gauntlet

    def is_unlisted(self) -> bool:
        return self.unlisted

    def is_demon(self) -> bool:
        return self.demon
