from typing import Any, ClassVar, Optional

from attrs import define, field
from pendulum import Duration, duration
from typing_aliases import StringDict, StringMapping

from gd.api.editor import Editor
from gd.api.recording import Recording
from gd.capacity import Capacity
from gd.constants import (
    DEFAULT_ATTEMPTS,
    DEFAULT_AUTO,
    DEFAULT_CHECK,
    DEFAULT_CLICKS,
    DEFAULT_COINS,
    DEFAULT_COLLECTED,
    DEFAULT_CUSTOM,
    DEFAULT_DEMON,
    DEFAULT_DENOMINATOR,
    DEFAULT_DOWNLOADS,
    DEFAULT_FAVORITE,
    DEFAULT_HIDDEN,
    DEFAULT_HIGH_OBJECT_COUNT,
    DEFAULT_ID,
    DEFAULT_JUMPS,
    DEFAULT_LEVEL_ORDER,
    DEFAULT_LOW_DETAIL,
    DEFAULT_LOW_DETAIL_TOGGLED,
    DEFAULT_NUMERATOR,
    DEFAULT_OBJECT_COUNT,
    DEFAULT_ORB_PERCENTAGE,
    DEFAULT_PASSWORD,
    DEFAULT_RATING,
    DEFAULT_RECORD,
    DEFAULT_REVISION,
    DEFAULT_SCORE,
    DEFAULT_STARS,
    DEFAULT_TWO_PLAYER,
    DEFAULT_UNLISTED,
    DEFAULT_UPLOADED,
    DEFAULT_VERIFIED,
    DEFAULT_VERIFIED_COINS,
    DEFAULT_VERSION,
    EMPTY,
    WEEKLY_ID_ADD,
)
from gd.decorators import cache_by
from gd.difficulty_parameters import DEFAULT_DEMON_DIFFICULTY_VALUE, DifficultyParameters
from gd.encoding import (
    decode_base64_string_url_safe,
    encode_base64_string_url_safe,
    generate_leaderboard_seed,
    unzip_level_string,
    zip_level_string,
)
from gd.enums import (
    CollectedCoins,
    Difficulty,
    InternalType,
    LevelLength,
    LevelType,
    RateType,
    TimelyType,
)
from gd.models_constants import OBJECTS_SEPARATOR
from gd.password import Password
from gd.progress import Progress
from gd.songs import SongReference
from gd.users import User, UserReference
from gd.versions import CURRENT_BINARY_VERSION, CURRENT_GAME_VERSION, GameVersion, RobTopVersion
from typing_extensions import Self


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
DIRECT_DIFFICULTY = "k7"
DIFFICULTY_DENOMINATOR = "k9"
DIFFICULTY_NUMERATOR = "k10"
AUTO = "k33"
DEMON = "k25"
DEMON_DIFFICULTY = "k76"
DOWNLOADS = "k11"
VERIFIED = "k14"
UPLOADED = "k15"
LEVEL_VERSION = "k16"
REVISION = "k46"
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
HIDDEN = "k35"
REQUIRED_COINS = "k37"
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
CAPACITY = "k67"
HIGH_OBJECT_COUNT = "k69"
ORB_PERCENTAGE = "k71"
LOW_DETAIL = "k72"
LOW_DETAIL_TOGGLED = "k73"
TIMELY_ID = "k74"
GAUNTLET = "k77"
NON_MAIN = "k78"  # XXX: needs more research
UNLISTED = "k79"
EDITOR_SECONDS = "k80"
COPIES_SECONDS = "k81"
FAVORITE = "k82"
LEVEL_ORDER = "k83"
FOLDER_ID = "k84"
BEST_CLICKS = "k85"
BEST_SECONDS = "k86"
PROGRESS = "k88"
CHECK = "k89"
LEADERBOARD_RECORD = "k90"
LEADERBOARD_SEED = "k87"

DEFAULT_EPIC = False

UNPROCESSED_DATA = "unprocessed_data"


@define()
class BaseLevelAPI:
    TYPE: ClassVar[LevelType] = LevelType.DEFAULT

    id: int = field()
    name: str = field()
    song_reference: SongReference = field()
    creator: UserReference = field()
    version: int = field(default=DEFAULT_VERSION)
    attempts: int = field(default=DEFAULT_ATTEMPTS)
    normal_record: int = field(default=DEFAULT_RECORD)
    practice_record: int = field(default=DEFAULT_RECORD)
    stars: int = field(default=DEFAULT_STARS)
    jumps: int = field(default=DEFAULT_JUMPS)
    binary_version: RobTopVersion = field(default=CURRENT_BINARY_VERSION)
    coins: int = field(default=DEFAULT_COINS)
    capacity: Capacity = field(factory=Capacity)
    orb_percentage: int = field(default=DEFAULT_ORB_PERCENTAGE)
    best_clicks: int = field(default=DEFAULT_CLICKS)
    best_time: Duration = field(factory=duration)
    progress: Progress = field(factory=Progress)
    check: bool = field(default=DEFAULT_CHECK)
    leaderboard_record: int = field(default=DEFAULT_RECORD)
    leaderboard_seed: int = field()  # computed automatically

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

    @classmethod
    def default(
        cls,
        id: int = DEFAULT_ID,
        song_id: int = DEFAULT_ID,
        song_custom: bool = DEFAULT_CUSTOM,
        creator_id: int = DEFAULT_ID,
        creator_account_id: int = DEFAULT_ID,
    ) -> Self:
        return cls(
            id=id,
            name=EMPTY,
            song_reference=SongReference.default(song_id, song_custom),
            creator=UserReference.default(creator_id, creator_account_id),
        )

    def compute_leaderboard_seed(self) -> int:
        return generate_leaderboard_seed(
            self.best_clicks,
            self.leaderboard_record,
            int(self.best_time.total_seconds()),
        )

    @leaderboard_seed.default
    def default_leaderboard_seed(self) -> int:
        return self.compute_leaderboard_seed()

    def refresh_leaderboard_seed(self) -> Self:
        self.leaderboard_seed = self.compute_leaderboard_seed()

        return self

    def is_check(self) -> bool:
        return self.check

    @classmethod
    def from_robtop_data(cls, data: StringMapping[Any]) -> Self:
        id = data.get(ID, DEFAULT_ID)

        name = data.get(NAME, EMPTY)

        official_song_id = data.get(OFFICIAL_SONG_ID, DEFAULT_ID)

        if official_song_id:
            song_reference = SongReference(official_song_id, custom=False)

        else:
            song_id = data.get(SONG_ID, DEFAULT_ID)

            song_reference = SongReference(song_id, custom=True)

        creator_id = data.get(CREATOR_ID, DEFAULT_ID)
        creator_name = data.get(CREATOR_NAME, EMPTY)
        creator_account_id = data.get(CREATOR_ACCOUNT_ID, DEFAULT_ID)

        creator = User(creator_id, creator_name, creator_account_id)

        level_version = data.get(LEVEL_VERSION, DEFAULT_VERSION)

        attempts = data.get(ATTEMPTS, DEFAULT_ATTEMPTS)

        normal_record = data.get(NORMAL_RECORD, DEFAULT_RECORD)
        practice_record = data.get(PRACTICE_RECORD, DEFAULT_RECORD)

        stars = data.get(STARS, DEFAULT_STARS)

        jumps = data.get(JUMPS, DEFAULT_JUMPS)

        binary_version_option = data.get(BINARY_VERSION)

        if binary_version_option is None:
            binary_version = CURRENT_BINARY_VERSION

        else:
            binary_version = RobTopVersion.from_value(binary_version_option)

        coins = data.get(COINS, DEFAULT_COINS)

        capacity_option = data.get(CAPACITY)

        if capacity_option is None:
            capacity = Capacity()

        else:
            capacity = Capacity.from_robtop(capacity_option)

        orb_percentage = data.get(ORB_PERCENTAGE, DEFAULT_ORB_PERCENTAGE)

        best_clicks = data.get(BEST_CLICKS, DEFAULT_CLICKS)

        best_option = data.get(BEST_SECONDS)

        if best_option is None:
            best_time = duration()

        else:
            best_time = duration(seconds=best_option)

        progress_option = data.get(PROGRESS)

        if progress_option is None:
            progress = Progress()

        else:
            progress = Progress.from_robtop(progress_option)

        check = data.get(CHECK, DEFAULT_CHECK)

        leaderboard_record = data.get(LEADERBOARD_RECORD, DEFAULT_RECORD)

        return cls(
            id=id,
            name=name,
            song_reference=song_reference,
            creator=creator,
            version=level_version,
            attempts=attempts,
            normal_record=normal_record,
            practice_record=practice_record,
            stars=stars,
            jumps=jumps,
            binary_version=binary_version,
            coins=coins,
            capacity=capacity,
            orb_percentage=orb_percentage,
            best_clicks=best_clicks,
            best_time=best_time,
            progress=progress,
            check=check,
            leaderboard_record=leaderboard_record,
        )

    def to_robtop_data(self) -> StringDict[Any]:
        creator = self.creator

        data = {
            INTERNAL_TYPE: InternalType.LEVEL.value,
            TYPE: self.TYPE.value,
            ID: self.id,
            NAME: self.name,
            CREATOR_ID: creator.id,
            CREATOR_NAME: creator.name,
            CREATOR_ACCOUNT_ID: creator.account_id,
            LEVEL_VERSION: self.version,
            ATTEMPTS: self.attempts,
            NORMAL_RECORD: self.normal_record,
            PRACTICE_RECORD: self.practice_record,
            STARS: self.stars,
            JUMPS: self.jumps,
            BINARY_VERSION: self.binary_version.to_value(),
            COINS: self.coins,
            CAPACITY: self.capacity.to_robtop(),
            ORB_PERCENTAGE: self.orb_percentage,
            BEST_CLICKS: self.best_clicks,
            BEST_SECONDS: int(self.best_time.total_seconds()),
            PROGRESS: self.progress.to_robtop(),
            CHECK: self.check,
            LEADERBOARD_RECORD: self.leaderboard_record,
            LEADERBOARD_SEED: self.leaderboard_seed,
        }

        song_reference = self.song_reference
        song_id = song_reference.id

        if song_reference.is_custom():
            data[SONG_ID] = song_id

        else:
            data[OFFICIAL_SONG_ID] = song_id

        return data


@define()
class OfficialLevelAPI(BaseLevelAPI):
    TYPE: ClassVar[LevelType] = LevelType.OFFICIAL

    difficulty: Difficulty = field(default=Difficulty.DEFAULT)
    required_coins: int = field(default=DEFAULT_COINS)

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

    def is_demon(self) -> bool:
        return self.difficulty.is_demon()

    @classmethod
    def from_robtop_data(cls, data: StringMapping[Any]) -> Self:
        level = super().from_robtop_data(data)

        direct_difficulty_option = data.get(DIRECT_DIFFICULTY)

        if direct_difficulty_option is None:
            difficulty = Difficulty.DEFAULT

        else:
            demon = data.get(DEMON, DEFAULT_DEMON)

            if demon:
                demon_difficulty_option = data.get(DEMON_DIFFICULTY)

                if demon_difficulty_option is None:
                    difficulty = Difficulty.DEMON  # unspecified demon

                else:
                    difficulty = DifficultyParameters(
                        demon_difficulty_value=demon_difficulty_option, demon=demon
                    ).into_difficulty()

            else:
                difficulty = Difficulty(direct_difficulty_option + 1)  # funky way to convert

        required_coins = data.get(REQUIRED_COINS, DEFAULT_COINS)

        level.difficulty = difficulty

        level.required_coins = required_coins

        return level

    def to_robtop_data(self) -> StringDict[Any]:
        data = super().to_robtop_data()

        difficulty = self.difficulty

        difficulty_parameters = DifficultyParameters.from_difficulty(difficulty)

        actual = {
            # difficulty parameters
            DIRECT_DIFFICULTY: difficulty.clamp_demon().value - 1,  # convert back
            AUTO: difficulty_parameters.is_auto(),
            DEMON: difficulty_parameters.is_demon(),
            DEMON_DIFFICULTY: difficulty_parameters.demon_difficulty_value,
            # others
            REQUIRED_COINS: self.required_coins,
        }

        data.update(actual)

        return data


DEFAULT_LENGTH_VALUE = LevelLength.DEFAULT.value


@define()
class CustomLevelAPI(BaseLevelAPI):
    description: str = field(default=EMPTY)
    unprocessed_data: str = field(default=EMPTY, repr=False)
    length: LevelLength = field(default=LevelLength.DEFAULT)
    password: Password = field(factory=Password)
    original_id: int = field(default=DEFAULT_ID)
    two_player: bool = field(default=DEFAULT_TWO_PLAYER)
    object_count: int = field(default=DEFAULT_OBJECT_COUNT)
    high_object_count: bool = field(default=DEFAULT_HIGH_OBJECT_COUNT)
    requested_stars: int = field(default=DEFAULT_STARS)
    low_detail: bool = field(default=DEFAULT_LOW_DETAIL)
    low_detail_toggled: bool = field(default=DEFAULT_LOW_DETAIL_TOGGLED)
    editor_time: Duration = field(factory=duration)
    copies_time: Duration = field(factory=duration)
    level_order: int = field(default=DEFAULT_LEVEL_ORDER)
    folder_id: int = field(default=DEFAULT_ID)

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

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

    def is_original(self) -> bool:
        return not self.original_id

    def is_two_player(self) -> bool:
        return self.two_player

    def has_high_object_count(self) -> bool:
        return self.high_object_count

    def has_low_detail(self) -> bool:
        return self.low_detail

    def has_low_detail_toggled(self) -> bool:
        return self.low_detail_toggled

    @classmethod
    def from_robtop_data(cls, data: StringMapping[Any]) -> Self:
        level = super().from_robtop_data(data)

        description = decode_base64_string_url_safe(data.get(DESCRIPTION, EMPTY))

        unprocessed_data = data.get(DATA, EMPTY)

        if OBJECTS_SEPARATOR in unprocessed_data:
            unprocessed_data = zip_level_string(unprocessed_data)

        length_value = data.get(LENGTH, DEFAULT_LENGTH_VALUE)

        length = LevelLength(length_value)

        password_value = data.get(PASSWORD, DEFAULT_PASSWORD)

        password = Password.from_robtop_value(password_value)

        original_id = data.get(ORIGINAL_ID, DEFAULT_ID)

        two_player = data.get(TWO_PLAYER, DEFAULT_TWO_PLAYER)

        object_count = data.get(OBJECT_COUNT, DEFAULT_OBJECT_COUNT)

        high_object_count = data.get(HIGH_OBJECT_COUNT, DEFAULT_HIGH_OBJECT_COUNT)

        requested_stars = data.get(REQUESTED_STARS, DEFAULT_STARS)

        low_detail = data.get(LOW_DETAIL, DEFAULT_LOW_DETAIL)
        low_detail_toggled = data.get(LOW_DETAIL_TOGGLED, DEFAULT_LOW_DETAIL_TOGGLED)

        editor_seconds = data.get(EDITOR_SECONDS)

        if editor_seconds is None:
            editor_time = duration()

        else:
            editor_time = duration(seconds=editor_seconds)

        copies_seconds = data.get(COPIES_SECONDS)

        if copies_seconds is None:
            copies_time = duration()

        else:
            copies_time = duration(seconds=copies_seconds)

        level_order = data.get(LEVEL_ORDER, DEFAULT_LEVEL_ORDER)

        folder_id = data.get(FOLDER_ID, DEFAULT_ID)

        level.description = description

        level.unprocessed_data = unprocessed_data

        level.length = length

        level.password = password

        level.original_id = original_id

        level.two_player = two_player

        level.object_count = object_count

        level.high_object_count = high_object_count

        level.requested_stars = requested_stars

        level.low_detail = low_detail
        level.low_detail_toggled = low_detail_toggled

        level.editor_time = editor_time
        level.copies_time = copies_time

        level.level_order = level_order

        level.folder_id = folder_id

        return level

    def to_robtop_data(self) -> StringDict[Any]:
        data = super().to_robtop_data()

        actual = {
            DESCRIPTION: encode_base64_string_url_safe(self.description),
            DATA: self.unprocessed_data,
            LENGTH: self.length.value,
            PASSWORD: self.password.to_robtop_value(),
            ORIGINAL_ID: self.original_id,
            TWO_PLAYER: self.is_two_player(),
            OBJECT_COUNT: self.object_count,
            HIGH_OBJECT_COUNT: self.has_high_object_count(),
            REQUESTED_STARS: self.requested_stars,
            LOW_DETAIL: self.has_low_detail(),
            LOW_DETAIL_TOGGLED: self.has_low_detail_toggled(),
            EDITOR_SECONDS: int(self.editor_time.total_seconds()),
            COPIES_SECONDS: int(self.copies_time.total_seconds()),
            LEVEL_ORDER: self.level_order,
            FOLDER_ID: self.folder_id,
        }

        data.update(actual)

        return data


@define()
class CreatedLevelAPI(CustomLevelAPI):
    TYPE: ClassVar[LevelType] = LevelType.CREATED

    revision: int = field(default=DEFAULT_REVISION)
    verified: bool = field(default=DEFAULT_VERIFIED)
    uploaded: bool = field(default=DEFAULT_UPLOADED)
    recording: Recording = field(factory=Recording, repr=False)
    collected_coins: CollectedCoins = field(default=CollectedCoins.DEFAULT)
    unlisted: bool = field(default=DEFAULT_UNLISTED)

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

    def is_verified(self) -> bool:
        return self.verified

    def is_uploaded(self) -> bool:
        return self.uploaded

    def is_unlisted(self) -> bool:
        return self.unlisted

    @classmethod
    def from_robtop_data(cls, data: StringMapping[Any]) -> Self:
        level = super().from_robtop_data(data)

        revision = data.get(REVISION, DEFAULT_REVISION)

        verified = data.get(VERIFIED, DEFAULT_VERIFIED)

        uploaded = data.get(UPLOADED, DEFAULT_UPLOADED)

        recording_string = data.get(RECORDING, EMPTY)

        recording = Recording.from_robtop(recording_string)

        first_coin = data.get(FIRST_COIN, DEFAULT_COLLECTED)
        second_coin = data.get(SECOND_COIN, DEFAULT_COLLECTED)
        third_coin = data.get(THIRD_COIN, DEFAULT_COLLECTED)

        collected_coins = CollectedCoins.NONE

        if first_coin:
            collected_coins |= CollectedCoins.FIRST

        if second_coin:
            collected_coins |= CollectedCoins.SECOND

        if third_coin:
            collected_coins |= CollectedCoins.THIRD

        unlisted = data.get(UNLISTED, DEFAULT_UNLISTED)

        level.revision = revision

        level.verified = verified
        level.uploaded = uploaded

        level.recording = recording

        level.collected_coins = collected_coins

        level.unlisted = unlisted

        return level

    def to_robtop_data(self) -> StringDict[Any]:
        data = super().to_robtop_data()

        collected_coins = self.collected_coins

        actual = {
            REVISION: self.revision,
            VERIFIED: self.is_verified(),
            UPLOADED: self.is_uploaded(),
            RECORDING: self.recording.to_robtop(),
            FIRST_COIN: collected_coins.first(),
            SECOND_COIN: collected_coins.second(),
            THIRD_COIN: collected_coins.third(),
            UNLISTED: self.is_unlisted(),
        }

        data.update(actual)

        return data


@define()
class SavedLevelAPI(CustomLevelAPI):
    TYPE: ClassVar[LevelType] = LevelType.SAVED

    difficulty: Difficulty = field(default=Difficulty.DEFAULT)
    downloads: int = field(default=DEFAULT_DOWNLOADS)
    game_version: GameVersion = field(default=CURRENT_GAME_VERSION)
    rating: int = field(default=DEFAULT_RATING)
    stars: int = field(default=DEFAULT_STARS)
    score: int = field(default=DEFAULT_SCORE)
    rate_type: RateType = field(default=RateType.DEFAULT)
    hidden: bool = field(default=DEFAULT_HIDDEN)
    verified_coins: bool = field(default=DEFAULT_VERIFIED_COINS)
    favorite: bool = field(default=DEFAULT_FAVORITE)

    @classmethod
    def from_robtop_data(cls, data: StringMapping[Any]) -> Self:
        level = super().from_robtop_data(data)

        difficulty_numerator = data.get(DIFFICULTY_NUMERATOR, DEFAULT_NUMERATOR)

        difficulty_denominator = data.get(DIFFICULTY_DENOMINATOR, DEFAULT_DENOMINATOR)

        demon_difficulty_value = data.get(DEMON_DIFFICULTY, DEFAULT_DEMON_DIFFICULTY_VALUE)

        auto = data.get(AUTO, DEFAULT_AUTO)

        demon = data.get(DEMON, DEFAULT_DEMON)

        difficulty_parameters = DifficultyParameters(
            difficulty_numerator=difficulty_numerator,
            difficulty_denominator=difficulty_denominator,
            demon_difficulty_value=demon_difficulty_value,
            auto=auto,
            demon=demon,
        )

        difficulty = difficulty_parameters.into_difficulty()

        downloads = data.get(DOWNLOADS, DEFAULT_DOWNLOADS)

        game_version_value = data.get(GAME_VERSION)

        if game_version_value is None:
            game_version = CURRENT_GAME_VERSION

        else:
            game_version = GameVersion.from_robtop_value(game_version_value)

        rating = data.get(RATING, DEFAULT_RATING)

        stars = data.get(STARS, DEFAULT_STARS)

        rate_type = RateType.NOT_RATED

        if stars > 0:
            rate_type = RateType.RATED

        score = data.get(SCORE, DEFAULT_SCORE)

        if score < 0:
            score = 0

        if score > 0:
            rate_type = RateType.FEATURED

        epic = data.get(EPIC, DEFAULT_EPIC)

        if epic:
            rate_type = RateType.EPIC

        hidden = data.get(HIDDEN, DEFAULT_HIDDEN)

        verified_coins = data.get(VERIFIED_COINS, DEFAULT_VERIFIED_COINS)

        favorite = data.get(FAVORITE, DEFAULT_FAVORITE)

        level.difficulty = difficulty

        level.downloads = downloads

        level.game_version = game_version

        level.rating = rating

        level.stars = stars

        level.score = score

        level.rate_type = rate_type

        level.hidden = hidden

        level.verified_coins = verified_coins

        level.favorite = favorite

        return level

    def to_robtop_data(self) -> StringDict[Any]:
        data = super().to_robtop_data()

        difficulty_parameters = DifficultyParameters.from_difficulty(self.difficulty)

        actual = {
            # difficulty parameters
            DIFFICULTY_NUMERATOR: difficulty_parameters.difficulty_numerator,
            DIFFICULTY_DENOMINATOR: difficulty_parameters.difficulty_denominator,
            DEMON_DIFFICULTY: difficulty_parameters.demon_difficulty_value,
            AUTO: difficulty_parameters.auto,
            DEMON: difficulty_parameters.demon,
            # others
            DOWNLOADS: self.downloads,
            GAME_VERSION: self.game_version.to_robtop_value(),
            RATING: self.rating,
            STARS: self.stars,
            SCORE: self.score,
            EPIC: self.is_epic(),
            HIDDEN: self.is_hidden(),
            VERIFIED_COINS: self.has_verified_coins(),
            FAVORITE: self.is_favorite(),
        }

        data.update(actual)

        return data

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

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

    def is_demon(self) -> bool:
        return self.difficulty.is_demon()

    def is_hidden(self) -> bool:
        return self.hidden

    def has_verified_coins(self) -> bool:
        return self.verified_coins

    def is_favorite(self) -> bool:
        return self.favorite


@define()
class TimelyLevelAPI(SavedLevelAPI):
    timely_id: int = field(default=DEFAULT_ID)
    timely_type: TimelyType = field(default=TimelyType.DEFAULT)

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

    @classmethod
    def from_robtop_data(cls, data: StringMapping[Any]) -> Self:
        level = super().from_robtop_data(data)

        timely_id = data.get(TIMELY_ID, DEFAULT_ID)

        result, timely_id = divmod(timely_id, WEEKLY_ID_ADD)

        if result:
            timely_type = TimelyType.WEEKLY

        else:
            timely_type = TimelyType.DAILY

        level.timely_id = timely_id
        level.timely_type = timely_type

        return level

    def to_robtop_data(self) -> StringDict[Any]:
        data = super().to_robtop_data()

        timely_id = self.timely_id

        if self.is_weekly():
            timely_id += WEEKLY_ID_ADD

        data[TIMELY_ID] = timely_id

        return data

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


@define()
class GauntletLevelAPI(SavedLevelAPI):
    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

    def to_robtop_data(self) -> StringDict[Any]:
        data = super().to_robtop_data()

        data[GAUNTLET] = True

        return data
