from gd.enums import GameMode, Speed
from gd.memory.arrays import ArrayData
from gd.memory.base import Struct, StructData, struct
from gd.memory.cocos import CCLayer, CCNode, CCNodeContainer, CCPoint, CCRectangle, CCSize, CCSprite, CCSpriteBatchNode, CCSpritePlus
from gd.memory.data import Bool, Double, Float, Int, UByte
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
    _unknown_bool_0 = Field(Bool())
    _unknown_bool_1 = Field(Bool())

    _unknown_float_0 = Field(Float())
    _unknown_float_1 = Field(Float())
    _unknown_float_2 = Field(Float())
    _unknown_float_3 = Field(Float())

    _unknown_bool_2 = Field(Bool())

    animation_speed = Field(Float())
    effect_object = Field(Bool())

    randomize_start = Field(Bool())

    animation_speed_repeated = Field(Float())

    black_child = Field(Bool())

    _unknown_bool_3 = Field(Bool())

    black_child_opacity = Field(Float())

    _unknown_bool_4 = Field(Bool())

    editor = Field(Bool())

    group_disabled = Field(Bool())

    color_on_top = Field(Bool())

    base_color = Field(MutPointerData(Void()))  # SpriteColor*
    detail_color = Field(MutPointerData(Void()))  # SpriteColor*

    color_1 = Field(Bool())
    color_2 = Field(Bool())

    object_position = Field(StructData(CCPoint))

    _unknown_float_4 = Field(Float())

    tint_trigger = Field(Bool())

    object_flip_x = Field(Bool())
    object_flip_y = Field(Bool())

    box_offset = Field(StructData(CCPoint))

    oriented = Field(Bool())

    box_offset_additional = Field(StructData(CCPoint))

    oriented_bounding_box = Field(MutPointerData(Void()))  # OBB2D*

    glow_sprite = Field(MutPointerData(StructData(CCSprite)))

    not_editor = Field(Bool())

    action = Field(MutPointerData(Void()))  # CCAction*

    _unknown_bool_5 = Field(Bool())

    run_action_with_tag = Field(Bool())

    object_powered_on = Field(Bool())

    object_size = Field(StructData(CCSize))

    trigger = Field(Bool())
    active = Field(Bool())

    animation_finished = Field(Bool())

    particle_system = Field(MutPointerData(Void()))  # CCParticleSystemQuad*

    effect_plist_name = Field(StringData())

    added_particle = Field(Bool())
    has_particles = Field(Bool())

    _unknown_bool_6 = Field(Bool())

    portal_position = Field(StructData(CCPoint))

    _unknown_bool_7 = Field(Bool())

    object_texture_rectangle = Field(StructData(CCRectangle))

    texture_rectangle_dirty = Field(Bool())

    _unknown_float_5 = Field(Float())

    object_rectangle = Field(StructData(CCRectangle))

    object_rectangle_dirty = Field(Bool())
    oriented_rectangle_dirty = Field(Bool())

    activated_1 = Field(Bool())
    activated_2 = Field(Bool())

    pad = Field(ArrayData(UByte(), 8))  # XXX: fix this asap >:(

    object_rectangle_dirty_repeated = Field(Bool())
    oriented_rectangle_dirty_repeated = Field(Bool())

    unique_activated = Field(Bool())
    activated = Field(Bool())

    collectable = Field(Bool())

    pulse = Field(Bool())

    can_rotate_freely = Field(Bool())

    linked_group_id = Field(Int())

    rotation_trigger = Field(Bool())

    custom_rotation_speed = Field(Int())  # ?

    disable_rotation = Field(Bool())

    main_color_black = Field(Bool())

    _unknown_bool_8 = Field(Bool())

    blending_1 = Field(Bool())
    blending_2 = Field(Bool())

    _unknown_bool_9 = Field(Bool())

    _unknown_bool_10 = Field(Bool())

    color_sprite = Field(MutPointerData(StructData(CCSprite)))

    ignore_screen_check = Field(Bool())

    radius = Field(Float())

    snapped_rotation = Field(Bool())

    scale_mod = Field(StructData(CCSize))

    unique_id = Field(Int())

    game_object_type_value = Field(Int())

    section_index = Field(Int())

    touch_triggered = Field(Bool())
    spawn_triggered = Field(Bool())

    start_position = Field(StructData(CCPoint))

    texture_frame_name = Field(StringData())

    use_audio_scale = Field(Bool())

    sleeping = Field(Bool())

    rotation = Field(Float())

    start_scale = Field(StructData(CCSize))

    start_flip_x = Field(Bool())
    start_flip_y = Field(Bool())

    should_hide = Field(Bool())

    spawn_x_position = Field(Float())

    invisible = Field(Bool())

    enter_angle = Field(Float())

    active_enter_effect = Field(Int())

    parent_node = Field(Int())

    disable_glow = Field(Bool())

    color_index = Field(Int())

    scale = Field(Float())

    object_id = Field(Int())

    do_not_transform = Field(Bool())

    # bool m_bDontTransform;
    # bool m_bDefaultDontFade;
    # bool m_bIgnoreEnter;
    # bool m_bIgnoreFade;
    # bool m_bDontFadeTinted;
    # bool m_bTintObject;
    # bool m_bDetailColourObject;
    # bool m_bDontEnter;
    # bool m_bDontFade;
    # bool m_bStateVar;
    # int m_nDefaultZOrder;
    # bool m_bPortal;
    # bool m_bLockColourAsChild;
    # bool m_bCustomAudioScale;
    # int m_fMinAudioScale;
    # int m_fMaxAudioScale;
    # bool m_bUnkParticleSystem2;
    # int m_nSecretCoinID;
    # int m_unkUnusedSaveStringKey53;
    # bool m_bInvisibleMode;
    # bool m_bGlowUserBackgroundColour;
    # bool m_bUseSpecialLight;
    # bool m_bOrbOrPad;
    # float m_fGlowOpacityMod;
    # bool m_bUpSlope;
    # int m_eSlopeType;
    # float m_fSlopeAngle;
    # bool m_bHazardousSlope;
    # float dword18C;
    # GJSpriteColor* m_pColour1;
    # GJSpriteColor* m_pColour2;
    # bool m_bBlendingBatchNode;
    # int m_nDefaultZLayer;
    # int m_nZLayer;
    # int m_nZOrder;
    # std::string m_sText;
    # bool m_bSpecialObject;
    # bool m_bObjectSelected2;
    # bool m_bObjectSelected;
    # int m_nGlobalClickCounter;
    # cocos2d::CCPoint m_obUnk2;
    # bool dword1BC;
    # bool field_3AD;
    # float m_fMultiScaleMultiplier;
    # std::vector<short> m_nGroupContainer;
    # int m_nGroupCount;
    # std::vector<short> m_nColourGroupContainer;
    # int m_nColourGroupCount;
    # std::vector<short> m_nOpacityGroupContainer;
    # int m_nOpacityGroupCount;
    # int m_nEditorLayer1;
    # int m_nEditorLayer2;
    # int m_nGroupDisabled;
    # bool dword1EC;
    # bool m_bUseCustomContentSize;
    # bool field_3DE;
    # cocos2d::CCSize m_obUnkSize;
    # cocos2d::CCPoint m_obLastPosition;
    # bool m_bDidUpdateLastPosition;
    # bool m_bUpdateLastPos;
    # BYTE PAD3[4]
    # bool m_bSyncedAnimation;
    # int m_eLavaBubbleColourID;
    # bool dword210;
    # bool field_401;
    # bool field_402;
    # bool field_403;
    # bool dword214;
    # bool m_bSpawnObject;
    # bool m_bHasObjectCount;
    # int m_nAnimFrame;
    # bool m_bHighDetail;
    # void* m_pMainColourSprite;
    # void* m_pSecondaryColourSprite;
    # GJEffectManager* m_pEffectManager;
    # bool dword22C;
    # bool m_bIsDecoration;
    # bool m_bOptimisedGroup;
    # bool field_41F;
    # bool dword230;
    # int m_eZagColour;
    # bool m_bMultiActivate;
    # cocos2d::_ccColor3B m_Colour;


@struct()
class Player(GameObject):
    ...
    # float m_fUnkDash;
    # float m_fRotationButBackwards;
    # double m_fUnkSlopeVel;
    # bool m_bPlacedStreakPoint;
    # cocos2d::CCNode* m_pCollisionNode;
    # cocos2d::CCDictionary* m_pCollisionDict2;
    # cocos2d::CCDictionary* m_pCollisionDict1;
    # float m_fAutoCheckPointInterval;
    # float m_fUnkCheckpoint;
    # bool m_bAutoCheckpointEnabled;
    # GameObject* m_pObject;
    # GameObject* m_pCollidedObject;
    # int m_nCurrentIcon;
    # float m_fUnkCollisionFloat;
    # bool m_bHasCollided;
    # float m_fUnkCollisionFloat2;
    # int m_nCollisionObjUID;
    # cocos2d::CCSprite* m_pDashSprite;
    # bool m_bRollModeRolling;
    # int m_nCollisionObjUID2;
    # GameObject* m_pCollidedSlope;
    # bool m_bNotOnSlope;
    # float m_fUnkSlopeColisionSlope;
    # GameObject* m_pSlope;
    # bool m_bGoingDown;
    # int m_nSlopeUniqueID;
    # bool m_bGlow;
    # cocos2d::CCArray* m_pParticleArray;
    # bool m_bIsHidden;
    # bool m_bVisibility;
    # GhostTrailEffect* m_pGhostTrail;
    # int m_eGhostTrailType;
    # cocos2d::CCSprite* m_pIconSecondary;
    # cocos2d::CCSprite* m_pIcon;
    # cocos2d::CCSprite* m_pIconExtra;
    # cocos2d::CCSprite* m_pIconWhitener;
    # cocos2d::CCSprite* m_pVehicleSecondary;
    # cocos2d::CCSprite* m_pVehicle;
    # cocos2d::CCSprite* m_pVehicleWhitener;
    # cocos2d::CCSprite* m_pVehicleExtras;
    # cocos2d::CCMotionStreak* m_pTrail;
    # cocos2d::CCSprite* m_pShipGlow;
    # HardStreak* m_pHardStreak;
    # HardStreak* m_pWaveTrail;
    # double m_dJumpAcceleration;
    # double m_dXAcceleration;
    # float m_fParticleLife;
    # double m_dGravity;
    # bool m_bUnk;
    # float m_fSafeModeTime;
    # bool m_bUnk3;
    # bool m_bUnk2;
    # bool m_bJumped;
    # bool m_bUnk4;
    # bool m_bUnk5;
    # bool m_bParticleActive;
    # bool m_bUnk7;
    # bool m_bUnk6;
    # double m_dUnk2;
    # double m_dUnk;
    # double m_dTimeCopy2;
    # double m_dTimeCopy;
    # float m_fUnkFlash2;
    # float m_fUnkFlash;
    # cocos2d::ccColor3B m_cSecondColour;
    # cocos2d::ccColor3B m_cFirstColour;
    # bool m_bUnk8;
    # double m_dSafeSpiderTime;
    # bool m_bSwitchWaveTrailCol;
    # bool m_bUnk9;
    # float m_fUnk;
    # bool m_bPracticeDeathEffect;
    # double m_dUnk4;
    # double m_dUnk3;
    # GameObject* m_pObject1;
    # bool m_bUnk10;
    # int m_nCheckpointTotal;
    # CheckpointObject* m_pPendingCheckpoint;
    # GJRobotSprite* m_pSpiderSprite;
    # GJRobotSprite* m_pRobotSprite;
    # cocos2d::CCParticleSystem* m_pParticles;
    # bool m_bSpecialGroundHit;
    # cocos2d::CCParticleSystem* m_pDragEffect;
    # cocos2d::CCParticleSystem* m_pFlipParticles;
    # cocos2d::CCParticleSystem* m_pBurstEffect;
    # cocos2d::CCParticleSystem* m_pShipDragParticles;
    # cocos2d::CCParticleSystem* m_pDashParticles;
    # cocos2d::CCParticleSystem* m_pBurstEffect2;
    # cocos2d::CCParticleSystem* m_pLandEffectParticle;
    # bool m_bHitGroundBool;
    # float m_pParticleAngle;
    # cocos2d::CCParticleSystem* m_pLandEffectParticle2;
    # int m_nStreakID;
    # float m_fParticleGravity;
    # bool dword180;
    # float m_fStreakStroke;
    # float dword184;
    # bool field_5AD;
    # float dword18C;
    # float dword188;
    # bool field_5BD;
    # bool dword190;
    # bool m_bSlopeFlippedX;
    # bool m_bBumpPlayer;
    # float m_fCollisionBottom;
    # float m_fCollisionTop;
    # bool field_5C9;
    # bool dword19C;
    # cocos2d::ccColor3B m_cSecondColourCopy;
    # cocos2d::ccColor3B m_cFirstColourCopy;
    # bool m_bUpKeyDown;
    # bool m_bTookDamage;
    # bool field_5D3;
    # bool m_bUpKeyPressed;
    # bool field_5D5;
    # bool dword1A8;
    # int m_nJumpHeightSeed;
    # bool field_5D6;
    # int m_nJumpHeight;
    # int m_nJumpHeightRand;
    # double m_dYAccel;
    # DWORD dword1B8;
    # bool m_bWasOnSlope;
    # bool m_bOnSlope;
    # bool m_bFlyMode;
    # float m_fSlopeYVelocity;
    # bool m_bRollMode;
    # bool m_bBirdMode;
    # bool m_bRobotMode;
    # bool m_bDartMode;
    # bool m_bGravity;
    # bool m_bSpiderMode;
    # bool m_bCanJump;
    # bool m_bTouchedRing;
    # float m_fPlayerScale;
    # bool m_bDashing;
    # cocos2d::CCPoint m_obLastPos;
    # float m_fTimeMod;
    # cocos2d::CCLayer* m_pGameLayer;
    # cocos2d::CCPoint m_onPortalPos;
    # bool m_bJumping;
    # bool m_bOnGround;
    # cocos2d::CCPoint m_obLastGroundPos;
    # bool m_bLocked;
    # GameObject* m_pLastActivatedPortal;
    # cocos2d::CCArray* m_pTouchedRings;
    # bool m_bHasRingJumped;
    # bool m_bHasJumped;
    # cocos2d::ccColor3B m_cColour2;
    # cocos2d::ccColor3B m_cColour;
    # bool m_bIsSecondPlayer;
    # cocos2d::CCPoint m_obRealPlayerPos;
    # double m_dTime;
    # bool m_bTwoPlayer;
    # float m_fMeteringValue;
    # bool m_bDisableEffects;
    # float m_fLastYVelocity;
    # float m_fGroundHeight;
    # bool m_bSwitchSpiderTeleportCol;
    # bool m_bDefaultMiniIcon;
    # float m_fOldYPositions[200];
    # bool m_bSwitchFireDashCol;
    # int m_nStateBlockDash;
    # float m_fSpecialTime;
    # int m_nStateBlockJump;
    # DWORD dword560;
    # int m_nStateBlockHead;
    # int m_nStateBlockWave;


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
    # DWORD dwordC;
    # bool gap2DC;
    # bool m_bCheated;
    # bool m_bStartGame;
    # bool field_2DF;
    # float dword14;
    # bool dword18;
    # cocos2d::CCDrawNode* m_pUnkDrawNode;
    # float m_fToCameraY;
    # float m_fVisibleHeightMaybe;
    # float m_fDoubleGroundFixedYPos;
    # float m_fPlayerToTopStartYDifference;
    # float m_fDeathHeightMaybe;
    # bool m_bDeactivateSectionObjects;
    # bool m_bDisableShake2;
    # bool m_bDisableShake;
    # BYTE PAD1[25];
    # StartPosObject* m_pStartPos;
    # CheckpointObject* m_pStartPosCheckpoint;
    # EndPortalObject* m_pEndPortal;
    # cocos2d::CCArray* m_pCheckpointArray;
    # cocos2d::CCArray* m_pSpeedObjects;
    # cocos2d::CCArray* m_pSpeedPortalArray;
    # cocos2d::CCArray* m_pSomeCollisionsArray;
    # cocos2d::CCSprite* m_pBackground;
    # cocos2d::CCRect m_obBackgroundRect;
    # cocos2d::CCArray* m_pSomeGroupArray;
    # cocos2d::CCArray* m_pActiveObjects;
    # cocos2d::CCArray* m_pUnkVisibleObjArr;
    # cocos2d::CCArray* m_pMoveActionsArr;
    # bool m_bMusicDisabled;
    # BYTE PAD2[7];
    # cocos2d::CCArray* m_pStateObjects;
    # cocos2d::CCParticleSystemQuad* m_pGlitterEffects;
    # cocos2d::CCDictionary* m_pItemDict;
    # cocos2d::CCArray* m_pCircleWaves;
    # cocos2d::CCArray* m_pTriggeredObjects;
    # AudioEffectsLayer* m_pAudioEffectsLayer;
    # float m_fGroundBottomYPos;
    # float m_fGroundTopYPos;
    # GJGroundLayer* m_pBottomGround;
    # GJGroundLayer* m_pTopGround;
    # BYTE PAD3[8];
    # bool m_bDead;
    # bool m_bFullLevelReset2;
    # bool m_bUnkCameraX;
    # bool m_bUnkCameraY;
    # BYTE PAD4[4];
    # int m_nRand;
    # float dwordCC;
    # bool m_bGroundsNotEqual;
    # float m_fTimeMod;
    # cocos2d::CCSize m_obLevelSize;
    # cocos2d::CCLabelBMFont* m_pAttemptLabel;
    # cocos2d::CCLabelBMFont* m_pPercentLabel;
    # bool m_bCameraShaking;
    # float m_fStrength;
    # float m_fInterval;
    # double m_dLastShakeTime;
    # cocos2d::CCPoint m_obCameraShake;
    # bool m_bShowedHint;
    # float m_fCameraXMaybe;
    # float m_fMirrorTransition2;
    # bool m_bFlipping;
    # int m_nTotalUnkSprites;
    # cocos2d::CCDictionary* m_pClaimedParticles;
    # cocos2d::CCDictionary* m_pParticleDict;
    # cocos2d::CCArray* m_pClaimedParticlesArray;
    # cocos2d::CCNode* m_pLightningNode;
    # cocos2d::CCSprite* m_pProgressBarGroove;
    # cocos2d::CCSprite* ProgressBar;
    # cocos2d::CCSize m_obSlider;
    # float m_fUnkFlashEffect;
    # int m_nTotalGravityEffectSprites;
    # int m_nGravityEffect;
    # int m_nGravitySpriteIdx;
    # cocos2d::CCArray* m_pGravitySprites;
    # bool m_bJustDont;
    # bool m_bIsLocalLevel;
    # bool m_bPlayer1PushedButtonMaybe;
    # bool m_bPlayerFrozen;
    # bool m_bPlayer2PushedButtonMaybe;
    # bool m_bPlayer2Frozen;
    # std::string m_sReplayData;
    # cocos2d::CCArray* m_pReplayArray;
    # double m_dTime;
    # float m_fGroundBottomYPos2;
    # BYTE PAD5[4];
    # bool m_bUnkMirrorFloatStepping;
    # bool m_bUseSoundManager;
    # cocos2d::CCDictionary* m_pColourDict;
    # std::map<short, bool> m_sBlending;
    # DWORD dword184;
    # DWORD dword188;
    # bool dword18C;
    # bool m_bForcePlaybackControl;
    # GameObject* m_pLastActivatedPortal;
    # GameObject* m_pPortal;
    # bool m_bFlipped;
    # float m_fFlipValue;
    # UILayer* m_pUILayer;
    # GJGameLevel* m_pLevel;
    # cocos2d::CCPoint m_obCameraPos;
    # bool m_bTestMode;
    # bool m_bPracticeMode;
    # bool m_bIsResetting;
    # bool field_47F;
    # cocos2d::CCArray* m_pBigActionContainer;
    # bool m_bFullLevelReset;
    # cocos2d::CCPoint m_obPlayerPosition;
    # int m_nAttempts;
    # int m_nJumpCount;
    # bool m_bHasClicked;
    # float m_fTime;
    # int m_nAttemptJumps;
    # bool m_bLeaderboardPercent;
    # bool m_bShowUI;
    # bool m_bTriggeredEvent;
    # bool m_bResetQueued;
    # int m_nBestPercent;
    # bool m_bDidAwardStars;
    # int m_nAwardedCurrency;
    # int m_nAwardedDiamonds;
    # bool m_bAwardedSecretKey;
    # bool m_bShouldRestartAfterStopped;
    # cocos2d::CCArray* m_pObjectStateArr;
    # cocos2d::CCDictionary* m_pSaveRequiredGroupsUIDs;
    # BYTE PAD6[4];
    # double dword1FC;
    # double dword204;
    # double dword20C;
    # bool dword214;
    # float field_4E4;
    # int dword21C;
    # double m_dAttemptTime;
    # double m_dTempMilliTime;
    # double m_dAttemptTimeSeed;
    # double m_dAttemptTimeRand;
    # DWORD dword244;
    # bool m_bGlitter;
    # bool m_bBGEffectVisibility;
    # bool gap516;
    # bool m_bGamePaused;
    # GameObject* m_pCollidedObject;
    # bool m_bVfDChk;
    # bool m_bDisableGravityEffect;

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
