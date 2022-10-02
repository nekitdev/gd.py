from gd.enums import GameMode, Speed
from gd.memory.base import Struct, StructData, struct
from gd.memory.cocos import CCLayer, CCNode, CCNodeContainer, CCPoint
from gd.memory.data import Bool, Float, Int
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


@struct(virtual=True)
class TriggerEffectDelegate(Struct):
    default_enter_effect = Field(Bool())


@struct(virtual=True)
class BaseGameManager(CCNode):
    file_name = Field(StringData())

    setup = Field(Bool())
    saved = Field(Bool())


@struct(virtual=True)
class GameManager(BaseGameManager):
    ...


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


@struct(virtual=True)
class BaseGameLayer(TriggerEffectDelegate, CCLayer):
    oriented_bounding_box = Field(MutPointerData(Void()))  # OBB2D*

    effect_manager = Field(MutPointerData(Void()))  # EffectManager*

    object_layer = Field(MutPointerData(StructData(CCLayer)))

    # cocos2d::CCSpriteBatchNode* m_pBatchNodeAddTop4;
    # cocos2d::CCSpriteBatchNode* m_pEffectBatchNodeAddTop4;
    # cocos2d::CCSpriteBatchNode* m_pBatchNodeTop3;
    # cocos2d::CCSpriteBatchNode* m_pBatchNodeAddTop3;
    # cocos2d::CCSpriteBatchNode* m_pBatchNodeAddGlowTop3;
    batch_node_top_3_container = Field(MutPointerData(StructData(CCNodeContainer)))
    # cocos2d::CCSpriteBatchNode* m_pBatchNodeTextTop3;
    # cocos2d::CCSpriteBatchNode* m_pBatchNodeAddTextTop3;
    # cocos2d::CCSpriteBatchNode* m_pEffectBatchNodeTop3;
    # cocos2d::CCSpriteBatchNode* m_pEffectBatchNodeAddTop3;
    # cocos2d::CCSpriteBatchNode* m_pBatchNodeTop2;
    # cocos2d::CCSpriteBatchNode* m_pBatchNodeAddTop2;
    # cocos2d::CCSpriteBatchNode* m_pBatchNodeAddGlowTop2;
    batch_node_top_2_container = Field(MutPointerData(StructData(CCNodeContainer)))
    # cocos2d::CCSpriteBatchNode* m_pBatchNodeTextTop2;
    # cocos2d::CCSpriteBatchNode* m_pBatchNodeAddTextTop2;
    # cocos2d::CCSpriteBatchNode* m_pEffectBatchNodeTop2;
    # cocos2d::CCSpriteBatchNode* m_pEffectBatchNodeAddTop2;
    # cocos2d::CCSpriteBatchNode* m_pBatchNode;
    # cocos2d::CCSpriteBatchNode* m_pBatchNodeAdd;
    # cocos2d::CCSpriteBatchNode* m_pBatchNodeAddGlow;
    batch_node_top_1_container = Field(MutPointerData(StructData(CCNodeContainer)))
    # cocos2d::CCSpriteBatchNode* m_pBatchNodeTextTop1;
    # cocos2d::CCSpriteBatchNode* m_pBatchNodeAddTextTop1;
    # cocos2d::CCSpriteBatchNode* m_pEffectBatchNodeTop1;
    # cocos2d::CCSpriteBatchNode* m_pEffectBatchNodeAddTop1;
    # cocos2d::CCSpriteBatchNode* m_pBatchNodePlayer;
    # cocos2d::CCSpriteBatchNode* m_pBatchNodeAddPlayer;
    # cocos2d::CCSpriteBatchNode* m_pBatchNodePlayerGlow;
    # cocos2d::CCSpriteBatchNode* m_pBatchNodeAddMid;
    # cocos2d::CCSpriteBatchNode* m_pBatchNodeBot;
    # cocos2d::CCSpriteBatchNode* m_pBatchNodeAddBot;
    # cocos2d::CCSpriteBatchNode* m_pBatchNodeAddBotGlow;
    batch_node_bottom_1_container = Field(MutPointerData(StructData(CCNodeContainer)))
    # cocos2d::CCSpriteBatchNode* m_pBatchNodeText;
    # cocos2d::CCSpriteBatchNode* m_pBatchNodeAddText;
    # cocos2d::CCSpriteBatchNode* m_pEffectBatchNode;
    # cocos2d::CCSpriteBatchNode* m_pEffectBatchNodeAdd;
    # cocos2d::CCSpriteBatchNode* m_pBatchNodeBot2;
    # cocos2d::CCSpriteBatchNode* m_pBatchNodeAddBot2;
    # cocos2d::CCSpriteBatchNode* m_pBatchNodeAddBot2Glow;
    batch_node_bottom_2_container = Field(MutPointerData(StructData(CCNodeContainer)))
    # cocos2d::CCSpriteBatchNode* m_pBatchNodeTextBot2;
    # cocos2d::CCSpriteBatchNode* m_pBatchNodeAddTextBot2;
    # cocos2d::CCSpriteBatchNode* m_pEffectBatchNodeBot2;
    # cocos2d::CCSpriteBatchNode* m_pEffectBatchNodeAddBot2;
    # cocos2d::CCSpriteBatchNode* m_pBatchNodeBot3;
    # cocos2d::CCSpriteBatchNode* m_pBatchNodeAddBot3;
    # cocos2d::CCSpriteBatchNode* m_pBatchNodeAddBot3Glow;
    batch_node_bottom_3_container = Field(MutPointerData(StructData(CCNodeContainer)))
    # cocos2d::CCSpriteBatchNode* m_pBatchNodeTextBot3;
    # cocos2d::CCSpriteBatchNode* m_pBatchNodeAddTextBot3;
    # cocos2d::CCSpriteBatchNode* m_pEffectBatchNodeBot3;
    # cocos2d::CCSpriteBatchNode* m_pEffectBatchNodeAddBot3;
    # cocos2d::CCSpriteBatchNode* m_pBatchNodeBot4;
    # cocos2d::CCSpriteBatchNode* m_pBatchNodeAddBot4;
    # cocos2d::CCSpriteBatchNode* m_pBatchNodeAddBot4Glow;
    batch_node_bottom_4_container = Field(MutPointerData(StructData(CCNodeContainer)))
    # cocos2d::CCSpriteBatchNode* m_pBatchNodeTextBot4;
    # cocos2d::CCSpriteBatchNode* m_pBatchNodeAddTextBot4;
    # cocos2d::CCSpriteBatchNode* m_pEffectBatchNodeBot4;
    # cocos2d::CCSpriteBatchNode* m_pEffectBatchNodeAddBot4;
    # PlayerObject* m_pPlayer1;
    # PlayerObject* m_pPlayer2;
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


# TODO: Player, Vector<T>?
