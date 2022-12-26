from typing import Any, Dict, Optional, Type, TypeVar

from attrs import define, field

from gd.api.editor import Editor
from gd.api.recording import Recording
from gd.binary import VERSION, Binary, BinaryReader, BinaryWriter
from gd.binary_utils import Reader, Writer
from gd.constants import (
    DEFAULT_ATTEMPTS,
    DEFAULT_AUTO,
    DEFAULT_CLICKS,
    DEFAULT_COINS,
    DEFAULT_COMPLETIONS,
    DEFAULT_DEMON,
    DEFAULT_DENOMINATOR,
    DEFAULT_DOWNLOADS,
    DEFAULT_EDITABLE,
    DEFAULT_ENCODING,
    DEFAULT_EPIC,
    DEFAULT_ERRORS,
    DEFAULT_FAVORITE,
    DEFAULT_GAUNTLET,
    DEFAULT_HIGH_OBJECT_COUNT,
    DEFAULT_ID,
    DEFAULT_JUMPS,
    DEFAULT_LEVEL_ORDER,
    DEFAULT_LOW_DETAIL,
    DEFAULT_LOW_DETAIL_TOGGLED,
    DEFAULT_NUMERATOR,
    DEFAULT_OBJECT_COUNT,
    DEFAULT_ORB_PERCENTAGE,
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
from gd.decorators import cache_by
from gd.difficulty_parameters import DEFAULT_DEMON_DIFFICULTY_VALUE, DifficultyParameters
from gd.encoding import (
    decode_base64_string_url_safe,
    encode_base64_string_url_safe,
    unzip_level_string,
    zip_level_string,
)
from gd.enums import ByteOrder, CollectedCoins, Difficulty, InternalType, LevelLength, LevelType, RateType
from gd.password import Password
from gd.progress import Progress
from gd.song import Song
from gd.users import User
from gd.versions import CURRENT_BINARY_VERSION, CURRENT_GAME_VERSION, GameVersion, Version

INTERNAL_TYPE = "kCEK"
ID = "k1"
NAME = "k2"
DESCRIPTION = "k3"
DATA = "k4"
CREATOR_NAME = "k5"
CREATOR_ID = "k6"
CREATOR_ACCOUNT_ID = "k60"
OFFICIAL_SONG_ID = "k8"
SONG_ID = "k45"
DIFFICULTY_DENOMINATOR = "k9"
DIFFICULTY_NUMERATOR = "k10"
AUTO = "k33"
DEMON = "k25"
DEMON_DIFFICULTY = "k76"
DOWNLOADS = "k11"
COMPLETIONS = "k12"
EDITABLE = "k13"
VERIFIED = "k14"
UPLOADED = "k15"
LEVEL_VERSION = "k16"
GAME_VERSION = "k17"
BINARY_VERSION = "k50"
ATTEMPTS = "k18"
JUMPS = "k36"
NORMAL_RECORD = "k19"
PRACTICE_RECORD = "k20"
TYPE = "k21"
RATING = "k22"
LENGTH = "k23"
STARS = "k26"
SCORE = "k27"
EPIC = "k75"
RECORDING = "k34"
PLAYABLE = "k35"
UNLOCKED = "k38"
PASSWORD = "k41"
ORIGINAL_ID = "k42"
TWO_PLAYER = "k43"
OBJECT_COUNT = "k48"
FIRST_COIN = "k61"
SECOND_COIN = "k62"
THIRD_COIN = "k63"
COINS = "k64"
VERIFIED_COINS = "k65"
REQUESTED_STARS = "k66"
HIGH_OBJECT_COUNT = "k69"
ORB_PERCENTAGE = "k71"
LOW_DETAIL = "k72"
LOW_DETAIL_TOGGLED = "k73"
TIMELY_ID = "k74"
GAUNTLET = "k77"
UNLISTED = "k79"
EDITOR_SECONDS = "k80"
COPIES_SECONDS = "k81"
FAVORITE = "k82"
LEVEL_ORDER = "k83"
FOLDER_ID = "k84"
BEST_CLICKS = "k85"
BEST_SECONDS = "k86"
PROGRESS = "k88"
LEADERBOARD_RECORD = "k90"

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
HIGH_OBJECT_COUNT_BIT = 0b10000000

TYPE_MASK = 0b00000111
RATE_TYPE_MASK = 0b11111000

RATE_TYPE_SHIFT = TYPE_MASK.bit_length()

UNPROCESSED_DATA = "unprocessed_data"

A = TypeVar("A", bound="LevelAPI")


@define()
class LevelAPI(Binary):
    id: int = field()
    name: str = field()
    creator: User = field()
    song: Song = field()
    description: str = field(default=EMPTY)
    unprocessed_data: str = field(default=EMPTY, repr=False)
    difficulty: Difficulty = field(default=Difficulty.DEFAULT)
    downloads: int = field(default=DEFAULT_DOWNLOADS)
    completions: int = field(default=DEFAULT_COMPLETIONS)
    editable: bool = field(default=DEFAULT_EDITABLE)
    verified: bool = field(default=DEFAULT_VERIFIED)
    uploaded: bool = field(default=DEFAULT_UPLOADED)
    version: int = field(default=DEFAULT_VERSION)
    game_version: GameVersion = field(default=CURRENT_GAME_VERSION)
    binary_version: Version = field(default=CURRENT_BINARY_VERSION)
    attempts: int = field(default=DEFAULT_ATTEMPTS)
    jumps: int = field(default=DEFAULT_JUMPS)
    normal_record: int = field(default=DEFAULT_RECORD)
    practice_record: int = field(default=DEFAULT_RECORD)
    type: LevelType = field(default=LevelType.DEFAULT)
    rating: int = field(default=DEFAULT_RATING)
    length: LevelLength = field(default=LevelLength.DEFAULT)
    stars: int = field(default=DEFAULT_STARS)
    score: int = field(default=DEFAULT_SCORE)
    rate_type: RateType = field(default=RateType.DEFAULT)
    recording: Recording = field(factory=Recording, repr=False)
    playable: bool = field(default=DEFAULT_PLAYABLE)
    unlocked: bool = field(default=DEFAULT_UNLOCKED)
    password_data: Password = field(factory=Password)
    original_id: int = field(default=DEFAULT_ID)
    two_player: bool = field(default=DEFAULT_TWO_PLAYER)
    object_count: int = field(default=DEFAULT_OBJECT_COUNT)
    high_object_count: bool = field(default=DEFAULT_HIGH_OBJECT_COUNT)
    collected_coins: CollectedCoins = field(default=CollectedCoins.DEFAULT)
    coins: int = field(default=DEFAULT_COINS)
    verified_coins: bool = field(default=DEFAULT_VERIFIED_COINS)
    requested_stars: int = field(default=DEFAULT_STARS)
    orb_percentage: int = field(default=DEFAULT_ORB_PERCENTAGE)
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

    @property
    @cache_by(UNPROCESSED_DATA)
    def processed_data(self) -> str:
        return unzip_level_string(self.unprocessed_data)

    @processed_data.setter
    def processed_data(self, processed_data: str) -> None:
        self.unprocessed_data = zip_level_string(processed_data)

    @property
    @cache_by(UNPROCESSED_DATA)
    def data(self) -> bytes:
        return self.open_editor().to_bytes()

    @data.setter
    def data(self, data: bytes) -> None:
        self.processed_data = Editor.from_bytes(data).to_robtop()

    def open_editor(self) -> Editor:
        return Editor.from_robtop(self.processed_data)

    @classmethod
    def from_robtop_data(cls: Type[A], data: Dict[str, Any]) -> A:
        id = data.get(ID, DEFAULT_ID)

        name = data.get(NAME, UNKNOWN)

        description = decode_base64_string_url_safe(data.get(DESCRIPTION, EMPTY))

        unprocessed_data = data.get(DATA, EMPTY)

        creator_name = data.get(CREATOR_NAME, UNKNOWN)

        creator_id = data.get(CREATOR_ID, DEFAULT_ID)

        creator_account_id = data.get(CREATOR_ACCOUNT_ID, DEFAULT_ID)

        creator = User(id=creator_id, name=creator_name, account_id=creator_account_id)

        official_song_id = data.get(OFFICIAL_SONG_ID, DEFAULT_ID)

        if official_song_id:
            song = Song.official(official_song_id, server_style=False)

        else:
            song_id = data.get(SONG_ID, DEFAULT_ID)

            song = Song.default()
            song.id = song_id

        difficulty = DifficultyParameters(
            data.get(DIFFICULTY_NUMERATOR, DEFAULT_NUMERATOR),
            data.get(DIFFICULTY_DENOMINATOR, DEFAULT_DENOMINATOR),
            data.get(DEMON_DIFFICULTY, DEFAULT_DEMON_DIFFICULTY_VALUE),
            data.get(AUTO, DEFAULT_AUTO),
            data.get(DEMON, DEFAULT_DEMON),
        ).into_difficulty()

        downloads = data.get(DOWNLOADS, DEFAULT_DOWNLOADS)

        editable = data.get(EDITABLE, DEFAULT_EDITABLE)

        completions = data.get(COMPLETIONS, DEFAULT_COMPLETIONS)

        verified = data.get(VERIFIED, DEFAULT_VERIFIED)
        uploaded = data.get(UPLOADED, DEFAULT_UPLOADED)

        version = data.get(LEVEL_VERSION, DEFAULT_VERSION)

        game_version_value = data.get(GAME_VERSION)

        if game_version_value is None:
            game_version = CURRENT_GAME_VERSION

        else:
            game_version = GameVersion.from_robtop_value(game_version_value)

        binary_version_value = data.get(BINARY_VERSION)

        if binary_version_value is None:
            binary_version = CURRENT_BINARY_VERSION

        else:
            binary_version = Version.from_value(binary_version_value)

        attempts = data.get(ATTEMPTS, DEFAULT_ATTEMPTS)
        jumps = data.get(JUMPS, DEFAULT_JUMPS)

        normal_record = data.get(NORMAL_RECORD, DEFAULT_RECORD)
        practice_record = data.get(PRACTICE_RECORD, DEFAULT_RECORD)

        type_value = data.get(TYPE)

        if type_value is None:
            type = LevelType.DEFAULT

        else:
            type = LevelType(type_value)

        rating = data.get(RATING, DEFAULT_RATING)

        length_value = data.get(LENGTH)

        if length_value is None:
            length = LevelLength.DEFAULT

        else:
            length = LevelLength(length_value)

        stars = data.get(STARS, DEFAULT_STARS)

        score = data.get(SCORE, DEFAULT_SCORE)

        if score < 0:
            score = 0

        rate_type = RateType.NOT_RATED

        if stars:
            rate_type = RateType.RATED

        if score:
            rate_type = RateType.FEATURED

        epic = data.get(EPIC, DEFAULT_EPIC)

        if epic:
            rate_type = RateType.EPIC

        # if godlike:
        #     rate_type = RateType.GODLIKE

        recording = Recording.from_robtop(unzip_level_string(data.get(RECORDING, EMPTY)))

        playable = data.get(PLAYABLE, DEFAULT_PLAYABLE)
        unlocked = data.get(UNLOCKED, DEFAULT_UNLOCKED)

        password = data.get(PASSWORD)

        if password is None:
            password_data = Password()

        else:
            password_data = Password.from_robtop_value(password)

        original_id = data.get(ORIGINAL_ID, DEFAULT_ID)

        two_player = data.get(TWO_PLAYER, DEFAULT_TWO_PLAYER)

        object_count = data.get(OBJECT_COUNT, DEFAULT_OBJECT_COUNT)

        high_object_count = data.get(HIGH_OBJECT_COUNT, DEFAULT_HIGH_OBJECT_COUNT)

        collected_coins = CollectedCoins.NONE

        first_coin = data.get(FIRST_COIN)

        if first_coin:
            collected_coins |= CollectedCoins.FIRST

        second_coin = data.get(SECOND_COIN)

        if second_coin:
            collected_coins |= CollectedCoins.SECOND

        third_coin = data.get(THIRD_COIN)

        if third_coin:
            collected_coins |= CollectedCoins.THIRD

        coins = data.get(COINS, DEFAULT_COINS)

        verified_coins = data.get(VERIFIED_COINS, DEFAULT_VERIFIED_COINS)

        requested_stars = data.get(REQUESTED_STARS, DEFAULT_STARS)

        orb_percentage = data.get(ORB_PERCENTAGE, DEFAULT_ORB_PERCENTAGE)

        low_detail = data.get(LOW_DETAIL, DEFAULT_LOW_DETAIL)
        low_detail_toggled = data.get(LOW_DETAIL_TOGGLED, DEFAULT_LOW_DETAIL_TOGGLED)

        timely_id = data.get(TIMELY_ID, DEFAULT_ID)

        gauntlet = data.get(GAUNTLET, DEFAULT_GAUNTLET)

        unlisted = data.get(UNLISTED, DEFAULT_UNLISTED)

        editor_seconds = data.get(EDITOR_SECONDS)

        if editor_seconds is None:
            editor_time = Duration()

        else:
            editor_time = Duration(seconds=editor_seconds)

        copies_seconds = data.get(EDITOR_SECONDS)

        if copies_seconds is None:
            copies_time = Duration()

        else:
            copies_time = Duration(seconds=copies_seconds)

        favorite = data.get(FAVORITE, DEFAULT_FAVORITE)

        level_order = data.get(LEVEL_ORDER, DEFAULT_LEVEL_ORDER)

        folder_id = data.get(FOLDER_ID, DEFAULT_ID)

        best_clicks = data.get(BEST_CLICKS, DEFAULT_CLICKS)

        best_seconds = data.get(BEST_SECONDS)

        if best_seconds is None:
            best_time = Duration()

        else:
            best_time = Duration(seconds=best_seconds)

        progress_string = data.get(PROGRESS)

        if progress_string is None:
            progress = Progress()

        else:
            progress = Progress.from_robtop(progress_string)

        leaderboard_record = data.get(LEADERBOARD_RECORD, DEFAULT_RECORD)

        return cls(
            id=id,
            name=name,
            creator=creator,
            song=song,
            description=description,
            unprocessed_data=unprocessed_data,
            difficulty=difficulty,
            downloads=downloads,
            completions=completions,
            editable=editable,
            verified=verified,
            uploaded=uploaded,
            version=version,
            game_version=game_version,
            binary_version=binary_version,
            attempts=attempts,
            jumps=jumps,
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
            high_object_count=high_object_count,
            collected_coins=collected_coins,
            coins=coins,
            verified_coins=verified_coins,
            requested_stars=requested_stars,
            orb_percentage=orb_percentage,
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

    def to_robtop_data(self) -> Dict[str, Any]:
        difficulty_parameters = DifficultyParameters.from_difficulty(self.difficulty)

        data = {
            INTERNAL_TYPE: InternalType.LEVEL.value,
            ID: self.id,
            NAME: self.name,
            DESCRIPTION: encode_base64_string_url_safe(self.description),
            DATA: self.unprocessed_data,
            CREATOR_NAME: self.creator.name,
            CREATOR_ID: self.creator.id,
            CREATOR_ACCOUNT_ID: self.creator.account_id,
            DIFFICULTY_DENOMINATOR: difficulty_parameters.difficulty_denominator,
            DIFFICULTY_NUMERATOR: difficulty_parameters.difficulty_numerator,
            DOWNLOADS: self.downloads,
            COMPLETIONS: self.completions,
            LEVEL_VERSION: self.version,
            GAME_VERSION: self.game_version.to_robtop_value(),
            BINARY_VERSION: self.binary_version.to_value(),
            ATTEMPTS: self.attempts,
            JUMPS: self.jumps,
            NORMAL_RECORD: self.normal_record,
            PRACTICE_RECORD: self.practice_record,
            TYPE: self.type.value,
            RATING: self.rating,
            LENGTH: self.length.value,
            STARS: self.stars,
            SCORE: self.score,
            ORIGINAL_ID: self.original_id,
            OBJECT_COUNT: self.object_count,
            COINS: self.coins,
            REQUESTED_STARS: self.requested_stars,
            ORB_PERCENTAGE: self.orb_percentage,
            TIMELY_ID: self.timely_id,
            EDITOR_SECONDS: int(self.editor_time.total_seconds()),
            COPIES_SECONDS: int(self.copies_time.total_seconds()),
            LEVEL_ORDER: self.level_order,
            FOLDER_ID: self.folder_id,
            BEST_CLICKS: self.best_clicks,
            BEST_SECONDS: int(self.best_time.total_seconds()),
            LEADERBOARD_RECORD: self.leaderboard_record,
        }

        song = self.song

        if song.is_custom():
            data[SONG_ID] = song.id

        else:
            data[OFFICIAL_SONG_ID] = song.id

        # false values have to be ignored either way, so only set if true here

        auto = difficulty_parameters.is_auto()

        if auto:
            data[AUTO] = auto

        demon = difficulty_parameters.is_demon()

        if demon:
            data[DEMON] = demon

            demon_difficulty_value = difficulty_parameters.demon_difficulty_value

            if demon_difficulty_value:
                data[DEMON_DIFFICULTY] = demon_difficulty_value

        editable = self.is_editable()

        if editable:
            data[EDITABLE] = editable

        verified = self.is_verified()

        if verified:
            data[VERIFIED] = verified

        uploaded = self.is_uploaded()

        if uploaded:
            data[UPLOADED] = uploaded

        epic = self.rate_type.is_epic()

        if epic:
            data[EPIC] = epic

        playable = self.is_playable()

        if playable:
            data[PLAYABLE] = playable

        unlocked = self.is_unlocked()

        if unlocked:
            data[UNLOCKED] = unlocked

        if self.is_copyable():
            data[PASSWORD] = self.password_data.to_robtop_value()

        two_player = self.is_two_player()

        if two_player:
            data[TWO_PLAYER] = two_player

        high_object_count = self.has_high_object_count()

        if high_object_count:
            data[HIGH_OBJECT_COUNT] = high_object_count

        collected_coins = self.collected_coins

        first_coin = collected_coins.first()

        if first_coin:
            data[FIRST_COIN] = first_coin

        second_coin = collected_coins.second()

        if second_coin:
            data[SECOND_COIN] = second_coin

        third_coin = collected_coins.third()

        if third_coin:
            data[THIRD_COIN] = third_coin

        verified_coins = self.has_verified_coins()

        if verified_coins:
            data[VERIFIED_COINS] = verified_coins

        low_detail = self.has_low_detail()

        if low_detail:
            data[LOW_DETAIL] = low_detail

        low_detail_toggled = self.is_low_detail_toggled()

        if low_detail_toggled:
            data[LOW_DETAIL_TOGGLED] = low_detail_toggled

        gauntlet = self.is_gauntlet()

        if gauntlet:
            data[GAUNTLET] = gauntlet

        unlisted = self.is_unlisted()

        if unlisted:
            data[UNLISTED] = unlisted

        favorite = self.is_favorite()

        if favorite:
            data[FAVORITE] = favorite

        progress_string = self.progress.to_robtop()

        if progress_string:
            data[PROGRESS] = progress_string

        recording_string = self.recording.to_robtop()

        if recording_string:
            data[RECORDING] = zip_level_string(recording_string)

        return data

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
        high_object_count_bit = HIGH_OBJECT_COUNT_BIT

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
        high_object_count = value & high_object_count_bit == high_object_count_bit

        downloads = reader.read_u32(order)

        completions = reader.read_u16(order)

        version = reader.read_u8(order)

        game_version = GameVersion.from_binary(binary, order, version)
        binary_version = Version.from_binary(binary, order, version)

        attempts = reader.read_u32(order)
        jumps = reader.read_u32(order)

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

        orb_percentage = reader.read_u8(order)

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

        level = cls(
            id=id,
            name=name,
            creator=creator,
            song=song,
            description=description,
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
            jumps=jumps,
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
            high_object_count=high_object_count,
            collected_coins=collected_coins,
            coins=coins,
            verified_coins=verified_coins,
            requested_stars=requested_stars,
            orb_percentage=orb_percentage,
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

        level.data = data

        return level

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

        if self.has_high_object_count():
            value |= HIGH_OBJECT_COUNT_BIT

        writer.write_u8(value, order)

        writer.write_u32(self.downloads, order)

        writer.write_u16(self.completions, order)

        writer.write_u8(self.version, order)

        self.game_version.to_binary(binary, order, version)
        self.binary_version.to_binary(binary, order, version)

        writer.write_u32(self.attempts, order)
        writer.write_u32(self.jumps, order)

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

        writer.write_u8(self.orb_percentage, order)

        writer.write_u32(self.timely_id, order)

        writer.write_f32(self.editor_time.total_seconds(), order)
        writer.write_f32(self.copies_time.total_seconds(), order)

        writer.write_u16(self.level_order, order)

        writer.write_u8(self.folder_id, order)

        writer.write_u16(self.best_clicks, order)
        writer.write_f32(self.best_time.total_seconds(), order)

        self.progress.to_binary(binary, order, version)

        writer.write_u8(self.leaderboard_record, order)

    @property
    def password(self) -> Optional[int]:
        return self.password_data.password

    def is_copyable(self) -> bool:
        return self.password_data.is_copyable()

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

    def has_high_object_count(self) -> bool:
        return self.high_object_count
