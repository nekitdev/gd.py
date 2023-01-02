from __future__ import annotations

from functools import partial
from typing import Any, Dict, List, Mapping, Tuple, Type, TypeVar
from uuid import UUID
from uuid import uuid4 as generate_uuid

from attrs import define, field
from iters import iter
from iters.ordered_set import OrderedSet, ordered_set
from iters.utils import unpack_binary
from typing_extensions import Literal, TypeGuard

from gd.api.folder import Folder
from gd.api.level import LevelAPI
from gd.api.like import Like
from gd.api.objects import Object, object_from_binary, object_to_binary
from gd.binary import VERSION, Binary, BinaryReader, BinaryWriter
from gd.binary_utils import Reader, Writer
from gd.constants import (
    DEFAULT_ATTEMPTS,
    DEFAULT_COLOR_1_ID,
    DEFAULT_COLOR_2_ID,
    DEFAULT_DEMONS,
    DEFAULT_DESTROYED,
    DEFAULT_DIAMONDS,
    DEFAULT_ENCODING,
    DEFAULT_ERRORS,
    DEFAULT_GLOW,
    DEFAULT_ICON_ID,
    DEFAULT_ID,
    DEFAULT_JUMPS,
    DEFAULT_LEVELS,
    DEFAULT_LIKED,
    DEFAULT_MAP_PACKS,
    DEFAULT_ORBS,
    DEFAULT_RATED,
    DEFAULT_RESOLUTION,
    DEFAULT_SECRET_COINS,
    DEFAULT_SHARDS,
    DEFAULT_STARS,
    DEFAULT_USER_COINS,
    EMPTY,
    UNKNOWN,
    WEEKLY_ID_ADD,
)
from gd.enums import ByteOrder, CollectedCoins, Filter, IconType, LevelLeaderboardStrategy, Quality
from gd.filters import Filters
from gd.iter_utils import unary_tuple
from gd.song import Song
from gd.string_utils import password_repr
from gd.text_utils import snake_to_camel, snake_to_camel_with_abbreviations
from gd.versions import CURRENT_BINARY_VERSION, Version
from gd.xml import PARSER

__all__ = ("Database",)

OFFICIAL = "n"
NORMAL = "c"
NORMAL_DEMONS = "demon"
TIMELY = "d"
TIMELY_DEMONS = TIMELY + NORMAL_DEMONS
GAUNTLETS = "g"
GAUNTLETS_DEMONS = GAUNTLETS + NORMAL_DEMONS
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

    @property
    def type_to_set(self) -> Dict[str, OrderedSet[int]]:
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

    @property
    def prefix_to_set(self) -> Dict[str, OrderedSet[int]]:
        return {prefix(type): set for type, set in self.type_to_set.items()}


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


DEFAULT_FOLLOW_PLAYER = True
DEFAULT_PLAY_MUSIC = True
DEFAULT_SWIPE = False
DEFAULT_FREE_MOVE = False
DEFAULT_ROTATE_TOGGLED = False
DEFAULT_SNAP_TOGGLED = False
DEFAULT_IGNORE_DAMAGE = True
DEFAULT_FLIP_TWO_PLAYER_CONTROLS = False
DEFAULT_ALWAYS_LIMIT_CONTROLS = False
DEFAULT_SHOWN_COMMENT_RULES = True
DEFAULT_INCREASE_MAX_HISTORY = True
DEFAULT_DISABLE_EXPLOSION_SHAKE = False
DEFAULT_FLIP_PAUSE_BUTTON = False
DEFAULT_SHOWN_SONG_TERMS = False
DEFAULT_NO_SONG_LIMIT = True
DEFAULT_IN_MEMORY_SONGS = True
DEFAULT_HIGHER_AUDIO_QUALITY = True
DEFAULT_SMOOTH_FIX = False
DEFAULT_SHOW_CURSOR_IN_GAME = False
DEFAULT_WINDOWED = False
DEFAULT_AUTO_RETRY = True
DEFAULT_AUTO_CHECKPOINTS = True
DEFAULT_DISABLE_ANALOG_STICK = False
DEFAULT_SHOWN_OPTIONS = True
DEFAULT_VSYNC = True
DEFAULT_CALL_GL_FINISH = False
DEFAULT_FORCE_TIMER_ENABLED = False
DEFAULT_CHANGE_SONG_PATH = False
DEFAULT_GAME_CENTER_ENABLED = False
DEFAULT_PREVIEW_MODE = True
DEFAULT_SHOW_GROUND = False
DEFAULT_SHOW_GRID = True
DEFAULT_GRID_ON_TOP = False
DEFAULT_SHOW_PERCENTAGE = True
DEFAULT_SHOW_OBJECT_INFO = True
DEFAULT_INCREASE_MAX_LEVELS = True
DEFAULT_SHOW_EFFECT_LINES = True
DEFAULT_SHOW_TRIGGER_BOXES = True
DEFAULT_DEBUG_DRAW = False
DEFAULT_HIDE_UI_ON_TEST = False
DEFAULT_SHOWN_PROFILE_INFO = True
DEFAULT_VIEWED_SELF_PROFILE = True
DEFAULT_SHOWN_NEWGROUNDS_MESSAGE = True
DEFAULT_FAST_PRACTICE_RESET = False
DEFAULT_FREE_GAMES = False
DEFAULT_CHECK_SERVER_ONLINE = True
DEFAULT_HOLD_TO_SWIPE = False
DEFAULT_SHOW_DURATION_LINES = False
DEFAULT_SWIPE_CYCLE = False
DEFAULT_DEFAULT_MINI_ICON = False
DEFAULT_SWITCH_SPIDER_TELEPORT_COLOR = False
DEFAULT_SWITCH_DASH_FIRE_COLOR = False
DEFAULT_SHOWN_UNVERIFIED_COINS_MESSAGE = True
DEFAULT_ENABLE_MOVE_OPTIMIZATION = False
DEFAULT_HIGH_CAPACITY = True
DEFAULT_QUICK_CHECKPOINTS = False
DEFAULT_SHOW_LEVEL_DESCRIPTION = True
DEFAULT_SHOWN_UNLISTED_LEVEL_MESSAGE = True
DEFAULT_DISABLE_GRAVITY_EFFECT = False
DEFAULT_NEW_COMPLETED_FILTER = False
DEFAULT_SHOW_RESTART_BUTTON = True
DEFAULT_DISABLE_LEVEL_COMMENTS = False
DEFAULT_DISABLE_USER_COMMENTS = False
DEFAULT_FEATURED_LEVELS_ONLY = False
DEFAULT_HIDE_BACKGROUND = False
DEFAULT_HIDE_GRID_ON_PLAY = True
DEFAULT_DISABLE_SHAKE = False
DEFAULT_DISABLE_HIGH_DETAIL_ALERT = True
DEFAULT_DISABLE_SONG_ALERT = True
DEFAULT_MANUAL_ORDER = False
DEFAULT_SMALL_COMMENTS = False
DEFAULT_EXTENDED_INFO = True
DEFAULT_AUTO_LOAD_COMMENTS = True
DEFAULT_INCREASE_LOCAL_LEVELS_PER_PAGE = True
DEFAULT_MORE_COMMENTS = False
DEFAULT_JUST_DO_NOT = False
DEFAULT_SWITCH_WAVE_TRAIL_COLOR = False
DEFAULT_ENABLE_LINK_CONTROLS = False
DEFAULT_SHOW_RECORD = True
DEFAULT_PRACTICE_DEATH_EFFECT = False
DEFAULT_FORCE_SMOOTH_FIX = False
DEFAULT_SMOOTH_FIX_IN_EDITOR = False


V = TypeVar("V", bound="Variables")


@define()
class Variables(Binary):
    """Represents game variables."""

    follow_player: bool = DEFAULT_FOLLOW_PLAYER  # editor
    play_music: bool = DEFAULT_PLAY_MUSIC  # editor
    swipe: bool = DEFAULT_SWIPE  # editor
    free_move: bool = DEFAULT_FREE_MOVE  # editor
    filter: Filter = Filter.DEFAULT
    filter_id: int = DEFAULT_ID
    rotate_toggled: bool = DEFAULT_ROTATE_TOGGLED  # editor
    snap_toggled: bool = DEFAULT_SNAP_TOGGLED  # editor
    ignore_damage: bool = DEFAULT_IGNORE_DAMAGE  # editor
    flip_two_player_controls: bool = DEFAULT_FLIP_TWO_PLAYER_CONTROLS  # normal
    always_limit_controls: bool = DEFAULT_ALWAYS_LIMIT_CONTROLS  # normal
    shown_comment_rules: bool = DEFAULT_SHOWN_COMMENT_RULES  # normal
    increase_max_history: bool = DEFAULT_INCREASE_MAX_HISTORY  # normal
    disable_explosion_shake: bool = DEFAULT_DISABLE_EXPLOSION_SHAKE  # normal
    flip_pause_button: bool = DEFAULT_FLIP_PAUSE_BUTTON  # normal
    shown_song_terms: bool = DEFAULT_SHOWN_SONG_TERMS  # normal
    no_song_limit: bool = DEFAULT_NO_SONG_LIMIT  # normal
    in_memory_songs: bool = DEFAULT_IN_MEMORY_SONGS  # normal
    higher_audio_quality: bool = DEFAULT_HIGHER_AUDIO_QUALITY  # normal
    smooth_fix: bool = DEFAULT_SMOOTH_FIX  # normal
    show_cursor_in_game: bool = DEFAULT_SHOW_CURSOR_IN_GAME  # normal
    windowed: bool = DEFAULT_WINDOWED  # normal
    auto_retry: bool = DEFAULT_AUTO_RETRY  # normal
    auto_checkpoints: bool = DEFAULT_AUTO_CHECKPOINTS  # normal
    disable_analog_stick: bool = DEFAULT_DISABLE_ANALOG_STICK  # normal
    shown_options: bool = DEFAULT_SHOWN_OPTIONS  # normal
    vsync: bool = DEFAULT_VSYNC  # normal
    call_gl_finish: bool = DEFAULT_CALL_GL_FINISH  # normal
    force_timer_enabled: bool = DEFAULT_FORCE_TIMER_ENABLED  # normal
    change_song_path: bool = DEFAULT_CHANGE_SONG_PATH  # normal
    game_center_enabled: bool = DEFAULT_GAME_CENTER_ENABLED  # normal
    preview_mode: bool = DEFAULT_PREVIEW_MODE  # editor
    show_ground: bool = DEFAULT_SHOW_GROUND  # editor
    show_grid: bool = DEFAULT_SHOW_GRID  # editor
    grid_on_top: bool = DEFAULT_GRID_ON_TOP  # editor
    show_percentage: bool = DEFAULT_SHOW_PERCENTAGE  # normal
    show_object_info: bool = DEFAULT_SHOW_OBJECT_INFO  # editor
    increase_max_levels: bool = DEFAULT_INCREASE_MAX_LEVELS  # normal
    show_effect_lines: bool = DEFAULT_SHOW_EFFECT_LINES  # editor
    show_trigger_boxes: bool = DEFAULT_SHOW_TRIGGER_BOXES  # editor
    debug_draw: bool = DEFAULT_DEBUG_DRAW  # editor
    hide_ui_on_test: bool = DEFAULT_HIDE_UI_ON_TEST  # editor
    shown_profile_info: bool = DEFAULT_SHOWN_PROFILE_INFO  # normal
    viewed_self_profile: bool = DEFAULT_VIEWED_SELF_PROFILE  # normal
    buttons_per_row: int = DEFAULT_BUTTONS_PER_ROW  # editor
    button_rows: int = DEFAULT_BUTTON_ROWS  # editor
    shown_newgrounds_message: bool = DEFAULT_SHOWN_NEWGROUNDS_MESSAGE  # normal
    fast_practice_reset: bool = DEFAULT_FAST_PRACTICE_RESET  # normal
    free_games: bool = DEFAULT_FREE_GAMES  # normal
    check_server_online: bool = DEFAULT_CHECK_SERVER_ONLINE  # normal
    hold_to_swipe: bool = DEFAULT_HOLD_TO_SWIPE  # editor
    show_duration_lines: bool = DEFAULT_SHOW_DURATION_LINES  # editor
    swipe_cycle: bool = DEFAULT_SWIPE_CYCLE  # editor
    default_mini_icon: bool = DEFAULT_DEFAULT_MINI_ICON  # normal
    switch_spider_teleport_color: bool = DEFAULT_SWITCH_SPIDER_TELEPORT_COLOR  # normal
    switch_dash_fire_color: bool = DEFAULT_SWITCH_DASH_FIRE_COLOR  # normal
    shown_unverified_coins_message: bool = DEFAULT_SHOWN_UNVERIFIED_COINS_MESSAGE  # normal
    enable_move_optimization: bool = DEFAULT_ENABLE_MOVE_OPTIMIZATION  # normal
    high_capacity: bool = DEFAULT_HIGH_CAPACITY  # normal
    quick_checkpoints: bool = DEFAULT_QUICK_CHECKPOINTS  # normal
    show_level_description: bool = DEFAULT_SHOW_LEVEL_DESCRIPTION  # normal
    shown_unlisted_level_message: bool = DEFAULT_SHOWN_UNLISTED_LEVEL_MESSAGE  # normal
    disable_gravity_effect: bool = DEFAULT_DISABLE_GRAVITY_EFFECT  # normal
    new_completed_filter: bool = DEFAULT_NEW_COMPLETED_FILTER  # normal
    show_restart_button: bool = DEFAULT_SHOW_RESTART_BUTTON  # normal
    disable_level_comments: bool = DEFAULT_DISABLE_LEVEL_COMMENTS  # normal
    disable_user_comments: bool = DEFAULT_DISABLE_USER_COMMENTS  # normal
    featured_levels_only: bool = DEFAULT_FEATURED_LEVELS_ONLY  # normal
    hide_background: bool = DEFAULT_HIDE_BACKGROUND  # editor
    hide_grid_on_play: bool = DEFAULT_HIDE_GRID_ON_PLAY  # editor
    disable_shake: bool = DEFAULT_DISABLE_SHAKE  # normal
    disable_high_detail_alert: bool = DEFAULT_DISABLE_HIGH_DETAIL_ALERT  # normal
    disable_song_alert: bool = DEFAULT_DISABLE_SONG_ALERT  # normal
    manual_order: bool = DEFAULT_MANUAL_ORDER  # normal
    small_comments: bool = DEFAULT_SMALL_COMMENTS  # normal
    extended_info: bool = DEFAULT_EXTENDED_INFO  # normal
    auto_load_comments: bool = DEFAULT_AUTO_LOAD_COMMENTS  # normal
    created_levels_folder_id: int = DEFAULT_CREATED_LEVELS_FOLDER_ID
    saved_levels_folder_id: int = DEFAULT_SAVED_LEVELS_FOLDER_ID
    increase_local_levels_per_page: bool = DEFAULT_INCREASE_LOCAL_LEVELS_PER_PAGE  # normal
    more_comments: bool = DEFAULT_MORE_COMMENTS  # normal
    just_do_not: bool = DEFAULT_JUST_DO_NOT  # normal
    switch_wave_trail_color: bool = DEFAULT_SWITCH_WAVE_TRAIL_COLOR  # normal
    enable_link_controls: bool = DEFAULT_ENABLE_LINK_CONTROLS  # editor
    level_leaderboard_strategy: LevelLeaderboardStrategy = LevelLeaderboardStrategy.DEFAULT
    show_record: bool = DEFAULT_SHOW_RECORD  # normal
    practice_death_effect: bool = DEFAULT_PRACTICE_DEATH_EFFECT  # normal
    force_smooth_fix: bool = DEFAULT_FORCE_SMOOTH_FIX  # normal
    smooth_fix_in_editor: bool = DEFAULT_SMOOTH_FIX_IN_EDITOR  # editor

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
    def from_binary(
        cls: Type[V],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> V:
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

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
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
class Values(Binary):
    variables: Variables = field(factory=Variables)

    cubes: OrderedSet[int] = field(factory=ordered_set)
    ships: OrderedSet[int] = field(factory=ordered_set)
    balls: OrderedSet[int] = field(factory=ordered_set)
    ufos: OrderedSet[int] = field(factory=ordered_set)
    waves: OrderedSet[int] = field(factory=ordered_set)
    robots: OrderedSet[int] = field(factory=ordered_set)
    spiders: OrderedSet[int] = field(factory=ordered_set)
    # swing_copters: OrderedSet[int] = field(factory=ordered_set)
    explosions: OrderedSet[int] = field(factory=ordered_set)
    colors_1: OrderedSet[int] = field(factory=ordered_set)
    colors_2: OrderedSet[int] = field(factory=ordered_set)

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        writer = Writer(binary)

        self.variables.to_binary(binary, order, version)

        for items in (
            self.cubes,
            self.ships,
            self.balls,
            self.ufos,
            self.waves,
            self.robots,
            self.spiders,
            # self.swing_copters,
            self.explosions,
            self.colors_1,
            self.colors_2,
        ):
            writer.write_u16(len(items), order)

            for item in items:
                writer.write_u16(item, order)

    @classmethod
    def from_binary(
        cls: Type[VS],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> VS:
        reader = Reader(binary)

        variables = Variables.from_binary(binary, order, version)

        read_u16 = partial(reader.read_u16, order)

        cubes_length = reader.read_u16(order)

        cubes = iter.repeat_exactly_with(read_u16, cubes_length).ordered_set()

        ships_length = reader.read_u16(order)

        ships = iter.repeat_exactly_with(read_u16, ships_length).ordered_set()

        balls_length = reader.read_u16(order)

        balls = iter.repeat_exactly_with(read_u16, balls_length).ordered_set()

        ufos_length = reader.read_u16(order)

        ufos = iter.repeat_exactly_with(read_u16, ufos_length).ordered_set()

        waves_length = reader.read_u16(order)

        waves = iter.repeat_exactly_with(read_u16, waves_length).ordered_set()

        robots_length = reader.read_u16(order)

        robots = iter.repeat_exactly_with(read_u16, robots_length).ordered_set()

        spiders_length = reader.read_u16(order)

        spiders = iter.repeat_exactly_with(read_u16, spiders_length).ordered_set()

        # swing_copters_length = reader.read_u16(order)

        # swing_copters = iter.repeat_exactly_with(read_u16, swing_copters_length).ordered_set()

        explosions_length = reader.read_u16(order)

        explosions = iter.repeat_exactly_with(read_u16, explosions_length).ordered_set()

        colors_1_length = reader.read_u16(order)

        colors_1 = iter.repeat_exactly_with(read_u16, colors_1_length).ordered_set()

        colors_2_length = reader.read_u16(order)

        colors_2 = iter.repeat_exactly_with(read_u16, colors_2_length).ordered_set()

        return cls(
            variables=variables,
            cubes=cubes,
            ships=ships,
            balls=balls,
            ufos=ufos,
            waves=waves,
            robots=robots,
            spiders=spiders,
            # swing_copters=swing_copters,
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


DEFAULT_THE_CHALLENGE_UNLOCKED = False
DEFAULT_GUBFLUB_HINT_1 = False
DEFAULT_GUBFLUB_HINT_2 = False
DEFAULT_THE_CHALLENGE_COMPLETED = False
DEFAULT_TREASURE_ROOM_UNLOCKED = False
DEFAULT_CHAMBER_OF_TIME_UNLOCKED = False
DEFAULT_CHAMBER_OF_TIME_DISCOVERED = False
DEFAULT_MASTER_EMBLEM_SHOWN = False
DEFAULT_GATE_KEEPER_DIALOG = False
DEFAULT_SCRATCH_DIALOG = False
DEFAULT_SECRET_SHOP_UNLOCKED = False
DEFAULT_DEMON_GUARDIAN_DIALOG = False
DEFAULT_DEMON_FREED = False
DEFAULT_DEMON_KEY_1 = False
DEFAULT_DEMON_KEY_2 = False
DEFAULT_DEMON_KEY_3 = False
DEFAULT_SHOP_KEEPER_DIALOG = False
DEFAULT_WORLD_ONLINE_LEVELS = False
DEFAULT_DEMON_DISCOVERED = False
DEFAULT_COMMUNITY_SHOP_UNLOCKED = False
DEFAULT_POTBOR_DIALOG = False
DEFAULT_YOUTUBE_CHEST_UNLOCKED = False
DEFAULT_FACEBOOK_CHEST_UNLOCKED = False
DEFAULT_TWITTER_CHEST_UNLOCKED = False
# DEFAULT_FIREBIRD_GATE_KEEPER = False
# DEFAULT_TWITCH_CHEST_UNLOCKED = False
# DEFAULT_DISCORD_CHEST_UNLOCKED = False


UV = TypeVar("UV", bound="UnlockValues")


@define()
class UnlockValues(Binary):
    the_challenge_unlocked: bool = DEFAULT_THE_CHALLENGE_UNLOCKED
    gubflub_hint_1: bool = DEFAULT_GUBFLUB_HINT_1
    gubflub_hint_2: bool = DEFAULT_GUBFLUB_HINT_2
    the_challenge_completed: bool = DEFAULT_THE_CHALLENGE_COMPLETED
    treasure_room_unlocked: bool = DEFAULT_TREASURE_ROOM_UNLOCKED
    chamber_of_time_unlocked: bool = DEFAULT_CHAMBER_OF_TIME_UNLOCKED
    chamber_of_time_discovered: bool = DEFAULT_CHAMBER_OF_TIME_DISCOVERED
    master_emblem_shown: bool = DEFAULT_MASTER_EMBLEM_SHOWN
    gate_keeper_dialog: bool = DEFAULT_GATE_KEEPER_DIALOG
    scratch_dialog: bool = DEFAULT_SCRATCH_DIALOG
    secret_shop_unlocked: bool = DEFAULT_SECRET_SHOP_UNLOCKED
    demon_guardian_dialog: bool = DEFAULT_DEMON_GUARDIAN_DIALOG
    demon_freed: bool = DEFAULT_DEMON_FREED
    demon_key_1: bool = DEFAULT_DEMON_KEY_1
    demon_key_2: bool = DEFAULT_DEMON_KEY_2
    demon_key_3: bool = DEFAULT_DEMON_KEY_3
    shop_keeper_dialog: bool = DEFAULT_SHOP_KEEPER_DIALOG
    world_online_levels: bool = DEFAULT_WORLD_ONLINE_LEVELS
    demon_discovered: bool = DEFAULT_DEMON_DISCOVERED
    community_shop_unlocked: bool = DEFAULT_COMMUNITY_SHOP_UNLOCKED
    potbor_dialog: bool = DEFAULT_POTBOR_DIALOG
    youtube_chest_unlocked: bool = DEFAULT_YOUTUBE_CHEST_UNLOCKED
    facebook_chest_unlocked: bool = DEFAULT_FACEBOOK_CHEST_UNLOCKED
    twitter_chest_unlocked: bool = DEFAULT_TWITTER_CHEST_UNLOCKED
    # firebird_gate_keeper: bool = DEFAULT_FIREBIRD_GATE_KEEPER
    # twitch_chest_unlocked: bool = DEFAULT_TWITCH_CHEST_UNLOCKED
    # discord_chest_unlocked: bool = DEFAULT_DISCORD_CHEST_UNLOCKED

    @classmethod
    def from_binary(
        cls: Type[UV],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> UV:
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

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
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


JUMPS_STATISTICS = "1"
ATTEMPTS_STATISTICS = "2"
OFFICIAL_LEVELS_STATISTICS = "3"
ONLINE_LEVELS_STATISTICS = "4"
DEMONS_STATISTICS = "5"
STARS_STATISTICS = "6"
MAP_PACKS_STATISTICS = "7"
SECRET_COINS_STATISTICS = "8"
DESTROYED_STATISTICS = "9"
LIKED_STATISTICS = "10"
RATED_STATISTICS = "11"
USER_COINS_STATISTICS = "12"
DIAMONDS_STATISTICS = "13"
ORBS_STATISTICS = "14"
TIMELY_LEVELS_STATISTICS = "15"
FIRE_SHARDS_STATISTICS = "16"
ICE_SHARDS_STATISTICS = "17"
POISON_SHARDS_STATISTICS = "18"
SHADOW_SHARDS_STATISTICS = "19"
LAVA_SHARDS_STATISTICS = "20"
BONUS_SHARDS_STATISTICS = "21"
TOTAL_ORBS_STATISTICS = "22"

FIRST = 1
SECOND = 2
THIRD = 3

UNIQUE = "unique"

S = TypeVar("S", bound="Statistics")


@define()
class Statistics(Binary):
    jumps: int = field(default=DEFAULT_JUMPS)
    attempts: int = field(default=DEFAULT_ATTEMPTS)
    official_levels: int = field(default=DEFAULT_LEVELS)
    online_levels: int = field(default=DEFAULT_LEVELS)
    demons: int = field(default=DEFAULT_DEMONS)
    stars: int = field(default=DEFAULT_STARS)
    map_packs: int = field(default=DEFAULT_MAP_PACKS)
    secret_coins: int = field(default=DEFAULT_SECRET_COINS)
    destroyed: int = field(default=DEFAULT_DESTROYED)
    liked: int = field(default=DEFAULT_LIKED)
    rated: int = field(default=DEFAULT_RATED)
    user_coins: int = field(default=DEFAULT_USER_COINS)
    diamonds: int = field(default=DEFAULT_DIAMONDS)
    orbs: int = field(default=DEFAULT_ORBS)
    timely_levels: int = field(default=DEFAULT_LEVELS)
    fire_shards: int = field(default=DEFAULT_SHARDS)
    ice_shards: int = field(default=DEFAULT_SHARDS)
    poison_shards: int = field(default=DEFAULT_SHARDS)
    shadow_shards: int = field(default=DEFAULT_SHARDS)
    lava_shards: int = field(default=DEFAULT_SHARDS)
    bonus_shards: int = field(default=DEFAULT_SHARDS)
    total_orbs: int = field(default=DEFAULT_ORBS)

    official_coins: Dict[int, CollectedCoins] = field(factory=dict)

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        writer = Writer(binary)

        writer.write_u32(self.jumps, order)
        writer.write_u32(self.attempts, order)
        writer.write_u8(self.official_levels, order)
        writer.write_u32(self.online_levels, order)
        writer.write_u16(self.demons, order)
        writer.write_u32(self.stars, order)
        writer.write_u16(self.map_packs, order)
        writer.write_u16(self.secret_coins, order)
        writer.write_u32(self.destroyed, order)
        writer.write_u32(self.liked, order)
        writer.write_u32(self.rated, order)
        writer.write_u32(self.user_coins, order)
        writer.write_u32(self.diamonds, order)
        writer.write_u32(self.orbs, order)
        writer.write_u32(self.timely_levels, order)
        writer.write_u16(self.fire_shards, order)
        writer.write_u16(self.ice_shards, order)
        writer.write_u16(self.poison_shards, order)
        writer.write_u16(self.shadow_shards, order)
        writer.write_u16(self.lava_shards, order)
        writer.write_u16(self.bonus_shards, order)
        writer.write_u32(self.total_orbs, order)

        official_coins = self.official_coins

        writer.write_u16(len(official_coins))

        for level_id, collected_coins in official_coins.items():
            writer.write_u16(level_id, order)
            writer.write_u8(collected_coins.value, order)

    @classmethod
    def from_binary(
        cls: Type[S],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> S:
        reader = Reader(binary)

        jumps = reader.read_u32(order)
        attempts = reader.read_u32(order)
        official_levels = reader.read_u8(order)
        online_levels = reader.read_u32(order)
        demons = reader.read_u16(order)
        stars = reader.read_u32(order)
        map_packs = reader.read_u16(order)
        secret_coins = reader.read_u16(order)
        destroyed = reader.read_u32(order)
        liked = reader.read_u32(order)
        rated = reader.read_u32(order)
        user_coins = reader.read_u32(order)
        diamonds = reader.read_u32(order)
        orbs = reader.read_u32(order)
        timely_levels = reader.read_u32(order)
        fire_shards = reader.read_u16(order)
        ice_shards = reader.read_u16(order)
        poison_shards = reader.read_u16(order)
        shadow_shards = reader.read_u16(order)
        lava_shards = reader.read_u16(order)
        bonus_shards = reader.read_u16(order)
        total_orbs = reader.read_u32(order)

        collected_coins = CollectedCoins

        official_coins_length = reader.read_u16(order)

        official_coins = {
            reader.read_u16(order): collected_coins(reader.read_u8(order))
            for _ in range(official_coins_length)
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
            timely_levels=timely_levels,
            fire_shards=fire_shards,
            ice_shards=ice_shards,
            poison_shards=poison_shards,
            shadow_shards=shadow_shards,
            lava_shards=lava_shards,
            bonus_shards=bonus_shards,
            total_orbs=total_orbs,
            official_coins=official_coins,
        )


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
DEFAULT_SFX_VOLUME = 1.0

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

CREATED_LEVELS = "LLM_01"
BINARY_VERSION_LEVELS = "LLM_02"

UUID_SIZE = 16

ONE = str(1)

IS_ARRAY = snake_to_camel("_is_arr")


KEY = "k_{}"
key = KEY.format


def is_true(item: Any) -> TypeGuard[Literal[True]]:
    return item is True


D = TypeVar("D", bound="Database")


@define()
class Database(Binary):
    volume: float = field(default=DEFAULT_VOLUME)
    sfx_volume: float = field(default=DEFAULT_SFX_VOLUME)

    uuid: UUID = field(factory=generate_uuid)

    player_name: str = field(default=UNKNOWN)

    name: str = field(default=UNKNOWN)
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

    official_levels: OrderedSet[LevelAPI] = field(factory=ordered_set)
    saved_levels: OrderedSet[LevelAPI] = field(factory=ordered_set)
    followed: OrderedSet[int] = field(factory=ordered_set)
    last_played: OrderedSet[int] = field(factory=ordered_set)
    filters: Filters = field(factory=Filters)
    timely_levels: OrderedSet[LevelAPI] = field(factory=ordered_set)
    daily_id: int = field(default=DEFAULT_ID)
    weekly_id: int = field(default=DEFAULT_ID)
    liked: OrderedSet[Like] = field(factory=dict)
    rated: OrderedSet[int] = field(factory=ordered_set)
    reported: OrderedSet[int] = field(factory=ordered_set)
    demon_rated: OrderedSet[int] = field(factory=ordered_set)
    gauntlet_levels: OrderedSet[LevelAPI] = field(factory=ordered_set)
    saved_folders: OrderedSet[Folder] = field(factory=ordered_set)
    created_folders: OrderedSet[Folder] = field(factory=ordered_set)

    created_levels: OrderedSet[LevelAPI] = field(factory=ordered_set)

    songs: OrderedSet[Song] = field(factory=ordered_set)

    binary_version: Version = field(default=CURRENT_BINARY_VERSION)

    # keybindings: Keybindings = field(factory=Keybindings)

    @classmethod
    def load_parts(cls: Type[D], main: bytes, levels: bytes) -> D:
        parser = PARSER

        main_data = parser.load(main)

        volume = main_data.get(VOLUME, DEFAULT_VOLUME)
        sfx_volume = main_data.get(SFX_VOLUME, DEFAULT_VOLUME)

        uuid_option = main_data.get(UUID_LITERAL)

        if uuid_option is None:
            uuid = generate_uuid()

        else:
            uuid = UUID(uuid_option)

        player_name = main_data.get(PLAYER_NAME, UNKNOWN)

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

        name = main_data.get(NAME, UNKNOWN)

        password = main_data.get(PASSWORD, EMPTY)

        account_id = main_data.get(ACCOUNT_ID, DEFAULT_ID)

        session_id = main_data.get(SESSION_ID, DEFAULT_ID)

        secret_value = main_data.get(SECRET_VALUE, DEFAULT_SECRET_VALUE)

        official_levels_data = main_data.get(OFFICIAL_LEVELS, {})

        official_levels = (
            iter(official_levels_data.values()).map(LevelAPI.from_robtop_data).ordered_set()
        )

        saved_levels_data = main_data.get(SAVED_LEVELS, {})

        saved_levels = iter(saved_levels_data.values()).map(LevelAPI.from_robtop_data).ordered_set()

        followed_data = main_data.get(FOLLOWED, {})

        followed = iter(followed_data.keys()).map(int).ordered_set()

        last_played_data = main_data.get(LAST_PLAYED, {})

        last_played = iter(last_played_data.keys()).map(int).ordered_set()

        timely_levels_data = main_data.get(TIMELY_LEVELS, {})

        timely_levels = (
            iter(timely_levels_data.values()).map(LevelAPI.from_robtop_data).ordered_set()
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
            iter(gauntlet_levels_data.values()).map(LevelAPI.from_robtop_data).ordered_set()
        )

        ...

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

        import json

        with open("main.json", "w") as file:
            json.dump(main_data, file, indent=2)

        levels_data = parser.load(levels)

        created_levels_data = levels_data.get(CREATED_LEVELS, {})
        binary_version_data = levels_data.get(BINARY_VERSION_LEVELS)

        if binary_version_data is None:
            binary_version = CURRENT_BINARY_VERSION

        else:
            binary_version = Version.from_value(binary_version_data)

        created_levels = (
            iter(created_levels_data.values())
            .drop_while(is_true)
            .map(LevelAPI.from_robtop_data)
            .ordered_set()
        )

        return cls(
            # main
            volume=volume,
            sfx_volume=sfx_volume,
            uuid=uuid,
            player_name=player_name,
            id=id,
            name=name,
            password=password,
            account_id=account_id,
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
            official_levels=official_levels,
            saved_levels=saved_levels,
            followed=followed,
            last_played=last_played,
            # ...
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
            # levels
            created_levels=created_levels,
            binary_version=binary_version,
        )

    def dump_main(self) -> bytes:
        one = ONE
        parser = PARSER

        main_data = {
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
            SECRET_VALUE: self.secret_value,
            DAILY_ID: self.daily_id,
            WEEKLY_ID: self.weekly_id,
            NAME: self.name,
            PASSWORD: self.password,
            ACCOUNT_ID: self.account_id,
            SESSION_ID: self.session_id,
        }

        glow = self.has_glow()

        if glow:
            main_data[GLOW] = glow

        moderator = self.is_moderator()

        if moderator:
            main_data[MODERATOR] = moderator

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

        demon_rated_data = {str(demon_id): one for demon_id in self.demon_rated}

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

        return parser.dump(main_data)

    def dump_levels(self) -> bytes:
        parser = PARSER

        created_levels_data: Dict[str, Any] = {IS_ARRAY: True}

        created_levels_data.update(
            {
                key(index): created_level.to_robtop_data()
                for index, created_level in enumerate(self.created_levels)
            }
        )

        binary_version_data = self.binary_version.to_value()

        levels_data = {CREATED_LEVELS: created_levels_data, BINARY_VERSION: binary_version_data}

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

        reader = Reader(binary)

        volume = reader.read_f32(order)
        sfx_volume = reader.read_f32(order)

        data = reader.read(UUID_SIZE)

        if order.is_little():
            uuid = UUID(bytes_le=data)

        else:
            uuid = UUID(bytes=data)

        player_name_length = reader.read_u8(order)

        player_name = reader.read(player_name_length).decode(encoding, errors)

        name_length = reader.read_u8(order)

        name = reader.read(name_length).decode(encoding, errors)

        id = reader.read_u32(order)
        account_id = reader.read_u32(order)

        password_length = reader.read_u8(order)

        password = reader.read(password_length).decode(encoding, errors)

        session_id = reader.read_u32(order)

        cube_id = reader.read_u16(order)
        ship_id = reader.read_u16(order)
        ball_id = reader.read_u16(order)
        ufo_id = reader.read_u16(order)
        wave_id = reader.read_u16(order)
        robot_id = reader.read_u16(order)
        spider_id = reader.read_u16(order)
        color_1_id = reader.read_u16(order)
        color_2_id = reader.read_u16(order)
        trail_id = reader.read_u16(order)
        explosion_id = reader.read_u16(order)

        icon_type_value = reader.read_u8(order)
        icon_type = IconType(icon_type_value)

        secret_value = reader.read_u32(order)

        value = reader.read_u8(order)

        show_song_markers = value & show_song_markers_bit == show_song_markers_bit
        show_progress_bar = value & show_progress_bar_bit == show_progress_bar_bit
        clicked_icons = value & clicked_icons_bit == clicked_icons_bit
        clicked_editor = value & clicked_editor_bit == clicked_editor_bit
        clicked_practice = value & clicked_practice_bit == clicked_practice_bit
        shown_editor_guide = value & shown_editor_guide_bit == shown_editor_guide_bit
        shown_low_detail = value & shown_low_detail_bit == shown_low_detail_bit
        rated_game = value & rated_game_bit == rated_game_bit

        value = reader.read_u8(order)

        moderator = value & moderator_bit == moderator_bit

        glow = value & glow_bit == glow_bit

        quality_value = (value & QUALITY_MASK) >> QUALITY_SHIFT

        quality = Quality(quality_value)

        achievements_length = reader.read_u16(order)

        achievements = {}

        for _ in range(achievements_length):
            name_length = reader.read_u8(order)

            name = reader.read(name_length).decode(encoding, errors)

            progress = reader.read_u16(order)

            achievements[name] = progress

        bootups = reader.read_u32(order)

        resolution = reader.read_i8(order)

        values = Values.from_binary(binary, order, version)
        unlock_values = UnlockValues.from_binary(binary, order, version)

        custom_objects_length = reader.read_u16(order)

        object_from_binary_function = partial(object_from_binary, binary, order, version)

        def custom_object_from_binary() -> List[Object]:
            custom_object_length = reader.read_u32(order)

            return iter.repeat_exactly_with(
                object_from_binary_function, custom_object_length
            ).list()

        custom_objects = iter.repeat_exactly_with(
            custom_object_from_binary, custom_objects_length
        ).list()

        statistics = Statistics.from_binary(binary, order, version)

        level_api_from_binary = partial(
            LevelAPI.from_binary, binary, order, version, encoding, errors
        )

        official_levels_length = reader.read_u8(order)

        official_levels = iter.repeat_exactly_with(
            level_api_from_binary, official_levels_length
        ).ordered_set()

        saved_levels_length = reader.read_u32(order)

        saved_levels = iter.repeat_exactly_with(
            level_api_from_binary, saved_levels_length
        ).ordered_set()

        read_u32 = partial(reader.read_u32, order)

        followed_length = reader.read_u32(order)

        followed = iter.repeat_exactly_with(read_u32, followed_length).ordered_set()

        last_played_length = reader.read_u16(order)

        last_played = iter.repeat_exactly_with(read_u32, last_played_length).ordered_set()

        filters = Filters.from_binary(binary, order, version)

        timely_levels_length = reader.read_u32(order)

        timely_levels = iter.repeat_exactly_with(
            level_api_from_binary, timely_levels_length
        ).ordered_set()

        daily_id = reader.read_u32(order)
        weekly_id = reader.read_u32(order)

        like_from_binary = partial(Like.from_binary, binary, order, version)

        liked_length = reader.read_u32(order)

        liked = iter.repeat_exactly_with(like_from_binary, liked_length).ordered_set()

        rated_length = reader.read_u32(order)

        rated = iter.repeat_exactly_with(read_u32, rated_length).ordered_set()

        reported_length = reader.read_u32(order)

        reported = iter.repeat_exactly_with(read_u32, reported_length).ordered_set()

        demon_rated_length = reader.read_u32(order)

        demon_rated = iter.repeat_exactly_with(read_u32, demon_rated_length).ordered_set()

        gauntlet_levels_length = reader.read_u16(order)

        gauntlet_levels = iter.repeat_exactly_with(
            level_api_from_binary, gauntlet_levels_length
        ).ordered_set()

        folder_from_binary = partial(Folder.from_binary, binary, order, version, encoding, errors)

        saved_folders_length = reader.read_u8(order)

        saved_folders = iter.repeat_exactly_with(
            folder_from_binary, saved_folders_length
        ).ordered_set()

        created_folders_length = reader.read_u8(order)

        created_folders = iter.repeat_exactly_with(
            folder_from_binary, created_folders_length
        ).ordered_set()

        created_levels_length = reader.read_u32(order)

        created_levels = iter.repeat_exactly_with(
            level_api_from_binary, created_levels_length
        ).ordered_set()

        song_from_binary = partial(Song.from_binary, binary, order, version, encoding, errors)

        songs_length = reader.read_u32(order)

        songs = iter.repeat_exactly_with(song_from_binary, songs_length).ordered_set()

        binary_version = Version.from_binary(binary, order, version)

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
            created_levels=created_levels,
            songs=songs,
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
        writer = Writer(binary)

        writer.write_f32(self.volume, order)
        writer.write_f32(self.sfx_volume, order)

        uuid = self.uuid

        data = uuid.bytes_le if order.is_little() else uuid.bytes

        writer.write(data)

        data = self.player_name.encode(encoding, errors)

        writer.write_u8(len(data), order)

        writer.write(data)

        data = self.name.encode(encoding, errors)

        writer.write_u8(len(data), order)

        writer.write(data)

        writer.write_u32(self.id, order)
        writer.write_u32(self.account_id, order)

        data = self.password.encode(encoding, errors)

        writer.write_u8(len(data), order)

        writer.write(data)

        writer.write_u32(self.session_id, order)

        writer.write_u16(self.cube_id, order)
        writer.write_u16(self.ship_id, order)
        writer.write_u16(self.ball_id, order)
        writer.write_u16(self.ufo_id, order)
        writer.write_u16(self.wave_id, order)
        writer.write_u16(self.robot_id, order)
        writer.write_u16(self.spider_id, order)
        writer.write_u16(self.color_1_id, order)
        writer.write_u16(self.color_2_id, order)
        writer.write_u16(self.trail_id, order)
        writer.write_u16(self.explosion_id, order)

        writer.write_u8(self.icon_type.value, order)

        writer.write_u32(self.secret_value, order)

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

        writer.write_u8(value, order)

        value = self.quality.value << QUALITY_SHIFT

        if self.is_moderator():
            value |= MODERATOR_BIT

        if self.has_glow():
            value |= GLOW_BIT

        writer.write_u8(value, order)

        achievements = self.achievements

        writer.write_u16(len(achievements), order)

        for name, progress in achievements.items():
            data = name.encode(encoding, errors)

            writer.write_u8(len(data), order)

            writer.write(data)

            writer.write_u16(progress, order)

        writer.write_u32(self.bootups, order)

        writer.write_i8(self.resolution, order)

        self.values.to_binary(binary, order, version)
        self.unlock_values.to_binary(binary, order, version)

        custom_objects = self.custom_objects

        writer.write_u16(len(custom_objects), order)

        for objects in custom_objects:
            writer.write_u32(len(objects), order)

            for object in objects:
                object_to_binary(object, binary, order)

        self.statistics.to_binary(binary, order, version)

        official_levels = self.official_levels

        writer.write_u8(len(official_levels), order)

        for official_level in official_levels:
            official_level.to_binary(binary, order, version, encoding, errors)

        saved_levels = self.saved_levels

        writer.write_u32(len(saved_levels), order)

        for saved_level in saved_levels:
            saved_level.to_binary(binary, order, version, encoding, errors)

        followed = self.followed

        writer.write_u32(len(followed), order)

        for account_id in followed:
            writer.write_u32(account_id, order)

        last_played = self.last_played

        writer.write_u16(len(last_played), order)

        for level_id in last_played:
            writer.write_u32(level_id, order)

        self.filters.to_binary(binary, order, version)

        timely_levels = self.timely_levels

        writer.write_u32(len(timely_levels), order)

        for timely_level in timely_levels:
            timely_level.to_binary(binary, order, version, encoding, errors)

        writer.write_u32(self.daily_id, order)
        writer.write_u32(self.weekly_id, order)

        liked = self.liked

        writer.write_u32(len(liked), order)

        for like in liked:
            like.to_binary(binary, order, version)

        rated = self.rated

        writer.write_u32(len(rated), order)

        for level_id in rated:
            writer.write_u32(level_id, order)

        reported = self.reported

        writer.write_u32(len(reported), order)

        for level_id in reported:
            writer.write_u32(level_id, order)

        demon_rated = self.demon_rated

        writer.write_u32(len(demon_rated), order)

        for level_id in demon_rated:
            writer.write_u32(level_id, order)

        gauntlet_levels = self.gauntlet_levels

        writer.write_u16(len(gauntlet_levels), order)

        for gauntlet_level in gauntlet_levels:
            gauntlet_level.to_binary(binary, order, version, encoding, errors)

        saved_folders = self.saved_folders

        writer.write_u8(len(saved_folders), order)

        for saved_folder in saved_folders:
            saved_folder.to_binary(binary, order, version, encoding, errors)

        created_folders = self.created_folders

        writer.write_u8(len(created_folders), order)

        for created_folder in created_folders:
            created_folder.to_binary(binary, order, version, encoding, errors)

        created_levels = self.created_levels

        writer.write_u32(len(created_levels), order)

        for created_level in created_levels:
            created_level.to_binary(binary, order, version, encoding, errors)

        songs = self.songs

        writer.write_u32(len(songs), order)

        for song in songs:
            song.to_binary(binary, order, version, encoding, errors)

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
