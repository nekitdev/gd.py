# type: ignore

from gd.memory.cocos import CCLayer, CCNode, CCPoint
from gd.memory.marker import Struct, mut_pointer, bool_t, float_t, int_t, string_t, void


class GameLevel(CCNode):
    last_save: mut_pointer(void)  # CCDictionary

    level_id_random: int_t
    level_id_seed: int_t
    level_id: int_t

    name: string_t
    description: string_t

    uncompressed_data: string_t

    user_name: string_t

    record_string: string_t

    uploaded_at_string: string_t
    updated_at_string: string_t

    user_id_random: int_t
    user_id_seed: int_t
    user_id: int_t

    account_id_random: int_t
    account_id_seed: int_t
    account_id: int_t

    difficulty: int_t
    track_id: int_t
    song_id: int_t

    revision: int_t

    unlisted: bool_t

    object_count_random: int_t
    object_count_seed: int_t
    object_count: int_t

    averate_difficulty: int_t
    difficulty_denominator: int_t
    difficulty_numerator: int_t

    downloads: int_t

    editable: bool_t

    gauntlet_level: bool_t
    gauntlet_level_other: bool_t

    editor_seconds: int_t
    copies_seconds: int_t

    low_detail_mode: bool_t
    low_detail_mode_toggled: bool_t

    verified_random: int_t
    verified_seed: int_t
    verified: bool_t

    uploaded: bool_t

    modified: bool_t

    version: int_t

    game_version_value: int_t

    attempts_rand: int_t
    attempts_seed: int_t
    attempts: int_t

    jumps_random: int_t
    jumps_seed: int_t
    jumps: int_t

    clicks_random: int_t
    clicks_seed: int_t
    clicks: int_t

    attempt_time_random: int_t
    attempt_time_seed: int_t
    attempt_time: int_t

    chk: int_t

    chk_valid: bool_t
    legit: bool_t

    normal_percent: int_t
    normal_percent_seed: int_t
    normal_percent_random: int_t

    orbs_random: int_t
    orbs_seed: int_t
    orbs: int_t

    new_normal_percent_random: int_t
    new_normal_percent_seed: int_t
    new_normal_percent: int_t

    practice_percent: int_t

    likes: int_t
    dislikes: int_t

    level_length_value: int_t

    score: int_t

    epic: bool_t
    level_favorite: bool_t

    level_folder: int_t

    timely_id_random: int_t
    timely_id_seed: int_t
    timely_id: int_t

    demon_random: int_t
    demon_seed: int_t
    demon: int_t

    demon_difficulty: int_t

    stars_random: int_t
    stars_seed: int_t
    stars: int_t

    auto: bool_t
    coins: int_t

    verified_coins_random: int_t
    verified_coins_seed: int_t
    verified_coins: int_t

    password_random: int_t
    password_seed: int_t

    original_id_random: int_t
    original_id_seed: int_t
    original_id: int_t

    two_player: bool_t

    failed_password_attempts: int_t

    first_coin_acquired_random: int_t
    first_coin_acquired_seed: int_t
    first_coin_acquired: int_t

    second_coin_acquired_random: int_t
    second_coin_acquired_seed: int_t
    second_coin_acquired: int_t

    third_coint_acquired_random: int_t
    third_coint_acquired_seed: int_t
    third_coint_acquired: int_t

    requested_stars: int_t

    song_warning: bool_t

    star_ratings: int_t
    total_star_ratings: int_t
    max_star_ratings: int_t
    min_star_ratings: int_t
    demon_votes: int_t
    rate_stars: int_t
    rate_feature: int_t

    rate_user: string_t

    do_not_save: bool_t
    downloaded: bool_t

    require_coins: int_t
    unlocked: bool_t

    last_camera_position: CCPoint

    last_editor_zoom: float_t
    last_build_time: int_t
    last_build_page: int_t
    last_build_group_id: int_t

    level_type_value: int_t  # enum

    some_id: int_t  # ?
    temporary_name: string_t
    capacity_string: string_t

    high_detail: bool_t

    progress_string: string_t


class TriggerEffectDelegate(Struct, vtable=True):
    pass


class BaseGameManager(CCNode, vtable=True):
    ...


class GameManager(BaseGameManager, vtable=True):
    ...


class BaseGameLayer(TriggerEffectDelegate, CCLayer, vtable=True):
    ...