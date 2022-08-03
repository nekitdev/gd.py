from typing import BinaryIO, Dict, Iterable, List, Optional, Type, TypeVar

from attrs import define, field
from gd.api.api import API

from gd.api.level_api import LevelAPI
from gd.api.objects import Object
from gd.api.ordered_set import OrderedSet, ordered_set
from gd.binary import Binary
from gd.binary_utils import Reader, Writer
from gd.constants import DEFAULT_ID, EMPTY
from gd.enums import ByteOrder, DeleteFilter, IconType, LevelLeaderboardStrategy
from gd.filters import Filters
from gd.song import Song
from gd.typing import Unary

__all__ = ("Database",)

MAIN = "CCGameManager.dat"
LEVELS = "CCLocalLevels.dat"

A = TypeVar("A", bound=LevelAPI)

Callback = Unary[Iterable[A], None]

C = TypeVar("C", bound="AnyLevelCollection")

CAN_NOT_DUMP_NOT_LOADED = "can not `dump` level collection that was created without `load`"


class LevelCollection(OrderedSet[A]):
    def __init__(self, levels: Iterable[A] = ()) -> None:
        super().__init__(levels)

        self.callback: Optional[Callback[A]] = None

    @classmethod
    def load(cls: Type[C], iterable: Iterable[A], callback: Callback[A]) -> C:
        self = cls(iterable)

        self.callback = callback

        return self

    def dump(self) -> None:
        callback = self.callback

        if callback is None:
            raise ValueError(CAN_NOT_DUMP_NOT_LOADED)

        callback(self)


def level_collection(iterable: Iterable[A] = ()) -> LevelCollection[A]:
    return LevelCollection(iterable)


AnyLevelCollection = LevelCollection[LevelAPI]


OFFICIAL = "n"
NORMAL = "c"
NORMAL_DEMONS = "demon"
TIMELY = "d"
TIMELY_DEMONS = "ddemon"
GAUNTLETS = "g"
GAUNTLETS_DEMONS = "gdemon"
MAP_PACKS = "pack"

PREFIX = "{}_"
prefix = PREFIX.format


class Storage:
    levels: OrderedSet[int] = field(factory=ordered_set)
    demons: OrderedSet[int] = field(factory=ordered_set)


@define()
class Completed:
    """Represents completed levels in the database."""

    official: OrderedSet[int] = field(factory=ordered_set)
    normal: Storage = field(factory=Storage)
    timely: Storage = field(factory=Storage)
    gauntlets: Storage = field(factory=Storage)
    map_packs: OrderedSet[int] = field(factory=ordered_set)

    def get_type_to_set(self) -> Dict[str, OrderedSet[int]]:
        official = self.official
        normal = self.normal
        timely = self.timely
        gauntlets = self.gauntlets
        map_packs = self.map_packs

        return {
            OFFICIAL: official,
            NORMAL: normal.levels,
            NORMAL_DEMONS: normal.demons,
            TIMELY: timely.levels,
            TIMELY_DEMONS: timely.demons,
            GAUNTLETS: gauntlets.levels,
            GAUNTLETS_DEMONS: gauntlets.demons,
            MAP_PACKS: map_packs,
        }

    def get_prefix_to_set(self) -> Dict[str, OrderedSet[int]]:
        return {prefix(type): set for type, set in self.get_type_to_set().items()}


@define()
class Folder:
    """Represents level folders."""

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
    """Represents game variables."""

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


VS = TypeVar("VS", bound="Values")


@define()
class Values(Binary, API):
    variables: Variables = field(factory=Variables)

    cubes: OrderedSet[int] = field(factory=ordered_set)
    ships: OrderedSet[int] = field(factory=ordered_set)
    balls: OrderedSet[int] = field(factory=ordered_set)
    ufos: OrderedSet[int] = field(factory=ordered_set)
    waves: OrderedSet[int] = field(factory=ordered_set)
    robots: OrderedSet[int] = field(factory=ordered_set)
    spiders: OrderedSet[int] = field(factory=ordered_set)
    swing_copters: OrderedSet[int] = field(factory=ordered_set)
    explosions: OrderedSet[int] = field(factory=ordered_set)
    colors_1: OrderedSet[int] = field(factory=ordered_set)
    colors_2: OrderedSet[int] = field(factory=ordered_set)

    def to_binary(self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT) -> None:
        writer = Writer(binary)

        self.variables.to_binary(binary, order)

        for items in (
            self.cubes,
            self.ships,
            self.balls,
            self.ufos,
            self.waves,
            self.robots,
            self.spiders,
            self.swing_copters,
            self.explosions,
            self.colors_1,
            self.colors_2,
        ):
            writer.write_u16(len(items), order)

            for item in items:
                writer.write_u16(item, order)

    @classmethod
    def from_binary(cls: Type[VS], binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT) -> VS:
        reader = Reader(binary)

        variables = Variables.from_binary(binary, order)

        cubes_length = reader.read_u16(order)

        cubes = ordered_set(reader.read_u16(order) for _ in range(cubes_length))

        ships_length = reader.read_u16(order)

        ships = ordered_set(reader.read_u16(order) for _ in range(ships_length))

        balls_length = reader.read_u16(order)

        balls = ordered_set(reader.read_u16(order) for _ in range(balls_length))

        ufos_length = reader.read_u16(order)

        ufos = ordered_set(reader.read_u16(order) for _ in range(ufos_length))

        waves_length = reader.read_u16(order)

        waves = ordered_set(reader.read_u16(order) for _ in range(waves_length))

        robots_length = reader.read_u16(order)

        robots = ordered_set(reader.read_u16(order) for _ in range(robots_length))

        spiders_length = reader.read_u16(order)

        spiders = ordered_set(reader.read_u16(order) for _ in range(spiders_length))

        swing_copters_length = reader.read_u16(order)

        swing_copters = ordered_set(reader.read_u16(order) for _ in range(swing_copters_length))

        explosions_length = reader.read_u16(order)

        explosions = ordered_set(reader.read_u16(order) for _ in range(explosions_length))

        colors_1_length = reader.read_u16(order)

        colors_1 = ordered_set(reader.read_u16(order) for _ in range(colors_1_length))

        colors_2_length = reader.read_u16(order)

        colors_2 = ordered_set(reader.read_u16(order) for _ in range(colors_2_length))

        return cls(
            variables=variables,
            cubes=cubes,
            ships=ships,
            balls=balls,
            ufos=ufos,
            waves=waves,
            robots=robots,
            spiders=spiders,
            swing_copters=swing_copters,
            explosions=explosions,
            colors_1=colors_1,
            colors_2=colors_2,
        )


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


S = TypeVar("S", bound="Statistics")


@define()
class Statistics(Binary, API):
    jumps: int = field(default=0)
    attempts: int = field(default=0)
    official_levels: int = field(default=0)
    online_levels: int = field(default=0)
    demons: int = field(default=0)
    stars: int = field(default=0)
    map_packs: int = field(default=0)
    secret_coins: int = field(default=0)
    destroyed: int = field(default=0)
    liked: int = field(default=0)
    rated: int = field(default=0)
    user_coins: int = field(default=0)
    diamonds: int = field(default=0)
    orbs: int = field(default=0)
    daily_levels: int = field(default=0)
    fire_shards: int = field(default=0)
    ice_shards: int = field(default=0)
    poison_shards: int = field(default=0)
    shadow_shards: int = field(default=0)
    lava_shards: int = field(default=0)
    bonus_shards: int = field(default=0)
    total_orbs: int = field(default=0)

    official_coins: Dict[int, int] = field(factory=dict)

    def to_binary(self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT) -> None:
        writer = Writer(binary)

        writer.write_u32(self.jumps, order)
        writer.write_u32(self.attempts, order)
        writer.write_u8(self.official_levels, order)
        writer.write_u32(self.online_levels, order)
        writer.write_u16(self.demons, order)
        writer.write_u32(self.stars, order)
        writer.write_u8(self.map_packs, order)
        writer.write_u8(self.secret_coins, order)
        writer.write_u32(self.destroyed, order)
        writer.write_u32(self.liked, order)
        writer.write_u32(self.rated, order)
        writer.write_u32(self.user_coins, order)
        writer.write_u32(self.diamonds, order)
        writer.write_u32(self.orbs, order)
        writer.write_u32(self.daily_levels, order)
        writer.write_u16(self.fire_shards, order)
        writer.write_u16(self.ice_shards, order)
        writer.write_u16(self.poison_shards, order)
        writer.write_u16(self.shadow_shards, order)
        writer.write_u16(self.lava_shards, order)
        writer.write_u16(self.bonus_shards, order)
        writer.write_u32(self.total_orbs, order)

        official_coins = self.official_coins

        writer.write_u16(len(official_coins))

        for level_id, count in official_coins.items():
            writer.write_u16(level_id, order)
            writer.write_u8(count, order)

    @classmethod
    def from_binary(cls: Type[S], binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT) -> S:
        reader = Reader(binary)

        jumps = reader.read_u32(order)
        attempts = reader.read_u32(order)
        official_levels = reader.read_u8(order)
        online_levels = reader.read_u32(order)
        demons = reader.read_u16(order)
        stars = reader.read_u32(order)
        map_packs = reader.read_u8(order)
        secret_coins = reader.read_u8(order)
        destroyed = reader.read_u32(order)
        liked = reader.read_u32(order)
        rated = reader.read_u32(order)
        user_coins = reader.read_u32(order)
        diamonds = reader.read_u32(order)
        orbs = reader.read_u32(order)
        daily_levels = reader.read_u32(order)
        fire_shards = reader.read_u16(order)
        ice_shards = reader.read_u16(order)
        poison_shards = reader.read_u16(order)
        shadow_shards = reader.read_u16(order)
        lava_shards = reader.read_u16(order)
        bonus_shards = reader.read_u16(order)
        total_orbs = reader.read_u32(order)

        official_coins_length = reader.read_u16(order)

        official_coins = {
            reader.read_u16(order): reader.read_u8(order) for _ in range(official_coins_length)
        }

        return cls(
            jumps=jumps,
            attempts=attempts,
            official_levels=official_levels,
            online_levels=online_levels,
            demons=demons,
            stars=stars,
            map_packs=map_packs,
            secret_coins=secret_coins,
            destroyed=destroyed,
            liked=liked,
            rated=rated,
            user_coins=user_coins,
            diamonds=diamonds,
            orbs=orbs,
            daily_levels=daily_levels,
            fire_shards=fire_shards,
            ice_shards=ice_shards,
            poison_shards=poison_shards,
            shadow_shards=shadow_shards,
            lava_shards=lava_shards,
            bonus_shards=bonus_shards,
            total_orbs=total_orbs,
            official_coins=official_coins,
        )


@define()
class Database:
    volume: float = field(default=1.0)
    sfx_volume: float = field(default=1.0)

    udid: str = field(default=EMPTY)
    name: str = field(default=EMPTY)
    id: int = field(default=DEFAULT_ID)
    account_id: int = field(default=DEFAULT_ID)
    password: str = field(default=EMPTY)
    session_id: int = field(default=DEFAULT_ID)

    cube_id: int = field(default=DEFAULT_ID)
    ship_id: int = field(default=DEFAULT_ID)
    ball_id: int = field(default=DEFAULT_ID)
    ufo_id: int = field(default=DEFAULT_ID)
    wave_id: int = field(default=DEFAULT_ID)
    spider_id: int = field(default=DEFAULT_ID)
    color_1_id: int = field(default=DEFAULT_ID)
    color_2_id: int = field(default=DEFAULT_ID)
    trail_id: int = field(default=DEFAULT_ID)
    explosion_id: int = field(default=DEFAULT_ID)

    icon_type: IconType = field(default=IconType.DEFAULT)

    secret_value: int = field(default=0)

    moderator: bool = field(default=False)

    values: Values = field(factory=Values)
    unlock_values: UnlockValues = field(factory=UnlockValues)
    custom_objects: List[List[Object]] = field(factory=list)

    statistics: Statistics = field(default=Statistics)

    show_song_markers: bool = field(default=True)
    show_progress_bar: bool = field(default=True)

    clicked_icons: bool = field(default=True)
    clicked_editor: bool = field(default=True)
    clicked_practice: bool = field(default=True)

    showed_editor_guide: bool = field(default=True)
    showed_low_detail: bool = field(default=True)

    bootups: int = field(default=0)

    rated_game: bool = field(default=False)

    official_levels: AnyLevelCollection = field(factory=level_collection)
    saved_levels: AnyLevelCollection = field(factory=level_collection)
    followed: OrderedSet[int] = field(factory=ordered_set)
    last_played: OrderedSet[int] = field(factory=ordered_set)
    filters: Filters = field(factory=Filters)
    daily_levels: AnyLevelCollection = field(factory=level_collection)
    daily_id: int = field(default=0)
    liked: Dict[int, int] = field(factory=dict)
    rated: Dict[int, int] = field(factory=dict)
    reported: OrderedSet[int] = field(factory=ordered_set)
    demon_rated: OrderedSet[int] = field(factory=ordered_set)
    gauntlet_levels: AnyLevelCollection = field(factory=level_collection)
    weekly_id: int = field(default=0)
    saved_folders: List[Folder] = field(factory=list)
    created_folders: List[Folder] = field(factory=list)

    created_levels: AnyLevelCollection = field(factory=level_collection)

    songs: OrderedSet[Song] = field(factory=ordered_set)

    # keybindings: Keybindings
