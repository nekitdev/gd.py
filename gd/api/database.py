from typing import BinaryIO, Dict, Iterable, List, Optional, Type, TypeVar

from attrs import define, field
from gd.api.api import API

from gd.api.level_api import LevelAPI
from gd.api.objects import Object
from gd.api.ordered_set import OrderedSet, ordered_set
from gd.binary import Binary
from gd.binary_utils import Reader, Writer
from gd.constants import DEFAULT_ID, EMPTY
from gd.enums import ByteOrder, Filter, IconType, LevelLeaderboardStrategy
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


DEFAULT_BUTTONS_PER_ROW = 6
DEFAULT_BUTTON_ROWS = 2

DEFAULT_CREATED_LEVELS_FOLDER_ID = 0
DEFAULT_SAVED_LEVELS_FOLDER_ID = 0

FOLLOW_PLAYER_BIT = 0b1
PLAY_MUSIC_BIT = 0b10
SWIPE_BIT = 0b100
FREE_MOVE_BIT = 0b1000
ROTATE_TOGGLED_BIT = 0b10000
SNAP_TOGGLED_BIT = 0b100000
IGNORE_DAMAGE_BIT = 0b1000000
PREVIEW_MODE_BIT = 0b10000000
SHOW_GROUND_BIT = 0b1_00000000
SHOW_GRID_BIT = 0b10_00000000
GRID_ON_TOP_BIT = 0b100_00000000
SHOW_OBJECT_INFO_BIT = 0b1000_00000000
SHOW_EFFECT_LINES_BIT = 0b10000_00000000
SHOW_TRIGGER_BOXES_BIT = 0b100000_00000000
DEBUG_DRAW_BIT = 0b1000000_00000000
HIDE_UI_ON_TEST_BIT = 0b10000000_00000000
HOLD_TO_SWIPE_BIT = 0b1_00000000_00000000
SHOW_DURATION_LINES_BIT = 0b10_00000000_00000000
SWIPE_CYCLE_BIT = 0b100_00000000_00000000
HIDE_BACKGROUND_BIT = 0b1000_00000000_00000000
HIDE_GRID_ON_PLAY_BIT = 0b10000_00000000_00000000
ENABLE_LINK_CONTROLS_BIT = 0b100000_00000000_00000000
SMOOTH_FIX_IN_EDITOR_BIT = 0b1000000_00000000_00000000

FLIP_TWO_PLAYER_CONTROLS_BIT = 0b1
ALWAYS_LIMIT_CONTROLS_BIT = 0b10
SHOWN_COMMENT_RULES_BIT = 0b100
INCREASE_MAX_HISTORY_BIT = 0b1000
DISABLE_EXPLOSION_SHAKE_BIT = 0b10000
FLIP_PAUSE_BUTTON_BIT = 0b100000
SHOWN_SONG_TERMS_BIT = 0b1000000
NO_SONG_LIMIT_BIT = 0b10000000
IN_MEMORY_SONGS_BIT = 0b1_00000000
HIGHER_AUDIO_QUALITY_BIT = 0b10_00000000
SMOOTH_FIX_BIT = 0b100_00000000
SHOW_CURSOR_IN_GAME_BIT = 0b1000_00000000
WINDOWED_BIT = 0b10000_00000000
AUTO_RETRY_BIT = 0b100000_00000000
AUTO_CHECKPOINTS_BIT = 0b1000000_00000000
DISABLE_ANALOG_STICK_BIT = 0b10000000_00000000
SHOWN_OPTIONS_BIT = 0b1_00000000_00000000
VSYNC_BIT = 0b10_00000000_00000000
CALL_GL_FINISH_BIT = 0b100_00000000_00000000
FORCE_TIMER_ENABLED_BIT = 0b1000_00000000_00000000
CHANGE_SONG_PATH_BIT = 0b10000_00000000_00000000
GAME_CENTER_ENABLED_BIT = 0b100000_00000000_00000000
SHOW_PERCENTAGE_BIT = 0b1000000_00000000_00000000
INCREASE_MAX_LEVELS_BIT = 0b10000000_00000000_00000000
SHOWN_PROFILE_INFO_BIT = 0b1_00000000_00000000_00000000
VIEWED_SELF_PROFILE_BIT = 0b10_00000000_00000000_00000000
SHOWN_NEWGROUNDS_MESSAGE_BIT = 0b100_00000000_00000000_00000000
FAST_PRACTICE_RESET_BIT = 0b1000_00000000_00000000_00000000
FREE_GAMES_BIT = 0b10000_00000000_00000000_00000000
CHECK_SERVER_ONLINE_BIT = 0b100000_00000000_00000000_00000000
DEFAULT_MINI_ICON_BIT = 0b1000000_00000000_00000000_00000000
SWITCH_SPIDER_TELEPORT_COLOR_BIT = 0b10000000_00000000_00000000_00000000
SWITCH_DASH_FIRE_COLOR_BIT = 0b1_00000000_00000000_00000000_00000000
SHOWN_UNVERIFIED_COINS_MESSAGE_BIT = 0b10_00000000_00000000_00000000_00000000
ENABLE_MOVE_OPTIMIZATION_BIT = 0b100_00000000_00000000_00000000_00000000
HIGH_CAPACITY_BIT = 0b1000_00000000_00000000_00000000_00000000
QUICK_CHECKPOINTS_BIT = 0b10000_00000000_00000000_00000000_00000000
SHOW_LEVEL_DESCRIPTION_BIT = 0b100000_00000000_00000000_00000000_00000000
SHOWN_UNLISTED_LEVEL_MESSAGE_BIT = 0b1000000_00000000_00000000_00000000_00000000
DISABLE_GRAVITY_EFFECT_BIT = 0b10000000_00000000_00000000_00000000_00000000
NEW_COMPLETED_FILTER_BIT = 0b1_00000000_00000000_00000000_00000000_00000000
SHOW_RESTART_BUTTON_BIT = 0b10_00000000_00000000_00000000_00000000_00000000
DISABLE_LEVEL_COMMENTS_BIT = 0b100_00000000_00000000_00000000_00000000_00000000
DISABLE_USER_COMMENTS_BIT = 0b1000_00000000_00000000_00000000_00000000_00000000
FEATURED_LEVELS_ONLY_BIT = 0b10000_00000000_00000000_00000000_00000000_00000000
DISABLE_SHAKE_BIT = 0b100000_00000000_00000000_00000000_00000000_00000000
DISABLE_HIGH_DETAIL_ALERT_BIT = 0b1000000_00000000_00000000_00000000_00000000_00000000
DISABLE_SONG_ALERT_BIT = 0b10000000_00000000_00000000_00000000_00000000_00000000
MANUAL_ORDER_BIT = 0b1_00000000_00000000_00000000_00000000_00000000_00000000
SMALL_COMMENTS_BIT = 0b10_00000000_00000000_00000000_00000000_00000000_00000000
EXTENDED_INFO_BIT = 0b100_00000000_00000000_00000000_00000000_00000000_00000000
AUTO_LOAD_COMMENTS_BIT = 0b1000_00000000_00000000_00000000_00000000_00000000_00000000
INCREASE_LOCAL_LEVELS_PER_PAGE_BIT = 0b10000_00000000_00000000_00000000_00000000_00000000_00000000
MORE_COMMENTS_BIT = 0b100000_00000000_00000000_00000000_00000000_00000000_00000000
JUST_DO_NOT_BIT = 0b1000000_00000000_00000000_00000000_00000000_00000000_00000000
SWITCH_WAVE_TRAIL_COLOR_BIT = 0b10000000_00000000_00000000_00000000_00000000_00000000_00000000
SHOW_RECORD_BIT = 0b1_00000000_00000000_00000000_00000000_00000000_00000000_00000000
PRACTICE_DEATH_EFFECT_BIT = 0b10_00000000_00000000_00000000_00000000_00000000_00000000_00000000
FORCE_SMOOTH_FIX_BIT = 0b100_00000000_00000000_00000000_00000000_00000000_00000000_00000000

FILTER_MASK = 0b11000000_00000000
FILTER_ID_MASK = 0b00111111_11111111

FILTER_SHIFT = FILTER_ID_MASK.bit_length()


V = TypeVar("V", bound="Variables")


@define()
class Variables(Binary, API):
    """Represents game variables."""

    follow_player: bool = True  # editor
    play_music: bool = True  # editor
    swipe: bool = False  # editor
    free_move: bool = False  # editor
    filter: Filter = Filter.DEFAULT
    filter_id: int = DEFAULT_ID
    rotate_toggled: bool = False  # editor
    snap_toggled: bool = False  # editor
    ignore_damage: bool = True  # editor
    flip_two_player_controls: bool = False  # normal
    always_limit_controls: bool = False  # normal
    shown_comment_rules: bool = True  # normal
    increase_max_history: bool = True  # normal
    disable_explosion_shake: bool = False  # normal
    flip_pause_button: bool = False  # normal
    shown_song_terms: bool = False  # normal
    no_song_limit: bool = True  # normal
    in_memory_songs: bool = True  # normal
    higher_audio_quality: bool = True  # normal
    smooth_fix: bool = False  # normal
    show_cursor_in_game: bool = False  # normal
    windowed: bool = False  # normal
    auto_retry: bool = True  # normal
    auto_checkpoints: bool = True  # normal
    disable_analog_stick: bool = False  # normal
    shown_options: bool = True  # normal
    vsync: bool = True  # normal
    call_gl_finish: bool = False  # normal
    force_timer_enabled: bool = False  # normal
    change_song_path: bool = False  # normal
    game_center_enabled: bool = False  # normal
    preview_mode: bool = True  # editor
    show_ground: bool = False  # editor
    show_grid: bool = True  # editor
    grid_on_top: bool = False  # editor
    show_percentage: bool = True  # normal
    show_object_info: bool = True  # editor
    increase_max_levels: bool = True  # normal
    show_effect_lines: bool = True  # editor
    show_trigger_boxes: bool = True  # editor
    debug_draw: bool = False  # editor
    hide_ui_on_test: bool = False  # editor
    shown_profile_info: bool = True  # normal
    viewed_self_profile: bool = True  # normal
    buttons_per_row: int = DEFAULT_BUTTONS_PER_ROW  # editor
    button_rows: int = DEFAULT_BUTTON_ROWS  # editor
    shown_newgrounds_message: bool = True  # normal
    fast_practice_reset: bool = False  # normal
    free_games: bool = False  # normal
    check_server_online: bool = True  # normal
    hold_to_swipe: bool = False  # editor
    show_duration_lines: bool = False  # editor
    swipe_cycle: bool = False  # editor
    default_mini_icon: bool = False  # normal
    switch_spider_teleport_color: bool = False  # normal
    switch_dash_fire_color: bool = False  # normal
    shown_unverified_coins_message: bool = True  # normal
    enable_move_optimization: bool = False  # normal
    high_capacity: bool = True  # normal
    quick_checkpoints: bool = False  # normal
    show_level_description: bool = True  # normal
    shown_unlisted_level_message: bool = True  # normal
    disable_gravity_effect: bool = False  # normal
    new_completed_filter: bool = False  # normal
    show_restart_button: bool = True  # normal
    disable_level_comments: bool = False  # normal
    disable_user_comments: bool = False  # normal
    featured_levels_only: bool = False  # normal
    hide_background: bool = False  # editor
    hide_grid_on_play: bool = True  # editor
    disable_shake: bool = False  # normal
    disable_high_detail_alert: bool = True  # normal
    disable_song_alert: bool = True  # normal
    manual_order: bool = False  # normal
    small_comments: bool = False  # normal
    extended_info: bool = True  # normal
    auto_load_comments: bool = True  # normal
    created_levels_folder_id: int = DEFAULT_CREATED_LEVELS_FOLDER_ID
    saved_levels_folder_id: int = DEFAULT_SAVED_LEVELS_FOLDER_ID
    increase_local_levels_per_page: bool = True  # normal
    more_comments: bool = False  # normal
    just_do_not: bool = False  # normal
    switch_wave_trail_color: bool = False  # normal
    enable_link_controls: bool = False  # editor
    level_leaderboard_strategy: LevelLeaderboardStrategy = LevelLeaderboardStrategy.DEFAULT
    show_record: bool = True  # normal
    practice_death_effect: bool = False  # normal
    force_smooth_fix: bool = False  # normal
    smooth_fix_in_editor: bool = False  # editor

    def is_follow_player(self) -> bool:
        return self.follow_player

    def is_play_music(self) -> bool:
        return self.play_music

    def is_swipe(self) -> bool:
        return self.swipe

    def is_free_move(self) -> bool:
        return self.free_move

    def is_rotate_toggled(self) -> bool:
        return self.rotate_toggled

    def is_snap_toggled(self) -> bool:
        return self.snap_toggled

    def is_ignore_damage(self) -> bool:
        return self.ignore_damage

    def is_flip_two_player_controls(self) -> bool:
        return self.flip_two_player_controls

    def is_always_limit_controls(self) -> bool:
        return self.always_limit_controls

    def has_shown_comment_rules(self) -> bool:
        return self.shown_comment_rules

    def is_increase_max_history(self) -> bool:
        return self.increase_max_history

    def is_disable_explosion_shake(self) -> bool:
        return self.disable_explosion_shake

    def is_flip_pause_button(self) -> bool:
        return self.flip_pause_button

    def has_shown_song_terms(self) -> bool:
        return self.shown_song_terms

    def is_no_song_limit(self) -> bool:
        return self.no_song_limit

    def is_in_memory_songs(self) -> bool:
        return self.in_memory_songs

    def is_higher_audio_quality(self) -> bool:
        return self.higher_audio_quality

    def is_smooth_fix(self) -> bool:
        return self.smooth_fix

    def is_show_cursor_in_game(self) -> bool:
        return self.show_cursor_in_game

    def is_windowed(self) -> bool:
        return self.windowed

    def is_auto_retry(self) -> bool:
        return self.auto_retry

    def is_auto_checkpoints(self) -> bool:
        return self.auto_checkpoints

    def is_disable_analog_stick(self) -> bool:
        return self.disable_analog_stick

    def has_shown_options(self) -> bool:
        return self.shown_options

    def is_vsync(self) -> bool:
        return self.vsync

    def is_call_gl_finish(self) -> bool:
        return self.call_gl_finish

    def is_force_timer_enabled(self) -> bool:
        return self.force_timer_enabled

    def is_change_song_path(self) -> bool:
        return self.change_song_path

    def is_game_center_enabled(self) -> bool:
        return self.game_center_enabled

    def is_preview_mode(self) -> bool:
        return self.preview_mode

    def is_show_ground(self) -> bool:
        return self.show_ground

    def is_show_grid(self) -> bool:
        return self.show_grid

    def is_grid_on_top(self) -> bool:
        return self.grid_on_top

    def is_show_percentage(self) -> bool:
        return self.show_percentage

    def is_show_object_info(self) -> bool:
        return self.show_object_info

    def is_increase_max_levels(self) -> bool:
        return self.increase_max_levels

    def is_show_effect_lines(self) -> bool:
        return self.show_effect_lines

    def is_show_trigger_boxes(self) -> bool:
        return self.show_trigger_boxes

    def is_debug_draw(self) -> bool:
        return self.debug_draw

    def is_hide_ui_on_test(self) -> bool:
        return self.hide_ui_on_test

    def has_shown_profile_info(self) -> bool:
        return self.shown_profile_info

    def has_viewed_self_profile(self) -> bool:
        return self.viewed_self_profile

    def has_shown_newgrounds_message(self) -> bool:
        return self.shown_newgrounds_message

    def is_fast_practice_reset(self) -> bool:
        return self.fast_practice_reset

    def is_free_games(self) -> bool:
        return self.free_games

    def is_check_server_online(self) -> bool:
        return self.check_server_online

    def is_hold_to_swipe(self) -> bool:
        return self.hold_to_swipe

    def is_show_duration_lines(self) -> bool:
        return self.show_duration_lines

    def is_swipe_cycle(self) -> bool:
        return self.swipe_cycle

    def is_default_mini_icon(self) -> bool:
        return self.default_mini_icon

    def is_switch_spider_teleport_color(self) -> bool:
        return self.switch_spider_teleport_color

    def is_switch_dash_fire_color(self) -> bool:
        return self.switch_dash_fire_color

    def has_shown_unverified_coins_message(self) -> bool:
        return self.shown_unverified_coins_message

    def is_enable_move_optimization(self) -> bool:
        return self.enable_move_optimization

    def is_high_capacity(self) -> bool:
        return self.high_capacity

    def is_quick_checkpoints(self) -> bool:
        return self.quick_checkpoints

    def is_show_level_description(self) -> bool:
        return self.show_level_description

    def has_shown_unlisted_level_message(self) -> bool:
        return self.shown_unlisted_level_message

    def is_disable_gravity_effect(self) -> bool:
        return self.disable_gravity_effect

    def is_new_completed_filter(self) -> bool:
        return self.new_completed_filter

    def is_show_restart_button(self) -> bool:
        return self.show_restart_button

    def is_disable_level_comments(self) -> bool:
        return self.disable_level_comments

    def is_disable_user_comments(self) -> bool:
        return self.disable_user_comments

    def is_featured_levels_only(self) -> bool:
        return self.featured_levels_only

    def is_hide_background(self) -> bool:
        return self.hide_background

    def is_hide_grid_on_play(self) -> bool:
        return self.hide_grid_on_play

    def is_disable_shake(self) -> bool:
        return self.disable_shake

    def is_disable_high_detail_alert(self) -> bool:
        return self.disable_high_detail_alert

    def is_disable_song_alert(self) -> bool:
        return self.disable_song_alert

    def is_manual_order(self) -> bool:
        return self.manual_order

    def is_small_comments(self) -> bool:
        return self.small_comments

    def is_extended_info(self) -> bool:
        return self.extended_info

    def is_auto_load_comments(self) -> bool:
        return self.auto_load_comments

    def is_increase_local_levels_per_page(self) -> bool:
        return self.increase_local_levels_per_page

    def is_more_comments(self) -> bool:
        return self.more_comments

    def is_just_do_not(self) -> bool:
        return self.just_do_not

    def is_switch_wave_trail_color(self) -> bool:
        return self.switch_wave_trail_color

    def is_enable_link_controls(self) -> bool:
        return self.enable_link_controls

    def is_show_record(self) -> bool:
        return self.show_record

    def is_practice_death_effect(self) -> bool:
        return self.practice_death_effect

    def is_force_smooth_fix(self) -> bool:
        return self.force_smooth_fix

    def is_smooth_fix_in_editor(self) -> bool:
        return self.smooth_fix_in_editor

    @classmethod
    def from_binary(cls: Type[V], binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT) -> V:
        reader = Reader(binary)

        follow_player_bit = FOLLOW_PLAYER_BIT
        play_music_bit = PLAY_MUSIC_BIT
        swipe_bit = SWIPE_BIT
        free_move_bit = FREE_MOVE_BIT
        rotate_toggled_bit = ROTATE_TOGGLED_BIT
        snap_toggled_bit = SNAP_TOGGLED_BIT
        ignore_damage_bit = IGNORE_DAMAGE_BIT
        preview_mode_bit = PREVIEW_MODE_BIT
        show_ground_bit = SHOW_GROUND_BIT
        show_grid_bit = SHOW_GRID_BIT
        grid_on_top_bit = GRID_ON_TOP_BIT
        show_object_info_bit = SHOW_OBJECT_INFO_BIT
        show_effect_lines_bit = SHOW_EFFECT_LINES_BIT
        show_trigger_boxes_bit = SHOW_TRIGGER_BOXES_BIT
        debug_draw_bit = DEBUG_DRAW_BIT
        hide_ui_on_test_bit = HIDE_UI_ON_TEST_BIT
        hold_to_swipe_bit = HOLD_TO_SWIPE_BIT
        show_duration_lines_bit = SHOW_DURATION_LINES_BIT
        swipe_cycle_bit = SWIPE_CYCLE_BIT
        hide_background_bit = HIDE_BACKGROUND_BIT
        hide_grid_on_play_bit = HIDE_GRID_ON_PLAY_BIT
        enable_link_controls_bit = ENABLE_LINK_CONTROLS_BIT
        smooth_fix_in_editor_bit = SMOOTH_FIX_IN_EDITOR_BIT

        flip_two_player_controls_bit = FLIP_TWO_PLAYER_CONTROLS_BIT
        always_limit_controls_bit = ALWAYS_LIMIT_CONTROLS_BIT
        shown_comment_rules_bit = SHOWN_COMMENT_RULES_BIT
        increase_max_history_bit = INCREASE_MAX_HISTORY_BIT
        disable_explosion_shake_bit = DISABLE_EXPLOSION_SHAKE_BIT
        flip_pause_button_bit = FLIP_PAUSE_BUTTON_BIT
        shown_song_terms_bit = SHOWN_SONG_TERMS_BIT
        no_song_limit_bit = NO_SONG_LIMIT_BIT
        in_memory_songs_bit = IN_MEMORY_SONGS_BIT
        higher_audio_quality_bit = HIGHER_AUDIO_QUALITY_BIT
        smooth_fix_bit = SMOOTH_FIX_BIT
        show_cursor_in_game_bit = SHOW_CURSOR_IN_GAME_BIT
        windowed_bit = WINDOWED_BIT
        auto_retry_bit = AUTO_RETRY_BIT
        auto_checkpoints_bit = AUTO_CHECKPOINTS_BIT
        disable_analog_stick_bit = DISABLE_ANALOG_STICK_BIT
        shown_options_bit = SHOWN_OPTIONS_BIT
        vsync_bit = VSYNC_BIT
        call_gl_finish_bit = CALL_GL_FINISH_BIT
        force_timer_enabled_bit = FORCE_TIMER_ENABLED_BIT
        change_song_path_bit = CHANGE_SONG_PATH_BIT
        game_center_enabled_bit = GAME_CENTER_ENABLED_BIT
        show_percentage_bit = SHOW_PERCENTAGE_BIT
        increase_max_levels_bit = INCREASE_MAX_LEVELS_BIT
        shown_profile_info_bit = SHOWN_PROFILE_INFO_BIT
        viewed_self_profile_bit = VIEWED_SELF_PROFILE_BIT
        shown_newgrounds_message_bit = SHOWN_NEWGROUNDS_MESSAGE_BIT
        fast_practice_reset_bit = FAST_PRACTICE_RESET_BIT
        free_games_bit = FREE_GAMES_BIT
        check_server_online_bit = CHECK_SERVER_ONLINE_BIT
        default_mini_icon_bit = DEFAULT_MINI_ICON_BIT
        switch_spider_teleport_color_bit = SWITCH_SPIDER_TELEPORT_COLOR_BIT
        switch_dash_fire_color_bit = SWITCH_DASH_FIRE_COLOR_BIT
        shown_unverified_coins_message_bit = SHOWN_UNVERIFIED_COINS_MESSAGE_BIT
        enable_move_optimization_bit = ENABLE_MOVE_OPTIMIZATION_BIT
        high_capacity_bit = HIGH_CAPACITY_BIT
        quick_checkpoints_bit = QUICK_CHECKPOINTS_BIT
        show_level_description_bit = SHOW_LEVEL_DESCRIPTION_BIT
        shown_unlisted_level_message_bit = SHOWN_UNLISTED_LEVEL_MESSAGE_BIT
        disable_gravity_effect_bit = DISABLE_GRAVITY_EFFECT_BIT
        new_completed_filter_bit = NEW_COMPLETED_FILTER_BIT
        show_restart_button_bit = SHOW_RESTART_BUTTON_BIT
        disable_level_comments_bit = DISABLE_LEVEL_COMMENTS_BIT
        disable_user_comments_bit = DISABLE_USER_COMMENTS_BIT
        featured_levels_only_bit = FEATURED_LEVELS_ONLY_BIT
        disable_shake_bit = DISABLE_SHAKE_BIT
        disable_high_detail_alert_bit = DISABLE_HIGH_DETAIL_ALERT_BIT
        disable_song_alert_bit = DISABLE_SONG_ALERT_BIT
        manual_order_bit = MANUAL_ORDER_BIT
        small_comments_bit = SMALL_COMMENTS_BIT
        extended_info_bit = EXTENDED_INFO_BIT
        auto_load_comments_bit = AUTO_LOAD_COMMENTS_BIT
        increase_local_levels_per_page_bit = INCREASE_LOCAL_LEVELS_PER_PAGE_BIT
        more_comments_bit = MORE_COMMENTS_BIT
        just_do_not_bit = JUST_DO_NOT_BIT
        switch_wave_trail_color_bit = SWITCH_WAVE_TRAIL_COLOR_BIT
        show_record_bit = SHOW_RECORD_BIT
        practice_death_effect_bit = PRACTICE_DEATH_EFFECT_BIT
        force_smooth_fix_bit = FORCE_SMOOTH_FIX_BIT

        value = reader.read_u32(order)

        follow_player = value & follow_player_bit == follow_player_bit
        play_music = value & play_music_bit == play_music_bit
        swipe = value & swipe_bit == swipe_bit
        free_move = value & free_move_bit == free_move_bit
        rotate_toggled = value & rotate_toggled_bit == rotate_toggled_bit
        snap_toggled = value & snap_toggled_bit == snap_toggled_bit
        ignore_damage = value & ignore_damage_bit == ignore_damage_bit
        preview_mode = value & preview_mode_bit == preview_mode_bit
        show_ground = value & show_ground_bit == show_ground_bit
        show_grid = value & show_grid_bit == show_grid_bit
        grid_on_top = value & grid_on_top_bit == grid_on_top_bit
        show_object_info = value & show_object_info_bit == show_object_info_bit
        show_effect_lines = value & show_effect_lines_bit == show_effect_lines_bit
        show_trigger_boxes = value & show_trigger_boxes_bit == show_trigger_boxes_bit
        debug_draw = value & debug_draw_bit == debug_draw_bit
        hide_ui_on_test = value & hide_ui_on_test_bit == hide_ui_on_test_bit
        hold_to_swipe = value & hold_to_swipe_bit == hold_to_swipe_bit
        show_duration_lines = value & show_duration_lines_bit == show_duration_lines_bit
        swipe_cycle = value & swipe_cycle_bit == swipe_cycle_bit
        hide_background = value & hide_background_bit == hide_background_bit
        hide_grid_on_play = value & hide_grid_on_play_bit == hide_grid_on_play_bit
        enable_link_controls = value & enable_link_controls_bit == enable_link_controls_bit
        smooth_fix_in_editor = value & smooth_fix_in_editor_bit == smooth_fix_in_editor_bit

        filter_value = reader.read_u16(order)

        filter_id = filter_value & FILTER_ID_MASK

        filter = Filter(filter_value >> FILTER_SHIFT)

        buttons_per_row = reader.read_u8(order)
        button_rows = reader.read_u8(order)

        created_levels_folder_id = reader.read_u8(order)
        saved_levels_folder_id = reader.read_u8(order)

        level_leaderboard_strategy_value = reader.read_u8(order)

        level_leaderboard_strategy = LevelLeaderboardStrategy(level_leaderboard_strategy_value)

        value = reader.read_u64(order)

        flip_two_player_controls = (
            value & flip_two_player_controls_bit == flip_two_player_controls_bit
        )
        always_limit_controls = value & always_limit_controls_bit == always_limit_controls_bit
        shown_comment_rules = value & shown_comment_rules_bit == shown_comment_rules_bit
        increase_max_history = value & increase_max_history_bit == increase_max_history_bit
        disable_explosion_shake = value & disable_explosion_shake_bit == disable_explosion_shake_bit
        flip_pause_button = value & flip_pause_button_bit == flip_pause_button_bit
        shown_song_terms = value & shown_song_terms_bit == shown_song_terms_bit
        no_song_limit = value & no_song_limit_bit == no_song_limit_bit
        in_memory_songs = value & in_memory_songs_bit == in_memory_songs_bit
        higher_audio_quality = value & higher_audio_quality_bit == higher_audio_quality_bit
        smooth_fix = value & smooth_fix_bit == smooth_fix_bit
        show_cursor_in_game = value & show_cursor_in_game_bit == show_cursor_in_game_bit
        windowed = value & windowed_bit == windowed_bit
        auto_retry = value & auto_retry_bit == auto_retry_bit
        auto_checkpoints = value & auto_checkpoints_bit == auto_checkpoints_bit
        disable_analog_stick = value & disable_analog_stick_bit == disable_analog_stick_bit
        shown_options = value & shown_options_bit == shown_options_bit
        vsync = value & vsync_bit == vsync_bit
        call_gl_finish = value & call_gl_finish_bit == call_gl_finish_bit
        force_timer_enabled = value & force_timer_enabled_bit == force_timer_enabled_bit
        change_song_path = value & change_song_path_bit == change_song_path_bit
        game_center_enabled = value & game_center_enabled_bit == game_center_enabled_bit
        show_percentage = value & show_percentage_bit == show_percentage_bit
        increase_max_levels = value & increase_max_levels_bit == increase_max_levels_bit
        shown_profile_info = value & shown_profile_info_bit == shown_profile_info_bit
        viewed_self_profile = value & viewed_self_profile_bit == viewed_self_profile_bit
        shown_newgrounds_message = (
            value & shown_newgrounds_message_bit == shown_newgrounds_message_bit
        )
        fast_practice_reset = value & fast_practice_reset_bit == fast_practice_reset_bit
        free_games = value & free_games_bit == free_games_bit
        check_server_online = value & check_server_online_bit == check_server_online_bit
        default_mini_icon = value & default_mini_icon_bit == default_mini_icon_bit
        switch_spider_teleport_color = (
            value & switch_spider_teleport_color_bit == switch_spider_teleport_color_bit
        )
        switch_dash_fire_color = value & switch_dash_fire_color_bit == switch_dash_fire_color_bit
        shown_unverified_coins_message = (
            value & shown_unverified_coins_message_bit == shown_unverified_coins_message_bit
        )
        enable_move_optimization = (
            value & enable_move_optimization_bit == enable_move_optimization_bit
        )
        high_capacity = value & high_capacity_bit == high_capacity_bit
        quick_checkpoints = value & quick_checkpoints_bit == quick_checkpoints_bit
        show_level_description = value & show_level_description_bit == show_level_description_bit
        shown_unlisted_level_message = (
            value & shown_unlisted_level_message_bit == shown_unlisted_level_message_bit
        )
        disable_gravity_effect = value & disable_gravity_effect_bit == disable_gravity_effect_bit
        new_completed_filter = value & new_completed_filter_bit == new_completed_filter_bit
        show_restart_button = value & show_restart_button_bit == show_restart_button_bit
        disable_level_comments = value & disable_level_comments_bit == disable_level_comments_bit
        disable_user_comments = value & disable_user_comments_bit == disable_user_comments_bit
        featured_levels_only = value & featured_levels_only_bit == featured_levels_only_bit
        disable_shake = value & disable_shake_bit == disable_shake_bit
        disable_high_detail_alert = (
            value & disable_high_detail_alert_bit == disable_high_detail_alert_bit
        )
        disable_song_alert = value & disable_song_alert_bit == disable_song_alert_bit
        manual_order = value & manual_order_bit == manual_order_bit
        small_comments = value & small_comments_bit == small_comments_bit
        extended_info = value & extended_info_bit == extended_info_bit
        auto_load_comments = value & auto_load_comments_bit == auto_load_comments_bit
        increase_local_levels_per_page = (
            value & increase_local_levels_per_page_bit == increase_local_levels_per_page_bit
        )
        more_comments = value & more_comments_bit == more_comments_bit
        just_do_not = value & just_do_not_bit == just_do_not_bit
        switch_wave_trail_color = value & switch_wave_trail_color_bit == switch_wave_trail_color_bit
        show_record = value & show_record_bit == show_record_bit
        practice_death_effect = value & practice_death_effect_bit == practice_death_effect_bit
        force_smooth_fix = value & force_smooth_fix_bit == force_smooth_fix_bit

        return cls(
            follow_player=follow_player,
            play_music=play_music,
            swipe=swipe,
            free_move=free_move,
            filter=filter,
            filter_id=filter_id,
            rotate_toggled=rotate_toggled,
            snap_toggled=snap_toggled,
            ignore_damage=ignore_damage,
            flip_two_player_controls=flip_two_player_controls,
            always_limit_controls=always_limit_controls,
            shown_comment_rules=shown_comment_rules,
            increase_max_history=increase_max_history,
            disable_explosion_shake=disable_explosion_shake,
            flip_pause_button=flip_pause_button,
            shown_song_terms=shown_song_terms,
            no_song_limit=no_song_limit,
            in_memory_songs=in_memory_songs,
            higher_audio_quality=higher_audio_quality,
            smooth_fix=smooth_fix,
            show_cursor_in_game=show_cursor_in_game,
            windowed=windowed,
            auto_retry=auto_retry,
            auto_checkpoints=auto_checkpoints,
            disable_analog_stick=disable_analog_stick,
            shown_options=shown_options,
            vsync=vsync,
            call_gl_finish=call_gl_finish,
            force_timer_enabled=force_timer_enabled,
            change_song_path=change_song_path,
            game_center_enabled=game_center_enabled,
            preview_mode=preview_mode,
            show_ground=show_ground,
            show_grid=show_grid,
            grid_on_top=grid_on_top,
            show_percentage=show_percentage,
            show_object_info=show_object_info,
            increase_max_levels=increase_max_levels,
            show_effect_lines=show_effect_lines,
            show_trigger_boxes=show_trigger_boxes,
            debug_draw=debug_draw,
            hide_ui_on_test=hide_ui_on_test,
            shown_profile_info=shown_profile_info,
            viewed_self_profile=viewed_self_profile,
            buttons_per_row=buttons_per_row,
            button_rows=button_rows,
            shown_newgrounds_message=shown_newgrounds_message,
            fast_practice_reset=fast_practice_reset,
            free_games=free_games,
            check_server_online=check_server_online,
            hold_to_swipe=hold_to_swipe,
            show_duration_lines=show_duration_lines,
            swipe_cycle=swipe_cycle,
            default_mini_icon=default_mini_icon,
            switch_spider_teleport_color=switch_spider_teleport_color,
            switch_dash_fire_color=switch_dash_fire_color,
            shown_unverified_coins_message=shown_unverified_coins_message,
            enable_move_optimization=enable_move_optimization,
            high_capacity=high_capacity,
            quick_checkpoints=quick_checkpoints,
            show_level_description=show_level_description,
            shown_unlisted_level_message=shown_unlisted_level_message,
            disable_gravity_effect=disable_gravity_effect,
            new_completed_filter=new_completed_filter,
            show_restart_button=show_restart_button,
            disable_level_comments=disable_level_comments,
            disable_user_comments=disable_user_comments,
            featured_levels_only=featured_levels_only,
            hide_background=hide_background,
            hide_grid_on_play=hide_grid_on_play,
            disable_shake=disable_shake,
            disable_high_detail_alert=disable_high_detail_alert,
            disable_song_alert=disable_song_alert,
            manual_order=manual_order,
            small_comments=small_comments,
            extended_info=extended_info,
            auto_load_comments=auto_load_comments,
            created_levels_folder_id=created_levels_folder_id,
            saved_levels_folder_id=saved_levels_folder_id,
            increase_local_levels_per_page=increase_local_levels_per_page,
            more_comments=more_comments,
            just_do_not=just_do_not,
            switch_wave_trail_color=switch_wave_trail_color,
            enable_link_controls=enable_link_controls,
            level_leaderboard_strategy=level_leaderboard_strategy,
            show_record=show_record,
            practice_death_effect=practice_death_effect,
            force_smooth_fix=force_smooth_fix,
            smooth_fix_in_editor=smooth_fix_in_editor,
        )

    def to_binary(self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT) -> None:
        writer = Writer(binary)

        value = 0

        if self.is_follow_player():
            value |= FOLLOW_PLAYER_BIT

        if self.is_play_music():
            value |= PLAY_MUSIC_BIT

        if self.is_swipe():
            value |= SWIPE_BIT

        if self.is_free_move():
            value |= FREE_MOVE_BIT

        if self.is_rotate_toggled():
            value |= ROTATE_TOGGLED_BIT

        if self.is_snap_toggled():
            value |= SNAP_TOGGLED_BIT

        if self.is_ignore_damage():
            value |= IGNORE_DAMAGE_BIT

        if self.is_preview_mode():
            value |= PREVIEW_MODE_BIT

        if self.is_show_ground():
            value |= SHOW_GROUND_BIT

        if self.is_show_grid():
            value |= SHOW_GRID_BIT

        if self.is_grid_on_top():
            value |= GRID_ON_TOP_BIT

        if self.is_show_object_info():
            value |= SHOW_OBJECT_INFO_BIT

        if self.is_show_effect_lines():
            value |= SHOW_EFFECT_LINES_BIT

        if self.is_show_trigger_boxes():
            value |= SHOW_TRIGGER_BOXES_BIT

        if self.is_debug_draw():
            value |= DEBUG_DRAW_BIT

        if self.is_hide_ui_on_test():
            value |= HIDE_UI_ON_TEST_BIT

        if self.is_hold_to_swipe():
            value |= HOLD_TO_SWIPE_BIT

        if self.is_show_duration_lines():
            value |= SHOW_DURATION_LINES_BIT

        if self.is_swipe_cycle():
            value |= SWIPE_CYCLE_BIT

        if self.is_hide_background():
            value |= HIDE_BACKGROUND_BIT

        if self.is_hide_grid_on_play():
            value |= HIDE_GRID_ON_PLAY_BIT

        if self.is_enable_link_controls():
            value |= ENABLE_LINK_CONTROLS_BIT

        if self.is_smooth_fix_in_editor():
            value |= SMOOTH_FIX_IN_EDITOR_BIT

        writer.write_u32(value, order)

        filter_value = (self.filter.value << FILTER_SHIFT) | self.filter_id

        writer.write_u16(filter_value, order)

        writer.write_u8(self.buttons_per_row, order)
        writer.write_u8(self.button_rows, order)

        writer.write_u8(self.created_levels_folder_id, order)
        writer.write_u8(self.saved_levels_folder_id, order)

        writer.write_u8(self.level_leaderboard_strategy.value, order)

        value = 0

        if self.is_flip_two_player_controls():
            value |= FLIP_TWO_PLAYER_CONTROLS_BIT

        if self.is_always_limit_controls():
            value |= ALWAYS_LIMIT_CONTROLS_BIT

        if self.has_shown_comment_rules():
            value |= SHOWN_COMMENT_RULES_BIT

        if self.is_increase_max_history():
            value |= INCREASE_MAX_HISTORY_BIT

        if self.is_disable_explosion_shake():
            value |= DISABLE_EXPLOSION_SHAKE_BIT

        if self.is_flip_pause_button():
            value |= FLIP_PAUSE_BUTTON_BIT

        if self.has_shown_song_terms():
            value |= SHOWN_SONG_TERMS_BIT

        if self.is_no_song_limit():
            value |= NO_SONG_LIMIT_BIT

        if self.is_in_memory_songs():
            value |= IN_MEMORY_SONGS_BIT

        if self.is_higher_audio_quality():
            value |= HIGHER_AUDIO_QUALITY_BIT

        if self.is_smooth_fix():
            value |= SMOOTH_FIX_BIT

        if self.is_show_cursor_in_game():
            value |= SHOW_CURSOR_IN_GAME_BIT

        if self.is_windowed():
            value |= WINDOWED_BIT

        if self.is_auto_retry():
            value |= AUTO_RETRY_BIT

        if self.is_auto_checkpoints():
            value |= AUTO_CHECKPOINTS_BIT

        if self.is_disable_analog_stick():
            value |= DISABLE_ANALOG_STICK_BIT

        if self.has_shown_options():
            value |= SHOWN_OPTIONS_BIT

        if self.is_vsync():
            value |= VSYNC_BIT

        if self.is_call_gl_finish():
            value |= CALL_GL_FINISH_BIT

        if self.is_force_timer_enabled():
            value |= FORCE_TIMER_ENABLED_BIT

        if self.is_change_song_path():
            value |= CHANGE_SONG_PATH_BIT

        if self.is_game_center_enabled():
            value |= GAME_CENTER_ENABLED_BIT

        if self.is_show_percentage():
            value |= SHOW_PERCENTAGE_BIT

        if self.is_increase_max_levels():
            value |= INCREASE_MAX_LEVELS_BIT

        if self.has_shown_profile_info():
            value |= SHOWN_PROFILE_INFO_BIT

        if self.has_viewed_self_profile():
            value |= VIEWED_SELF_PROFILE_BIT

        if self.has_shown_newgrounds_message():
            value |= SHOWN_NEWGROUNDS_MESSAGE_BIT

        if self.is_fast_practice_reset():
            value |= FAST_PRACTICE_RESET_BIT

        if self.is_free_games():
            value |= FREE_GAMES_BIT

        if self.is_check_server_online():
            value |= CHECK_SERVER_ONLINE_BIT

        if self.is_default_mini_icon():
            value |= DEFAULT_MINI_ICON_BIT

        if self.is_switch_spider_teleport_color():
            value |= SWITCH_SPIDER_TELEPORT_COLOR_BIT

        if self.is_switch_dash_fire_color():
            value |= SWITCH_DASH_FIRE_COLOR_BIT

        if self.has_shown_unverified_coins_message():
            value |= SHOWN_UNVERIFIED_COINS_MESSAGE_BIT

        if self.is_enable_move_optimization():
            value |= ENABLE_MOVE_OPTIMIZATION_BIT

        if self.is_high_capacity():
            value |= HIGH_CAPACITY_BIT

        if self.is_quick_checkpoints():
            value |= QUICK_CHECKPOINTS_BIT

        if self.is_show_level_description():
            value |= SHOW_LEVEL_DESCRIPTION_BIT

        if self.has_shown_unlisted_level_message():
            value |= SHOWN_UNLISTED_LEVEL_MESSAGE_BIT

        if self.is_disable_gravity_effect():
            value |= DISABLE_GRAVITY_EFFECT_BIT

        if self.is_new_completed_filter():
            value |= NEW_COMPLETED_FILTER_BIT

        if self.is_show_restart_button():
            value |= SHOW_RESTART_BUTTON_BIT

        if self.is_disable_level_comments():
            value |= DISABLE_LEVEL_COMMENTS_BIT

        if self.is_disable_user_comments():
            value |= DISABLE_USER_COMMENTS_BIT

        if self.is_featured_levels_only():
            value |= FEATURED_LEVELS_ONLY_BIT

        if self.is_disable_shake():
            value |= DISABLE_SHAKE_BIT

        if self.is_disable_high_detail_alert():
            value |= DISABLE_HIGH_DETAIL_ALERT_BIT

        if self.is_disable_song_alert():
            value |= DISABLE_SONG_ALERT_BIT

        if self.is_manual_order():
            value |= MANUAL_ORDER_BIT

        if self.is_small_comments():
            value |= SMALL_COMMENTS_BIT

        if self.is_extended_info():
            value |= EXTENDED_INFO_BIT

        if self.is_auto_load_comments():
            value |= AUTO_LOAD_COMMENTS_BIT

        if self.is_increase_local_levels_per_page():
            value |= INCREASE_LOCAL_LEVELS_PER_PAGE_BIT

        if self.is_more_comments():
            value |= MORE_COMMENTS_BIT

        if self.is_just_do_not():
            value |= JUST_DO_NOT_BIT

        if self.is_switch_wave_trail_color():
            value |= SWITCH_WAVE_TRAIL_COLOR_BIT

        if self.is_show_record():
            value |= SHOW_RECORD_BIT

        if self.is_practice_death_effect():
            value |= PRACTICE_DEATH_EFFECT_BIT

        if self.is_force_smooth_fix():
            value |= FORCE_SMOOTH_FIX_BIT

        writer.write_u64(value, order)


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


THE_CHALLENGE_UNLOCKED_BIT = 0b1
GUBFLUB_HINT_1_BIT = 0b10
GUBFLUB_HINT_2_BIT = 0b100
THE_CHALLENGE_COMPLETED_BIT = 0b1000
TREASURE_ROOM_UNLOCKED_BIT = 0b10000
CHAMBER_OF_TIME_UNLOCKED_BIT = 0b100000
CHAMBER_OF_TIME_DISCOVERED_BIT = 0b1000000
MASTER_EMBLEM_SHOWN_BIT = 0b10000000
GATE_KEEPER_DIALOG_BIT = 0b1_00000000
SCRATCH_DIALOG_BIT = 0b10_00000000
SECRET_SHOP_UNLOCKED_BIT = 0b100_00000000
DEMON_GUARDIAN_DIALOG_BIT = 0b1000_00000000
DEMON_FREED_BIT = 0b10000_00000000
DEMON_KEY_1_BIT = 0b100000_00000000
DEMON_KEY_2_BIT = 0b1000000_00000000
DEMON_KEY_3_BIT = 0b10000000_00000000
SHOP_KEEPER_DIALOG_BIT = 0b1_00000000_00000000
WORLD_ONLINE_LEVELS_BIT = 0b10_00000000_00000000
DEMON_DISCOVERED_BIT = 0b100_00000000_00000000
COMMUNITY_SHOP_UNLOCKED_BIT = 0b1000_00000000_00000000
POTBOR_DIALOG_BIT = 0b10000_00000000_00000000
YOUTUBE_CHEST_UNLOCKED_BIT = 0b100000_00000000_00000000
FACEBOOK_CHEST_UNLOCKED_BIT = 0b1000000_00000000_00000000
TWITTER_CHEST_UNLOCKED_BIT = 0b10000000_00000000_00000000
# FIREBIRD_GATE_KEEPER_BIT = 0b1_00000000_00000000_00000000
# TWITCH_CHEST_UNLOCKED_BIT = 0b10_00000000_00000000_00000000
# DISCORD_CHEST_UNLOCKED_BIT = 0b100_00000000_00000000_00000000

UV = TypeVar("UV", bound="UnlockValues")


@define()
class UnlockValues(Binary, API):
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

    @classmethod
    def from_binary(cls: Type[UV], binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT) -> UV:
        reader = Reader(binary)

        the_challenge_unlocked_bit = THE_CHALLENGE_UNLOCKED_BIT
        gubflub_hint_1_bit = GUBFLUB_HINT_1_BIT
        gubflub_hint_2_bit = GUBFLUB_HINT_2_BIT
        the_challenge_completed_bit = THE_CHALLENGE_COMPLETED_BIT
        treasure_room_unlocked_bit = TREASURE_ROOM_UNLOCKED_BIT
        chamber_of_time_unlocked_bit = CHAMBER_OF_TIME_UNLOCKED_BIT
        chamber_of_time_discovered_bit = CHAMBER_OF_TIME_DISCOVERED_BIT
        master_emblem_shown_bit = MASTER_EMBLEM_SHOWN_BIT
        gate_keeper_dialog_bit = GATE_KEEPER_DIALOG_BIT
        scratch_dialog_bit = SCRATCH_DIALOG_BIT
        secret_shop_unlocked_bit = SECRET_SHOP_UNLOCKED_BIT
        demon_guardian_dialog_bit = DEMON_GUARDIAN_DIALOG_BIT
        demon_freed_bit = DEMON_FREED_BIT
        demon_key_1_bit = DEMON_KEY_1_BIT
        demon_key_2_bit = DEMON_KEY_2_BIT
        demon_key_3_bit = DEMON_KEY_3_BIT
        shop_keeper_dialog_bit = SHOP_KEEPER_DIALOG_BIT
        world_online_levels_bit = WORLD_ONLINE_LEVELS_BIT
        demon_discovered_bit = DEMON_DISCOVERED_BIT
        community_shop_unlocked_bit = COMMUNITY_SHOP_UNLOCKED_BIT
        potbor_dialog_bit = POTBOR_DIALOG_BIT
        youtube_chest_unlocked_bit = YOUTUBE_CHEST_UNLOCKED_BIT
        facebook_chest_unlocked_bit = FACEBOOK_CHEST_UNLOCKED_BIT
        twitter_chest_unlocked_bit = TWITTER_CHEST_UNLOCKED_BIT
        # firebird_gate_keeper_bit = FIREBIRD_GATE_KEEPER_BIT
        # twitch_chest_unlocked_bit = TWITCH_CHEST_UNLOCKED_BIT
        # discord_chest_unlocked_bit = DISCORD_CHEST_UNLOCKED_BIT

        value = reader.read_u64(order)

        the_challenge_unlocked = value & the_challenge_unlocked_bit == the_challenge_unlocked_bit
        gubflub_hint_1 = value & gubflub_hint_1_bit == gubflub_hint_1_bit
        gubflub_hint_2 = value & gubflub_hint_2_bit == gubflub_hint_2_bit
        the_challenge_completed = value & the_challenge_completed_bit == the_challenge_completed_bit
        treasure_room_unlocked = value & treasure_room_unlocked_bit == treasure_room_unlocked_bit
        chamber_of_time_unlocked = (
            value & chamber_of_time_unlocked_bit == chamber_of_time_unlocked_bit
        )
        chamber_of_time_discovered = (
            value & chamber_of_time_discovered_bit == chamber_of_time_discovered_bit
        )
        master_emblem_shown = value & master_emblem_shown_bit == master_emblem_shown_bit
        gate_keeper_dialog = value & gate_keeper_dialog_bit == gate_keeper_dialog_bit
        scratch_dialog = value & scratch_dialog_bit == scratch_dialog_bit
        secret_shop_unlocked = value & secret_shop_unlocked_bit == secret_shop_unlocked_bit
        demon_guardian_dialog = value & demon_guardian_dialog_bit == demon_guardian_dialog_bit
        demon_freed = value & demon_freed_bit == demon_freed_bit
        demon_key_1 = value & demon_key_1_bit == demon_key_1_bit
        demon_key_2 = value & demon_key_2_bit == demon_key_2_bit
        demon_key_3 = value & demon_key_3_bit == demon_key_3_bit
        shop_keeper_dialog = value & shop_keeper_dialog_bit == shop_keeper_dialog_bit
        world_online_levels = value & world_online_levels_bit == world_online_levels_bit
        demon_discovered = value & demon_discovered_bit == demon_discovered_bit
        community_shop_unlocked = value & community_shop_unlocked_bit == community_shop_unlocked_bit
        potbor_dialog = value & potbor_dialog_bit == potbor_dialog_bit
        youtube_chest_unlocked = value & youtube_chest_unlocked_bit == youtube_chest_unlocked_bit
        facebook_chest_unlocked = value & facebook_chest_unlocked_bit == facebook_chest_unlocked_bit
        twitter_chest_unlocked = value & twitter_chest_unlocked_bit == twitter_chest_unlocked_bit
        # firebird_gate_keeper = value & firebird_gate_keeper_bit == firebird_gate_keeper_bit
        # twitch_chest_unlocked = value & twitch_chest_unlocked_bit == twitch_chest_unlocked_bit
        # discord_chest_unlocked = value & discord_chest_unlocked_bit == discord_chest_unlocked_bit

        return cls(
            the_challenge_unlocked=the_challenge_unlocked,
            gubflub_hint_1=gubflub_hint_1,
            gubflub_hint_2=gubflub_hint_2,
            the_challenge_completed=the_challenge_completed,
            treasure_room_unlocked=treasure_room_unlocked,
            chamber_of_time_unlocked=chamber_of_time_unlocked,
            chamber_of_time_discovered=chamber_of_time_discovered,
            master_emblem_shown=master_emblem_shown,
            gate_keeper_dialog=gate_keeper_dialog,
            scratch_dialog=scratch_dialog,
            secret_shop_unlocked=secret_shop_unlocked,
            demon_guardian_dialog=demon_guardian_dialog,
            demon_freed=demon_freed,
            demon_key_1=demon_key_1,
            demon_key_2=demon_key_2,
            demon_key_3=demon_key_3,
            shop_keeper_dialog=shop_keeper_dialog,
            world_online_levels=world_online_levels,
            demon_discovered=demon_discovered,
            community_shop_unlocked=community_shop_unlocked,
            potbor_dialog=potbor_dialog,
            youtube_chest_unlocked=youtube_chest_unlocked,
            facebook_chest_unlocked=facebook_chest_unlocked,
            twitter_chest_unlocked=twitter_chest_unlocked,
            # firebird_gate_keeper=firebird_gate_keeper,
            # twitch_chest_unlocked=twitch_chest_unlocked,
            # discord_chest_unlocked=discord_chest_unlocked,
        )

    def to_binary(self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT) -> None:
        writer = Writer(binary)

        value = 0

        if self.is_the_challenge_unlocked():
            value |= THE_CHALLENGE_UNLOCKED_BIT

        if self.is_gubflub_hint_1():
            value |= GUBFLUB_HINT_1_BIT

        if self.is_gubflub_hint_2():
            value |= GUBFLUB_HINT_2_BIT

        if self.is_the_challenge_completed():
            value |= THE_CHALLENGE_COMPLETED_BIT

        if self.is_treasure_room_unlocked():
            value |= TREASURE_ROOM_UNLOCKED_BIT

        if self.is_chamber_of_time_unlocked():
            value |= CHAMBER_OF_TIME_UNLOCKED_BIT

        if self.is_chamber_of_time_discovered():
            value |= CHAMBER_OF_TIME_DISCOVERED_BIT

        if self.is_master_emblem_shown():
            value |= MASTER_EMBLEM_SHOWN_BIT

        if self.is_gate_keeper_dialog():
            value |= GATE_KEEPER_DIALOG_BIT

        if self.is_scratch_dialog():
            value |= SCRATCH_DIALOG_BIT

        if self.is_secret_shop_unlocked():
            value |= SECRET_SHOP_UNLOCKED_BIT

        if self.is_demon_guardian_dialog():
            value |= DEMON_GUARDIAN_DIALOG_BIT

        if self.is_demon_freed():
            value |= DEMON_FREED_BIT

        if self.is_demon_key_1():
            value |= DEMON_KEY_1_BIT

        if self.is_demon_key_2():
            value |= DEMON_KEY_2_BIT

        if self.is_demon_key_3():
            value |= DEMON_KEY_3_BIT

        if self.is_shop_keeper_dialog():
            value |= SHOP_KEEPER_DIALOG_BIT

        if self.is_world_online_levels():
            value |= WORLD_ONLINE_LEVELS_BIT

        if self.is_demon_discovered():
            value |= DEMON_DISCOVERED_BIT

        if self.is_community_shop_unlocked():
            value |= COMMUNITY_SHOP_UNLOCKED_BIT

        if self.is_potbor_dialog():
            value |= POTBOR_DIALOG_BIT

        if self.is_youtube_chest_unlocked():
            value |= YOUTUBE_CHEST_UNLOCKED_BIT

        if self.is_facebook_chest_unlocked():
            value |= FACEBOOK_CHEST_UNLOCKED_BIT

        if self.is_twitter_chest_unlocked():
            value |= TWITTER_CHEST_UNLOCKED_BIT

        # if self.is_firebird_gate_keeper():
        #     value |= FIREBIRD_GATE_KEEPER_BIT

        # if self.is_twitch_chest_unlocked():
        #     value |= TWITCH_CHEST_UNLOCKED_BIT

        # if self.is_discord_chest_unlocked():
        #     value |= DISCORD_CHEST_UNLOCKED_BIT

        writer.write_u64(value, order)

    def is_the_challenge_unlocked(self) -> bool:
        return self.the_challenge_unlocked

    def is_gubflub_hint_1(self) -> bool:
        return self.gubflub_hint_1

    def is_gubflub_hint_2(self) -> bool:
        return self.gubflub_hint_2

    def is_the_challenge_completed(self) -> bool:
        return self.the_challenge_completed

    def is_treasure_room_unlocked(self) -> bool:
        return self.treasure_room_unlocked

    def is_chamber_of_time_unlocked(self) -> bool:
        return self.chamber_of_time_unlocked

    def is_chamber_of_time_discovered(self) -> bool:
        return self.chamber_of_time_discovered

    def is_master_emblem_shown(self) -> bool:
        return self.master_emblem_shown

    def is_gate_keeper_dialog(self) -> bool:
        return self.gate_keeper_dialog

    def is_scratch_dialog(self) -> bool:
        return self.scratch_dialog

    def is_secret_shop_unlocked(self) -> bool:
        return self.secret_shop_unlocked

    def is_demon_guardian_dialog(self) -> bool:
        return self.demon_guardian_dialog

    def is_demon_freed(self) -> bool:
        return self.demon_freed

    def is_demon_key_1(self) -> bool:
        return self.demon_key_1

    def is_demon_key_2(self) -> bool:
        return self.demon_key_2

    def is_demon_key_3(self) -> bool:
        return self.demon_key_3

    def is_shop_keeper_dialog(self) -> bool:
        return self.shop_keeper_dialog

    def is_world_online_levels(self) -> bool:
        return self.world_online_levels

    def is_demon_discovered(self) -> bool:
        return self.demon_discovered

    def is_community_shop_unlocked(self) -> bool:
        return self.community_shop_unlocked

    def is_potbor_dialog(self) -> bool:
        return self.potbor_dialog

    def is_youtube_chest_unlocked(self) -> bool:
        return self.youtube_chest_unlocked

    def is_facebook_chest_unlocked(self) -> bool:
        return self.facebook_chest_unlocked

    def is_twitter_chest_unlocked(self) -> bool:
        return self.twitter_chest_unlocked

    # def is_firebird_gate_keeper(self) -> bool:
    #     return self.firebird_gate_keeper

    # def is_twitch_chest_unlocked(self) -> bool:
    #     return self.twitch_chest_unlocked

    # def is_discord_chest_unlocked(self) -> bool:
    #     return self.discord_chest_unlocked


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

    shown_editor_guide: bool = field(default=True)
    shown_low_detail: bool = field(default=True)

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
