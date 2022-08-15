from datetime import timedelta
from typing import BinaryIO

from attrs import define, field

from gd.api.recording import Recording
from gd.binary import VERSION, Binary
from gd.binary_utils import UTF_8, Writer
from gd.constants import DEFAULT_ID, DEFAULT_VERSION, EMPTY, EMPTY_BYTES
from gd.enums import ByteOrder, Difficulty, LevelLength, LevelType
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


@define()
class LevelAPI:
    id: int = field()
    name: str = field()
    creator: User = field()
    song: Song = field()
    description: str = field(default=EMPTY)
    data: bytes = field(default=EMPTY_BYTES)
    difficulty: Difficulty = field(default=Difficulty.DEFAULT)
    downloads: int = field(default=0)
    editable: bool = field(default=True)
    completions: int = field(default=0)
    verified: bool = field(default=False)
    uploaded: bool = field(default=False)
    version: int = field(default=DEFAULT_VERSION)
    game_version: GameVersion = field(default=CURRENT_GAME_VERSION)
    binary_version: Version = field(default=CURRENT_BINARY_VERSION)
    attempts: int = field(default=0)
    normal_record: int = field(default=0)
    practice_record: int = field(default=0)
    type: LevelType = field(default=LevelType.DEFAULT)
    rating: int = field(default=0)
    length: LevelLength = field(default=LevelLength.DEFAULT)
    stars: int = field(default=0)
    score: int = field(default=0)
    recording: Recording = field(factory=Recording)
    playable: bool = field(default=True)
    original_id: int = field(default=DEFAULT_ID)
    two_player: bool = field(default=False)
    object_count: int = field(default=0)
    first_coin_acquired: bool = field(default=False)
    second_coin_acquired: bool = field(default=False)
    third_coin_acquired: bool = field(default=False)
    coins: int = field(default=0)
    verified_coins: bool = field(default=False)
    requested_stars: int = field(default=0)
    low_detail: bool = field(default=False)
    low_detail_toggled: bool = field(default=False)
    timely_id: int = field(default=DEFAULT_ID)
    epic: bool = field(default=False)
    gauntlet: bool = field(default=False)
    unlisted: bool = field(default=False)
    editor_time: timedelta = field(factory=timedelta)
    copies_time: timedelta = field(factory=timedelta)
    favorite: bool = field(default=False)
    best_clicks: int = field(default=0)
    best_time: timedelta = field(factory=timedelta)
    progress: Progress = field(factory=Progress)
    leaderboard_record: int = field(default=0)

    def __hash__(self) -> int:
        return self.id

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

        writer.write_u16(len(data), order)

        writer.write(data)

        self.creator.to_binary(binary, order, version)
        self.song.to_binary(binary, order, version)

        data = self.description.encode(encoding)
