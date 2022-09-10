# type: ignore

from typing_extensions import TypeAlias

from gd.memory.cocos import CCLayer, CCNode, CCPoint
from gd.memory.fields import mut_field
from gd.memory.markers import Struct, bool_t, float_t, int_t, mut_pointer, string_t, void

void_mut_pointer = mut_pointer(void)


class GameLevel(CCNode):
    last_save: void_mut_pointer = mut_field()

    level_id_random: int_t = mut_field()
    level_id_seed: int_t = mut_field()
    level_id: int_t = mut_field()

    name: string_t = mut_field()
    description: string_t = mut_field()

    unprocessed_data: string_t = mut_field()

    user_name: string_t = mut_field()

    record_string: string_t = mut_field()

    uploaded_at_string: string_t = mut_field()
    updated_at_string: string_t = mut_field()

    user_id_random: int_t = mut_field()
    user_id_seed: int_t = mut_field()
    user_id: int_t = mut_field()

    account_id_random: int_t = mut_field()
    account_id_seed: int_t = mut_field()
    account_id: int_t = mut_field()

    difficulty: int_t = mut_field()
    track_id: int_t = mut_field()
    song_id: int_t = mut_field()

    revision: int_t = mut_field()

    unlisted: bool_t = mut_field()

    object_count_random: int_t = mut_field()
    object_count_seed: int_t = mut_field()
    object_count: int_t = mut_field()

    averate_difficulty: int_t = mut_field()
    difficulty_denominator: int_t = mut_field()
    difficulty_numerator: int_t = mut_field()

    downloads: int_t = mut_field()

    editable: bool_t = mut_field()

    gauntlet_level: bool_t = mut_field()
    gauntlet_level_other: bool_t = mut_field()

    editor_seconds: int_t = mut_field()
    copies_seconds: int_t = mut_field()

    low_detail_mode: bool_t = mut_field()
    low_detail_mode_toggled: bool_t = mut_field()

    verified_random: int_t = mut_field()
    verified_seed: int_t = mut_field()
    verified: bool_t = mut_field()

    uploaded: bool_t = mut_field()

    modified: bool_t = mut_field()

    version: int_t = mut_field()

    game_version_value: int_t = mut_field()

    attempts_rand: int_t = mut_field()
    attempts_seed: int_t = mut_field()
    attempts: int_t = mut_field()

    jumps_random: int_t = mut_field()
    jumps_seed: int_t = mut_field()
    jumps: int_t = mut_field()

    clicks_random: int_t = mut_field()
    clicks_seed: int_t = mut_field()
    clicks: int_t = mut_field()

    attempt_time_random: int_t = mut_field()
    attempt_time_seed: int_t = mut_field()
    attempt_time: int_t = mut_field()

    chk: int_t = mut_field()

    chk_valid: bool_t = mut_field()
    legit: bool_t = mut_field()

    normal_percent: int_t = mut_field()
    normal_percent_seed: int_t = mut_field()
    normal_percent_random: int_t = mut_field()

    orbs_random: int_t = mut_field()
    orbs_seed: int_t = mut_field()
    orbs: int_t = mut_field()

    new_normal_percent_random: int_t = mut_field()
    new_normal_percent_seed: int_t = mut_field()
    new_normal_percent: int_t = mut_field()

    practice_percent: int_t = mut_field()

    likes: int_t = mut_field()
    dislikes: int_t = mut_field()

    level_length_value: int_t = mut_field()

    score: int_t = mut_field()

    epic: bool_t = mut_field()
    level_favorite: bool_t = mut_field()

    level_folder: int_t = mut_field()

    timely_id_random: int_t = mut_field()
    timely_id_seed: int_t = mut_field()
    timely_id: int_t = mut_field()

    demon_random: int_t = mut_field()
    demon_seed: int_t = mut_field()
    demon: int_t = mut_field()

    demon_difficulty: int_t = mut_field()

    stars_random: int_t = mut_field()
    stars_seed: int_t = mut_field()
    stars: int_t = mut_field()

    auto: bool_t = mut_field()
    coins: int_t = mut_field()

    verified_coins_random: int_t = mut_field()
    verified_coins_seed: int_t = mut_field()
    verified_coins: int_t = mut_field()

    password_random: int_t = mut_field()
    password_seed: int_t = mut_field()

    original_id_random: int_t = mut_field()
    original_id_seed: int_t = mut_field()
    original_id: int_t = mut_field()

    two_player: bool_t = mut_field()

    failed_password_attempts: int_t = mut_field()

    first_coin_acquired_random: int_t = mut_field()
    first_coin_acquired_seed: int_t = mut_field()
    first_coin_acquired: int_t = mut_field()

    second_coin_acquired_random: int_t = mut_field()
    second_coin_acquired_seed: int_t = mut_field()
    second_coin_acquired: int_t = mut_field()

    third_coint_acquired_random: int_t = mut_field()
    third_coint_acquired_seed: int_t = mut_field()
    third_coint_acquired: int_t = mut_field()

    requested_stars: int_t = mut_field()

    song_warning: bool_t = mut_field()

    star_ratings: int_t = mut_field()
    total_star_ratings: int_t = mut_field()
    max_star_ratings: int_t = mut_field()
    min_star_ratings: int_t = mut_field()
    demon_votes: int_t = mut_field()
    rate_stars: int_t = mut_field()
    rate_feature: int_t = mut_field()

    rate_user: string_t = mut_field()

    do_not_save: bool_t = mut_field()
    downloaded: bool_t = mut_field()

    require_coins: int_t = mut_field()
    unlocked: bool_t = mut_field()

    last_camera_position: CCPoint = mut_field()

    last_editor_zoom: float_t = mut_field()
    last_build_time: int_t = mut_field()
    last_build_page: int_t = mut_field()
    last_build_group_id: int_t = mut_field()

    level_type_value: int_t = mut_field()  # enum

    some_id: int_t = mut_field()  # ?
    temporary_name: string_t = mut_field()
    capacity_string: string_t = mut_field()

    high_detail: bool_t = mut_field()

    progress_string: string_t = mut_field()


class TriggerEffectDelegate(Struct, vtable=True):
    pass


class BaseGameManager(CCNode, vtable=True):
    file_name: string_t = mut_field()

    setup: bool_t = mut_field()
    saved: bool_t = mut_field()


class GameManager(BaseGameManager, vtable=True):
    # file: string_t

    ...


class AccountManager(CCNode, vtable=True):
    data: void_mut_pointer = mut_field()  # CCDictionary

    password: string_t = mut_field()
    user_name: string_t = mut_field()

    account_id: int_t = mut_field()

    # check types of these fields
    _unknown_0: int_t = mut_field()
    _unknown_1: int_t = mut_field()

    register_delegate: void_mut_pointer = mut_field()
    login_delegate: void_mut_pointer = mut_field()
    account_delegate: void_mut_pointer = mut_field()
    backup_delegate: void_mut_pointer = mut_field()
    sync_delegate: void_mut_pointer = mut_field()
    update_account_delegate: void_mut_pointer = mut_field()


class BaseGameLayer(TriggerEffectDelegate, CCLayer, vtable=True):
    ...


class PlayLayer(BaseGameLayer, vtable=True):
    ...


class EditorLayer(BaseGameLayer, vtable=True):
    ...
