from typing import Type, TypeVar

from attrs import define
from typing_aliases import StringDict, StringMapping

from gd.binary import VERSION, Binary, BinaryReader, BinaryWriter
from gd.binary_utils import Reader, Writer
from gd.constants import DEFAULT_ID
from gd.enums import ByteOrder, CommentStrategy, Filter, LevelLeaderboardStrategy
from gd.models_utils import bool_str, int_bool, parse_get_or, partial_parse_enum

__all__ = ("Variables",)

FOLLOW_PLAYER = "gv_0001"
PLAY_MUSIC = "gv_0002"
SWIPE = "gv_0003"
FREE_MOVE = "gv_0004"
FILTER = "gv_0005"
FILTER_ID = "gv_0006"
ROTATE_TOGGLED = "gv_0007"
SNAP_TOGGLED = "gv_0008"
IGNORE_DAMAGE = "gv_0009"
FLIP_TWO_PLAYER_CONTROLS = "gv_0010"
ALWAYS_LIMIT_CONTROLS = "gv_0011"
SHOWN_COMMENT_RULES = "gv_0012"
INCREASE_MAX_HISTORY = "gv_0013"
DISABLE_EXPLOSION_SHAKE = "gv_0014"
FLIP_PAUSE_BUTTON = "gv_0015"
SHOWN_SONG_TERMS = "gv_0016"
NO_SONG_LIMIT = "gv_0018"
IN_MEMORY_SONGS = "gv_0019"
HIGHER_AUDIO_QUALITY = "gv_0022"
SMOOTH_FIX = "gv_0023"
SHOW_CURSOR_IN_GAME = "gv_0024"
WINDOWED = "gv_0025"
AUTO_RETRY = "gv_0026"
AUTO_CHECKPOINTS = "gv_0027"
DISABLE_ANALOG_STICK = "gv_0028"
SHOWN_OPTIONS = "gv_0029"
VSYNC = "gv_0030"
CALL_GL_FINISH = "gv_0031"
FORCE_TIMER = "gv_0032"
CHANGE_SONG_PATH = "gv_0033"
GAME_CENTER = "gv_0034"
PREVIEW_MODE = "gv_0036"
SHOW_GROUND = "gv_0037"
SHOW_GRID = "gv_0038"
GRID_ON_TOP = "gv_0039"
SHOW_PERCENTAGE = "gv_0040"
SHOW_OBJECT_INFO = "gv_0041"
INCREASE_MAX_LEVELS = "gv_0042"
SHOW_EFFECT_LINES = "gv_0043"
SHOW_TRIGGER_BOXES = "gv_0044"
DEBUG_DRAW = "gv_0045"
HIDE_UI_ON_TEST = "gv_0046"
SHOWN_PROFILE_INFO = "gv_0047"
VIEWED_SELF_PROFILE = "gv_0048"
BUTTONS_PER_ROW = "gv_0049"
BUTTON_ROWS = "gv_0050"
SHOWN_NEWGROUNDS_MESSAGE = "gv_0051"
FAST_PRACTICE_RESET = "gv_0052"
FREE_GAMES = "gv_0053"
CHECK_SERVER_ONLINE = "gv_0055"
DISABLE_HIGH_DETAIL_ALERT = "gv_0056"
HOLD_TO_SWIPE = "gv_0057"
SHOW_DURATION_LINES = "gv_0058"
SWIPE_CYCLE = "gv_0059"
DEFAULT_MINI_ICON = "gv_0060"
SWITCH_SPIDER_TELEPORT_COLOR = "gv_0061"
SWITCH_DASH_FIRE_COLOR = "gv_0062"
SHOWN_UNVERIFIED_COINS_MESSAGE = "gv_0063"
SELECT_FILTER = "gv_0064"  # copies `FILTER`
ENABLE_MOVE_OPTIMIZATION = "gv_0065"
HIGH_CAPACITY = "gv_0066"
HIGH_START_POSITION_ACCURACY = "gv_0067"
QUICK_CHECKPOINTS = "gv_0068"
COMMENT_STRATEGY = "gv_0069"
SHOWN_UNLISTED_LEVEL_MESSAGE = "gv_0070"
DISABLE_GRAVITY_EFFECT = "gv_0072"
NEW_COMPLETED_FILTER = "gv_0073"
SHOW_RESTART_BUTTON = "gv_0074"
DISABLE_LEVEL_COMMENTS = "gv_0075"
DISABLE_USER_COMMENTS = "gv_0076"
FEATURED_LEVELS_ONLY = "gv_0077"
HIDE_BACKGROUND = "gv_0078"
HIDE_GRID_ON_PLAY = "gv_0079"
DISABLE_SHAKE = "gv_0081"
DISABLE_HIGH_DETAIL_ALERT_OTHER = "gv_0082"
DISABLE_SONG_ALERT = "gv_0083"
MANUAL_ORDER = "gv_0084"
SMALL_COMMENTS = "gv_0088"
HIDE_DESCRIPTION = "gv_0089"
AUTO_LOAD_COMMENTS = "gv_0090"
CREATED_LEVELS_FOLDER_ID = "gv_0091"
SAVED_LEVELS_FOLDER_ID = "gv_0092"
INCREASE_LOCAL_LEVELS_PER_PAGE = "gv_0093"
MORE_COMMENTS = "gv_0094"
JUST_DO_NOT = "gv_0095"
SWITCH_WAVE_TRAIL_COLOR = "gv_0096"
ENABLE_LINK_CONTROLS = "gv_0097"
LEVEL_LEADERBOARD_STRATEGY = "gv_0098"
SHOW_RECORD = "gv_0099"
PRACTICE_DEATH_EFFECT = "gv_100"
FORCE_SMOOTH_FIX = "gv_0101"
SMOOTH_FIX_IN_EDITOR = "gv_0102"

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
FORCE_TIMER_BIT = 0b1000_00000000_00000000
CHANGE_SONG_PATH_BIT = 0b10000_00000000_00000000
GAME_CENTER_BIT = 0b100000_00000000_00000000
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
HIGH_START_POSITION_ACCURACY_BIT = 0b10000_00000000_00000000_00000000_00000000
QUICK_CHECKPOINTS_BIT = 0b100000_00000000_00000000_00000000_00000000
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
HIDE_DESCRIPTION_BIT = 0b100_00000000_00000000_00000000_00000000_00000000_00000000
AUTO_LOAD_COMMENTS_BIT = 0b1000_00000000_00000000_00000000_00000000_00000000_00000000
INCREASE_LOCAL_LEVELS_PER_PAGE_BIT = 0b10000_00000000_00000000_00000000_00000000_00000000_00000000
MORE_COMMENTS_BIT = 0b100000_00000000_00000000_00000000_00000000_00000000_00000000
JUST_DO_NOT_BIT = 0b1000000_00000000_00000000_00000000_00000000_00000000_00000000
SWITCH_WAVE_TRAIL_COLOR_BIT = 0b10000000_00000000_00000000_00000000_00000000_00000000_00000000
SHOW_RECORD_BIT = 0b1_00000000_00000000_00000000_00000000_00000000_00000000_00000000
PRACTICE_DEATH_EFFECT_BIT = 0b10_00000000_00000000_00000000_00000000_00000000_00000000_00000000
FORCE_SMOOTH_FIX_BIT = 0b100_00000000_00000000_00000000_00000000_00000000_00000000_00000000

FILTER_MASK = 0b00000011
LEVEL_LEADERBOARD_STRATEGY_MASK = 0b00001100
COMMENT_STRATEGY_MASK = 0b00010000

LEVEL_LEADERBOARD_STRATEGY_SHIFT = FILTER_MASK.bit_length()
COMMENT_STRATEGY_SHIFT = LEVEL_LEADERBOARD_STRATEGY_MASK.bit_length()

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
DEFAULT_FORCE_TIMER = False
DEFAULT_CHANGE_SONG_PATH = False
DEFAULT_GAME_CENTER = False
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
DEFAULT_CHECK_SERVER_ONLINE = False
DEFAULT_HOLD_TO_SWIPE = False
DEFAULT_SHOW_DURATION_LINES = False
DEFAULT_SWIPE_CYCLE = False
DEFAULT_DEFAULT_MINI_ICON = False
DEFAULT_SWITCH_SPIDER_TELEPORT_COLOR = False
DEFAULT_SWITCH_DASH_FIRE_COLOR = False
DEFAULT_SHOWN_UNVERIFIED_COINS_MESSAGE = True
DEFAULT_ENABLE_MOVE_OPTIMIZATION = False
DEFAULT_HIGH_CAPACITY = True
DEFAULT_HIGH_START_POSITION_ACCURACY = True
DEFAULT_QUICK_CHECKPOINTS = False
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
DEFAULT_HIDE_DESCRIPTION = True
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
    force_timer: bool = DEFAULT_FORCE_TIMER  # normal
    change_song_path: bool = DEFAULT_CHANGE_SONG_PATH  # normal
    game_center: bool = DEFAULT_GAME_CENTER  # normal
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
    high_start_position_accuracy: bool = DEFAULT_HIGH_START_POSITION_ACCURACY  # normal
    quick_checkpoints: bool = DEFAULT_QUICK_CHECKPOINTS  # normal
    comment_strategy: CommentStrategy = CommentStrategy.DEFAULT  # normal
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
    hide_description: bool = DEFAULT_HIDE_DESCRIPTION  # normal
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

    def is_force_timer(self) -> bool:
        return self.force_timer

    def is_change_song_path(self) -> bool:
        return self.change_song_path

    def is_game_center(self) -> bool:
        return self.game_center

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

    def is_high_start_position_accuracy(self) -> bool:
        return self.high_start_position_accuracy

    def is_quick_checkpoints(self) -> bool:
        return self.quick_checkpoints

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

    def is_hide_description(self) -> bool:
        return self.hide_description

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
        reader = Reader(binary, order)

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
        force_timer_bit = FORCE_TIMER_BIT
        change_song_path_bit = CHANGE_SONG_PATH_BIT
        game_center_bit = GAME_CENTER_BIT
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
        high_start_position_accuracy_bit = HIGH_START_POSITION_ACCURACY_BIT
        quick_checkpoints_bit = QUICK_CHECKPOINTS_BIT
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
        hide_description_bit = HIDE_DESCRIPTION_BIT
        auto_load_comments_bit = AUTO_LOAD_COMMENTS_BIT
        increase_local_levels_per_page_bit = INCREASE_LOCAL_LEVELS_PER_PAGE_BIT
        more_comments_bit = MORE_COMMENTS_BIT
        just_do_not_bit = JUST_DO_NOT_BIT
        switch_wave_trail_color_bit = SWITCH_WAVE_TRAIL_COLOR_BIT
        show_record_bit = SHOW_RECORD_BIT
        practice_death_effect_bit = PRACTICE_DEATH_EFFECT_BIT
        force_smooth_fix_bit = FORCE_SMOOTH_FIX_BIT

        value = reader.read_u32()

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

        filter_id = reader.read_u16()

        filter_and_strategies = reader.read_u8()

        filter_value = filter_and_strategies & FILTER_MASK

        filter = Filter(filter_value)

        level_leaderboard_strategy_value = (
            filter_and_strategies & LEVEL_LEADERBOARD_STRATEGY_MASK
        ) >> LEVEL_LEADERBOARD_STRATEGY_SHIFT

        level_leaderboard_strategy = LevelLeaderboardStrategy(level_leaderboard_strategy_value)

        comment_strategy_value = (
            filter_and_strategies & COMMENT_STRATEGY_MASK
        ) >> COMMENT_STRATEGY_SHIFT

        comment_strategy = CommentStrategy(comment_strategy_value)

        buttons_per_row = reader.read_u8()
        button_rows = reader.read_u8()

        created_levels_folder_id = reader.read_u8()
        saved_levels_folder_id = reader.read_u8()

        value = reader.read_u64()

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
        force_timer = value & force_timer_bit == force_timer_bit
        change_song_path = value & change_song_path_bit == change_song_path_bit
        game_center = value & game_center_bit == game_center_bit
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
        high_start_position_accuracy = (
            value & high_start_position_accuracy_bit == high_start_position_accuracy_bit
        )
        quick_checkpoints = value & quick_checkpoints_bit == quick_checkpoints_bit
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
        hide_description = value & hide_description_bit == hide_description_bit
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
            force_timer=force_timer,
            change_song_path=change_song_path,
            game_center=game_center,
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
            high_start_position_accuracy=high_start_position_accuracy,
            quick_checkpoints=quick_checkpoints,
            comment_strategy=comment_strategy,
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
            hide_description=hide_description,
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
        writer = Writer(binary, order)

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

        writer.write_u32(value)

        writer.write_u16(self.filter_id)

        value = self.filter.value

        value |= self.level_leaderboard_strategy.value << LEVEL_LEADERBOARD_STRATEGY_SHIFT
        value |= self.comment_strategy.value << COMMENT_STRATEGY_SHIFT

        writer.write_u8(value)

        writer.write_u8(self.buttons_per_row)
        writer.write_u8(self.button_rows)

        writer.write_u8(self.created_levels_folder_id)
        writer.write_u8(self.saved_levels_folder_id)

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

        if self.is_force_timer():
            value |= FORCE_TIMER_BIT

        if self.is_change_song_path():
            value |= CHANGE_SONG_PATH_BIT

        if self.is_game_center():
            value |= GAME_CENTER_BIT

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

        if self.is_high_start_position_accuracy():
            value |= HIGH_START_POSITION_ACCURACY_BIT

        if self.is_quick_checkpoints():
            value |= QUICK_CHECKPOINTS_BIT

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

        if self.is_hide_description():
            value |= HIDE_DESCRIPTION_BIT

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

        writer.write_u64(value)

    @classmethod
    def from_robtop_data(cls: Type[V], data: StringMapping[str]) -> V:
        follow_player = parse_get_or(int_bool, DEFAULT_FOLLOW_PLAYER, data.get(FOLLOW_PLAYER))
        play_music = parse_get_or(int_bool, DEFAULT_PLAY_MUSIC, data.get(PLAY_MUSIC))
        swipe = parse_get_or(int_bool, DEFAULT_SWIPE, data.get(SWIPE))
        free_move = parse_get_or(int_bool, DEFAULT_FREE_MOVE, data.get(FREE_MOVE))
        filter = parse_get_or(partial_parse_enum(int, Filter), Filter.DEFAULT, data.get(FILTER))
        filter_id = parse_get_or(int, DEFAULT_ID, data.get(FILTER_ID))
        rotate_toggled = parse_get_or(int_bool, DEFAULT_ROTATE_TOGGLED, data.get(ROTATE_TOGGLED))
        snap_toggled = parse_get_or(int_bool, DEFAULT_SNAP_TOGGLED, data.get(SNAP_TOGGLED))
        ignore_damage = parse_get_or(int_bool, DEFAULT_IGNORE_DAMAGE, data.get(IGNORE_DAMAGE))
        flip_two_player_controls = parse_get_or(
            int_bool, DEFAULT_FLIP_TWO_PLAYER_CONTROLS, data.get(FLIP_TWO_PLAYER_CONTROLS)
        )
        always_limit_controls = parse_get_or(
            int_bool, DEFAULT_ALWAYS_LIMIT_CONTROLS, data.get(ALWAYS_LIMIT_CONTROLS)
        )
        shown_comment_rules = parse_get_or(
            int_bool, DEFAULT_SHOWN_COMMENT_RULES, data.get(SHOWN_COMMENT_RULES)
        )
        increase_max_history = parse_get_or(
            int_bool, DEFAULT_INCREASE_MAX_HISTORY, data.get(INCREASE_MAX_HISTORY)
        )
        disable_explosion_shake = parse_get_or(
            int_bool, DEFAULT_DISABLE_EXPLOSION_SHAKE, data.get(DISABLE_EXPLOSION_SHAKE)
        )
        flip_pause_button = parse_get_or(
            int_bool, DEFAULT_FLIP_PAUSE_BUTTON, data.get(FLIP_PAUSE_BUTTON)
        )
        shown_song_terms = parse_get_or(
            int_bool, DEFAULT_SHOWN_SONG_TERMS, data.get(SHOWN_SONG_TERMS)
        )
        no_song_limit = parse_get_or(int_bool, DEFAULT_NO_SONG_LIMIT, data.get(NO_SONG_LIMIT))
        in_memory_songs = parse_get_or(int_bool, DEFAULT_IN_MEMORY_SONGS, data.get(IN_MEMORY_SONGS))
        higher_audio_quality = parse_get_or(
            int_bool, DEFAULT_HIGHER_AUDIO_QUALITY, data.get(HIGHER_AUDIO_QUALITY)
        )
        smooth_fix = parse_get_or(int_bool, DEFAULT_SMOOTH_FIX, data.get(SMOOTH_FIX))
        show_cursor_in_game = parse_get_or(
            int_bool, DEFAULT_SHOW_CURSOR_IN_GAME, data.get(SHOW_CURSOR_IN_GAME)
        )
        windowed = parse_get_or(int_bool, DEFAULT_WINDOWED, data.get(WINDOWED))
        auto_retry = parse_get_or(int_bool, DEFAULT_AUTO_RETRY, data.get(AUTO_RETRY))
        auto_checkpoints = parse_get_or(
            int_bool, DEFAULT_AUTO_CHECKPOINTS, data.get(AUTO_CHECKPOINTS)
        )
        disable_analog_stick = parse_get_or(
            int_bool, DEFAULT_DISABLE_ANALOG_STICK, data.get(DISABLE_ANALOG_STICK)
        )
        shown_options = parse_get_or(int_bool, DEFAULT_SHOWN_OPTIONS, data.get(SHOWN_OPTIONS))
        vsync = parse_get_or(int_bool, DEFAULT_VSYNC, data.get(VSYNC))
        call_gl_finish = parse_get_or(int_bool, DEFAULT_CALL_GL_FINISH, data.get(CALL_GL_FINISH))
        force_timer = parse_get_or(int_bool, DEFAULT_FORCE_TIMER, data.get(FORCE_TIMER))
        change_song_path = parse_get_or(
            int_bool, DEFAULT_CHANGE_SONG_PATH, data.get(CHANGE_SONG_PATH)
        )
        game_center = parse_get_or(int_bool, DEFAULT_GAME_CENTER, data.get(GAME_CENTER))
        preview_mode = parse_get_or(int_bool, DEFAULT_PREVIEW_MODE, data.get(PREVIEW_MODE))
        show_ground = parse_get_or(int_bool, DEFAULT_SHOW_GROUND, data.get(SHOW_GROUND))
        show_grid = parse_get_or(int_bool, DEFAULT_SHOW_GRID, data.get(SHOW_GRID))
        grid_on_top = parse_get_or(int_bool, DEFAULT_GRID_ON_TOP, data.get(GRID_ON_TOP))
        show_percentage = parse_get_or(int_bool, DEFAULT_SHOW_PERCENTAGE, data.get(SHOW_PERCENTAGE))
        show_object_info = parse_get_or(
            int_bool, DEFAULT_SHOW_OBJECT_INFO, data.get(SHOW_OBJECT_INFO)
        )
        increase_max_levels = parse_get_or(
            int_bool, DEFAULT_INCREASE_MAX_LEVELS, data.get(INCREASE_MAX_LEVELS)
        )
        show_effect_lines = parse_get_or(
            int_bool, DEFAULT_SHOW_EFFECT_LINES, data.get(SHOW_EFFECT_LINES)
        )
        show_trigger_boxes = parse_get_or(
            int_bool, DEFAULT_SHOW_TRIGGER_BOXES, data.get(SHOW_TRIGGER_BOXES)
        )
        debug_draw = parse_get_or(int_bool, DEFAULT_DEBUG_DRAW, data.get(DEBUG_DRAW))
        hide_ui_on_test = parse_get_or(int_bool, DEFAULT_HIDE_UI_ON_TEST, data.get(HIDE_UI_ON_TEST))
        shown_profile_info = parse_get_or(
            int_bool, DEFAULT_SHOWN_PROFILE_INFO, data.get(SHOWN_PROFILE_INFO)
        )
        viewed_self_profile = parse_get_or(
            int_bool, DEFAULT_VIEWED_SELF_PROFILE, data.get(VIEWED_SELF_PROFILE)
        )
        buttons_per_row = parse_get_or(int, DEFAULT_BUTTONS_PER_ROW, data.get(BUTTONS_PER_ROW))
        button_rows = parse_get_or(int, DEFAULT_BUTTON_ROWS, data.get(BUTTON_ROWS))
        shown_newgrounds_message = parse_get_or(
            int_bool, DEFAULT_SHOWN_NEWGROUNDS_MESSAGE, data.get(SHOWN_NEWGROUNDS_MESSAGE)
        )
        fast_practice_reset = parse_get_or(
            int_bool, DEFAULT_FAST_PRACTICE_RESET, data.get(FAST_PRACTICE_RESET)
        )
        free_games = parse_get_or(int_bool, DEFAULT_FREE_GAMES, data.get(FREE_GAMES))
        check_server_online = parse_get_or(
            int_bool, DEFAULT_CHECK_SERVER_ONLINE, data.get(CHECK_SERVER_ONLINE)
        )
        hold_to_swipe = parse_get_or(int_bool, DEFAULT_HOLD_TO_SWIPE, data.get(HOLD_TO_SWIPE))
        show_duration_lines = parse_get_or(
            int_bool, DEFAULT_SHOW_DURATION_LINES, data.get(SHOW_DURATION_LINES)
        )
        swipe_cycle = parse_get_or(int_bool, DEFAULT_SWIPE_CYCLE, data.get(SWIPE_CYCLE))
        default_mini_icon = parse_get_or(
            int_bool, DEFAULT_DEFAULT_MINI_ICON, data.get(DEFAULT_MINI_ICON)
        )
        switch_spider_teleport_color = parse_get_or(
            int_bool, DEFAULT_SWITCH_SPIDER_TELEPORT_COLOR, data.get(SWITCH_SPIDER_TELEPORT_COLOR)
        )
        switch_dash_fire_color = parse_get_or(
            int_bool, DEFAULT_SWITCH_DASH_FIRE_COLOR, data.get(SWITCH_DASH_FIRE_COLOR)
        )
        shown_unverified_coins_message = parse_get_or(
            int_bool,
            DEFAULT_SHOWN_UNVERIFIED_COINS_MESSAGE,
            data.get(SHOWN_UNVERIFIED_COINS_MESSAGE),
        )
        enable_move_optimization = parse_get_or(
            int_bool, DEFAULT_ENABLE_MOVE_OPTIMIZATION, data.get(ENABLE_MOVE_OPTIMIZATION)
        )
        high_capacity = parse_get_or(int_bool, DEFAULT_HIGH_CAPACITY, data.get(HIGH_CAPACITY))
        high_start_position_accuracy = parse_get_or(
            int_bool, DEFAULT_HIGH_START_POSITION_ACCURACY, data.get(HIGH_START_POSITION_ACCURACY)
        )
        quick_checkpoints = parse_get_or(
            int_bool, DEFAULT_QUICK_CHECKPOINTS, data.get(QUICK_CHECKPOINTS)
        )
        comment_strategy = parse_get_or(
            partial_parse_enum(int, CommentStrategy),
            CommentStrategy.DEFAULT,
            data.get(COMMENT_STRATEGY),
        )
        shown_unlisted_level_message = parse_get_or(
            int_bool, DEFAULT_SHOWN_UNLISTED_LEVEL_MESSAGE, data.get(SHOWN_UNLISTED_LEVEL_MESSAGE)
        )
        disable_gravity_effect = parse_get_or(
            int_bool, DEFAULT_DISABLE_GRAVITY_EFFECT, data.get(DISABLE_GRAVITY_EFFECT)
        )
        new_completed_filter = parse_get_or(
            int_bool, DEFAULT_NEW_COMPLETED_FILTER, data.get(NEW_COMPLETED_FILTER)
        )
        show_restart_button = parse_get_or(
            int_bool, DEFAULT_SHOW_RESTART_BUTTON, data.get(SHOW_RESTART_BUTTON)
        )
        disable_level_comments = parse_get_or(
            int_bool, DEFAULT_DISABLE_LEVEL_COMMENTS, data.get(DISABLE_LEVEL_COMMENTS)
        )
        disable_user_comments = parse_get_or(
            int_bool, DEFAULT_DISABLE_USER_COMMENTS, data.get(DISABLE_USER_COMMENTS)
        )
        featured_levels_only = parse_get_or(
            int_bool, DEFAULT_FEATURED_LEVELS_ONLY, data.get(FEATURED_LEVELS_ONLY)
        )
        hide_background = parse_get_or(int_bool, DEFAULT_HIDE_BACKGROUND, data.get(HIDE_BACKGROUND))
        hide_grid_on_play = parse_get_or(
            int_bool, DEFAULT_HIDE_GRID_ON_PLAY, data.get(HIDE_GRID_ON_PLAY)
        )
        disable_shake = parse_get_or(int_bool, DEFAULT_DISABLE_SHAKE, data.get(DISABLE_SHAKE))
        disable_high_detail_alert = parse_get_or(
            int_bool, DEFAULT_DISABLE_HIGH_DETAIL_ALERT, data.get(DISABLE_HIGH_DETAIL_ALERT)
        )
        disable_song_alert = parse_get_or(
            int_bool, DEFAULT_DISABLE_SONG_ALERT, data.get(DISABLE_SONG_ALERT)
        )
        manual_order = parse_get_or(int_bool, DEFAULT_MANUAL_ORDER, data.get(MANUAL_ORDER))
        small_comments = parse_get_or(int_bool, DEFAULT_SMALL_COMMENTS, data.get(SMALL_COMMENTS))
        hide_description = parse_get_or(
            int_bool, DEFAULT_HIDE_DESCRIPTION, data.get(HIDE_DESCRIPTION)
        )
        auto_load_comments = parse_get_or(
            int_bool, DEFAULT_AUTO_LOAD_COMMENTS, data.get(AUTO_LOAD_COMMENTS)
        )
        created_levels_folder_id = parse_get_or(
            int, DEFAULT_CREATED_LEVELS_FOLDER_ID, data.get(CREATED_LEVELS_FOLDER_ID)
        )
        saved_levels_folder_id = parse_get_or(
            int, DEFAULT_SAVED_LEVELS_FOLDER_ID, data.get(SAVED_LEVELS_FOLDER_ID)
        )
        increase_local_levels_per_page = parse_get_or(
            int_bool,
            DEFAULT_INCREASE_LOCAL_LEVELS_PER_PAGE,
            data.get(INCREASE_LOCAL_LEVELS_PER_PAGE),
        )
        more_comments = parse_get_or(int_bool, DEFAULT_MORE_COMMENTS, data.get(MORE_COMMENTS))
        just_do_not = parse_get_or(int_bool, DEFAULT_JUST_DO_NOT, data.get(JUST_DO_NOT))
        switch_wave_trail_color = parse_get_or(
            int_bool, DEFAULT_SWITCH_WAVE_TRAIL_COLOR, data.get(SWITCH_WAVE_TRAIL_COLOR)
        )
        enable_link_controls = parse_get_or(
            int_bool, DEFAULT_ENABLE_LINK_CONTROLS, data.get(ENABLE_LINK_CONTROLS)
        )
        level_leaderboard_strategy = parse_get_or(
            partial_parse_enum(int, LevelLeaderboardStrategy),
            LevelLeaderboardStrategy.DEFAULT,
            data.get(LEVEL_LEADERBOARD_STRATEGY),
        )
        show_record = parse_get_or(int_bool, DEFAULT_SHOW_RECORD, data.get(SHOW_RECORD))
        practice_death_effect = parse_get_or(
            int_bool, DEFAULT_PRACTICE_DEATH_EFFECT, data.get(PRACTICE_DEATH_EFFECT)
        )
        force_smooth_fix = parse_get_or(
            int_bool, DEFAULT_FORCE_SMOOTH_FIX, data.get(FORCE_SMOOTH_FIX)
        )
        smooth_fix_in_editor = parse_get_or(
            int_bool, DEFAULT_SMOOTH_FIX_IN_EDITOR, data.get(SMOOTH_FIX_IN_EDITOR)
        )

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
            force_timer=force_timer,
            change_song_path=change_song_path,
            game_center=game_center,
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
            high_start_position_accuracy=high_start_position_accuracy,
            quick_checkpoints=quick_checkpoints,
            comment_strategy=comment_strategy,
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
            hide_description=hide_description,
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

    def to_robtop_data(self) -> StringDict[str]:
        data: StringDict[str] = {}

        follow_player = self.is_follow_player()

        if follow_player:
            data[FOLLOW_PLAYER] = bool_str(follow_player)

        play_music = self.is_play_music()

        if play_music:
            data[PLAY_MUSIC] = bool_str(play_music)

        swipe = self.is_swipe()

        if swipe:
            data[SWIPE] = bool_str(swipe)

        free_move = self.is_free_move()

        if free_move:
            data[SWIPE] = bool_str(free_move)

        filter = self.filter

        if not filter.is_none():
            string = str(filter.value)

            data[FILTER] = string
            data[SELECT_FILTER] = string

        filter_id = self.filter_id

        if filter_id:
            data[FILTER_ID] = str(filter_id)

        rotate_toggled = self.is_rotate_toggled()

        if rotate_toggled:
            data[ROTATE_TOGGLED] = bool_str(rotate_toggled)

        snap_toggled = self.is_snap_toggled()

        if snap_toggled:
            data[SNAP_TOGGLED] = bool_str(snap_toggled)

        ignore_damage = self.is_ignore_damage()

        if ignore_damage:
            data[IGNORE_DAMAGE] = bool_str(ignore_damage)

        flip_two_player_controls = self.is_flip_two_player_controls()

        if flip_two_player_controls:
            data[FLIP_TWO_PLAYER_CONTROLS] = bool_str(flip_two_player_controls)

        always_limit_controls = self.is_always_limit_controls()

        if always_limit_controls:
            data[ALWAYS_LIMIT_CONTROLS] = bool_str(always_limit_controls)

        shown_comment_rules = self.has_shown_comment_rules()

        if shown_comment_rules:
            data[SHOWN_COMMENT_RULES] = bool_str(shown_comment_rules)

        increase_max_history = self.is_increase_max_history()

        if increase_max_history:
            data[INCREASE_MAX_HISTORY] = bool_str(increase_max_history)

        disable_explosion_shake = self.is_disable_explosion_shake()

        if disable_explosion_shake:
            data[DISABLE_EXPLOSION_SHAKE] = bool_str(disable_explosion_shake)

        flip_pause_button = self.is_flip_pause_button()

        if flip_pause_button:
            data[FLIP_PAUSE_BUTTON] = bool_str(flip_pause_button)

        shown_song_terms = self.has_shown_song_terms()

        if shown_song_terms:
            data[SHOWN_SONG_TERMS] = bool_str(shown_song_terms)

        no_song_limit = self.is_no_song_limit()

        if no_song_limit:
            data[NO_SONG_LIMIT] = bool_str(no_song_limit)

        in_memory_songs = self.is_in_memory_songs()

        if in_memory_songs:
            data[IN_MEMORY_SONGS] = bool_str(in_memory_songs)

        higher_audio_quality = self.is_higher_audio_quality()

        if higher_audio_quality:
            data[HIGHER_AUDIO_QUALITY] = bool_str(higher_audio_quality)

        smooth_fix = self.is_smooth_fix()

        if smooth_fix:
            data[SMOOTH_FIX] = bool_str(smooth_fix)

        show_cursor_in_game = self.is_show_cursor_in_game()

        if show_cursor_in_game:
            data[SHOW_CURSOR_IN_GAME] = bool_str(show_cursor_in_game)

        windowed = self.is_windowed()

        if windowed:
            data[WINDOWED] = bool_str(windowed)

        auto_retry = self.is_auto_retry()

        if auto_retry:
            data[AUTO_RETRY] = bool_str(auto_retry)

        auto_checkpoints = self.is_auto_checkpoints()

        if auto_checkpoints:
            data[AUTO_CHECKPOINTS] = bool_str(auto_checkpoints)

        disable_analog_stick = self.is_disable_analog_stick()

        if disable_analog_stick:
            data[DISABLE_ANALOG_STICK] = bool_str(disable_analog_stick)

        shown_options = self.has_shown_options()

        if shown_options:
            data[SHOWN_OPTIONS] = bool_str(shown_options)

        vsync = self.is_vsync()

        if vsync:
            data[VSYNC] = bool_str(vsync)

        call_gl_finish = self.is_call_gl_finish()

        if call_gl_finish:
            data[CALL_GL_FINISH] = bool_str(call_gl_finish)

        force_timer = self.is_force_timer()

        if force_timer:
            data[FORCE_TIMER] = bool_str(force_timer)

        change_song_path = self.is_change_song_path()

        if change_song_path:
            data[CHANGE_SONG_PATH] = bool_str(change_song_path)

        game_center = self.is_game_center()

        if game_center:
            data[GAME_CENTER] = bool_str(game_center)

        preview_mode = self.is_preview_mode()

        if preview_mode:
            data[PREVIEW_MODE] = bool_str(preview_mode)

        show_ground = self.is_show_ground()

        if show_ground:
            data[SHOW_GROUND] = bool_str(show_ground)

        show_grid = self.is_show_grid()

        if show_grid:
            data[SHOW_GRID] = bool_str(show_grid)

        grid_on_top = self.is_grid_on_top()

        if grid_on_top:
            data[GRID_ON_TOP] = bool_str(grid_on_top)

        show_percentage = self.is_show_percentage()

        if show_percentage:
            data[SHOW_PERCENTAGE] = bool_str(show_percentage)

        show_object_info = self.is_show_object_info()

        if show_object_info:
            data[SHOW_OBJECT_INFO] = bool_str(show_object_info)

        increase_max_levels = self.is_increase_max_levels()

        if increase_max_levels:
            data[INCREASE_MAX_LEVELS] = bool_str(increase_max_levels)

        show_effect_lines = self.is_show_effect_lines()

        if show_effect_lines:
            data[SHOW_EFFECT_LINES] = bool_str(show_effect_lines)

        show_trigger_boxes = self.is_show_trigger_boxes()

        if show_trigger_boxes:
            data[SHOW_TRIGGER_BOXES] = bool_str(show_trigger_boxes)

        debug_draw = self.is_debug_draw()

        if debug_draw:
            data[DEBUG_DRAW] = bool_str(debug_draw)

        hide_ui_on_test = self.is_hide_ui_on_test()

        if hide_ui_on_test:
            data[HIDE_UI_ON_TEST] = bool_str(hide_ui_on_test)

        shown_profile_info = self.has_shown_profile_info()

        if shown_profile_info:
            data[SHOWN_PROFILE_INFO] = bool_str(shown_profile_info)

        viewed_self_profile = self.has_viewed_self_profile()

        if viewed_self_profile:
            data[VIEWED_SELF_PROFILE] = bool_str(viewed_self_profile)

        buttons_per_row = self.buttons_per_row

        data[BUTTONS_PER_ROW] = str(buttons_per_row)

        button_rows = self.button_rows

        data[BUTTON_ROWS] = str(button_rows)

        shown_newgrounds_message = self.has_shown_newgrounds_message()

        if shown_newgrounds_message:
            data[SHOWN_NEWGROUNDS_MESSAGE] = bool_str(shown_newgrounds_message)

        fast_practice_reset = self.is_fast_practice_reset()

        if fast_practice_reset:
            data[FAST_PRACTICE_RESET] = bool_str(fast_practice_reset)

        free_games = self.is_free_games()

        if free_games:
            data[FREE_GAMES] = bool_str(free_games)

        check_server_online = self.is_check_server_online()

        if check_server_online:
            data[CHECK_SERVER_ONLINE] = bool_str(check_server_online)

        hold_to_swipe = self.is_hold_to_swipe()

        if hold_to_swipe:
            data[HOLD_TO_SWIPE] = bool_str(hold_to_swipe)

        show_duration_lines = self.is_show_duration_lines()

        if show_duration_lines:
            data[SHOW_DURATION_LINES] = bool_str(show_duration_lines)

        swipe_cycle = self.is_swipe_cycle()

        if swipe_cycle:
            data[SWIPE_CYCLE] = bool_str(swipe_cycle)

        default_mini_icon = self.is_default_mini_icon()

        if default_mini_icon:
            data[DEFAULT_MINI_ICON] = bool_str(default_mini_icon)

        switch_spider_teleport_color = self.is_switch_spider_teleport_color()

        if switch_spider_teleport_color:
            data[SWITCH_SPIDER_TELEPORT_COLOR] = bool_str(switch_spider_teleport_color)

        switch_dash_fire_color = self.is_switch_dash_fire_color()

        if switch_dash_fire_color:
            data[SWITCH_DASH_FIRE_COLOR] = bool_str(switch_dash_fire_color)

        shown_unverified_coins_message = self.has_shown_unverified_coins_message()

        if shown_unverified_coins_message:
            data[SHOWN_UNVERIFIED_COINS_MESSAGE] = bool_str(shown_unverified_coins_message)

        enable_move_optimization = self.is_enable_move_optimization()

        if enable_move_optimization:
            data[ENABLE_MOVE_OPTIMIZATION] = bool_str(enable_move_optimization)

        high_capacity = self.is_high_capacity()

        if high_capacity:
            data[HIGH_CAPACITY] = bool_str(high_capacity)

        high_start_position_accuracy = self.is_high_start_position_accuracy()

        if high_start_position_accuracy:
            data[HIGH_START_POSITION_ACCURACY] = bool_str(high_start_position_accuracy)

        quick_checkpoints = self.is_quick_checkpoints()

        if quick_checkpoints:
            data[QUICK_CHECKPOINTS] = bool_str(quick_checkpoints)

        comment_strategy = self.comment_strategy

        data[COMMENT_STRATEGY] = str(comment_strategy.value)

        shown_unlisted_level_message = self.has_shown_unlisted_level_message()

        if shown_unlisted_level_message:
            data[SHOWN_UNLISTED_LEVEL_MESSAGE] = bool_str(shown_unlisted_level_message)

        disable_gravity_effect = self.is_disable_gravity_effect()

        if disable_gravity_effect:
            data[DISABLE_GRAVITY_EFFECT] = bool_str(disable_gravity_effect)

        new_completed_filter = self.is_new_completed_filter()

        if new_completed_filter:
            data[NEW_COMPLETED_FILTER] = bool_str(new_completed_filter)

        show_restart_button = self.is_show_restart_button()

        if show_restart_button:
            data[SHOW_RESTART_BUTTON] = bool_str(show_restart_button)

        disable_level_comments = self.is_disable_level_comments()

        if disable_level_comments:
            data[DISABLE_LEVEL_COMMENTS] = bool_str(disable_level_comments)

        disable_user_comments = self.is_disable_user_comments()

        if disable_user_comments:
            data[DISABLE_USER_COMMENTS] = bool_str(disable_user_comments)

        featured_levels_only = self.is_featured_levels_only()

        if featured_levels_only:
            data[FEATURED_LEVELS_ONLY] = bool_str(featured_levels_only)

        hide_background = self.is_hide_background()

        if hide_background:
            data[HIDE_BACKGROUND] = bool_str(hide_background)

        hide_grid_on_play = self.is_hide_grid_on_play()

        if hide_grid_on_play:
            data[HIDE_GRID_ON_PLAY] = bool_str(hide_grid_on_play)

        disable_shake = self.is_disable_shake()

        if disable_shake:
            data[DISABLE_SHAKE] = bool_str(disable_shake)

        disable_high_detail_alert = self.is_disable_high_detail_alert()

        if disable_high_detail_alert:
            data[DISABLE_HIGH_DETAIL_ALERT] = bool_str(disable_high_detail_alert)

        disable_song_alert = self.is_disable_song_alert()

        if disable_song_alert:
            data[DISABLE_SONG_ALERT] = bool_str(disable_song_alert)

        manual_order = self.is_manual_order()

        if manual_order:
            data[MANUAL_ORDER] = bool_str(manual_order)

        small_comments = self.is_small_comments()

        if small_comments:
            data[SMALL_COMMENTS] = bool_str(small_comments)

        hide_description = self.is_hide_description()

        if hide_description:
            data[HIDE_DESCRIPTION] = bool_str(hide_description)

        auto_load_comments = self.is_auto_load_comments()

        if auto_load_comments:
            data[AUTO_LOAD_COMMENTS] = bool_str(auto_load_comments)

        created_levels_folder_id = self.created_levels_folder_id

        data[CREATED_LEVELS_FOLDER_ID] = str(created_levels_folder_id)

        saved_levels_folder_id = self.saved_levels_folder_id

        data[SAVED_LEVELS_FOLDER_ID] = str(saved_levels_folder_id)

        increase_local_levels_per_page = self.is_increase_local_levels_per_page()

        if increase_local_levels_per_page:
            data[INCREASE_LOCAL_LEVELS_PER_PAGE] = bool_str(increase_local_levels_per_page)

        more_comments = self.is_more_comments()

        if more_comments:
            data[MORE_COMMENTS] = bool_str(more_comments)

        just_do_not = self.is_just_do_not()

        if just_do_not:
            data[JUST_DO_NOT] = bool_str(just_do_not)

        switch_wave_trail_color = self.is_switch_wave_trail_color()

        if switch_wave_trail_color:
            data[SWITCH_WAVE_TRAIL_COLOR] = bool_str(switch_wave_trail_color)

        enable_link_controls = self.is_enable_link_controls()

        if enable_link_controls:
            data[ENABLE_LINK_CONTROLS] = bool_str(enable_link_controls)

        level_leaderboard_strategy = self.level_leaderboard_strategy

        data[LEVEL_LEADERBOARD_STRATEGY] = str(level_leaderboard_strategy.value)

        show_record = self.is_show_record()

        if show_record:
            data[SHOW_RECORD] = bool_str(show_record)

        practice_death_effect = self.is_practice_death_effect()

        if practice_death_effect:
            data[PRACTICE_DEATH_EFFECT] = bool_str(practice_death_effect)

        force_smooth_fix = self.is_force_smooth_fix()

        if force_smooth_fix:
            data[FORCE_SMOOTH_FIX] = bool_str(force_smooth_fix)

        smooth_fix_in_editor = self.is_smooth_fix_in_editor()

        if smooth_fix_in_editor:
            data[SMOOTH_FIX_IN_EDITOR] = bool_str(smooth_fix_in_editor)

        return data
