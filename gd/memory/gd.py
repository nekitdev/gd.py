from gd.enums import (
    VALUE_TO_DEMON_DIFFICULTY,
    DemonDifficulty,
    Difficulty,
    GameMode,
    LevelDifficulty,
    LevelLength,
    LevelType,
    Scene,
    Score,
    Speed,
)
from gd.memory.arrays import DynamicFill, MutArrayData
from gd.memory.base import Struct, StructData, struct
from gd.memory.cocos import (
    CCArray,
    CCLayer,
    CCNode,
    CCNodeContainer,
    CCPoint,
    CCRectangle,
    CCSize,
    CCSprite,
    CCSpriteBatchNode,
    CCSpritePlus,
)
from gd.memory.data import Bool, Double, Float, Int, Short, USize
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

    difficulty_value = Field(Int())
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

    best_clicks_random = Field(Int())
    best_clicks_seed = Field(Int())
    best_clicks = Field(Int())

    best_seconds_random = Field(Int())
    best_seconds_seed = Field(Int())
    best_seconds = Field(Int())

    seed = Field(Int())

    chk_valid = Field(Bool())
    anticheat = Field(Bool())

    normal_record = Field(Int())
    normal_record_seed = Field(Int())
    normal_record_random = Field(Int())

    orbs_random = Field(Int())
    orbs_seed = Field(Int())
    orbs = Field(Int())

    new_normal_record_random = Field(Int())
    new_normal_record_seed = Field(Int())
    new_normal_record = Field(Int())

    practice_record = Field(Int())

    likes = Field(Int())
    dislikes = Field(Int())

    length_value = Field(Int())

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

    demon_difficulty_value = Field(Int())

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

    type_value = Field(Int())

    some_id = Field(Int())  # ?

    temporary_name = Field(StringData())
    capacity_string = Field(StringData())

    high_detail = Field(Bool())

    progress_string = Field(StringData())

    @property
    def type(self) -> LevelType:
        return LevelType(self.type_value)

    @property
    def length(self) -> LevelLength:
        return LevelLength(self.length_value)

    @property
    def score_type(self) -> Score:
        return Score(self.score)

    def is_rated(self) -> bool:
        return self.stars > 0

    def is_unfeatured(self) -> bool:
        return self.score_type.is_unfeatured()

    def is_epic_only(self) -> bool:
        return self.score_type.is_epic_only()

    def is_featured(self) -> bool:
        return self.score_type.is_featured()

    def is_epic(self) -> bool:
        return self.epic

    def is_original(self) -> bool:
        return not self.original_id

    def is_two_player(self) -> bool:
        return self.two_player

    def is_demon(self) -> bool:
        return bool(self.demon)  # thanks rob

    def is_auto(self) -> bool:
        return self.auto

    def has_low_detail(self) -> bool:
        return self.low_detail

    def has_verified_coins(self) -> bool:
        return bool(self.verified_coins)  # thanks rob

    @property
    def demon_difficulty(self) -> DemonDifficulty:
        return VALUE_TO_DEMON_DIFFICULTY.get(
            self.demon_difficulty_value, DemonDifficulty.HARD_DEMON
        )

    @property
    def level_difficulty(self) -> LevelDifficulty:
        difficulty_numerator = self.difficulty_numerator
        difficulty_denominator = self.difficulty_denominator

        if difficulty_denominator:
            difficulty_value = difficulty_numerator // difficulty_denominator

            if difficulty_value:
                return LevelDifficulty(difficulty_value)

        return LevelDifficulty.DEFAULT

    @property
    def difficulty(self) -> Difficulty:
        if self.is_auto():
            return Difficulty.AUTO

        if self.is_demon():
            return self.demon_difficulty.into_difficulty()

        return self.level_difficulty.into_difficulty()


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
class ShortVector(Struct):  # monomorphization
    pointer = Field(MutPointerData(MutArrayData(Short())))
    length = Field(USize())
    capacity = Field(USize())


@struct()
class GameObject(CCSpritePlus):
    ...


@struct()
class Player(GameObject):
    ...


@struct(virtual=True)
class TriggerEffectDelegate(Struct):
    pass


@struct()
class GameObjectVector(Struct):  # monomorphization
    pointer = Field(MutPointerData(MutArrayData(MutPointerData(StructData(GameObject)))))
    length = Field(USize())
    capacity = Field(USize())


@struct()
class CCArrayVector(Struct):  # monomorphization
    pointer = Field(MutPointerData(MutArrayData(MutPointerData(StructData(CCArray)))))
    length = Field(USize())
    capacity = Field(USize())


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

    disabled_groups = Field(MutPointerData(Void()))  # CCDictionary*

    objects = Field(MutPointerData(StructData(CCArray)))
    section_objects = Field(MutPointerData(StructData(CCArray)))
    sections = Field(MutPointerData(StructData(CCArray)))
    collision_blocks = Field(MutPointerData(StructData(CCArray)))

    spawn_objects = Field(MutPointerData(StructData(CCArray)))

    _unknown_array_0 = Field(MutPointerData(StructData(CCArray)))

    group_nodes = Field(MutPointerData(StructData(CCNode)))

    game_objects = Field(StructData(GameObjectVector))
    disabled_objects = Field(StructData(GameObjectVector))

    group_dict = Field(MutPointerData(Void()))  # CCDictionary*
    static_group_dict = Field(MutPointerData(Void()))  # CCDictionary*
    optimized_group_dict = Field(MutPointerData(Void()))  # CCDictionary*

    groups = Field(StructData(CCArrayVector))
    static_groups = Field(StructData(CCArrayVector))
    optimized_groups = Field(StructData(CCArrayVector))

    batch_nodes = Field(MutPointerData(StructData(CCArray)))
    processed_groups = Field(MutPointerData(StructData(CCArray)))

    count_dict = Field(MutPointerData(Void()))  # CCDictionary*
    spawned_groups = Field(MutPointerData(Void()))  # CCDictionary*

    updated_normal_capacity = Field(Bool())
    two_player = Field(Bool())

    _unknown_int_0 = Field(Int())

    active_dual_touch = Field(Bool())

    attempt_click_count = Field(Int())

    current_section = Field(Int())

    old_section = Field(Int())

    objects_disabled = Field(Bool())

    blending = Field(Bool())

    _pad_0 = Field(DynamicFill(8, android_x32=0, android_x64=0))


@struct(virtual=True)
class PlayLayer(BaseGameLayer):
    _unknown_float_0 = Field(Float())

    _unknown_bool_0 = Field(Bool())

    cheated = Field(Bool())

    do_not_save_random = Field(Int())
    do_not_save_seed = Field(Int())

    _unknown_int_1 = Field(Int())

    debug_pause_off = Field(Bool())
    smooth_camera = Field(Bool())

    _unknown_float_1 = Field(Float())

    _pad_1 = Field(DynamicFill(4))

    _unknown_draw_node = Field(MutPointerData(Void()))  # CCDrawNode*

    to_camera_y = Field(Float())

    _unknown_int_2 = Field(Int())

    _unknown_float_3 = Field(Float())

    ground_restriction = Field(Float())

    ceiling_restriction = Field(Float())

    full_level_reset = Field(Bool())

    _unknown_bool_1 = Field(Bool())

    _unknown_float_4 = Field(Float())
    _unknown_float_5 = Field(Float())
    _unknown_float_6 = Field(Float())
    _unknown_float_7 = Field(Float())
    _unknown_float_8 = Field(Float())

    _pad_2 = Field(DynamicFill(4))

    start_position = Field(MutPointerData(Void()))  # StartPositionObject*
    start_position_checkpoint = Field(MutPointerData(Void()))  # CheckpointObject*

    end_portal = Field(MutPointerData(Void()))  # EndPortalObject*

    checkpoints = Field(MutPointerData(StructData(CCArray)))
    speed_objects = Field(MutPointerData(StructData(CCArray)))
    speed_portals = Field(MutPointerData(StructData(CCArray)))
    _unknown_array_1 = Field(MutPointerData(StructData(CCArray)))

    background = Field(MutPointerData(StructData(CCSprite)))
    background_rectangle = Field(StructData(CCRectangle))

    _unknown_array_2 = Field(MutPointerData(StructData(CCArray)))

    active_objects = Field(MutPointerData(StructData(CCArray)))

    _unknown_array_3 = Field(MutPointerData(StructData(CCArray)))

    move_actions = Field(MutPointerData(StructData(CCArray)))

    music_disabled = Field(Bool())

    _pad_3 = Field(DynamicFill(7))

    state_objects = Field(MutPointerData(StructData(CCArray)))

    glitter_effects = Field(MutPointerData(Void()))  # CCParticleSystemQuad*

    picked_up_items = Field(MutPointerData(Void()))  # CCDictionary*

    circle_waves = Field(MutPointerData(StructData(CCArray)))
    triggered_objects = Field(MutPointerData(StructData(CCArray)))

    audio_effects_layer = Field(MutPointerData(Void()))  # AudioEffectsLayer*

    ground_bottom_y_position = Field(Float())
    ground_top_y_position = Field(Float())

    bottom_ground = Field(MutPointerData(Void()))  # GroundLayer*
    top_ground = Field(MutPointerData(Void()))  # GroundLayer*

    _pad_4 = Field(DynamicFill(8))

    dead = Field(Bool())

    start_camera_at_corner = Field(Bool())

    camera_x_locked = Field(Bool())
    camera_y_locked = Field(Bool())

    _pad_5 = Field(DynamicFill(4))

    random = Field(Int())

    _unknown_float_9 = Field(Float())

    grounds_not_equal = Field(Bool())

    time_mod = Field(Float())

    level_size = Field(StructData(CCSize))

    attempt_label = Field(MutPointerData(Void()))  # CCLabelBMFont*
    percent_label = Field(MutPointerData(Void()))  # CCLabelBMFont*

    shaking = Field(Bool())

    strength = Field(Float())
    interval = Field(Float())

    last_shake_time = Field(Double())

    shake = Field(StructData(CCPoint))

    showed_hint = Field(Bool())

    _unknown_float_10 = Field(Float())

    mirror_transition = Field(Float())

    flipping = Field(Bool())

    _unknown_int_3 = Field(Int())

    claimed_particles_dict = Field(MutPointerData(Void()))  # CCDictionary*
    particle_dict = Field(MutPointerData(Void()))  # CCDictionary*

    claimed_particles = Field(MutPointerData(StructData(CCArray)))

    lighting_mode = Field(MutPointerData(StructData(CCNode)))

    progress_bar_groove = Field(MutPointerData(StructData(CCSprite)))
    progress_bar = Field(MutPointerData(StructData(CCSprite)))

    slider = Field(StructData(CCSize))

    _unknown_float_11 = Field(Float())

    total_gravity_effect_sprites = Field(Int())

    gravity_effect = Field(Int())

    gravity_sprite_index = Field(Int())

    gravity_sprites = Field(MutPointerData(StructData(CCArray)))

    just_do_not = Field(Bool())

    local_level = Field(Bool())

    player_1_pushed_button = Field(Bool())
    player_1_frozen = Field(Bool())
    player_2_pushed_button = Field(Bool())
    player_2_frozen = Field(Bool())

    recording_string = Field(StringData())
    recording = Field(MutPointerData(StructData(CCArray)))

    time = Field(Double())

    ground_bottom_y_position_other = Field(Float())

    _pad_6 = Field(DynamicFill(5))

    _unknown_bool_2 = Field(Bool())

    use_sound_manager = Field(Bool())

    color_dict = Field(MutPointerData(Void()))  # CCDictionary*

    _pad_7 = Field(DynamicFill(windows_x32=8, windows_x64=16))

    _unknown_int_4 = Field(Int())

    _unknown_int_5 = Field(Int())

    _unknown_bool_3 = Field(Bool())

    force_recording_control = Field(Bool())

    last_activated_portal = Field(MutPointerData(StructData(GameObject)))
    portal = Field(MutPointerData(StructData(GameObject)))

    flipped = Field(Bool())

    flip_value = Field(Float())

    ui_layer = Field(MutPointerData(Void()))  # UILayer*

    level = Field(MutPointerData(StructData(GameLevel)))

    camera_position = Field(StructData(CCPoint))

    test = Field(Bool())
    practice = Field(Bool())
    resetting = Field(Bool())

    _unknown_bool_4 = Field(Bool())

    big_action_container = Field(MutPointerData(StructData(CCArray)))

    full_level_reset_other = Field(Bool())

    player_position = Field(StructData(CCPoint))

    attempt = Field(Int())
    jumps = Field(Int())
    clicked = Field(Bool())

    time_other = Field(Float())

    attempt_jumps = Field(Int())

    leaderboard_record = Field(Bool())

    show_ui = Field(Bool())

    triggered_event = Field(Bool())

    reset_queued = Field(Bool())

    record = Field(Int())

    awarded = Field(Bool())

    awarded_orbs = Field(Int())
    awarded_diamonds = Field(Int())

    awarded_secret_key = Field(Bool())

    restart_after_stopped = Field(Bool())

    object_states = Field(MutPointerData(StructData(CCArray)))

    save_required_groups = Field(MutPointerData(Void()))  # CCDictionary*

    _pad_8 = Field(DynamicFill(4))

    _unknown_double_1 = Field(Double())
    _unknown_double_2 = Field(Double())
    _unknown_double_3 = Field(Double())

    _unknown_bool_5 = Field(Bool())

    _unknown_float_12 = Field(Float())

    _unknown_int_6 = Field(Int())

    attempt_time = Field(Double())

    temporary_milliseconds = Field(Double())

    attempt_time_random = Field(Double())
    attempt_time_seed = Field(Double())

    _unknown_int_7 = Field(Int())

    glitter = Field(Bool())

    background_effect = Field(Bool())

    _unknown_bool_6 = Field(Bool())

    paused = Field(Bool())

    collided_object = Field(MutPointerData(StructData(GameObject)))

    check = Field(Bool())

    disable_gravity_effect = Field(Bool())

    @property
    def level_length(self) -> float:
        return self.level_size.width

    def is_practice(self) -> bool:
        return self.practice

    def is_test(self) -> bool:
        return self.test


@struct(virtual=True)
class EditorLayer(BaseGameLayer):
    ...
    # bool m_bIgnoreDamage;
    # bool m_bFollowPlayer;
    # bool m_bDrawTriggerBoxes;
    # bool m_bDebugDraw;
    # bool m_bShowGrid;
    # bool m_bHideGridOnPlay;
    # bool m_bEffectLines;
    # bool m_bShowGround;
    # bool m_bDurationLines;
    # bool m_bIncreaseMaxUndos;
    # bool m_bHideBackground;
    # bool m_bEditorSmoothFix;
    # bool m_bHighDetail;
    # cocos2d::CCArray* m_pTouchTriggeredGroups;
    # cocos2d::CCArray* m_pTriggeredGroups;
    # cocos2d::CCDictionary* m_pStickyGroups;
    # int m_nStickyGroupID;
    # cocos2d::CCArray* m_pUnkObjectArr;
    # cocos2d::CCArray* m_pPulseTriggers;
    # cocos2d::CCArray* m_pColourObjects;
    # cocos2d::CCArray* m_pAlphaTriggers;
    # cocos2d::CCArray* m_pSpawnTriggers;
    # cocos2d::CCArray* m_pMoveTriggers;
    # cocos2d::CCDictionary* m_pUnkDict5;
    # cocos2d::CCArray* m_pEnabledGroups;
    # GameObject* m_pCopiedObject;
    # cocos2d::CCDictionary* m_pUnkDict6;
    # cocos2d::CCArray* m_pUnkArray12;
    # bool field_14;
    # bool field_31D;
    # int m_nCoinsSeed;
    # int m_nCoinsRand;
    # int m_nCoins;
    # bool m_bMoveTrigger;
    # bool m_bColourTrigger;
    # bool m_bPulseTrigger;
    # bool m_bAlphaTrigger;
    # bool m_bSpawnTrigger;
    # cocos2d::CCArray* m_pToggleTriggersMaybe;
    # bool m_bUnkArr2Obj;
    # cocos2d::CCArray* m_pDelayedSpawnArray2;
    # bool m_bDelaySpawnNode;
    # cocos2d::CCDictionary* m_pUnkDict3;
    # cocos2d::CCDictionary* m_pUnkDict4;
    # bool m_bEditorInitialising;
    # bool field_34D;
    # float m_fTimeMod;
    # int m_nEditorLayer1;
    # StartPosObject* m_pStartPos;
    # float m_fObjectLayerScale;
    # OBB2D* m_pOBB2D;
    # cocos2d::CCSprite* m_pCrossSprite;
    # cocos2d::CCPoint m_obUnkPoint2;
    # float m_fUnkFloat1;
    # bool m_bTwoPlayer;
    # bool m_bUnkRectBool;
    # GameObject* m_pCurrentPortal;
    # GameObject* m_pPortal;
    # EditorUI* m_pEditorUI;
    # cocos2d::CCSprite* m_pBackgroundSprite;
    # cocos2d::CCArray* m_pUndoArray;
    # cocos2d::CCArray* m_pRedoArray;
    # cocos2d::CCPoint m_obUnkPoint1;
    # int m_nObjectCountSeed;
    # int m_nObjectCountRand;
    # int m_nObjectCount;
    # DrawGridLayer* m_pDrawGridLayer;
    # GJGameLevel* m_pLevel;
    # int m_ePlaybackMode;
    # cocos2d::CCPoint m_obGroundTopMaybe;
    # float m_fTime;
    # cocos2d::CCDictionary* m_pEnabledGroupsDict;
    # bool field_3D;
    # bool m_bPreviewMode;
    # GJGroundLayer* m_pGround;
    # std::string m_sRawLevelString;
    # void* m_pTriggerHitbox;
    # std::vector<GameObject*> m_pObjectVector;
    # std::vector<GameObject*> m_pGroupVector;
    # std::vector<cocos2d::CCArray*> m_pNestedObjects;
    # cocos2d::CCDictionary* m_pTriggerGroupsDict;
    # std::vector<cocos2d::CCArray*> m_pTriggerGroupsVector;
    # bool m_bToggleGroupsMaybe;
    # std::vector<bool> m_bUnkVector3; // everything set to false if in playbackmode
    # std::vector<bool> m_bDisabledGroupVector;
    # std::vector<bool> m_bBlendObjectsVector;
    # std::vector<bool> m_bBlendColourVector;
    # std::vector<uint8_t> m_uToggledGroupsVector;
    # std::vector<float> m_fPreviewGroupsVector;
    # double m_dUnkDouble1;
    # cocos2d::CCArray* m_pDelayedSpawnArray1;
    # bool m_bRemovingObjects;


@struct(virtual=True)
class BaseGameManager(CCNode):
    file_name = Field(StringData())

    setup = Field(Bool())
    saved = Field(Bool())

    quick_save = Field(Bool())


@struct(virtual=True)
class GameManager(BaseGameManager):
    switch_modes = Field(Bool())
    to_fullscreen = Field(Bool())
    reloading = Field(Bool())

    _unknown_bool_0 = Field(Bool())

    _unknown_int_0 = Field(Int())

    value_keeper = Field(MutPointerData(Void()))  # CCDictionary*
    unlock_value_keeper = Field(MutPointerData(Void()))  # CCDictionary*
    custom_objects = Field(MutPointerData(Void()))  # CCDictionary*

    ad_timer = Field(Double())
    ad_cache = Field(Double())

    _pad_0 = Field(DynamicFill(8))

    _unknown_double_0 = Field(Double())

    _pad_1 = Field(DynamicFill(8))

    loaded = Field(Bool())

    _unknown_string_0 = Field(StringData())

    play_layer = Field(MutPointerData(StructData(PlayLayer)))
    editor_layer = Field(MutPointerData(StructData(EditorLayer)))

    _unknown_int_1 = Field(Int())

    menu_layer = Field(MutPointerData(Void()))  # MenuLayer*

    _unknown_bool_2 = Field(Bool())

    _unknown_int_2 = Field(Int())

    _unknown_bool_3 = Field(Bool())

    _unknown_bool_4 = Field(Bool())

    _unknown_bool_5 = Field(Bool())
    _unknown_bool_6 = Field(Bool())

    uuid = Field(StringData())
    name = Field(StringData())

    comments_enabled = Field(Bool())

    user_id_random = Field(Int())
    user_id_seed = Field(Int())
    user_id = Field(Int())

    volume = Field(Float())
    sfx_volume = Field(Float())
    # time_offset = Field(Float())  # idk why but removing this works

    rated = Field(Bool())

    facebook = Field(Bool())
    twitter = Field(Bool())
    youtube = Field(Bool())

    _unknown_int_3 = Field(Int())

    socials_duration = Field(Double())

    shown_ad = Field(Bool())

    _unknown_bool_7 = Field(Bool())

    editor_enabled = Field(Bool())

    scene_value = Field(Int())

    _unknown_int_4 = Field(Int())

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

    _unknown_int_5 = Field(Int())

    _unknown_int_6 = Field(Int())

    _unknown_int_7 = Field(Int())

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

    _unknown_int_8 = Field(Int())
    _unknown_int_9 = Field(Int())
    _unknown_int_10 = Field(Int())

    ad_reward = Field(Int())

    _unknown_int_11 = Field(Int())

    @property
    def scene(self) -> Scene:
        return Scene(self.scene_value)


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
