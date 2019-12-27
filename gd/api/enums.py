from ..utils.enums import NEnum

__all__ = (
    'ObjectDataEnum',
    'ColorChannelProperties',
    'PlayerColor',
    'CustomParticleGrouping',
    'CustomParticleProperty1',
    'Easing',
    'PulseMode',
    'InstantCountComparison',
    'OrbType',
    'PadType',
    'PortalType',
    'PickupItemMode',
    'PulseType',
    'SpecialBlockType',
    'SpecialColorID',
    'TargetPosCoordinates',
    'TouchToggleMode',
    'TriggerType',
    'ZLayer',
    'Gamemode',
    'Speed',
    'SpeedMagic',
    'LevelDataEnum',
    'LevelHeaderEnum'
)


class ObjectDataEnum(NEnum):
    ID = 1
    X = 2  # in Units
    Y = 3  # in Units
    H_FLIPPED = 4
    V_FLIPPED = 5
    ROTATION = 6
    RED = 7  # Color-related Trigger
    GREEN = 8  # Color-related Trigger
    BLUE = 9  # Color-related Trigger
    R, G, B = RED, GREEN, BLUE  # aliases
    DURATION = 10
    TOUCH_TRIGGERED = 11
    SECRET_COIN_ID = 12
    IS_CHECKED = 13  # Portal
    TINT_GROUND = 14  # deprecated
    SET_TO_PLAYER_COLOR_1 = 15
    SET_TO_PLAYER_COLOR_2 = 16  # Trigger
    BLENDING = 17
    UNKNOWN_18 = 18
    UNKNOWN_19 = 19
    EDITOR_LAYER_1 = 20
    COLOR_1 = 21
    COLOR_2 = 22
    TARGET_COLOR_ID = 23
    Z_LAYER = 24
    Z_ORDER = 25
    UNKNOWN_26 = 26
    UNKNOWN_27 = 27
    MOVE_X = 28  # Move Trigger (in Units)
    MOVE_Y = 29  # Move Trigger (in Units)
    EASING = 30  # Move and Rotate Trigger
    TEXT = 31  # Text Object
    SCALE = 32
    UNKNOWN_33 = 33
    GROUP_PARENT = 34
    OPACITY = 35  # Alpha/Color Trigger
    IS_ACTIVE_TRIGGER = 36  # ???
    UNKNOWN_37 = 37
    UNKNOWN_38 = 38
    UNKNOWN_39 = 39
    UNKNOWN_40 = 40
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
    PULSE_TYPE = 52  # Pulse Trigger (0 = Channel, 1 = Group)
    UNKNOWN_53 = 53
    TP_PORTAL_DISTANCE = 54  # Blue Teleportation Portal
    UNKNOWN_55 = 55
    ACTIVATE_GROUP = 56  # Trigger
    GROUPS = 57  # Separated with '.'
    LOCK_TO_PLAYER_X = 58  # Move Trigger
    LOCK_TO_PLAYER_Y = 59  # Move Trigger
    COPY_OPACITY = 60  # Trigger
    EDITOR_LAYER_2 = 61
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
    UNKNOWN_74 = 74
    STRENGTH = 75  # Shake Trigger
    ANIMATION_ID = 76  # Animation Trigger
    COUNT = 77  # Count, Instant Count and Pickup Trigger
    SUBTRACT_COUNT = 78  # Pickup Item Trigger ("Subtract")
    PICKUP_MODE = 79  # Pickup Item Trigger (1 = Pickup Item, 2 = Toggle Trigger)
    ITEM_ID = 80  # Pickup Trigger
    BLOCK_ID = 80  # Collision Trigger
    BLOCK_A_ID = 80  # Collision Trigger
    HOLD_MODE = 81  # Touch Trigger
    TOGGLE_MODE = 82  # Touch Trigger (0 = Default, 1 = On, 2 = Off)
    UNKNOWN_83 = 83
    INTERVAL = 84  # Shake Trigger
    EASING_RATE = 85  # Move and Rotate Trigger
    EXCLUSIVE = 86  # Pulse Trigger
    MULTI_TRIGGER = 87  # Trigger
    COMPARISON = 88  # Instant Count Trigger (0 = Equals, 1 = Larger, 2 = Smaller)
    DUAL_MODE = 89  # Touch Trigger
    SPEED = 90  # Follow Player Y
    FOLLOW_DELAY = 91  # Follow Player Y
    OFFSET_Y = 92  # Follow Player Y (In Units)
    TRIGGER_ON_EXIT = 93  # Collision Trigger
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
    UNKNOWN_104 = 104
    MAX_SPEED = 105  # Follow Y Trigger
    RANDOMIZE_START = 106  # Animation Trigger
    ANIMATION_SPEED = 107  # Animation Trigger
    LINKED_GROUP = 108

    # <-- 2.2 -->
    UNKNOWN_115 = 115
    SWITCH_PLAYER_DIRECTION = 117
    NO_EFFECTS = 116
    ICE_BLOCK = -201
    NON_STICK = -202
    UNSTUCKABLE = -203
    UNREADABLE_PROPERTY_1 = -204
    UNREADABLE_PROPERTY_2 = -205
    TRANSFORM_SCALE_X = -206
    TRANSFORM_SCALE_Y = -207
    TRANSFORM_SCALE_CENTER_X = -208
    TRANSFORM_SCALE_CENTER_Y = -209

    EXIT_STATIC = 110

    REVERSED = 118
    LOCK_Y = 59

    CHANCE = 0  # needs checking
    CHANCE_LOTS = -300
    CHANCE_LOT_GROUPS = -301

    ZOOM = 109

    GROUPING = -108
    PROPERTY_1 = -109
    MAX_PARTICLES = -110
    CUSTOM_PARTICLE_DURATION = -111
    LIFETIME = -112
    LIFETIME_ADJUSTMENT = -113
    EMISSION = -114
    ANGLE = -115
    ANGLE_ADJUSTMENT = -116
    CUSTOM_PARTICLE_SPEED = -117
    SPEED_ADJUSTMENT = -118
    POS_VAR_X = -119
    POS_VAR_Y = -120
    GRAVITY_X = -121
    GRAVITY_Y = -122
    ACCEL_RAD = -123
    ACCEL_RAD_ADJUSTMENT = -124
    ACCEL_TAN = -125
    ACCEL_TAN_ADJUSTMENT = -126
    START_SIZE = -127
    START_SIZE_ADJUSTMENT = -128
    END_SIZE = -129
    END_SIZE_ADJUSTMENT = -130
    START_SPIN = -131
    START_SPIN_ADJUSTMENT = -132
    END_SPIN = -133
    END_SPIN_ADJUSTMENT = -134
    START_A = -135
    START_A_ADJUSTMENT = -136
    START_R = -137
    START_R_ADJUSTMENT = -138
    START_G = -139
    START_G_ADJUSTMENT = -140
    START_B = -141
    START_B_ADJUSTMENT = -142
    END_A = -143
    END_A_ADJUSTMENT = -144
    END_R = -145
    END_R_ADJUSTEMENT = -146
    END_G = -147
    END_G_ADJUSTMENT = -148
    END_B = -149
    END_B_ADJUSTMENT = -150
    CUSTOM_PARTICLE_FADE_IN = -151
    FADE_IN_ADJUSTMENT = -152
    CUSTOM_PARTICLE_FADE_OUT_ADJUSTMENT = -153
    FADE_OUT_ADJUSTMENT = -15
    ADDICTIVE = -155
    START_SIZE_EQUALS_END = -156
    START_SPIN_EQUALS_END = -157
    START_RADIUS_EQUALS_END = -158
    IS_START_ROTATION_DIR = -159
    DYNAMIC_ROTATION = -160
    USE_OBJECT_COLOR = -161
    UNIFORM_OBJECT_COLOR = -162
    TEXTURE = -163

    SCALE_X = -164
    SCALE_Y = -165
    LOCK_OBJECT_SCALE = -166
    ONLY_MOVE_SCALE = -167

    LOCK_TO_CAMERA_X = -302
    LOCK_TO_CAMERA_Y = -303


class ColorChannelProperties(NEnum):
    RED = 1
    GREEN = 2
    BLUE = 3
    R, G, B = RED, GREEN, BLUE
    PLAYER_COLOR = 4
    BLENDING = 5
    ID = 6
    OPACITY = 7
    UNKNOWN_8 = 8  # 1?
    COPIED_COLOR_ID = 9
    HSV_VALUES = 10
    UNKNOWN_RED = 11
    UNKNOWN_GREEN = 12
    UNKNOWN_BLUE = 13
    UNKNOWN_15 = 15  # 1?
    COPY_OPACITY = 17
    UNKNOWN_18 = 18  # 0?


class PlayerColor(NEnum):
    NotUsed = -1
    Default = 0
    P1 = 1
    P2 = 2


class CustomParticleGrouping(NEnum):
    Free = 0
    Relative = 1
    Grouped = 2


class CustomParticleProperty1(NEnum):
    Gravity = 0
    Radius = 1


class Easing(NEnum):
    Default = 0
    EaseInOut = 1
    EaseIn = 2
    EaseOut = 3
    ElasticInOut = 4
    ElasticIn = 5
    ElasticOut = 6
    BounceInOut = 7
    BounceIn = 8
    BounceOut = 9
    ExponentialInOut = 10
    ExponentialIn = 11
    ExponentialOut = 12
    SineInOut = 13
    SineIn = 14
    SineOut = 15
    BackInOut = 16
    BackIn = 17
    BackOut = 18


class PulseMode(NEnum):
    Color = 0
    HSV = 1


class InstantCountComparison(NEnum):
    Equals = 0
    Larger = 1
    Smaller = 2


class OrbType(NEnum):
    Yellow = 36
    Pink = 141
    Red = 1333
    Blue = 84
    Green = 1022
    Black = 1330
    Dash = 1704
    ReverseDash = 1751
    Trigger = 1594


class PadType(NEnum):
    Yellow  = 35
    Pink = 140
    Red = 1332
    Blue = 67


class PickupItemMode(NEnum):
    Default = 0
    Pickup = 1
    ToggleTrigger = 2


class Gamemode(NEnum):
    Cube = 0
    Ship = 1
    Ball = 2
    UFO = 3
    Wave = 4
    Robot = 5
    Spider = 6
    SwingCopter = 7  # ?


class PortalType(NEnum):
    Cube = 12
    Ship = 13
    Ball = 47
    UFO = 111
    Wave = 660
    Robot = 745
    Spider = 1331

    YellowGravity = 11
    BlueGravity = 10
    YellowMirror = 45
    BlueMirror = 46
    PinkSize = 101
    GreenSize = 99
    YellowDual = 286
    BlueDual = 287
    BlueTeleportation = 747
    YellowTeleportation = 749

    SlowSpeed = 200
    NormalSpeed = 201
    FastSpeed = 202
    FasterSpeed = 203
    FastestSpeed = 1334


class PulseType(NEnum):
    ColorChannel = 0
    Group = 1


class SpecialBlockType(NEnum):
    D = 1755
    J = 1813
    S = 1829
    H = 1859


class SpecialColorID(NEnum):
    BG = 1000
    GRND = 1001
    Line = 1002
    Obj = 1003
    Line3D = 1004
    P1 = 1005
    P2 = 1006
    LBG = 1007
    GRND2 = 1009
    Black = 1010
    White = 1011
    Lighter = 1012


class TargetPosCoordinates(NEnum):
    Both  = 0
    OnlyX = 1
    OnlyY = 2


class TouchToggleMode(NEnum):
    Default = 0
    On = 1
    Off = 2


class TriggerType(NEnum):
    BG = 29
    GRND = 30
    StartPos = 31
    EnableTrail = 32
    DisableTrail = 33
    Line = 104
    Obj = 105
    Color1 = 221
    Color2 = 717
    Color3 = 718
    Color4 = 743
    ThreeDL = 744
    Color = 899
    GRND2 = 900
    Move = 901
    Line2 = 915
    Pulse = 1006
    Alpha = 1007
    Toggle = 1049
    Spawn = 1268
    Rotate = 1346
    Follow = 1347
    Shake = 1520
    Animate = 1585
    Touch = 1595
    Count = 1611
    HidePlayer = 1612
    ShowPlayer = 1613
    Stop = 1616
    InstantCount = 1811
    OnDeath = 1812
    FollowPlayerY = 1814
    Collision = 1815
    Pickup = 1817
    BGEffectOn = 1818
    BGEffectOff = 1819

    Random = 1912
    Zoom = 1913
    StaticCamera = 1914
    CameraOffset = 1916
    Reverse = 1917
    End = 1931
    StopJump = 1932
    Scale = -11
    Song = -12
    TimeWarp = -13


class ZLayer(NEnum):
    B4 = -3
    B3 = -1
    B2 = 1
    B1 = 3
    T1 = 5
    T2 = 7
    T3 = 9

    Bottom = 1
    Middle = 3
    Top = 5
    HigherTop = 7
    AbsZero = 4


class Speed(NEnum):
    NORMAL = 0   # x 1
    SLOW = 1     # x 0.5
    FAST = 2     # x 2
    FASTER = 3   # x 3
    FASTEST = 4  # x 4


class SpeedMagic(NEnum):
    SLOW = 251.16     # x 0.5
    NORMAL = 311.58   # x 1
    FAST = 387.42     # x 2
    FASTER = 468.0    # x 3
    FASTEST = 576.0   # x 4
    DEFAULT = NORMAL  # -> x 1


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


class LevelHeaderEnum(NEnum):
    AUDIO_TRACK = 'kA1'
    GAMEMODE = 'kA2'
    MINIMODE = 'kA3'
    SPEED = 'kA4'
    COLOR_1_BLEND = 'kA5'
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
    COLOR_PAGES = 'kS39'

    # <= 1.9
    BACKGROUND_R = 'kS1'
    BACKGROUND_G = 'kS2'
    BACKGROUND_B = 'kS3'
    GROUND_R = 'kS4'
    GROUND_G = 'kS5'
    GROUND_B = 'kS6'
    LINE_R = 'kS7'
    LINE_G = 'kS8'
    LINE_B = 'kS9'
    OBJECT_R = 'kS10'
    OBJECT_G = 'kS11'
    OBJECT_B = 'kS12'
    COLOR_1_R = 'kS13'
    COLOR_1_G = 'kS14'
    COLOR_1_B = 'kS15'
    BACKGROUND_PLAYER_COLOR = 'kS16'
    GROUND_PLAYER_COLOR = 'kS17'
    LINE_PLAYER_COLOR = 'kS18'
    OBJECT_FORMAT = 'kS19'
    COLOR_1_PLAYER_COLOR = 'kS20'

    # 1.9
    BACKGROUND_COLOR = 'kS29'
    GROUND_COLOR = 'kS30'
    LINE_COLOR = 'kS31'
    OBJECT_COLOR = 'kS32'
    COLOR_1 = 'kS33'
    COLOR_2 = 'kS34'
    COLOR_3 = 'kS35'
    COLOR_4 = 'kS36'
    COLOR_3DL = 'kS37'
