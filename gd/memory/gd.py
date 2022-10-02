from gd.enums import GameMode, Speed
from gd.http import R
from gd.memory.base import Struct, StructData, struct
from gd.memory.cocos import CCLayer, CCNode, CCNodeContainer, CCPoint, CCSpriteBatchNode, CCSpritePlus
from gd.memory.data import Bool, Double, Float, Int
from gd.memory.fields import Field
from gd.memory.pointers import MutPointerData
from gd.memory.special import Void
from gd.memory.string import StringData

__all__ = (
    "GameManager",
    "AccountManager",
    "BaseGameLayer",
    "PlayLayer",
    "EditorLayer",
    "LevelSettings",
    "GameLevel",
)


@struct()
class GameLevel(CCNode):
    last_save = Field(MutPointerData(Void()))  # CCDictionary*

    level_id_random = Field(Int())
    level_id_seed = Field(Int())
    level_id = Field(Int())

    name = Field(StringData())
    description = Field(StringData())

    unprocessed_data = Field(StringData())

    creator_name = Field(StringData())

    recording_string = Field(StringData())

    uploaded_at_string = Field(StringData())
    updated_at_string = Field(StringData())

    user_id_random = Field(Int())
    user_id_seed = Field(Int())
    user_id = Field(Int())

    account_id_random = Field(Int())
    account_id_seed = Field(Int())
    account_id = Field(Int())

    difficulty = Field(Int())
    official_song_id = Field(Int())
    custom_song_id = Field(Int())

    revision = Field(Int())

    unlisted = Field(Bool())

    object_count_random = Field(Int())
    object_count_seed = Field(Int())
    object_count = Field(Int())

    level_order = Field(Int())

    difficulty_denominator = Field(Int())
    difficulty_numerator = Field(Int())

    downloads = Field(Int())

    editable = Field(Bool())

    gauntlet = Field(Bool())
    free_game = Field(Bool())

    editor_seconds = Field(Int())
    copies_seconds = Field(Int())

    low_detail = Field(Bool())
    low_detail_toggled = Field(Bool())

    verified_random = Field(Int())
    verified_seed = Field(Int())
    verified = Field(Bool())

    uploaded = Field(Bool())

    modified = Field(Bool())

    version = Field(Int())

    game_version_value = Field(Int())

    attempts_rand = Field(Int())
    attempts_seed = Field(Int())
    attempts = Field(Int())

    jumps_random = Field(Int())
    jumps_seed = Field(Int())
    jumps = Field(Int())

    clicks_random = Field(Int())
    clicks_seed = Field(Int())
    clicks = Field(Int())

    attempt_time_random = Field(Int())
    attempt_time_seed = Field(Int())
    attempt_time = Field(Int())

    seed = Field(Int())

    chk_valid = Field(Bool())
    anticheat = Field(Bool())

    normal_percent = Field(Int())
    normal_percent_seed = Field(Int())
    normal_percent_random = Field(Int())

    orbs_random = Field(Int())
    orbs_seed = Field(Int())
    orbs = Field(Int())

    new_normal_percent_random = Field(Int())
    new_normal_percent_seed = Field(Int())
    new_normal_percent = Field(Int())

    practice_percent = Field(Int())

    likes = Field(Int())
    dislikes = Field(Int())

    level_length_value = Field(Int())

    score = Field(Int())

    epic = Field(Bool())
    favorite = Field(Bool())

    folder_id = Field(Int())

    timely_id_random = Field(Int())
    timely_id_seed = Field(Int())
    timely_id = Field(Int())

    demon_random = Field(Int())
    demon_seed = Field(Int())
    demon = Field(Int())

    demon_difficulty = Field(Int())

    stars_random = Field(Int())
    stars_seed = Field(Int())
    stars = Field(Int())

    auto = Field(Bool())
    coins = Field(Int())

    verified_coins_random = Field(Int())
    verified_coins_seed = Field(Int())
    verified_coins = Field(Int())

    password_random = Field(Int())
    password_seed = Field(Int())

    original_id_random = Field(Int())
    original_id_seed = Field(Int())
    original_id = Field(Int())

    two_player = Field(Bool())

    failed_password_attempts = Field(Int())

    first_coin_collected_random = Field(Int())
    first_coin_collected_seed = Field(Int())
    first_coin_collected = Field(Int())

    second_coin_collected_random = Field(Int())
    second_coin_collected_seed = Field(Int())
    second_coin_collected = Field(Int())

    third_coin_collected_random = Field(Int())
    third_coin_collected_seed = Field(Int())
    third_coin_collected = Field(Int())

    requested_stars = Field(Int())

    song_warning = Field(Bool())

    star_ratings = Field(Int())
    total_star_ratings = Field(Int())
    max_star_ratings = Field(Int())
    min_star_ratings = Field(Int())
    demon_votes = Field(Int())
    rate_stars = Field(Int())
    rate_feature = Field(Int())

    rate_user = Field(StringData())

    do_not_save = Field(Bool())
    downloadable = Field(Bool())

    required_coins = Field(Int())
    unlocked = Field(Bool())

    last_editor_position = Field(StructData(CCPoint))

    last_editor_zoom = Field(Float())

    last_build_time = Field(Int())
    last_build_page = Field(Int())
    last_build_group_id = Field(Int())

    level_type_value = Field(Int())

    some_id = Field(Int())  # ?

    temporary_name = Field(StringData())
    capacity_string = Field(StringData())

    high_detail = Field(Bool())

    progress_string = Field(StringData())


@struct()
class LevelSettings(CCNode):
    effect_manager = Field(MutPointerData(Void()))
    game_mode_value = Field(Int())
    speed_value = Field(Int())
    mini_mode = Field(Bool())
    dual_mode = Field(Bool())
    two_player = Field(Bool())
    song_offset = Field(Float())
    song_fade_in = Field(Bool())
    song_fade_out = Field(Bool())
    background_id = Field(Int())
    ground_id = Field(Int())
    font_id = Field(Int())
    start_position = Field(Bool())
    flip_gravity = Field(Bool())
    level = Field(MutPointerData(StructData(GameLevel)))
    guidelines_string = Field(StringData())
    song_custom = Field(Bool())
    color_page = Field(Int())
    ground_line_id = Field(Int())

    @property
    def speed(self) -> Speed:
        return Speed(self.speed_value)

    @property
    def game_mode(self) -> GameMode:
        return GameMode(self.game_mode_value)

    def is_song_custom(self) -> bool:
        return self.song_custom


@struct()
class GameObject(CCSpritePlus):
    ...


@struct()
class Player(GameObject):
    ...


@struct(virtual=True)
class TriggerEffectDelegate(Struct):
    pass


@struct(virtual=True)
class BaseGameLayer(TriggerEffectDelegate, CCLayer):
    oriented_bounding_box = Field(MutPointerData(Void()))  # OBB2D*

    effect_manager = Field(MutPointerData(Void()))  # EffectManager*

    object_layer = Field(MutPointerData(StructData(CCLayer)))

    batch_node_add_top_4 = Field(MutPointerData(Void()))
    effect_batch_node_add_top_4 = Field(MutPointerData(Void()))
    batch_node_top_3 = Field(MutPointerData(Void()))

    batch_node_add_top_3 = Field(MutPointerData(Void()))
    batch_node_add_glow_top_3 = Field(MutPointerData(Void()))

    batch_node_top_3_container = Field(MutPointerData(StructData(CCNodeContainer)))

    batch_node_text_top_3 = Field(MutPointerData(Void()))
    batch_node_add_text_top_3 = Field(MutPointerData(Void()))
    effect_batch_node_top_3 = Field(MutPointerData(Void()))
    effect_batch_node_add_top_3 = Field(MutPointerData(Void()))

    batch_node_top_2 = Field(MutPointerData(Void()))
    batch_node_add_top_2 = Field(MutPointerData(Void()))
    batch_node_add_glow_top_2 = Field(MutPointerData(Void()))

    batch_node_top_2_container = Field(MutPointerData(StructData(CCNodeContainer)))

    batch_node_text_top_2 = Field(MutPointerData(Void()))
    batch_node_add_text_top_2 = Field(MutPointerData(Void()))
    effect_batch_node_top_2 = Field(MutPointerData(Void()))
    effect_batch_node_add_top_2 = Field(MutPointerData(Void()))

    batch_node = Field(MutPointerData(Void()))
    batch_node_add = Field(MutPointerData(Void()))
    batch_node_add_glow = Field(MutPointerData(Void()))

    batch_node_top_1_container = Field(MutPointerData(StructData(CCNodeContainer)))

    batch_node_text_top_1 = Field(MutPointerData(Void()))
    batch_node_add_text_top_1 = Field(MutPointerData(Void()))
    effect_batch_node_top_1 = Field(MutPointerData(Void()))
    effect_batch_node_add_top_1 = Field(MutPointerData(Void()))

    batch_node_player = Field(MutPointerData(Void()))
    batch_node_add_player = Field(MutPointerData(Void()))
    batch_node_player_glow = Field(MutPointerData(Void()))

    batch_node_add_middle = Field(MutPointerData(Void()))

    batch_node_bottom = Field(MutPointerData(Void()))
    batch_node_add_bottom = Field(MutPointerData(Void()))
    batch_node_add_bottom_glow = Field(MutPointerData(Void()))

    batch_node_bottom_1_container = Field(MutPointerData(StructData(CCNodeContainer)))

    batch_node_text = Field(MutPointerData(Void()))
    batch_node_add_text = Field(MutPointerData(Void()))
    effect_batch_node = Field(MutPointerData(Void()))
    effect_batch_node_add = Field(MutPointerData(StructData(CCSpriteBatchNode)))

    batch_node_bottom_2 = Field(MutPointerData(StructData(CCSpriteBatchNode)))
    batch_node_add_bottom_2 = Field(MutPointerData(StructData(CCSpriteBatchNode)))
    batch_node_add_bottom_2_glow = Field(MutPointerData(StructData(CCSpriteBatchNode)))

    batch_node_bottom_2_container = Field(MutPointerData(StructData(CCNodeContainer)))

    batch_node_text_bottom_2 = Field(MutPointerData(StructData(CCSpriteBatchNode)))
    batch_node_add_text_bottom_2 = Field(MutPointerData(StructData(CCSpriteBatchNode)))
    effect_batch_node_bottom_2 = Field(MutPointerData(StructData(CCSpriteBatchNode)))
    effect_batch_node_add_bottom_2 = Field(MutPointerData(StructData(CCSpriteBatchNode)))

    batch_node_bottom_3 = Field(MutPointerData(StructData(CCSpriteBatchNode)))
    batch_node_add_bottom_3 = Field(MutPointerData(StructData(CCSpriteBatchNode)))
    batch_node_add_bottom_3_glow = Field(MutPointerData(StructData(CCSpriteBatchNode)))

    batch_node_bottom_3_container = Field(MutPointerData(StructData(CCNodeContainer)))

    batch_node_text_bottom_3 = Field(MutPointerData(StructData(CCSpriteBatchNode)))
    batch_node_add_text_bottom_3 = Field(MutPointerData(StructData(CCSpriteBatchNode)))
    effect_batch_node_bottom_3 = Field(MutPointerData(StructData(CCSpriteBatchNode)))
    effect_batch_node_add_bottom_3 = Field(MutPointerData(StructData(CCSpriteBatchNode)))

    batch_node_bottom_4 = Field(MutPointerData(StructData(CCSpriteBatchNode)))
    batch_node_add_bottom_4 = Field(MutPointerData(StructData(CCSpriteBatchNode)))
    batch_node_add_bottom_4_glow = Field(MutPointerData(Void()))

    batch_node_bottom_4_container = Field(MutPointerData(StructData(CCNodeContainer)))

    batch_node_text_bottom_4 = Field(MutPointerData(StructData(CCSpriteBatchNode)))
    batch_node_add_text_bottom_4 = Field(MutPointerData(StructData(CCSpriteBatchNode)))
    effect_batch_node_bottom_4 = Field(MutPointerData(StructData(CCSpriteBatchNode)))
    effect_batch_node_add_bottom_4 = Field(MutPointerData(StructData(CCSpriteBatchNode)))

    player_1 = Field(MutPointerData(StructData(Player)))
    player_2 = Field(MutPointerData(StructData(Player)))

    level_settings = Field(MutPointerData(StructData(LevelSettings)))

    # cocos2d::CCDictionary* m_pDisabledGroupsDictMaybe;
    # cocos2d::CCArray* m_pObjects;
    # cocos2d::CCArray* m_pSectionObjectsArray;
    # cocos2d::CCArray* m_pSections;
    # cocos2d::CCArray* m_pCollisionBlocksArray;
    # cocos2d::CCArray* m_pSpawnObjectsArray;
    # cocos2d::CCArray* m_pUnkArr4;
    # cocos2d::CCNode* m_pGroupNodes;
    # std::vector<GameObject*> m_pGameObjects;
    # std::vector<GameObject*> m_pDisabledObjects;
    # cocos2d::CCDictionary* m_pGroupDict;
    # cocos2d::CCDictionary* m_pStaticGroupDict;
    # cocos2d::CCDictionary* m_pOptimisedGroupDict;
    # std::vector<cocos2d::CCArray*> m_pGroups;
    # std::vector<cocos2d::CCArray*> m_pStaticGroups;
    # std::vector<cocos2d::CCArray*> m_pOptimisedGroups;
    # cocos2d::CCArray* m_pBatchNodeArray;
    # cocos2d::CCArray* m_pProcessedGroups;
    # cocos2d::CCDictionary* m_pCounterDict;
    # cocos2d::CCDictionary* m_pSpawnedGroups;
    # bool m_bUpdatedNormalCapacity;
    # bool m_bTwoPlayer;
    # int m_nUnk;
    # bool m_bActiveDualTouch;
    # int m_nPushedButtons;
    # int m_nCurrentSection;
    # int m_nOldSection;
    # bool m_bDisabledObjects;
    # bool m_bBlending;


@struct(virtual=True)
class PlayLayer(BaseGameLayer):
    ...


@struct(virtual=True)
class EditorLayer(BaseGameLayer):
    ...


@struct(virtual=True)
class BaseGameManager(CCNode):
    file_name = Field(StringData())

    setup = Field(Bool())
    saving = Field(Bool())


@struct(virtual=True)
class GameManager(BaseGameManager):
    switch_modes = Field(Bool())
    to_fullscreen = Field(Bool())
    reloading = Field(Bool())

    _unknown_bool_0 = Field(Bool())

    value_keeper = Field(MutPointerData(Void()))  # CCDictionary*
    unlock_value_keeper = Field(MutPointerData(Void()))  # CCDictionary*
    custom_objects = Field(MutPointerData(Void()))  # CCDictionary*

    _unknown_int_0 = Field(Int())

    ad_timer = Field(Double())
    ad_cache = Field(Double())

    _unknown_bool_1 = Field(Bool())

    _unknown_int_1 = Field(Int())

    _unknown_double_0 = Field(Double())

    _unknown_int_2 = Field(Int())
    _unknown_int_3 = Field(Int())

    first_load = Field(Bool())

    synced_platform_achievements = Field(Bool())

    _unknown_string_0 = Field(StringData())

    play_layer = Field(MutPointerData(StructData(PlayLayer)))
    editor_layer = Field(MutPointerData(StructData(EditorLayer)))

    _unknown_int_4 = Field(Int())

    menu_layer = Field(MutPointerData(Void()))  # MenuLayer*

    _unknown_bool_2 = Field(Bool())

    _unknown_int_5 = Field(Int())

    _unknown_bool_3 = Field(Bool())

    _unknown_bool_4 = Field(Bool())

    _unknown_bool_5 = Field(Bool())
    _unknown_bool_6 = Field(Bool())

    udid = Field(StringData())
    name = Field(StringData())

    comments_enabled = Field(Bool())

    user_id_random = Field(Int())
    user_id_seed = Field(Int())
    user_id = Field(Int())

    volume = Field(Float())
    sfx_volume = Field(Float())
    time_offset = Field(Float())

    rated = Field(Bool())

    facebook = Field(Bool())
    twitter = Field(Bool())
    youtube = Field(Bool())

    _unknown_int_6 = Field(Int())

    socials_duration = Field(Double())

    shown_ad = Field(Bool())

    _unknown_bool_7 = Field(Bool())

    editor = Field(Bool())

    scene_value = Field(Int())

    _unknown_int_7 = Field(Int())

    _unknown_bool_8 = Field(Bool())

    cube_id_random = Field(Int())
    cube_id_seed = Field(Int())
    cube_id = Field(Int())

    ship_id_random = Field(Int())
    ship_id_seed = Field(Int())
    ship_id = Field(Int())

    ball_id_random = Field(Int())
    ball_id_seed = Field(Int())
    ball_id = Field(Int())

    ufo_id_random = Field(Int())
    ufo_id_seed = Field(Int())
    ufo_id = Field(Int())

    wave_id_random = Field(Int())
    wave_id_seed = Field(Int())
    wave_id = Field(Int())

    robot_id_random = Field(Int())
    robot_id_seed = Field(Int())
    robot_id = Field(Int())

    spider_id_random = Field(Int())
    spider_id_seed = Field(Int())
    spider_id = Field(Int())

    color_1_id_random = Field(Int())
    color_1_id_seed = Field(Int())
    color_1_id = Field(Int())

    color_2_id_random = Field(Int())
    color_2_id_seed = Field(Int())
    color_2_id = Field(Int())

    streak_id_random = Field(Int())
    streak_id_seed = Field(Int())
    streak_id = Field(Int())

    explosion_id_random = Field(Int())
    explosion_id_seed = Field(Int())
    explosion_id = Field(Int())

    check_random = Field(Int())
    check_seed = Field(Int())

    codebreaker_random = Field(Int())
    codebreaker_seed = Field(Int())

    glow = Field(Bool())

    icon_type_value = Field(Int())

    everyplay_setup = Field(Bool())

    show_song_markers = Field(Bool())

    show_bpm_markers = Field(Bool())

    record_gameplay = Field(Bool())

    show_progress_bar = Field(Bool())

    performance_mode = Field(Bool())

    clicked_icons = Field(Bool())
    clicked_editor = Field(Bool())
    clicked_name = Field(Bool())
    clicked_practice = Field(Bool())

    shown_editor_guide = Field(Bool())
    shown_rate_difficulty_dialog = Field(Bool())
    shown_rate_star_dialog = Field(Bool())
    shown_low_detail_dialog = Field(Bool())

    game_rate_delegate = Field(MutPointerData(Void()))  # GameRateDelegate*
    unknown_delegate = Field(MutPointerData(Void()))

    _unknown_int_8 = Field(Int())

    _unknown_int_9 = Field(Int())

    _unknown_int_10 = Field(Int())

    group_id = Field(Int())
    background_id = Field(Int())
    ground_id = Field(Int())
    font_id = Field(Int())
    explosion_id_repeated = Field(Int())

    _unknown_attempts = Field(Int())
    _unknown_attempts_another = Field(Int())

    bootups = Field(Int())

    rated_repeated = Field(Bool())

    _unknown_bool_9 = Field(Bool())

    _unknown_bool_10 = Field(Bool())

    important = Field(Bool())

    _unknown_bool_11 = Field(Bool())

    smooth_fix = Field(Bool())

    rate_power_random = Field(Int())
    rate_power_seed = Field(Int())
    rate_power = Field(Int())

    can_get_level_data = Field(Bool())

    resolution = Field(Int())

    texture_quality = Field(Int())

    _unknown_bool_12 = Field(Bool())

    daily_level_page = Field(MutPointerData(Void()))  # DailyLevelPage*

    _unknown_bool_13 = Field(Bool())

    _unknown_int_11 = Field(Int())
    _unknown_int_12 = Field(Int())
    _unknown_int_13 = Field(Int())

    ad_reward = Field(Int())

    _unknown_int_14 = Field(Int())


@struct(virtual=True)
class AccountManager(CCNode):
    data = Field(MutPointerData(Void()))

    password = Field(StringData())
    name = Field(StringData())

    account_id = Field(Int())
    account_id_seed = Field(Int())
    account_id_random = Field(Int())

    register_delegate = Field(MutPointerData(Void()))  # AccountRegisterDelegate*
    login_delegate = Field(MutPointerData(Void()))  # AccountLoginDelegate*
    account_delegate = Field(MutPointerData(Void()))  # AccountDelegate*
    backup_delegate = Field(MutPointerData(Void()))  # AccountBackupDelegate*
    sync_delegate = Field(MutPointerData(Void()))  # AccountSyncDelegate*
    update_account_delegate = Field(MutPointerData(Void()))  # AccountSettingsDelegate*
