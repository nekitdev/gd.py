from attrs import define
from typing_aliases import StringDict
from typing_extensions import Self

from gd.constants import DEFAULT_ID
from gd.enums import CommentStrategy, Filter, LevelLeaderboardStrategy
from gd.models_utils import bool_str, int_bool
from gd.robtop_view import StringRobTopView

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


@define()
class Variables:
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
    def from_robtop_view(cls, view: StringRobTopView[str]) -> Self:
        follow_player = (
            view.get_option(FOLLOW_PLAYER).map(int_bool).unwrap_or(DEFAULT_FOLLOW_PLAYER)
        )
        play_music = view.get_option(PLAY_MUSIC).map(int_bool).unwrap_or(DEFAULT_PLAY_MUSIC)
        swipe = view.get_option(SWIPE).map(int_bool).unwrap_or(DEFAULT_SWIPE)
        free_move = view.get_option(FREE_MOVE).map(int_bool).unwrap_or(DEFAULT_FREE_MOVE)
        filter = view.get_option(FILTER).map(int).map(Filter).unwrap_or(Filter.DEFAULT)
        filter_id = view.get_option(FILTER_ID).map(int).unwrap_or(DEFAULT_ID)
        rotate_toggled = (
            view.get_option(ROTATE_TOGGLED).map(int_bool).unwrap_or(DEFAULT_ROTATE_TOGGLED)
        )
        snap_toggled = view.get_option(SNAP_TOGGLED).map(int_bool).unwrap_or(DEFAULT_SNAP_TOGGLED)
        ignore_damage = (
            view.get_option(IGNORE_DAMAGE).map(int_bool).unwrap_or(DEFAULT_IGNORE_DAMAGE)
        )
        flip_two_player_controls = (
            view.get_option(FLIP_TWO_PLAYER_CONTROLS)
            .map(int_bool)
            .unwrap_or(DEFAULT_FLIP_TWO_PLAYER_CONTROLS)
        )
        always_limit_controls = (
            view.get_option(ALWAYS_LIMIT_CONTROLS)
            .map(int_bool)
            .unwrap_or(DEFAULT_ALWAYS_LIMIT_CONTROLS)
        )
        shown_comment_rules = (
            view.get_option(SHOWN_COMMENT_RULES)
            .map(int_bool)
            .unwrap_or(DEFAULT_SHOWN_COMMENT_RULES)
        )
        increase_max_history = (
            view.get_option(INCREASE_MAX_HISTORY)
            .map(int_bool)
            .unwrap_or(DEFAULT_INCREASE_MAX_HISTORY)
        )
        disable_explosion_shake = (
            view.get_option(DISABLE_EXPLOSION_SHAKE)
            .map(int_bool)
            .unwrap_or(DEFAULT_DISABLE_EXPLOSION_SHAKE)
        )
        flip_pause_button = (
            view.get_option(FLIP_PAUSE_BUTTON).map(int_bool).unwrap_or(DEFAULT_FLIP_PAUSE_BUTTON)
        )
        shown_song_terms = (
            view.get_option(SHOWN_SONG_TERMS).map(int_bool).unwrap_or(DEFAULT_SHOWN_SONG_TERMS)
        )
        no_song_limit = (
            view.get_option(NO_SONG_LIMIT).map(int_bool).unwrap_or(DEFAULT_NO_SONG_LIMIT)
        )
        in_memory_songs = (
            view.get_option(IN_MEMORY_SONGS).map(int_bool).unwrap_or(DEFAULT_IN_MEMORY_SONGS)
        )
        higher_audio_quality = (
            view.get_option(HIGHER_AUDIO_QUALITY)
            .map(int_bool)
            .unwrap_or(DEFAULT_HIGHER_AUDIO_QUALITY)
        )
        smooth_fix = view.get_option(SMOOTH_FIX).map(int_bool).unwrap_or(DEFAULT_SMOOTH_FIX)
        show_cursor_in_game = (
            view.get_option(SHOW_CURSOR_IN_GAME)
            .map(int_bool)
            .unwrap_or(DEFAULT_SHOW_CURSOR_IN_GAME)
        )
        windowed = view.get_option(WINDOWED).map(int_bool).unwrap_or(DEFAULT_WINDOWED)
        auto_retry = view.get_option(AUTO_RETRY).map(int_bool).unwrap_or(DEFAULT_AUTO_RETRY)
        auto_checkpoints = (
            view.get_option(AUTO_CHECKPOINTS).map(int_bool).unwrap_or(DEFAULT_AUTO_CHECKPOINTS)
        )
        disable_analog_stick = (
            view.get_option(DISABLE_ANALOG_STICK)
            .map(int_bool)
            .unwrap_or(DEFAULT_DISABLE_ANALOG_STICK)
        )
        shown_options = (
            view.get_option(SHOWN_OPTIONS).map(int_bool).unwrap_or(DEFAULT_SHOWN_OPTIONS)
        )
        vsync = view.get_option(VSYNC).map(int_bool).unwrap_or(DEFAULT_VSYNC)
        call_gl_finish = (
            view.get_option(CALL_GL_FINISH).map(int_bool).unwrap_or(DEFAULT_CALL_GL_FINISH)
        )
        force_timer = view.get_option(FORCE_TIMER).map(int_bool).unwrap_or(DEFAULT_FORCE_TIMER)
        change_song_path = (
            view.get_option(CHANGE_SONG_PATH).map(int_bool).unwrap_or(DEFAULT_CHANGE_SONG_PATH)
        )
        game_center = view.get_option(GAME_CENTER).map(int_bool).unwrap_or(DEFAULT_GAME_CENTER)
        preview_mode = view.get_option(PREVIEW_MODE).map(int_bool).unwrap_or(DEFAULT_PREVIEW_MODE)
        show_ground = view.get_option(SHOW_GROUND).map(int_bool).unwrap_or(DEFAULT_SHOW_GROUND)
        show_grid = view.get_option(SHOW_GRID).map(int_bool).unwrap_or(DEFAULT_SHOW_GRID)
        grid_on_top = view.get_option(GRID_ON_TOP).map(int_bool).unwrap_or(DEFAULT_GRID_ON_TOP)
        show_percentage = (
            view.get_option(SHOW_PERCENTAGE).map(int_bool).unwrap_or(DEFAULT_SHOW_PERCENTAGE)
        )
        show_object_info = (
            view.get_option(SHOW_OBJECT_INFO).map(int_bool).unwrap_or(DEFAULT_SHOW_OBJECT_INFO)
        )
        increase_max_levels = (
            view.get_option(INCREASE_MAX_LEVELS)
            .map(int_bool)
            .unwrap_or(DEFAULT_INCREASE_MAX_LEVELS)
        )
        show_effect_lines = (
            view.get_option(SHOW_EFFECT_LINES).map(int_bool).unwrap_or(DEFAULT_SHOW_EFFECT_LINES)
        )
        show_trigger_boxes = (
            view.get_option(SHOW_TRIGGER_BOXES).map(int_bool).unwrap_or(DEFAULT_SHOW_TRIGGER_BOXES)
        )
        debug_draw = view.get_option(DEBUG_DRAW).map(int_bool).unwrap_or(DEFAULT_DEBUG_DRAW)
        hide_ui_on_test = (
            view.get_option(HIDE_UI_ON_TEST).map(int_bool).unwrap_or(DEFAULT_HIDE_UI_ON_TEST)
        )
        shown_profile_info = (
            view.get_option(SHOWN_PROFILE_INFO).map(int_bool).unwrap_or(DEFAULT_SHOWN_PROFILE_INFO)
        )
        viewed_self_profile = (
            view.get_option(VIEWED_SELF_PROFILE)
            .map(int_bool)
            .unwrap_or(DEFAULT_VIEWED_SELF_PROFILE)
        )
        buttons_per_row = (
            view.get_option(BUTTONS_PER_ROW).map(int).unwrap_or(DEFAULT_BUTTONS_PER_ROW)
        )
        button_rows = view.get_option(BUTTON_ROWS).map(int).unwrap_or(DEFAULT_BUTTON_ROWS)
        shown_newgrounds_message = (
            view.get_option(SHOWN_NEWGROUNDS_MESSAGE)
            .map(int_bool)
            .unwrap_or(DEFAULT_SHOWN_NEWGROUNDS_MESSAGE)
        )
        fast_practice_reset = (
            view.get_option(FAST_PRACTICE_RESET)
            .map(int_bool)
            .unwrap_or(DEFAULT_FAST_PRACTICE_RESET)
        )
        free_games = view.get_option(FREE_GAMES).map(int_bool).unwrap_or(DEFAULT_FREE_GAMES)
        check_server_online = (
            view.get_option(CHECK_SERVER_ONLINE)
            .map(int_bool)
            .unwrap_or(DEFAULT_CHECK_SERVER_ONLINE)
        )
        hold_to_swipe = (
            view.get_option(HOLD_TO_SWIPE).map(int_bool).unwrap_or(DEFAULT_HOLD_TO_SWIPE)
        )
        show_duration_lines = (
            view.get_option(SHOW_DURATION_LINES)
            .map(int_bool)
            .unwrap_or(DEFAULT_SHOW_DURATION_LINES)
        )
        swipe_cycle = view.get_option(SWIPE_CYCLE).map(int_bool).unwrap_or(DEFAULT_SWIPE_CYCLE)
        default_mini_icon = (
            view.get_option(DEFAULT_MINI_ICON).map(int_bool).unwrap_or(DEFAULT_DEFAULT_MINI_ICON)
        )
        switch_spider_teleport_color = (
            view.get_option(SWITCH_SPIDER_TELEPORT_COLOR)
            .map(int_bool)
            .unwrap_or(DEFAULT_SWITCH_SPIDER_TELEPORT_COLOR)
        )
        switch_dash_fire_color = (
            view.get_option(SWITCH_DASH_FIRE_COLOR)
            .map(int_bool)
            .unwrap_or(DEFAULT_SWITCH_DASH_FIRE_COLOR)
        )
        shown_unverified_coins_message = (
            view.get_option(SHOWN_UNVERIFIED_COINS_MESSAGE)
            .map(int_bool)
            .unwrap_or(DEFAULT_SHOWN_UNVERIFIED_COINS_MESSAGE)
        )
        enable_move_optimization = (
            view.get_option(ENABLE_MOVE_OPTIMIZATION)
            .map(int_bool)
            .unwrap_or(DEFAULT_ENABLE_MOVE_OPTIMIZATION)
        )
        high_capacity = (
            view.get_option(HIGH_CAPACITY).map(int_bool).unwrap_or(DEFAULT_HIGH_CAPACITY)
        )
        high_start_position_accuracy = (
            view.get_option(HIGH_START_POSITION_ACCURACY)
            .map(int_bool)
            .unwrap_or(DEFAULT_HIGH_START_POSITION_ACCURACY)
        )
        quick_checkpoints = (
            view.get_option(QUICK_CHECKPOINTS).map(int_bool).unwrap_or(DEFAULT_QUICK_CHECKPOINTS)
        )
        comment_strategy = (
            view.get_option(COMMENT_STRATEGY)
            .map(int)
            .map(CommentStrategy)
            .unwrap_or(CommentStrategy.DEFAULT)
        )
        shown_unlisted_level_message = (
            view.get_option(SHOWN_UNLISTED_LEVEL_MESSAGE)
            .map(int_bool)
            .unwrap_or(DEFAULT_SHOWN_UNLISTED_LEVEL_MESSAGE)
        )
        disable_gravity_effect = (
            view.get_option(DISABLE_GRAVITY_EFFECT)
            .map(int_bool)
            .unwrap_or(DEFAULT_DISABLE_GRAVITY_EFFECT)
        )
        new_completed_filter = (
            view.get_option(NEW_COMPLETED_FILTER)
            .map(int_bool)
            .unwrap_or(DEFAULT_NEW_COMPLETED_FILTER)
        )
        show_restart_button = (
            view.get_option(SHOW_RESTART_BUTTON)
            .map(int_bool)
            .unwrap_or(DEFAULT_SHOW_RESTART_BUTTON)
        )
        disable_level_comments = (
            view.get_option(DISABLE_LEVEL_COMMENTS)
            .map(int_bool)
            .unwrap_or(DEFAULT_DISABLE_LEVEL_COMMENTS)
        )
        disable_user_comments = (
            view.get_option(DISABLE_USER_COMMENTS)
            .map(int_bool)
            .unwrap_or(DEFAULT_DISABLE_USER_COMMENTS)
        )
        featured_levels_only = (
            view.get_option(FEATURED_LEVELS_ONLY)
            .map(int_bool)
            .unwrap_or(DEFAULT_FEATURED_LEVELS_ONLY)
        )
        hide_background = (
            view.get_option(HIDE_BACKGROUND).map(int_bool).unwrap_or(DEFAULT_HIDE_BACKGROUND)
        )
        hide_grid_on_play = (
            view.get_option(HIDE_GRID_ON_PLAY).map(int_bool).unwrap_or(DEFAULT_HIDE_GRID_ON_PLAY)
        )
        disable_shake = (
            view.get_option(DISABLE_SHAKE).map(int_bool).unwrap_or(DEFAULT_DISABLE_SHAKE)
        )
        disable_high_detail_alert = (
            view.get_option(DISABLE_HIGH_DETAIL_ALERT)
            .map(int_bool)
            .unwrap_or(DEFAULT_DISABLE_HIGH_DETAIL_ALERT)
        )
        disable_song_alert = (
            view.get_option(DISABLE_SONG_ALERT).map(int_bool).unwrap_or(DEFAULT_DISABLE_SONG_ALERT)
        )
        manual_order = view.get_option(MANUAL_ORDER).map(int_bool).unwrap_or(DEFAULT_MANUAL_ORDER)
        small_comments = (
            view.get_option(SMALL_COMMENTS).map(int_bool).unwrap_or(DEFAULT_SMALL_COMMENTS)
        )
        hide_description = (
            view.get_option(HIDE_DESCRIPTION).map(int_bool).unwrap_or(DEFAULT_HIDE_DESCRIPTION)
        )
        auto_load_comments = (
            view.get_option(AUTO_LOAD_COMMENTS).map(int_bool).unwrap_or(DEFAULT_AUTO_LOAD_COMMENTS)
        )
        created_levels_folder_id = (
            view.get_option(CREATED_LEVELS_FOLDER_ID)
            .map(int)
            .unwrap_or(DEFAULT_CREATED_LEVELS_FOLDER_ID)
        )
        saved_levels_folder_id = (
            view.get_option(SAVED_LEVELS_FOLDER_ID)
            .map(int)
            .unwrap_or(DEFAULT_SAVED_LEVELS_FOLDER_ID)
        )
        increase_local_levels_per_page = (
            view.get_option(INCREASE_LOCAL_LEVELS_PER_PAGE)
            .map(int_bool)
            .unwrap_or(DEFAULT_INCREASE_LOCAL_LEVELS_PER_PAGE)
        )
        more_comments = (
            view.get_option(MORE_COMMENTS).map(int_bool).unwrap_or(DEFAULT_MORE_COMMENTS)
        )
        just_do_not = view.get_option(JUST_DO_NOT).map(int_bool).unwrap_or(DEFAULT_JUST_DO_NOT)
        switch_wave_trail_color = (
            view.get_option(SWITCH_WAVE_TRAIL_COLOR)
            .map(int_bool)
            .unwrap_or(DEFAULT_SWITCH_WAVE_TRAIL_COLOR)
        )
        enable_link_controls = (
            view.get_option(ENABLE_LINK_CONTROLS)
            .map(int_bool)
            .unwrap_or(DEFAULT_ENABLE_LINK_CONTROLS)
        )
        level_leaderboard_strategy = (
            view.get_option(LEVEL_LEADERBOARD_STRATEGY)
            .map(int)
            .map(LevelLeaderboardStrategy)
            .unwrap_or(LevelLeaderboardStrategy.DEFAULT)
        )
        show_record = view.get_option(SHOW_RECORD).map(int_bool).unwrap_or(DEFAULT_SHOW_RECORD)
        practice_death_effect = (
            view.get_option(PRACTICE_DEATH_EFFECT)
            .map(int_bool)
            .unwrap_or(DEFAULT_PRACTICE_DEATH_EFFECT)
        )
        force_smooth_fix = (
            view.get_option(FORCE_SMOOTH_FIX).map(int_bool).unwrap_or(DEFAULT_FORCE_SMOOTH_FIX)
        )
        smooth_fix_in_editor = (
            view.get_option(SMOOTH_FIX_IN_EDITOR)
            .map(int_bool)
            .unwrap_or(DEFAULT_SMOOTH_FIX_IN_EDITOR)
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
