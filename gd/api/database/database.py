from __future__ import annotations

from typing import Any, Dict, Iterable, List, Tuple, Type, TypeVar
from uuid import UUID
from uuid import uuid4 as generate_uuid

from attrs import define, field
from funcs.application import partial
from funcs.unpacking import unpack_binary
from iters.iters import iter
from iters.ordered_set import OrderedSet, ordered_set
from iters.utils import unary_tuple
from typing_aliases import StringDict, StringMapping, is_instance, is_true

from gd.api.database.completed import Completed
from gd.api.database.statistics import Statistics
from gd.api.database.storage import Storage
from gd.api.database.unlock_values import UnlockValues
from gd.api.database.values import Values
from gd.api.folder import Folder
from gd.api.levels import (
    CreatedLevelAPI,
    GauntletLevelAPI,
    OfficialLevelAPI,
    SavedLevelAPI,
    TimelyLevelAPI,
)
from gd.api.like import Like
from gd.api.objects import (
    Object,
    migrate_objects,
    object_from_binary,
    object_from_robtop,
    object_to_binary,
    object_to_robtop,
)
from gd.api.songs import SongAPI
from gd.binary import VERSION, Binary, BinaryReader, BinaryWriter
from gd.binary_utils import Reader, Writer
from gd.constants import (
    DEFAULT_COLOR_1_ID,
    DEFAULT_COLOR_2_ID,
    DEFAULT_ENCODING,
    DEFAULT_ERRORS,
    DEFAULT_GLOW,
    DEFAULT_ICON_ID,
    DEFAULT_ID,
    DEFAULT_PRIORITY,
    DEFAULT_RESOLUTION,
    DEFAULT_ROUNDING,
    EMPTY,
    WEEKLY_ID_ADD,
)
from gd.enums import ByteOrder, IconType, Quality
from gd.filters import Filters
from gd.models_utils import concat_objects, split_objects
from gd.plist import PARSER
from gd.string_utils import password_repr, snake_to_camel, snake_to_camel_with_abbreviations
from gd.versions import CURRENT_BINARY_VERSION, RobTopVersion

SHOW_SONG_MARKERS_BIT = 0b00000001
SHOW_PROGRESS_BAR_BIT = 0b00000010
CLICKED_ICONS_BIT = 0b00000100
CLICKED_EDITOR_BIT = 0b00001000
CLICKED_PRACTICE_BIT = 0b00010000
SHOWN_EDITOR_GUIDE_BIT = 0b00100000
SHOWN_LOW_DETAIL_BIT = 0b01000000
RATED_GAME_BIT = 0b10000000
MODERATOR_BIT = 0b00000001
GLOW_BIT = 0b00000010
QUALITY_MASK = 0b00001100
QUALITY_SHIFT = GLOW_BIT.bit_length()

DEFAULT_VOLUME = 1.0

DEFAULT_SECRET_VALUE = 0
DEFAULT_MODERATOR = False

DEFAULT_SHOW_SONG_MARKERS = True
DEFAULT_SHOW_PROGRESS_BAR = True

DEFAULT_CLICKED_ICONS = True
DEFAULT_CLICKED_EDITOR = True
DEFAULT_CLICKED_PRACTICE = True

DEFAULT_SHOWN_EDITOR_GUIDE = True
DEFAULT_SHOWN_LOW_DETAIL = True

DEFAULT_RATED_GAME = False

DEFAULT_BOOTUPS = 0

VOLUME = snake_to_camel("bg_volume")
SFX_VOLUME = snake_to_camel("sfx_volume")

UUID_LITERAL = snake_to_camel_with_abbreviations("player_udid", unary_tuple("UDID"))  # funny, huh?

PLAYER_NAME = snake_to_camel("player_name")
USER_ID = snake_to_camel_with_abbreviations("player_user_id")

CUBE_ID = snake_to_camel("player_frame")
SHIP_ID = snake_to_camel("player_ship")
BALL_ID = snake_to_camel("player_ball")
UFO_ID = snake_to_camel("player_bird")
WAVE_ID = snake_to_camel("player_dart")
ROBOT_ID = snake_to_camel("player_robot")
SPIDER_ID = snake_to_camel("player_spider")
COLOR_1_ID = snake_to_camel("player_color")
COLOR_2_ID = snake_to_camel("player_color_2")

TRAIL_ID = snake_to_camel("player_streak")

EXPLOSION_ID = snake_to_camel("player_death_effect")

ICON_TYPE = snake_to_camel("player_icon_type")

GLOW = snake_to_camel("player_glow")

SECRET_VALUE = snake_to_camel("secret_number")

MODERATOR = snake_to_camel_with_abbreviations("has_rp", unary_tuple("RP"))

VALUES = snake_to_camel("value_keeper")

UNLOCK_VALUES = snake_to_camel("unlock_value_keeper")

CUSTOM_OBJECTS = snake_to_camel("custom_object_dict")

ACHIEVEMENTS = snake_to_camel("reported_achievements")

SHOW_SONG_MARKERS = snake_to_camel("show_song_markers")
SHOW_PROGRESS_BAR = snake_to_camel("show_progress_bar")

CLICKED_ICONS = snake_to_camel("clicked_garage")
CLICKED_EDITOR = snake_to_camel("clicked_editor")
CLICKED_PRACTICE = snake_to_camel("clicked_practice")

SHOWN_EDITOR_GUIDE = snake_to_camel("showed_editor_guide")
SHOWN_LOW_DETAIL = snake_to_camel("show_low_detail_dialog")

BOOTUPS = snake_to_camel("bootups")

RATED_GAME = snake_to_camel("has_rated_game")

BINARY_VERSION = snake_to_camel("binary_version")

RESOLUTION = snake_to_camel("resolution")

QUALITY = snake_to_camel("tex_quality")

ACHIVEMENTS = snake_to_camel("reported_achievements")

COMPLETED = "GS_completed"
STATISTICS = "GS_value"

NAME = "GJA_001"
PASSWORD = "GJA_002"
ACCOUNT_ID = "GJA_003"
SESSION_ID = "GJA_004"

OFFICIAL_LEVELS = "GLM_01"
SAVED_LEVELS = "GLM_03"
FOLLOWED = "GLM_06"
LAST_PLAYED = "GLM_07"
FILTERS = "GLM_08"  # TODO
AVAILABLE_FILTERS = "GLM_09"  # TODO
TIMELY_LEVELS = "GLM_10"
DAILY_ID = "GLM_11"
LIKED = "GLM_12"
RATED = "GLM_13"
REPORTED = "GLM_14"
DEMON_RATED = "GLM_15"
GAUNTLET_LEVELS = "GLM_16"
WEEKLY_ID = "GLM_17"
SAVED_FOLDERS = "GLM_18"
CREATED_FOLDERS = "GLM_19"

SONGS = "MDLM_001"
PRIORITY = "MDLM_002"

CREATED_LEVELS = "LLM_01"
BINARY_VERSION_LEVELS = "LLM_02"

UUID_SIZE = 16

ONE = str(1)

IS_ARRAY = snake_to_camel("_is_arr")


KEY = "k_{}"
key = KEY.format


EXPECTED_STRING_DICT = "expected string dict"


D = TypeVar("D", bound="Database")


@define()
class Database(Binary):
    volume: float = field(default=DEFAULT_VOLUME)
    sfx_volume: float = field(default=DEFAULT_VOLUME)

    uuid: UUID = field(factory=generate_uuid)

    player_name: str = field(default=EMPTY)

    name: str = field(default=EMPTY)
    id: int = field(default=DEFAULT_ID)
    account_id: int = field(default=DEFAULT_ID)
    password: str = field(default=EMPTY, repr=password_repr)
    session_id: int = field(default=DEFAULT_ID)

    cube_id: int = field(default=DEFAULT_ICON_ID)
    ship_id: int = field(default=DEFAULT_ICON_ID)
    ball_id: int = field(default=DEFAULT_ICON_ID)
    ufo_id: int = field(default=DEFAULT_ICON_ID)
    wave_id: int = field(default=DEFAULT_ICON_ID)
    robot_id: int = field(default=DEFAULT_ICON_ID)
    spider_id: int = field(default=DEFAULT_ICON_ID)
    # swing_copter_id: int = field(default=DEFAULT_ICON_ID)
    color_1_id: int = field(default=DEFAULT_COLOR_1_ID)
    color_2_id: int = field(default=DEFAULT_COLOR_2_ID)
    trail_id: int = field(default=DEFAULT_ICON_ID)
    explosion_id: int = field(default=DEFAULT_ICON_ID)

    icon_type: IconType = field(default=IconType.DEFAULT)

    glow: bool = field(default=DEFAULT_GLOW)

    secret_value: int = field(default=DEFAULT_SECRET_VALUE)

    moderator: bool = field(default=DEFAULT_MODERATOR)

    values: Values = field(factory=Values)
    unlock_values: UnlockValues = field(factory=UnlockValues)
    custom_objects: List[List[Object]] = field(factory=list)

    storage: Storage = field(factory=Storage)

    completed: Completed = field(factory=Completed)
    statistics: Statistics = field(factory=Statistics)

    show_song_markers: bool = field(default=DEFAULT_SHOW_SONG_MARKERS)
    show_progress_bar: bool = field(default=DEFAULT_SHOW_PROGRESS_BAR)

    clicked_icons: bool = field(default=DEFAULT_CLICKED_ICONS)
    clicked_editor: bool = field(default=DEFAULT_CLICKED_EDITOR)
    clicked_practice: bool = field(default=DEFAULT_CLICKED_PRACTICE)

    shown_editor_guide: bool = field(default=DEFAULT_SHOWN_EDITOR_GUIDE)
    shown_low_detail: bool = field(default=DEFAULT_SHOWN_LOW_DETAIL)

    bootups: int = field(default=DEFAULT_BOOTUPS)

    rated_game: bool = field(default=DEFAULT_RATED_GAME)

    resolution: int = field(default=DEFAULT_RESOLUTION)

    quality: Quality = field(default=Quality.DEFAULT)

    achievements: Dict[str, int] = field(factory=dict)

    official_levels: OrderedSet[OfficialLevelAPI] = field(factory=ordered_set)
    saved_levels: OrderedSet[SavedLevelAPI] = field(factory=ordered_set)
    followed: OrderedSet[int] = field(factory=ordered_set)
    last_played: OrderedSet[int] = field(factory=ordered_set)
    filters: Filters = field(factory=Filters)
    timely_levels: OrderedSet[TimelyLevelAPI] = field(factory=ordered_set)
    daily_id: int = field(default=DEFAULT_ID)
    weekly_id: int = field(default=DEFAULT_ID)
    liked: OrderedSet[Like] = field(factory=dict)
    rated: OrderedSet[int] = field(factory=ordered_set)
    reported: OrderedSet[int] = field(factory=ordered_set)
    demon_rated: OrderedSet[int] = field(factory=ordered_set)
    gauntlet_levels: OrderedSet[GauntletLevelAPI] = field(factory=ordered_set)
    saved_folders: OrderedSet[Folder] = field(factory=ordered_set)
    created_folders: OrderedSet[Folder] = field(factory=ordered_set)

    songs: OrderedSet[SongAPI] = field(factory=ordered_set)
    priority: int = field(default=DEFAULT_PRIORITY)

    created_levels: OrderedSet[CreatedLevelAPI] = field(factory=ordered_set)
    binary_version: RobTopVersion = field(default=CURRENT_BINARY_VERSION)

    # keybindings: Keybindings = field(factory=Keybindings)

    @classmethod
    def load_parts(cls: Type[D], main: bytes, levels: bytes) -> D:
        parser = PARSER

        main_payload = parser.load(main)

        if is_instance(main_payload, Dict):
            main_data: StringMapping[Any] = main_payload

        else:
            raise ValueError(EXPECTED_STRING_DICT)

        volume = main_data.get(VOLUME, DEFAULT_VOLUME)
        sfx_volume = main_data.get(SFX_VOLUME, DEFAULT_VOLUME)

        uuid_option = main_data.get(UUID_LITERAL)

        if uuid_option is None:
            uuid = generate_uuid()

        else:
            uuid = UUID(uuid_option)

        player_name = main_data.get(PLAYER_NAME, EMPTY)

        id = main_data.get(USER_ID, DEFAULT_ID)

        cube_id = main_data.get(CUBE_ID, DEFAULT_ICON_ID)
        ship_id = main_data.get(SHIP_ID, DEFAULT_ICON_ID)
        ball_id = main_data.get(BALL_ID, DEFAULT_ICON_ID)
        ufo_id = main_data.get(UFO_ID, DEFAULT_ICON_ID)
        wave_id = main_data.get(WAVE_ID, DEFAULT_ICON_ID)
        robot_id = main_data.get(ROBOT_ID, DEFAULT_ICON_ID)
        spider_id = main_data.get(SPIDER_ID, DEFAULT_ICON_ID)
        # swing_copter_id = main_data.get(SWING_COPTER_ID, DEFAULT_ICON_ID)

        color_1_id = main_data.get(COLOR_1_ID, DEFAULT_COLOR_1_ID)
        color_2_id = main_data.get(COLOR_2_ID, DEFAULT_COLOR_2_ID)

        trail_id = main_data.get(TRAIL_ID, DEFAULT_ICON_ID)

        explosion_id = main_data.get(EXPLOSION_ID, DEFAULT_ICON_ID)

        icon_type_option = main_data.get(ICON_TYPE)

        if icon_type_option is None:
            icon_type = IconType.DEFAULT

        else:
            icon_type = IconType(icon_type_option)

        glow = main_data.get(GLOW, DEFAULT_GLOW)

        moderator = main_data.get(MODERATOR, DEFAULT_MODERATOR)

        name = main_data.get(NAME, EMPTY)

        password = main_data.get(PASSWORD, EMPTY)

        account_id = main_data.get(ACCOUNT_ID, DEFAULT_ID)

        session_id = main_data.get(SESSION_ID, DEFAULT_ID)

        secret_value = main_data.get(SECRET_VALUE, DEFAULT_SECRET_VALUE)

        show_song_markers = main_data.get(SHOW_SONG_MARKERS, DEFAULT_SHOW_SONG_MARKERS)

        show_progress_bar = main_data.get(SHOW_PROGRESS_BAR, DEFAULT_SHOW_PROGRESS_BAR)

        clicked_icons = main_data.get(CLICKED_ICONS, DEFAULT_CLICKED_ICONS)
        clicked_editor = main_data.get(CLICKED_EDITOR, DEFAULT_CLICKED_EDITOR)
        clicked_practice = main_data.get(CLICKED_PRACTICE, DEFAULT_CLICKED_PRACTICE)

        shown_editor_guide = main_data.get(SHOWN_EDITOR_GUIDE, DEFAULT_SHOWN_EDITOR_GUIDE)
        shown_low_detail = main_data.get(SHOWN_LOW_DETAIL, DEFAULT_SHOWN_LOW_DETAIL)

        rated_game = main_data.get(RATED_GAME, DEFAULT_RATED_GAME)

        bootups = main_data.get(BOOTUPS, DEFAULT_BOOTUPS)

        resolution = main_data.get(RESOLUTION, DEFAULT_RESOLUTION)

        quality_value = main_data.get(QUALITY)

        if quality_value is None:
            quality = Quality.DEFAULT

        else:
            quality = Quality(quality_value)

        achievements_data = main_data.get(ACHIEVEMENTS, {})

        achievements = {name: int(progress) for name, progress in achievements_data.items()}

        values_data = main_data.get(VALUES, {})

        values = Values.from_robtop_data(values_data)

        unlock_values_data = main_data.get(UNLOCK_VALUES, {})

        unlock_values = UnlockValues.from_robtop_data(unlock_values_data)

        custom_objects_data = main_data.get(CUSTOM_OBJECTS, {})

        def objects_from_robtop(iterable: Iterable[str]) -> List[Object]:
            return (
                iter(iterable)
                .filter(None)
                .map(object_from_robtop)
                .collect_iter(migrate_objects)
                .list()
            )

        custom_objects = (
            iter(custom_objects_data.values()).map(split_objects).map(objects_from_robtop).list()
        )

        storage = Storage.from_robtop_data(main_data)

        completed_data = main_data.get(COMPLETED, {})

        completed = Completed.from_robtop_data(completed_data)

        statistics_data = main_data.get(STATISTICS, {})

        statistics = Statistics.from_robtop_data(statistics_data)

        official_levels_data = main_data.get(OFFICIAL_LEVELS, {})

        official_levels = (
            iter(official_levels_data.values()).map(OfficialLevelAPI.from_robtop_data).ordered_set()
        )

        saved_levels_data = main_data.get(SAVED_LEVELS, {})

        saved_levels = (
            iter(saved_levels_data.values()).map(SavedLevelAPI.from_robtop_data).ordered_set()
        )

        followed_data = main_data.get(FOLLOWED, {})

        followed = iter(followed_data.keys()).map(int).ordered_set()

        last_played_data = main_data.get(LAST_PLAYED, {})

        last_played = iter(last_played_data.keys()).map(int).ordered_set()

        timely_levels_data = main_data.get(TIMELY_LEVELS, {})

        timely_levels = (
            iter(timely_levels_data.values()).map(TimelyLevelAPI.from_robtop_data).ordered_set()
        )

        daily_id = main_data.get(DAILY_ID, DEFAULT_ID)
        weekly_id = main_data.get(WEEKLY_ID, DEFAULT_ID) % WEEKLY_ID_ADD

        liked_data = main_data.get(LIKED, {})

        liked = iter(liked_data.keys()).map(Like.from_robtop).ordered_set()

        rated_data = main_data.get(RATED, {})

        rated = iter(rated_data.keys()).map(int).ordered_set()

        reported_data = main_data.get(REPORTED, {})

        reported = iter(reported_data.keys()).map(int).ordered_set()

        demon_rated_data = main_data.get(DEMON_RATED, {})

        demon_rated = iter(demon_rated_data.keys()).map(int).ordered_set()

        gauntlet_levels_data = main_data.get(GAUNTLET_LEVELS, {})

        gauntlet_levels = (
            iter(gauntlet_levels_data.values()).map(GauntletLevelAPI.from_robtop_data).ordered_set()
        )

        def create_folder(string: str, name: str) -> Folder:
            return Folder(int(string), name)

        saved_folders_data = main_data.get(SAVED_FOLDERS, {})

        saved_folders = (
            iter(saved_folders_data.items()).map(unpack_binary(create_folder)).ordered_set()
        )

        created_folders_data = main_data.get(CREATED_FOLDERS, {})

        created_folders = (
            iter(created_folders_data.items()).map(unpack_binary(create_folder)).ordered_set()
        )

        songs_data = main_data.get(SONGS, {})

        songs = iter(songs_data.values()).map(SongAPI.from_robtop_data).ordered_set()

        priority = main_data.get(PRIORITY, DEFAULT_PRIORITY)

        levels_payload = parser.load(levels)

        if is_instance(levels_payload, Dict):
            levels_data: StringMapping[Any] = levels_payload

        else:
            raise ValueError(EXPECTED_STRING_DICT)

        created_levels_data = levels_data.get(CREATED_LEVELS, {})
        binary_version_data = levels_data.get(BINARY_VERSION_LEVELS)

        if binary_version_data is None:
            binary_version = CURRENT_BINARY_VERSION

        else:
            binary_version = RobTopVersion.from_value(binary_version_data)

        created_levels = (
            iter(created_levels_data.values())
            .skip_while(is_true)
            .map(CreatedLevelAPI.from_robtop_data)
            .ordered_set()
        )

        return cls(
            volume=volume,
            sfx_volume=sfx_volume,
            uuid=uuid,
            player_name=player_name,
            name=name,
            id=id,
            account_id=account_id,
            password=password,
            session_id=session_id,
            cube_id=cube_id,
            ship_id=ship_id,
            ball_id=ball_id,
            ufo_id=ufo_id,
            wave_id=wave_id,
            robot_id=robot_id,
            spider_id=spider_id,
            # swing_copter_id=swing_copter_id,
            color_1_id=color_1_id,
            color_2_id=color_2_id,
            trail_id=trail_id,
            explosion_id=explosion_id,
            icon_type=icon_type,
            glow=glow,
            secret_value=secret_value,
            moderator=moderator,
            show_song_markers=show_song_markers,
            show_progress_bar=show_progress_bar,
            clicked_icons=clicked_icons,
            clicked_editor=clicked_editor,
            clicked_practice=clicked_practice,
            shown_editor_guide=shown_editor_guide,
            shown_low_detail=shown_low_detail,
            rated_game=rated_game,
            bootups=bootups,
            resolution=resolution,
            quality=quality,
            achievements=achievements,
            values=values,
            unlock_values=unlock_values,
            custom_objects=custom_objects,
            storage=storage,
            completed=completed,
            statistics=statistics,
            official_levels=official_levels,
            saved_levels=saved_levels,
            followed=followed,
            last_played=last_played,
            # filters=filters,  # TODO
            timely_levels=timely_levels,
            daily_id=daily_id,
            weekly_id=weekly_id,
            liked=liked,
            rated=rated,
            reported=reported,
            demon_rated=demon_rated,
            gauntlet_levels=gauntlet_levels,
            saved_folders=saved_folders,
            created_folders=created_folders,
            songs=songs,
            priority=priority,
            created_levels=created_levels,
            binary_version=binary_version,
            # keybindings=keybindings,
        )

    def dump_main(self) -> bytes:
        parser = PARSER

        one = ONE

        main_data: StringDict[Any] = {
            VOLUME: self.volume,
            SFX_VOLUME: self.sfx_volume,
            UUID_LITERAL: str(self.uuid),
            PLAYER_NAME: self.player_name,
            USER_ID: self.id,
            CUBE_ID: self.cube_id,
            SHIP_ID: self.ship_id,
            BALL_ID: self.ball_id,
            UFO_ID: self.ufo_id,
            WAVE_ID: self.wave_id,
            ROBOT_ID: self.robot_id,
            SPIDER_ID: self.spider_id,
            # SWING_COPTER_ID: self.swing_copter_id,
            COLOR_1_ID: self.color_1_id,
            COLOR_2_ID: self.color_2_id,
            TRAIL_ID: self.trail_id,
            EXPLOSION_ID: self.explosion_id,
            ICON_TYPE: self.icon_type.value,
            GLOW: self.has_glow(),
            MODERATOR: self.is_moderator(),
            SECRET_VALUE: self.secret_value,
            SHOW_SONG_MARKERS: self.is_show_song_markers(),
            SHOW_PROGRESS_BAR: self.is_show_progress_bar(),
            CLICKED_ICONS: self.has_clicked_icons(),
            CLICKED_EDITOR: self.has_clicked_editor(),
            CLICKED_PRACTICE: self.has_clicked_practice(),
            SHOWN_EDITOR_GUIDE: self.has_shown_editor_guide(),
            SHOWN_LOW_DETAIL: self.has_shown_low_detail(),
            RATED_GAME: self.has_rated_game(),
            BOOTUPS: self.bootups,
            RESOLUTION: self.resolution,
            QUALITY: self.quality.value,
            DAILY_ID: self.daily_id,
            WEEKLY_ID: self.weekly_id,
            NAME: self.name,
            PASSWORD: self.password,
            ACCOUNT_ID: self.account_id,
            SESSION_ID: self.session_id,
        }

        achievements_data = {name: str(progress) for name, progress in self.achievements.items()}

        main_data[ACHIEVEMENTS] = achievements_data

        values_data = self.values.to_robtop_data()

        main_data[VALUES] = values_data

        unlock_values_data = self.unlock_values.to_robtop_data()

        main_data[UNLOCK_VALUES] = unlock_values_data

        custom_objects = self.custom_objects

        custom_objects_data = {
            str(-index): iter(objects).map(object_to_robtop).collect(concat_objects)
            for index, objects in iter(custom_objects).enumerate_from(1).unwrap()
        }

        main_data[CUSTOM_OBJECTS] = custom_objects_data

        storage_data = self.storage.to_robtop_data()

        main_data.update(storage_data)

        completed_data = self.completed.to_robtop_data()

        main_data[COMPLETED] = completed_data

        statistics_data = self.statistics.to_robtop_data()

        main_data[STATISTICS] = statistics_data

        official_levels_data = {
            str(level.id): level.to_robtop_data() for level in self.official_levels
        }

        main_data[OFFICIAL_LEVELS] = official_levels_data

        saved_levels_data = {str(level.id): level.to_robtop_data() for level in self.saved_levels}

        main_data[SAVED_LEVELS] = saved_levels_data

        followed_data = {str(account_id): one for account_id in self.followed}

        main_data[FOLLOWED] = followed_data

        last_played_data = {str(level_id): one for level_id in self.last_played}

        main_data[LAST_PLAYED] = last_played_data

        timely_levels_data = {str(level.id): level.to_robtop_data() for level in self.timely_levels}

        main_data[TIMELY_LEVELS] = timely_levels_data

        liked_data = {like.to_robtop(): one for like in self.liked}

        main_data[LIKED] = liked_data

        rated_data = {str(level_id): one for level_id in self.rated}

        main_data[RATED] = rated_data

        reported_data = {str(level_id): one for level_id in self.reported}

        main_data[REPORTED] = reported_data

        demon_rated_data = {str(level_id): one for level_id in self.demon_rated}

        main_data[DEMON_RATED] = demon_rated_data

        gauntlet_levels_data = {
            str(gauntlet_level.id): gauntlet_level.to_robtop_data()
            for gauntlet_level in self.gauntlet_levels
        }

        main_data[GAUNTLET_LEVELS] = gauntlet_levels_data

        saved_folders_data = {
            str(saved_folder.id): saved_folder.name for saved_folder in self.saved_folders
        }

        main_data[SAVED_FOLDERS] = saved_folders_data

        created_folders_data = {
            str(created_folder.id): created_folder.name for created_folder in self.created_folders
        }

        main_data[CREATED_FOLDERS] = created_folders_data

        songs_data = {str(song.id): song.to_robtop_data() for song in self.songs}

        main_data[SONGS] = songs_data

        main_data[PRIORITY] = self.priority

        # keybindings_data = self.keybindings.to_robtop_data()

        return parser.dump(main_data)

    def dump_levels(self) -> bytes:
        parser = PARSER

        created_levels_data: StringDict[Any] = {IS_ARRAY: True}

        created_levels_data.update(
            {
                key(index): created_level.to_robtop_data()
                for index, created_level in enumerate(self.created_levels)
            }
        )

        binary_version_data = self.binary_version.to_value()

        levels_data: StringDict[Any] = {
            CREATED_LEVELS: created_levels_data,
            BINARY_VERSION_LEVELS: binary_version_data,
        }

        return parser.dump(levels_data)

    def dump_parts(self) -> Tuple[bytes, bytes]:
        return (self.dump_main(), self.dump_levels())

    @classmethod
    def create_save_manager(cls: Type[D]) -> SaveManager[D]:
        return SaveManager(cls)

    @classmethod
    def load(cls: Type[D]) -> D:
        return cls.create_save_manager().load()

    def dump(self) -> None:
        self.create_save_manager().dump(self)

    @classmethod
    def from_binary(
        cls: Type[D],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
    ) -> D:
        rounding = DEFAULT_ROUNDING

        show_song_markers_bit = SHOW_SONG_MARKERS_BIT
        show_progress_bar_bit = SHOW_PROGRESS_BAR_BIT
        clicked_icons_bit = CLICKED_ICONS_BIT
        clicked_editor_bit = CLICKED_EDITOR_BIT
        clicked_practice_bit = CLICKED_PRACTICE_BIT
        shown_editor_guide_bit = SHOWN_EDITOR_GUIDE_BIT
        shown_low_detail_bit = SHOWN_LOW_DETAIL_BIT
        rated_game_bit = RATED_GAME_BIT
        moderator_bit = MODERATOR_BIT
        glow_bit = GLOW_BIT

        reader = Reader(binary, order)

        volume = round(reader.read_f32(), rounding)
        sfx_volume = round(reader.read_f32(), rounding)

        data = reader.read(UUID_SIZE)

        if order.is_little():
            uuid = UUID(bytes_le=data)

        else:
            uuid = UUID(bytes=data)

        player_name_length = reader.read_u8()

        player_name = reader.read(player_name_length).decode(encoding, errors)

        name_length = reader.read_u8()

        name = reader.read(name_length).decode(encoding, errors)

        id = reader.read_u32()
        account_id = reader.read_u32()

        password_length = reader.read_u8()

        password = reader.read(password_length).decode(encoding, errors)

        session_id = reader.read_u32()

        cube_id = reader.read_u16()
        ship_id = reader.read_u8()
        ball_id = reader.read_u8()
        ufo_id = reader.read_u8()
        wave_id = reader.read_u8()
        robot_id = reader.read_u8()
        spider_id = reader.read_u8()
        # swing_copter_id = reader.read_u8()
        color_1_id = reader.read_u8()
        color_2_id = reader.read_u8()
        trail_id = reader.read_u8()
        explosion_id = reader.read_u8()

        icon_type_value = reader.read_u8()
        icon_type = IconType(icon_type_value)

        secret_value = reader.read_u32()

        value = reader.read_u8()

        show_song_markers = value & show_song_markers_bit == show_song_markers_bit
        show_progress_bar = value & show_progress_bar_bit == show_progress_bar_bit
        clicked_icons = value & clicked_icons_bit == clicked_icons_bit
        clicked_editor = value & clicked_editor_bit == clicked_editor_bit
        clicked_practice = value & clicked_practice_bit == clicked_practice_bit
        shown_editor_guide = value & shown_editor_guide_bit == shown_editor_guide_bit
        shown_low_detail = value & shown_low_detail_bit == shown_low_detail_bit
        rated_game = value & rated_game_bit == rated_game_bit

        value = reader.read_u8()

        moderator = value & moderator_bit == moderator_bit

        glow = value & glow_bit == glow_bit

        quality_value = (value & QUALITY_MASK) >> QUALITY_SHIFT

        quality = Quality(quality_value)

        achievements_length = reader.read_u16()

        achievements = {}

        for _ in range(achievements_length):
            name_length = reader.read_u8()

            name = reader.read(name_length).decode(encoding, errors)

            progress = reader.read_u16()

            achievements[name] = progress

        bootups = reader.read_u32()

        resolution = reader.read_i8()

        values = Values.from_binary(binary, order, version)
        unlock_values = UnlockValues.from_binary(binary, order, version)

        custom_objects_length = reader.read_u16()

        object_from_binary_function = partial(object_from_binary, binary, order, version)

        def custom_object_from_binary() -> List[Object]:
            custom_object_length = reader.read_u32()

            return iter.repeat_exactly_with(
                object_from_binary_function, custom_object_length
            ).list()

        custom_objects = iter.repeat_exactly_with(
            custom_object_from_binary, custom_objects_length
        ).list()

        storage = Storage.from_binary(binary, order, version)

        completed = Completed.from_binary(binary, order, version)

        statistics = Statistics.from_binary(binary, order, version)

        official_level_from_binary = partial(
            OfficialLevelAPI.from_binary, binary, order, version, encoding, errors
        )

        official_levels_length = reader.read_u8()

        official_levels = iter.repeat_exactly_with(
            official_level_from_binary, official_levels_length
        ).ordered_set()

        saved_level_from_binary = partial(
            SavedLevelAPI.from_binary, binary, order, version, encoding, errors
        )

        saved_levels_length = reader.read_u32()

        saved_levels = iter.repeat_exactly_with(
            saved_level_from_binary, saved_levels_length
        ).ordered_set()

        followed_length = reader.read_u32()

        followed = iter.repeat_exactly_with(reader.read_u32, followed_length).ordered_set()

        last_played_length = reader.read_u16()

        last_played = iter.repeat_exactly_with(reader.read_u32, last_played_length).ordered_set()

        filters = Filters.from_binary(binary, order, version)

        timely_level_from_binary = partial(
            TimelyLevelAPI.from_binary, binary, order, version, encoding, errors
        )

        timely_levels_length = reader.read_u32()

        timely_levels = iter.repeat_exactly_with(
            timely_level_from_binary, timely_levels_length
        ).ordered_set()

        daily_id = reader.read_u32()
        weekly_id = reader.read_u32()

        like_from_binary = partial(Like.from_binary, binary, order, version)

        liked_length = reader.read_u32()

        liked = iter.repeat_exactly_with(like_from_binary, liked_length).ordered_set()

        rated_length = reader.read_u32()

        rated = iter.repeat_exactly_with(reader.read_u32, rated_length).ordered_set()

        reported_length = reader.read_u32()

        reported = iter.repeat_exactly_with(reader.read_u32, reported_length).ordered_set()

        demon_rated_length = reader.read_u32()

        demon_rated = iter.repeat_exactly_with(reader.read_u32, demon_rated_length).ordered_set()

        gauntlet_level_from_binary = partial(
            GauntletLevelAPI.from_binary, binary, order, version, encoding, errors
        )

        gauntlet_levels_length = reader.read_u16()

        gauntlet_levels = iter.repeat_exactly_with(
            gauntlet_level_from_binary, gauntlet_levels_length
        ).ordered_set()

        folder_from_binary = partial(Folder.from_binary, binary, order, version, encoding, errors)

        saved_folders_length = reader.read_u8()

        saved_folders = iter.repeat_exactly_with(
            folder_from_binary, saved_folders_length
        ).ordered_set()

        created_folders_length = reader.read_u8()

        created_folders = iter.repeat_exactly_with(
            folder_from_binary, created_folders_length
        ).ordered_set()

        song_from_binary = partial(SongAPI.from_binary, binary, order, version, encoding, errors)

        songs_length = reader.read_u32()

        songs = iter.repeat_exactly_with(song_from_binary, songs_length).ordered_set()

        created_level_from_binary = partial(
            CreatedLevelAPI.from_binary, binary, order, version, encoding, errors
        )

        created_levels_length = reader.read_u32()

        created_levels = iter.repeat_exactly_with(
            created_level_from_binary, created_levels_length
        ).ordered_set()

        binary_version = RobTopVersion.from_binary(binary, order, version)

        # keybindings = Keybindings.from_binary(binary, order, version, encoding, errors)

        return cls(
            volume=volume,
            sfx_volume=sfx_volume,
            uuid=uuid,
            player_name=player_name,
            name=name,
            id=id,
            account_id=account_id,
            password=password,
            session_id=session_id,
            cube_id=cube_id,
            ship_id=ship_id,
            ball_id=ball_id,
            ufo_id=ufo_id,
            wave_id=wave_id,
            robot_id=robot_id,
            spider_id=spider_id,
            # swing_copter_id=swing_copter_id,
            color_1_id=color_1_id,
            color_2_id=color_2_id,
            trail_id=trail_id,
            explosion_id=explosion_id,
            icon_type=icon_type,
            glow=glow,
            secret_value=secret_value,
            moderator=moderator,
            show_song_markers=show_song_markers,
            show_progress_bar=show_progress_bar,
            clicked_icons=clicked_icons,
            clicked_editor=clicked_editor,
            clicked_practice=clicked_practice,
            shown_editor_guide=shown_editor_guide,
            shown_low_detail=shown_low_detail,
            rated_game=rated_game,
            bootups=bootups,
            resolution=resolution,
            quality=quality,
            achievements=achievements,
            values=values,
            unlock_values=unlock_values,
            custom_objects=custom_objects,
            storage=storage,
            completed=completed,
            statistics=statistics,
            official_levels=official_levels,
            saved_levels=saved_levels,
            followed=followed,
            last_played=last_played,
            filters=filters,
            timely_levels=timely_levels,
            daily_id=daily_id,
            weekly_id=weekly_id,
            liked=liked,
            rated=rated,
            reported=reported,
            demon_rated=demon_rated,
            gauntlet_levels=gauntlet_levels,
            saved_folders=saved_folders,
            created_folders=created_folders,
            songs=songs,
            created_levels=created_levels,
            binary_version=binary_version,
            # keybindings=keybindings,
        )

    def to_binary(
        self,
        binary: BinaryWriter,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
    ) -> None:
        writer = Writer(binary, order)

        writer.write_f32(self.volume)
        writer.write_f32(self.sfx_volume)

        uuid = self.uuid

        data = uuid.bytes_le if order.is_little() else uuid.bytes

        writer.write(data)

        data = self.player_name.encode(encoding, errors)

        writer.write_u8(len(data))

        writer.write(data)

        data = self.name.encode(encoding, errors)

        writer.write_u8(len(data))

        writer.write(data)

        writer.write_u32(self.id)
        writer.write_u32(self.account_id)

        data = self.password.encode(encoding, errors)

        writer.write_u8(len(data))

        writer.write(data)

        writer.write_u32(self.session_id)

        writer.write_u16(self.cube_id)
        writer.write_u8(self.ship_id)
        writer.write_u8(self.ball_id)
        writer.write_u8(self.ufo_id)
        writer.write_u8(self.wave_id)
        writer.write_u8(self.robot_id)
        writer.write_u8(self.spider_id)
        # writer.write_u8(self.swing_copter_id)
        writer.write_u8(self.color_1_id)
        writer.write_u8(self.color_2_id)
        writer.write_u8(self.trail_id)
        writer.write_u8(self.explosion_id)

        writer.write_u8(self.icon_type.value)

        writer.write_u32(self.secret_value)

        value = 0

        if self.is_show_song_markers():
            value |= SHOW_SONG_MARKERS_BIT

        if self.is_show_progress_bar():
            value |= SHOW_PROGRESS_BAR_BIT

        if self.has_clicked_icons():
            value |= CLICKED_ICONS_BIT

        if self.has_clicked_editor():
            value |= CLICKED_EDITOR_BIT

        if self.has_clicked_practice():
            value |= CLICKED_PRACTICE_BIT

        if self.has_shown_editor_guide():
            value |= SHOWN_EDITOR_GUIDE_BIT

        if self.has_shown_low_detail():
            value |= SHOWN_LOW_DETAIL_BIT

        if self.has_rated_game():
            value |= RATED_GAME_BIT

        writer.write_u8(value)

        value = self.quality.value << QUALITY_SHIFT

        if self.is_moderator():
            value |= MODERATOR_BIT

        if self.has_glow():
            value |= GLOW_BIT

        writer.write_u8(value)

        achievements = self.achievements

        writer.write_u16(len(achievements))

        for name, progress in achievements.items():
            data = name.encode(encoding, errors)

            writer.write_u8(len(data))

            writer.write(data)

            writer.write_u16(progress)

        writer.write_u32(self.bootups)

        writer.write_i8(self.resolution)

        self.values.to_binary(binary, order, version)
        self.unlock_values.to_binary(binary, order, version)

        custom_objects = self.custom_objects

        writer.write_u16(len(custom_objects))

        for objects in custom_objects:
            writer.write_u32(len(objects))

            for object in objects:
                object_to_binary(object, binary, order)

        self.storage.to_binary(binary, order, version)

        self.completed.to_binary(binary, order, version)

        self.statistics.to_binary(binary, order, version)

        official_levels = self.official_levels

        writer.write_u8(len(official_levels))

        for official_level in official_levels:
            official_level.to_binary(binary, order, version, encoding, errors)

        saved_levels = self.saved_levels

        writer.write_u32(len(saved_levels))

        for saved_level in saved_levels:
            saved_level.to_binary(binary, order, version, encoding, errors)

        followed = self.followed

        writer.write_u32(len(followed))

        for account_id in followed:
            writer.write_u32(account_id)

        last_played = self.last_played

        writer.write_u16(len(last_played))

        for level_id in last_played:
            writer.write_u32(level_id)

        self.filters.to_binary(binary, order, version)

        timely_levels = self.timely_levels

        writer.write_u32(len(timely_levels))

        for timely_level in timely_levels:
            timely_level.to_binary(binary, order, version, encoding, errors)

        writer.write_u32(self.daily_id)
        writer.write_u32(self.weekly_id)

        liked = self.liked

        writer.write_u32(len(liked))

        for like in liked:
            like.to_binary(binary, order, version)

        rated = self.rated

        writer.write_u32(len(rated))

        for level_id in rated:
            writer.write_u32(level_id)

        reported = self.reported

        writer.write_u32(len(reported))

        for level_id in reported:
            writer.write_u32(level_id)

        demon_rated = self.demon_rated

        writer.write_u32(len(demon_rated))

        for level_id in demon_rated:
            writer.write_u32(level_id)

        gauntlet_levels = self.gauntlet_levels

        writer.write_u16(len(gauntlet_levels))

        for gauntlet_level in gauntlet_levels:
            gauntlet_level.to_binary(binary, order, version, encoding, errors)

        saved_folders = self.saved_folders

        writer.write_u8(len(saved_folders))

        for saved_folder in saved_folders:
            saved_folder.to_binary(binary, order, version, encoding, errors)

        created_folders = self.created_folders

        writer.write_u8(len(created_folders))

        for created_folder in created_folders:
            created_folder.to_binary(binary, order, version, encoding, errors)

        songs = self.songs

        writer.write_u32(len(songs))

        for song in songs:
            song.to_binary(binary, order, version, encoding, errors)

        created_levels = self.created_levels

        writer.write_u32(len(created_levels))

        for created_level in created_levels:
            created_level.to_binary(binary, order, version, encoding, errors)

        self.binary_version.to_binary(binary, order, version)

        # self.keybindings.to_binary(binary, order, version, encoding, errors)

    def is_moderator(self) -> bool:
        return self.moderator

    def is_show_song_markers(self) -> bool:
        return self.show_song_markers

    def is_show_progress_bar(self) -> bool:
        return self.show_progress_bar

    def has_clicked_icons(self) -> bool:
        return self.clicked_icons

    def has_clicked_editor(self) -> bool:
        return self.clicked_editor

    def has_clicked_practice(self) -> bool:
        return self.clicked_practice

    def has_shown_editor_guide(self) -> bool:
        return self.shown_editor_guide

    def has_shown_low_detail(self) -> bool:
        return self.shown_low_detail

    def has_rated_game(self) -> bool:
        return self.rated_game

    def has_glow(self) -> bool:
        return self.glow


from gd.api.save_manager import SaveManager
