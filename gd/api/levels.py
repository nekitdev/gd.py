from typing import Any, ClassVar, Optional

from attrs import define, field
from funcs.primitives import decrement, increment
from pendulum import Duration, duration
from typing_aliases import StringDict
from typing_extensions import Self

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
    DEFAULT_DEMON,
    DEFAULT_DENOMINATOR,
    DEFAULT_DOWNLOADS,
    DEFAULT_FAVORITE,
    DEFAULT_HIDDEN,
    DEFAULT_HIGH_OBJECT_COUNT,
    DEFAULT_ID,
    DEFAULT_JUMPS,
    DEFAULT_LOW_DETAIL,
    DEFAULT_LOW_DETAIL_TOGGLED,
    DEFAULT_NUMERATOR,
    DEFAULT_OBJECT_COUNT,
    DEFAULT_ORB_PERCENTAGE,
    DEFAULT_ORDER,
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
from gd.date_time import duration_from_seconds
from gd.decorators import cache_by
from gd.difficulty_parameters import (
    DEFAULT_DEMON_DIFFICULTY_VALUE,
    DifficultyParameters,
)
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
    SpecialRateType,
    TimelyType,
)
from gd.password import Password
from gd.progress import Progress
from gd.robtop_view import StringRobTopView
from gd.songs import SongReference
from gd.users import UserReference
from gd.versions import (
    CURRENT_BINARY_VERSION,
    CURRENT_GAME_VERSION,
    GameVersion,
    RobTopVersion,
)

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
VERSION = "k16"
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
SPECIAL_RATE_TYPE = "k75"
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
ORDER = "k83"
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
    def default(cls, id: int = DEFAULT_ID, name: str = EMPTY) -> Self:
        return cls(id=id, name=name)

    def compute_leaderboard_seed(self) -> int:
        return generate_leaderboard_seed(
            self.best_clicks,
            self.leaderboard_record,
            round(self.best_time.total_seconds()),
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
    def from_robtop_view(cls, view: StringRobTopView[Any]) -> Self:
        id = view.get_option(ID).unwrap_or(DEFAULT_ID)

        name = view.get_option(NAME).unwrap_or(EMPTY)

        version = view.get_option(VERSION).unwrap_or(DEFAULT_VERSION)

        attempts = view.get_option(ATTEMPTS).unwrap_or(DEFAULT_ATTEMPTS)

        normal_record = view.get_option(NORMAL_RECORD).unwrap_or(DEFAULT_RECORD)
        practice_record = view.get_option(PRACTICE_RECORD).unwrap_or(DEFAULT_RECORD)

        stars = view.get_option(STARS).unwrap_or(DEFAULT_STARS)

        jumps = view.get_option(JUMPS).unwrap_or(DEFAULT_JUMPS)

        binary_version = (
            view.get_option(BINARY_VERSION)
            .map(RobTopVersion.from_value)
            .unwrap_or(CURRENT_BINARY_VERSION)
        )

        coins = view.get_option(COINS).unwrap_or(DEFAULT_COINS)

        capacity = view.get_option(CAPACITY).map(Capacity.from_robtop).unwrap_or_else(Capacity)

        orb_percentage = view.get_option(ORB_PERCENTAGE).unwrap_or(DEFAULT_ORB_PERCENTAGE)

        best_clicks = view.get_option(BEST_CLICKS).unwrap_or(DEFAULT_CLICKS)
        best_time = (
            view.get_option(BEST_SECONDS).map(duration_from_seconds).unwrap_or_else(duration)
        )

        progress = view.get_option(PROGRESS).map(Progress.from_robtop).unwrap_or_else(Progress)

        check = view.get_option(CHECK).unwrap_or(DEFAULT_CHECK)

        leaderboard_record = view.get_option(LEADERBOARD_RECORD).unwrap_or(DEFAULT_RECORD)

        return cls(
            id=id,
            name=name,
            version=version,
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
        data = {
            INTERNAL_TYPE: InternalType.LEVEL.value,
            TYPE: self.TYPE.value,
            ID: self.id,
            NAME: self.name,
            VERSION: self.version,
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
            CHECK: self.is_check(),
            LEADERBOARD_RECORD: self.leaderboard_record,
            LEADERBOARD_SEED: self.leaderboard_seed,
        }

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
    def from_robtop_view(cls, view: StringRobTopView[Any]) -> Self:
        level = super().from_robtop_view(view)

        direct_difficulty_value = view.get_option(DIRECT_DIFFICULTY).extract()

        if direct_difficulty_value is None:
            difficulty = Difficulty.DEFAULT

        else:
            demon = view.get_option(DEMON).unwrap_or(DEFAULT_DEMON)

            if demon:
                demon_difficulty_value = view.get_option(DEMON_DIFFICULTY).extract()

                if demon_difficulty_value is None:
                    difficulty = Difficulty.DEMON  # unspecified demon

                else:
                    difficulty = DifficultyParameters(
                        demon_difficulty_value=demon_difficulty_value, demon=demon
                    ).into_difficulty()

            else:
                difficulty = Difficulty(increment(direct_difficulty_value))

        required_coins = view.get_option(REQUIRED_COINS).unwrap_or(DEFAULT_COINS)

        level.difficulty = difficulty

        level.required_coins = required_coins

        return level

    def to_robtop_data(self) -> StringDict[Any]:
        data = super().to_robtop_data()

        difficulty = self.difficulty

        difficulty_parameters = DifficultyParameters.from_difficulty(difficulty)

        here = {
            # difficulty parameters
            DIRECT_DIFFICULTY: decrement(difficulty.clamp_demon().value),  # convert back
            AUTO: difficulty_parameters.is_auto(),
            DEMON: difficulty_parameters.is_demon(),
            DEMON_DIFFICULTY: difficulty_parameters.demon_difficulty_value,
            # others
            REQUIRED_COINS: self.required_coins,
        }

        data.update(here)

        return data


@define()
class CustomLevelAPI(BaseLevelAPI):
    song: SongReference = field(factory=SongReference.default)
    creator: UserReference = field(factory=UserReference.default)

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
    order: int = field(default=DEFAULT_ORDER)
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
    def from_robtop_view(cls, view: StringRobTopView[Any]) -> Self:
        level = super().from_robtop_view(view)

        official_song_id = view.get_option(OFFICIAL_SONG_ID).extract()

        if official_song_id is None:
            song_id = view.get_option(SONG_ID).unwrap_or(DEFAULT_ID)

            song = SongReference(id=song_id, custom=True)

        else:
            song = SongReference(id=official_song_id, custom=False)

        creator_id = view.get_option(CREATOR_ID).unwrap_or(DEFAULT_ID)
        creator_name = view.get_option(CREATOR_NAME).unwrap_or(EMPTY)
        creator_account_id = view.get_option(CREATOR_ACCOUNT_ID).unwrap_or(DEFAULT_ID)

        creator = UserReference(id=creator_id, name=creator_name, account_id=creator_account_id)

        description = (
            view.get_option(DESCRIPTION).map(decode_base64_string_url_safe).unwrap_or(EMPTY)
        )

        unprocessed_data = view.get_option(DATA).unwrap_or(EMPTY)

        if Editor.can_be_in(unprocessed_data):
            unprocessed_data = zip_level_string(unprocessed_data)

        length = view.get_option(LENGTH).map(LevelLength).unwrap_or(LevelLength.DEFAULT)

        password = (
            view.get_option(PASSWORD).map(Password.from_robtop_value).unwrap_or_else(Password)
        )

        original_id = view.get_option(ORIGINAL_ID).unwrap_or(DEFAULT_ID)

        two_player = view.get_option(TWO_PLAYER).unwrap_or(DEFAULT_TWO_PLAYER)

        object_count = view.get_option(OBJECT_COUNT).unwrap_or(DEFAULT_OBJECT_COUNT)

        high_object_count = view.get_option(HIGH_OBJECT_COUNT).unwrap_or(DEFAULT_HIGH_OBJECT_COUNT)

        requested_stars = view.get_option(REQUESTED_STARS).unwrap_or(DEFAULT_STARS)

        low_detail = view.get_option(LOW_DETAIL).unwrap_or(DEFAULT_LOW_DETAIL)
        low_detail_toggled = view.get_option(LOW_DETAIL_TOGGLED).unwrap_or(
            DEFAULT_LOW_DETAIL_TOGGLED
        )

        editor_time = (
            view.get_option(EDITOR_SECONDS).map(duration_from_seconds).unwrap_or_else(duration)
        )
        copies_time = (
            view.get_option(COPIES_SECONDS).map(duration_from_seconds).unwrap_or_else(duration)
        )

        order = view.get_option(ORDER).unwrap_or(DEFAULT_ORDER)

        folder_id = view.get_option(FOLDER_ID).unwrap_or(DEFAULT_ID)

        level.song = song

        level.creator = creator

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

        level.order = order

        level.folder_id = folder_id

        return level

    def to_robtop_data(self) -> StringDict[Any]:
        data = super().to_robtop_data()

        creator = self.creator

        here = {
            CREATOR_ID: creator.id,
            CREATOR_NAME: creator.name,
            CREATOR_ACCOUNT_ID: creator.account_id,
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
            EDITOR_SECONDS: round(self.editor_time.total_seconds()),
            COPIES_SECONDS: round(self.copies_time.total_seconds()),
            ORDER: self.order,
            FOLDER_ID: self.folder_id,
        }

        data.update(here)

        song = self.song

        if song.is_custom():
            data[SONG_ID] = song.id

        else:
            data[OFFICIAL_SONG_ID] = song.id

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
    def from_robtop_view(cls, view: StringRobTopView[Any]) -> Self:
        level = super().from_robtop_view(view)

        revision = view.get_option(REVISION).unwrap_or(DEFAULT_REVISION)

        verified = view.get_option(VERIFIED).unwrap_or(DEFAULT_VERIFIED)

        uploaded = view.get_option(UPLOADED).unwrap_or(DEFAULT_UPLOADED)

        recording = view.get_option(RECORDING).map(Recording.from_robtop).unwrap_or_else(Recording)

        first_coin = view.get_option(FIRST_COIN).unwrap_or(DEFAULT_COLLECTED)
        second_coin = view.get_option(SECOND_COIN).unwrap_or(DEFAULT_COLLECTED)
        third_coin = view.get_option(THIRD_COIN).unwrap_or(DEFAULT_COLLECTED)

        collected_coins = CollectedCoins.NONE

        if first_coin:
            collected_coins |= CollectedCoins.FIRST

        if second_coin:
            collected_coins |= CollectedCoins.SECOND

        if third_coin:
            collected_coins |= CollectedCoins.THIRD

        unlisted = view.get_option(UNLISTED).unwrap_or(DEFAULT_UNLISTED)

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
    def from_robtop_view(cls, view: StringRobTopView[Any]) -> Self:
        level = super().from_robtop_view(view)

        difficulty_numerator = view.get_option(DIFFICULTY_NUMERATOR).unwrap_or(DEFAULT_NUMERATOR)
        difficulty_denominator = view.get_option(DIFFICULTY_DENOMINATOR).unwrap_or(
            DEFAULT_DENOMINATOR
        )

        demon_difficulty_value = view.get_option(DEMON_DIFFICULTY).unwrap_or(
            DEFAULT_DEMON_DIFFICULTY_VALUE
        )

        auto = view.get_option(AUTO).unwrap_or(DEFAULT_AUTO)
        demon = view.get_option(DEMON).unwrap_or(DEFAULT_DEMON)

        difficulty_parameters = DifficultyParameters(
            difficulty_numerator=difficulty_numerator,
            difficulty_denominator=difficulty_denominator,
            demon_difficulty_value=demon_difficulty_value,
            auto=auto,
            demon=demon,
        )

        difficulty = difficulty_parameters.into_difficulty()

        downloads = view.get_option(DOWNLOADS).unwrap_or(DEFAULT_DOWNLOADS)

        game_version = (
            view.get_option(GAME_VERSION)
            .map(GameVersion.from_robtop_value)
            .unwrap_or(CURRENT_GAME_VERSION)
        )

        rating = view.get_option(RATING).unwrap_or(DEFAULT_RATING)

        stars = view.get_option(STARS).unwrap_or(DEFAULT_STARS)

        rate_type = RateType.NOT_RATED

        if stars > 0:
            rate_type = RateType.RATED

        score = view.get_option(SCORE).unwrap_or(DEFAULT_SCORE)

        if score < 0:
            score = 0

        if score > 0:
            rate_type = RateType.FEATURED

        special_rate_type = (
            view.get_option(SPECIAL_RATE_TYPE)
            .map(SpecialRateType)
            .unwrap_or(SpecialRateType.DEFAULT)
        )

        if special_rate_type.is_epic():
            rate_type = RateType.EPIC

        if special_rate_type.is_legendary():
            rate_type = RateType.LEGENDARY

        if special_rate_type.is_mythic():
            rate_type = RateType.MYTHIC

        hidden = view.get_option(HIDDEN).unwrap_or(DEFAULT_HIDDEN)

        verified_coins = view.get_option(VERIFIED_COINS).unwrap_or(DEFAULT_VERIFIED_COINS)

        favorite = view.get_option(FAVORITE).unwrap_or(DEFAULT_FAVORITE)

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

        rate_type = self.rate_type

        special_rate_type = SpecialRateType.NONE

        if rate_type.is_epic():
            special_rate_type = SpecialRateType.EPIC

        if rate_type.is_legendary():
            special_rate_type = SpecialRateType.LEGENDARY

        if rate_type.is_mythic():
            special_rate_type = SpecialRateType.MYTHIC

        here = {
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
            SPECIAL_RATE_TYPE: special_rate_type.value,
            HIDDEN: self.is_hidden(),
            VERIFIED_COINS: self.has_verified_coins(),
            FAVORITE: self.is_favorite(),
        }

        data.update(here)

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
    def from_robtop_view(cls, view: StringRobTopView[Any]) -> Self:
        level = super().from_robtop_view(view)

        timely_id = view.get_option(TIMELY_ID).unwrap_or(DEFAULT_ID)

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
