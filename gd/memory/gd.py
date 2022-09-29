from gd.memory.base import struct
from gd.memory.cocos import CCLayer, CCNode, CCPoint
from gd.memory.data import Bool, Float, Int, MutPointerData, StructData, Void


class GameLevel(CCNode):
    last_save = MutPointerData(Void())

    level_id_random = Int()
    level_id_seed = Int()
    level_id = Int()

    name = StringData()
    description = StringData()

    unprocessed_data = StringData()

    user_name = StringData()

    record_string = StringData()

    uploaded_at_string = StringData()
    updated_at_string = StringData()

    user_id_random = Int()
    user_id_seed = Int()
    user_id = Int()

    account_id_random = Int()
    account_id_seed = Int()
    account_id = Int()

    difficulty = Int()
    track_id = Int()
    song_id = Int()

    revision = Int()

    unlisted = Bool()

    object_count_random = Int()
    object_count_seed = Int()
    object_count = Int()

    average_difficulty = Int()
    difficulty_denominator = Int()
    difficulty_numerator = Int()

    downloads = Int()

    editable = Bool()

    gauntlet_level = Bool()
    gauntlet_level_other = Bool()

    editor_seconds = Int()
    copies_seconds = Int()

    low_detail = Bool()
    low_detail_toggled = Bool()

    verified_random = Int()
    verified_seed = Int()
    verified = Bool()

    uploaded = Bool()

    modified = Bool()

    version = Int()

    game_version_value = Int()

    attempts_rand = Int()
    attempts_seed = Int()
    attempts = Int()

    jumps_random = Int()
    jumps_seed = Int()
    jumps = Int()

    clicks_random = Int()
    clicks_seed = Int()
    clicks = Int()

    attempt_time_random = Int()
    attempt_time_seed = Int()
    attempt_time = Int()

    chk = Int()

    chk_valid = Bool()
    legit = Bool()

    normal_percent = Int()
    normal_percent_seed = Int()
    normal_percent_random = Int()

    orbs_random = Int()
    orbs_seed = Int()
    orbs = Int()

    new_normal_percent_random = Int()
    new_normal_percent_seed = Int()
    new_normal_percent = Int()

    practice_percent = Int()

    likes = Int()
    dislikes = Int()

    level_length_value = Int()

    score = Int()

    epic = Bool()
    level_favorite = Bool()

    level_folder = Int()

    timely_id_random = Int()
    timely_id_seed = Int()
    timely_id = Int()

    demon_random = Int()
    demon_seed = Int()
    demon = Int()

    demon_difficulty = Int()

    stars_random = Int()
    stars_seed = Int()
    stars = Int()

    auto = Bool()
    coins = Int()

    verified_coins_random = Int()
    verified_coins_seed = Int()
    verified_coins = Int()

    password_random = Int()
    password_seed = Int()

    original_id_random = Int()
    original_id_seed = Int()
    original_id = Int()

    two_player = Bool()

    failed_password_attempts = Int()

    first_coin_acquired_random = Int()
    first_coin_acquired_seed = Int()
    first_coin_acquired = Int()

    second_coin_acquired_random = Int()
    second_coin_acquired_seed = Int()
    second_coin_acquired = Int()

    third_coint_acquired_random = Int()
    third_coint_acquired_seed = Int()
    third_coint_acquired = Int()

    requested_stars = Int()

    song_warning = Bool()

    star_ratings = Int()
    total_star_ratings = Int()
    max_star_ratings = Int()
    min_star_ratings = Int()
    demon_votes = Int()
    rate_stars = Int()
    rate_feature = Int()

    rate_user = StringData()

    do_not_save = Bool()
    downloaded = Bool()

    require_coins = Int()
    unlocked = Bool()

    last_camera_position = StructData(CCPoint)

    last_editor_zoom = Float()
    last_build_time = Int()
    last_build_page = Int()
    last_build_group_id = Int()

    level_type_value = Int()  # enum

    some_id = Int()  # ?
    temporary_name = StringData()
    capacity_string = StringData()

    high_detail = Bool()

    progress_string = StringData()


@struct(virtual=True)
class TriggerEffectDelegate(Struct):
    default_enter_effect = Bool()


@struct(virtual=True)
class BaseGameManager(CCNode, vtable=True):
    file_name = StringData()

    setup = Bool()
    saved = Bool()

    quick_save = Bool()
    reload_all = Bool()


class GameManager(BaseGameManager, vtable=True):
    ...


class AccountManager(CCNode, vtable=True):
    data = MutPointerData(Void())

    password = StringData()
    user_name = StringData()

    account_id_random = Int()
    account_id_seed = Int()
    account_id = Int()

    register_delegate = MutPointerData(Void())
    login_delegate = MutPointerData(Void())
    account_delegate = MutPointerData(Void())
    backup_delegate = MutPointerData(Void())
    sync_delegate = MutPointerData(Void())
    update_account_delegate = MutPointerData(Void())


class BaseGameLayer(TriggerEffectDelegate, CCLayer, vtable=True):
    ...


class PlayLayer(BaseGameLayer, vtable=True):
    ...


class EditorLayer(BaseGameLayer, vtable=True):
    ...
