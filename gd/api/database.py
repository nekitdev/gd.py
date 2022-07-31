# DOCUMENT + REWRITE

from collections import UserList as ListDerive
from pathlib import Path
from typing import Dict, List, Set, Tuple, TypeVar

from attrs import define, field
from iters import iter

from gd.api.struct import LevelAPI
from gd.enums import DeleteFilter, IconType, LevelLeaderboardStrategy  # type: ignore
from gd.json import dumps
from gd.text_utils import snake_to_camel
from gd.typing import is_instance

__all__ = ("Part", "Database", "LevelStore", "LevelValues", "LevelCollection")

MAIN = "CCGameManager.dat"
LEVELS = "CCLocalLevels.dat"

T = TypeVar("T")


def is_dict(some: Any) -> bool:
    return is_instance(some, dict)


@dataclass
class LevelStore:
    """Values that particular completed levels in the save."""

    completed: List[int] = attrib()
    stars: List[int] = attrib()
    demons: List[int] = attrib()

    @classmethod
    def create_empty(cls) -> "LevelStore":
        return cls(completed=[], stars=[], demons=[])


@dataclass
class LevelValues:
    """Values that represent completed levels in the save."""

    official: List[int] = attrib()
    normal: LevelStore = attrib()
    timely: LevelStore = attrib()
    gauntlet: LevelStore = attrib()
    packs: List[int] = attrib()

    def get_type_to_array(self) -> Dict[str, List[int]]:
        values, normal, timely, gauntlet = self, self.normal, self.timely, self.gauntlet

        return {
            "n": values.official,
            "c": normal.completed,
            "d": timely.completed,
            "g": gauntlet.completed,
            "star": normal.stars,
            "dstar": timely.stars,
            "gstar": gauntlet.stars,
            "demon": normal.demons,
            "ddemon": timely.demons,
            "gdemon": gauntlet.demons,
            "pack": values.packs,
        }

    def get_prefix_to_array(self) -> Dict[str, List[int]]:
        return {f"{type}_": array for type, array in self.get_type_to_array().items()}

    @classmethod
    def create_empty(cls) -> "LevelValues":
        return cls(
            official=[],
            normal=LevelStore.create_empty(),
            timely=LevelStore.create_empty(),
            gauntlet=LevelStore.create_empty(),
            packs=[],
        )


def remove_prefix(string: str, prefix: str) -> str:
    if string.startswith(prefix):
        return string[len(prefix) :]

    return string


class Part(Dict[str, T]):
    @classmethod
    def load(cls, stream: AnyString, default: Optional[Dict[str, T]] = None) -> "Part":
        self = cls()

        try:
            self.update(self.parser.load(stream))

        except Exception:
            if default is None:
                default = {}

            self.update(default)

        return self

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.parser = XMLParser()

    def __str__(self) -> str:
        return dumps(self, indent=4)

    def __repr__(self) -> str:
        info = {"length": len(self)}

        return nice_repr(self, info)

    def copy(self) -> "Part":
        return self.__class__(super().copy())

    def set(self, key: str, value: T) -> None:
        """Same as self[key] = value."""
        self[key] = value

    def dump_as_bytes(self) -> bytes:
        """Dump the part and return xml data."""
        return self.parser.dump_as_bytes(self)

    def dump(self) -> str:
        """Dump the part and return xml string."""
        return self.parser.dump(self)


DEFAULT_DISLIKE = False


@define()
class LevelRating:
    level_id: int
    dislike: bool = DEFAULT_DISLIKE


@define()
class Folder:
    id: int
    name: str


DEFAULT_DELETE_FILTER_OBJECT_ID = 0
DEFAULT_SELECT_FILTER_OBJECT_ID = 0

DEFAULT_BUTTONS_PER_ROW = 6
DEFAULT_BUTTON_ROWS = 2

DEFAULT_CREATED_LEVELS_FOLDER_ID = 0
DEFAULT_SAVED_LEVELS_FOLDER_ID = 0


@define()
class Variables:
    follow_player: bool = True
    play_music: bool = True
    swipe: bool = False
    free_move: bool = False
    delete_filter: DeleteFilter = DeleteFilter.DEFAULT
    delete_filter_object_id: int = DEFAULT_DELETE_FILTER_OBJECT_ID
    rotate_toggled: bool = False
    snap_toggled: bool = False
    ignore_damage: bool = True
    flip_two_player_controls: bool = False
    always_limit_controls: bool = False
    showed_comment_rules: bool = True
    increase_max_history: bool = True
    disable_explosion_shake: bool = False
    flip_pause_button: bool = False
    showed_song_terms: bool = False
    no_song_limit: bool = True
    in_memory_songs: bool = True
    higher_audio_quality: bool = True
    smooth_fix: bool = False
    show_cursor_in_game: bool = False
    windowed: bool = False
    auto_retry: bool = True
    auto_checkpoints: bool = True
    disable_analog_stick: bool = False
    showed_options: bool = True
    vsync: bool = True
    call_gl_finish: bool = False
    force_timer_enabled: bool = False
    change_song_path: bool = False
    game_center_enabled: bool = False
    preview_mode: bool = True
    show_ground: bool = False
    show_grid: bool = True
    grid_on_top: bool = False
    show_percentage: bool = True
    show_object_info: bool = True
    increase_max_levels: bool = True
    show_effect_lines: bool = True
    show_trigger_boxes: bool = True
    debug_draw: bool = False
    hide_ui_on_test: bool = False
    showed_profile_info: bool = True
    viewed_self_profile: bool = True
    buttons_per_row: int = DEFAULT_BUTTONS_PER_ROW
    button_rows: int = DEFAULT_BUTTON_ROWS
    showed_newgrounds_message: bool = True
    fast_practice_reset: bool = False
    free_games: bool = False
    check_server_online: bool = True
    hold_to_swipe: bool = False
    show_duration_lines: bool = False
    swipe_cycle: bool = False
    default_mini_icon: bool = False
    switch_spider_teleport_color: bool = False
    switch_dash_fire_color: bool = False
    showed_unverified_coins_message: bool = True
    select_filter_object_id: int = DEFAULT_SELECT_FILTER_OBJECT_ID
    enable_move_optimization: bool = False
    high_capacity: bool = True
    quick_checkpoints: bool = False
    show_level_description: bool = True
    showed_unlisted_level_message: bool = True
    disable_gravity_effect: bool = False
    new_completed_filter: bool = False
    show_restart_button: bool = True
    disable_level_comments: bool = False
    disable_user_comments: bool = False
    featured_levels_only: bool = False
    hide_background: bool = False
    hide_grid_on_play: bool = True
    disable_shake: bool = False
    disable_high_detail_alert: bool = True
    disable_song_alert: bool = True
    manual_order: bool = False
    small_comments: bool = False
    extended_info: bool = True
    auto_load_comments: bool = True
    created_levels_folder_id: int = DEFAULT_CREATED_LEVELS_FOLDER_ID
    saved_levels_folder_id: int = DEFAULT_SAVED_LEVELS_FOLDER_ID
    increase_local_levels_per_page: bool = True
    more_comments: bool = False
    just_do_not: bool = False
    switch_wave_trail_color: bool = False
    enable_link_controls: bool = False
    level_leaderboard_strategy: LevelLeaderboardStrategy = LevelLeaderboardStrategy.DEFAULT
    show_record: bool = True
    practice_death_effect: bool = False
    force_smooth_fix: bool = False
    smooth_fix_in_editor: bool = False


@define()
class Values:
    variables: Variables = field(factory=Variables)

    cubes: Set[int] = field(factory=set)
    ships: Set[int] = field(factory=set)
    balls: Set[int] = field(factory=set)
    ufos: Set[int] = field(factory=set)
    waves: Set[int] = field(factory=set)
    robots: Set[int] = field(factory=set)
    spiders: Set[int] = field(factory=set)
    explosions: Set[int] = field(factory=set)
    colors_1: Set[int] = field(factory=set)
    colors_2: Set[int] = field(factory=set)


@define()
class UnlockValues:
    the_challenge_unlocked: bool = False
    gubflub_hint_1: bool = False
    gubflub_hint_2: bool = False
    the_challenge_completed: bool = False
    treasure_room_unlocked: bool = False
    chamber_of_time_unlocked: bool = False
    chamber_of_time_discovered: bool = False
    master_emblem_shown: bool = False
    gate_keeper_dialog: bool = False
    scratch_dialog: bool = False
    secret_shop_unlocked: bool = False
    demon_guardian_dialog: bool = False
    demon_freed: bool = False
    demon_key_1: bool = False
    demon_key_2: bool = False
    demon_key_3: bool = False
    shop_keeper_dialog: bool = False
    world_online_levels: bool = False
    demon_discovered: bool = False
    community_shop_unlocked: bool = False
    potbor_dialog: bool = False
    youtube_chest_unlocked: bool = False
    facebook_chest_unlocked: bool = False
    twitter_chest_unlocked: bool = False
    # firebird_gate_keeper: bool = False
    # twitch_chest_unlocked: bool = False
    # discord_chest_unlocked: bool = False


@define()
class Statistics:
    jumps: int
    attempts: int
    official_levels: int
    online_levels: int
    demons: int
    stars: int
    map_packs: int
    secret_coins: int
    destroyed: int
    voted: int
    rated: int
    user_coins: int
    diamonds: int
    orbs: int
    daily_levels: int
    fire_shards: int
    ice_shards: int
    poison_shards: int
    shadow_shards: int
    lava_shards: int
    bonus_shards: int
    total_orbs: int

    official_coins: Dict[int, int]


@define()
class Database:
    volume: float
    sfx_volume: float

    udid: str
    name: str
    id: int
    account_id: int
    password: str
    session_id: int

    cube_id: int
    ship_id: int
    ball_id: int
    ufo_id: int
    wave_id: int
    spider_id: int
    color_1_id: int
    color_2_id: int
    trail_id: int
    explosion_id: int
    icon_type: IconType

    secret_value: int

    moderator: bool

    values: Values
    unlock_values: UnlockValues
    custom_objects: CustomObjects

    statistics: Statistics

    show_song_markers: bool
    show_progress_bar: bool

    clicked_icons: bool
    clicked_editor: bool
    clicked_practice: bool

    showed_editor_guide: bool
    showed_low_detail: bool

    bootups: int

    rated_game: bool

    official_levels: AnyLevelCollection
    saved_levels: AnyLevelCollection
    followed: Set[int]
    last_played: Set[int]
    filters: Filters
    daily_levels: AnyLevelCollection
    daily_id: int
    level_rated: Set[LevelRating]
    reported: Set[int]
    demon_rated: Set[int]
    gauntlet_levels: AnyLevelCollection
    weekly_id: int
    saved_folders: List[Folder]
    created_folders: List[Folder]

    created_levels: AnyLevelCollection

    songs: Songs

    keybindings: Keybindings


class Database:
    def __init__(
        self, main: Optional[AnyString] = None, levels: Optional[AnyString] = None
    ) -> None:
        self.main = Part.load(main) if main else Part()
        self.levels = Part.load(levels) if levels else Part()

    def __repr__(self) -> str:
        info = {"main": repr(self.main), "levels": repr(self.levels)}

        return nice_repr(self, info)

    def __json__(self) -> Dict[str, Part]:
        return {"main": self.main, "levels": self.levels}

    def __bool__(self) -> bool:
        if self.main:
            return True

        if self.levels:
            return True

        return False

    def is_empty(self) -> bool:
        """Check if the database is empty."""
        return not self

    def get_user_name(self) -> str:
        """Player name."""
        return self.main.get("GJA_001", "unknown")

    def set_user_name(self, user_name: str) -> None:
        """Set player name to ``user_name``."""
        self.main.set("GJA_001", user_name)

    user_name = property(get_user_name, set_user_name)

    def get_password(self) -> str:
        """Player password."""
        return self.main.get("GJA_002", "unknown")

    def set_password(self, password: str) -> None:
        """Set player password to ``password``."""
        self.main.set("GJA_002", password)

    password = property(get_password, set_password)

    def get_account_id(self) -> int:
        """Player Account ID, same as ``account_id`` of users."""
        return self.main.get("GJA_003", 0)

    def set_account_id(self, account_id: int) -> None:
        """Set player Account ID to ``account_id``."""
        self.main.set("GJA_003", account_id)

    account_id = property(get_account_id, set_account_id)

    def get_user_id(self) -> int:
        """Player User ID, same as ``id`` of users."""
        return self.main.get("playerUserID", 0)

    def set_user_id(self, user_id: int) -> None:
        """Set player User ID to ``user_id``."""
        self.main.set("playerUserID", user_id)

    user_id = property(get_user_id, set_user_id)

    def get_udid(self) -> str:
        """Player UDID."""
        return self.main.get("playerUDID", "S0")

    def set_udid(self, udid: str) -> None:
        """Set player UDID to ``user_id``."""
        self.main.set("playerUDID", udid)

    udid = property(get_udid, set_udid)

    def get_bootups(self) -> int:
        """Count of game bootups."""
        return self.main.get("bootups", 0)

    def set_bootups(self, bootups: int) -> None:
        """Set bootups to ``bootups``."""
        self.main.set("bootups", bootups)

    bootups = property(get_bootups, set_bootups)

    def get_followed(self) -> List[int]:
        """List of followed users."""
        return list(map(int, self.main.get("GLM_06", {}).keys()))

    def set_followed(self, followed: Iterable[int]) -> None:
        """Set followed users to ``followed``."""
        self.main.set("GLM_06", {str(account_id): 1 for account_id in followed})

    followed = property(get_followed, set_followed)

    def get_values(self) -> LevelValues:  # O(nm), thanks rob
        """:class:`~gd.api.database.LevelValues` that represent completed levels."""
        values = LevelValues.create_empty()
        prefix_to_array = values.get_prefix_to_array()

        for string in self.main.get("GS_completed", {}).keys():
            for prefix, array in prefix_to_array.items():
                id_string = remove_prefix(string, prefix)

                if id_string != string:
                    array.append(int(id_string))
                    break

        return values

    def set_values(self, values: LevelValues) -> None:
        """Set :class:`~gd.api.database.LevelValues` to ``values``."""
        mapping = {}
        prefix_to_array = values.get_prefix_to_array()

        for prefix, array in prefix_to_array.items():
            mapping.update({f"{prefix}{value_id}": 1 for value_id in array})

        self.main.set("GS_completed", mapping)

    values = property(get_values, set_values)

    def to_levels(self, raw_levels: Iterable[Dict[str, T]], function: str) -> "LevelCollection":
        return LevelCollection.launch(
            self, function, map(LevelAPI.from_data, filter(is_dict, raw_levels))
        )

    def load_saved_levels(self) -> "LevelCollection":
        """Load saved levels into :class:`~gd.api.LevelCollection`."""
        return self.to_levels(self.main.get("GLM_03", {}).values(), "dump_saved_levels")

    get_saved_levels = load_saved_levels

    def dump_saved_levels(self, levels: "LevelCollection") -> None:
        """Dump saved levels from :class:`~gd.api.LevelCollection`."""
        self.main.set("GLM_03", {str(level.id): level.to_data() for level in levels})

    set_saved_levels = dump_saved_levels

    saved_levels = property(get_saved_levels, set_saved_levels)

    def load_created_levels(self) -> "LevelCollection":
        """Load created levels into :class:`~gd.api.LevelCollection`."""
        return self.to_levels(self.levels.get("LLM_01", {}).values(), "dump_created_levels")

    get_created_levels = load_created_levels

    def dump_created_levels(self, levels: "LevelCollection") -> None:
        """Dump created levels from :class:`~gd.api.LevelCollection`."""
        store = {IS_ARRAY: True}

        store.update({f"k_{index}": level.to_data() for index, level in enumerate(levels)})

        self.levels.set("LLM_01", store)

    set_created_levels = dump_created_levels

    created_levels = property(get_created_levels, set_created_levels)

    @classmethod
    def load(
        cls,
        main: Optional[PathLike] = None,
        levels: Optional[PathLike] = None,
        main_file: PathLike = MAIN,
        levels_file: PathLike = LEVELS,
    ) -> "Database":
        """Load the database. See :meth:`~gd.api.SaveUtils.load` for more."""
        from gd.api.save_manager import save  # ...

        return save.load(main=main, levels=levels, main_file=main_file, levels_file=levels_file)

    def dump(
        self,
        main: Optional[PathLike] = None,
        levels: Optional[PathLike] = None,
        main_file: PathLike = MAIN,
        levels_file: PathLike = LEVELS,
    ) -> None:
        """Dump the database back. See :meth:`~gd.api.SaveUtils.dump` for more."""
        from gd.api.save_manager import save  # I hate circular imports.

        save.dump(self, main=main, levels=levels, main_file=main_file, levels_file=levels_file)

    def as_tuple(self) -> Tuple[Part, Part]:
        return (self.main, self.levels)


A = TypeVar("A", bound=LevelAPI)


class LevelCollection(BaseList[A]):
    """Collection of :class:`~gd.api.LevelAPI` objects."""

    def __init__(self, levels: Iterable[A]) -> None:
        super().__init__(extract_iterable_from_tuple(args))  # type: ignore

        self._callback: Optional[Database] = None
        self._function: Optional[str] = None

    def get_by_name(self, name: str) -> Optional[LevelAPI]:
        """Fetch a level by ``name``. Returns ``None`` if not found."""
        return iter(self).get_or_none(name=name)

    @classmethod
    def launch(
        cls, callback: Database, function: str, iterable: Iterable[A]
    ) -> "LevelCollection":
        self = cls(iterable)

        self._callback = callback
        self._function = function

        return self

    def dump(self, database: Optional[Database] = None) -> None:
        """Dump levels to ``database``, if provided.
        Otherwise, try to dump back to the database that created this collection.
        """
        if database is None:
            database = self._callback  # type: ignore

        getattr(database, self._function)(self)  # type: ignore
