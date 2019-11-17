from ..utils.enums import NEnum

__all__ = ('ObjectDataEnum', 'LevelDataEnum')


class ObjectDataEnum(NEnum):
    OBJECT_ID = 1
    X = 2  # in Units
    Y = 3  # in Units
    IS_H_FLIPPED = 4
    IS_V_FLIPPED = 5
    ROTATION = 6
    RED = 7  # Color-related Trigger
    GREEN = 8  # Color-related Trigger
    BLUE = 9  # Color-related Trigger
    DURATION = 10
    TOUCH_TRIGGERED = 11
    # ??? = 12
    IS_PORTAL_CHECKED = 13  # Portal
    # ??? = 14
    PLAYER_COLOR_1 = 15
    PLAYER_COLOR_2 = 16  # Trigger
    BLENDING = 17
    # ??? = 18
    # ??? = 19
    EDITOR_LAYER_1 = 20
    COLOR_1 = 21
    COLOR_2 = 22
    TARGET_COLOR_ID = 23
    Z_LAYER = 24
    Z_ORDER = 25
    # ??? = 26
    # ??? = 27
    MOVE_X = 28  # Move Trigger (in Units)
    MOVE_Y = 29  # Move Trigger (in Units)
    EASING = 30  # Move and Rotate Trigger
    TEXT_OF_TEXT_OBJECT = 31  # Text Object
    SCALING = 32
    # ??? = 33
    GROUP_PARENT = 34
    OPACITY = 35  # Trigger
    IS_OR_ACTIVE_TRIGGER_TYPE = 36  # ???
    # ??? = 37
    # ??? = 38
    # ??? = 39
    # ??? = 40
    # HSV - Related: HaSaVaS_CHECKEDaV_CHECKED
    COLOR_1_HSV_ENABLED = 41
    COLOR_2_HSV_ENABLED = 42
    COLOR_1_HSV_VALUES = 43
    COLOR_2_HSV_VALUES = 44
    FADE_IN_TIME = 45  # Pulse Trigger
    HOLD_TIME = 46  # Pulse Trigger
    FADE_OUT_TIME = 47  # Pulse Trigger
    PULSE_MODE = 48  # Pulse Trigger (0 = Color, 1 = HSV)
    COPIED_COLOR_HSV_VALUES = 49  # Color-related Trigger
    COPIED_COLOR_ID = 50  # Color-related Trigger
    TARGET_GROUP_ID = 51  # Trigger
    TARGET_TYPE = 52  # Pulse Trigger (0 = Channel, 1 = Group)
    # ??? = 53
    YELLOW_TP_PORTAL_DISTANCE = 54  # Blue Teleportation Portal
    # ??? = 55
    ACTIVATE_GROUP = 56  # Trigger
    GROUP_IDS = 57  # Separated with '.'
    LOCK_TO_PLAYER_X = 58  # Move Trigger
    LOCK_TO_PLAYER_Y = 59  # Move Trigger
    COPY_OPACITY = 60  # Trigger
    EDITOR_LAYER_2 = 61  # ???
    SPAWN_TRIGGERED = 62  # Trigger
    SPAWN_DURATION = 63  # Spawn Trigger Delay
    DO_NOT_FADE = 64
    MAIN_ONLY = 65  # Pulse Trigger
    DETAIL_ONLY = 66  # Pulse Trigger
    DO_NOT_ENTER = 67
    DEGREES = 68  # Rotate Trigger
    TIMES_360 = 69  # Rotate Trigger
    LOCK_OBJECT_ROTATION = 70  # Rotate Trigger
    FOLLOW_TARGET_POS_CENTER_ID = 71  # Follow, Move and Rotate Trigger
    X_MOD = 72  # Follow Trigger
    Y_MOD = 73  # Follow Trigger
    # ??? = 74
    STRENGTH = 75  # Shake Trigger
    ANIMATION_ID = 76  # Animation Trigger
    COUNT = 77  # Count, Instant Count and Pickup Trigger
    SUBSTRACT_COUNT = 78  # Pickup Item Trigger ("Subtract")
    PICKUP_MODE = 79  # Pickup Item Trigger (1 = Pickup Item, 2 = Toggle Trigger)
    ITEM_OR_BLOCK_A_ID = 80  # Collision and Count, Pickup, Instant Count Trigger
    HOLD_MODE = 81  # Touch Trigger
    TOGGLE = 82  # Touch Trigger (0 = Default, 1 = On, 2 = Off)
    # ??? = 83
    INTERVAL = 84  # Shake Trigger
    EASING_RATE = 85  # Move and Rotate Trigger
    EXCLUSIVE = 86  # Pulse Trigger
    MULTI_TRIGGER = 87  # Trigger
    COMPARISON = 88  # Instant Count Trigger (0 = Equals, 1 = Larger, 2 = Smaller)
    DUAL_MODE = 89  # Touch Trigger
    SPEED = 90  # Follow Player Y
    DELAY = 91  # Follow Player Y
    OFFSET_Y = 92  # Follow Player Y (In Units)
    ACTIVATE_ON_EXIT = 93  # Collision Trigger
    DYNAMIC_BLOCK = 94  # Collision Trigger
    BLOCK_B_ID = 95  # Collision Trigger
    GLOW_DISABLED = 96
    CUSTOM_ROTATION_SPEED = 97  # Rotate Trigger
    DISABLE_ROTATION = 98  # Rotate Trigger
    MULTI_ACTIVATE = 99  # Count Trigger
    USE_TARGET_ENABLED = 100  # Move Trigger
    TARGET_POS_COORDINATES = 101  # Move Trigger (0 = Both, 1 = X Only, 2 = Y Only)
    EDITOR_DISABLE = 102  # Spawn Trigger
    HIGH_DETAIL = 103
    # ??? = 104
    MAX_SPEED = 105  # Follow Y Trigger
    RANDOMIZE_START = 106  # Animation Trigger
    ANIMATION_SPEED = 107  # Animation Trigger
    LINKED_GROUP = 108


class LevelDataEnum(NEnum):
    ID = 'k1'
    LEVEL_NAME = 'k2'
    DESCRIPTION = 'k3'
    DATA = 'k4'
    CREATOR = 'k5'
    OFFICIAL_SONG = 'k8'
    DOWNLOADS = 'k11'
    VERIFIED = 'k14'
    UPLOADED = 'k15'
    VERSION = 'k16'
    ATTEMPTS = 'k18'
    NORMAL_MODE_PERCENTAGE = 'k19'
    PRACTICE_MODE_PERCENTAGE = 'k20'
    LIKES = 'k22'
    LENGTH = 'k23'
    STARS = 'k26'
    PASSWORD = 'k41'
    ORIGINAL = 'k42'
    CUSTOM_SONG = 'k45'
    REVISION = 'k46'
    OBJECTS = 'k48'
    FIRST_COIN_ACQUIRED = 'k61'
    SECOND_COIN_ACQUIRED = 'k62'
    THIRD_COIN_ACQUIRED = 'k63'
    REQUESTED_STARS = 'k66'
    UNLISTED = 'k79'
    SECONDS_SPENT_IN_EDITOR = 'k80'
    FOLDER = 'k84'

    X_POSITION_IN_EDITOR = 'kI1'
    Y_POSITION_IN_EDITOR = 'kI2'
    ZOOM = 'kI3'
    BUILD_TAB_PAGE = 'kI4'
    BUILD_TAB = 'kI5'
    BUILD_TAB_PAGES_DICT = 'kI6'
    EDITOR_LAYER = 'kI7'

    GAMEMODE = 'kA2'
    MINIMODE = 'kA3'
    SPEED = 'kA4'
    BACKGROUND = 'kA6'
    GROUND = 'kA7'
    DUAL_MODE = 'kA8'
    LEVEL_OR_START_POS_OBJECT = 'kA9'
    TWO_PLAYER_MODE = 'kA10'
    FLIP_GRAVITY = 'kA11'
    SONG_OFFSET = 'kA13'
    GUIDELINES = 'kA14'
    SONG_FADE_IN = 'kA15'
    SONG_FADE_OUT = 'kA16'
    GROUND_LINE = 'kA17'
    FONT = 'kA18'
    COLORS = 'kS38'
    COLOR_PAGE = 'kS39'
