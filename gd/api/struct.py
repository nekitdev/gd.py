# type: ignore

# DOCUMENT

from builtins import iter as std_iter

from iters import iter

from gd.api.guidelines import Guidelines
from gd.api.hsv import HSV
from gd.api.recording import Recording, RecordingEntry
from gd.api.utils import get_dir, get_id
from gd.color import Color
from gd.converters import Password, Version
from gd.crypto import decode_base64_str, encode_base64_str, unzip_level_str, zip_level_str
from gd.decorators import cache_by
from gd.enums import (
    Easing,
    Enum,
    Gamemode,
    InstantCountComparison,
    InternalType,
    LevelLength,
    LevelType,
    PickupItemMode,
    PlayerColor,
    PortalType,
    PulseMode,
    PulseType,
    Speed,
    SpeedChange,
    SpeedMagic,
    TargetPosCoordinates,
    TouchToggleMode,
    ZLayer,
)
from gd.index_parser import IndexParser
from gd.iter_utils import is_iterable
from gd.model_backend import (
    Base64Field,
    BaseField,
    BoolField,
    EnumField,
    FloatField,
    IntField,
    IterableField,
    MappingField,
    Model,
    ModelField,
    ModelIterField,
    StrField,
    partial,
)
from gd.text_utils import is_level_probably_decoded
from gd.typing import (
    TYPE_CHECKING,
    Callable,
    Dict,
    Iterable,
    Iterator,
    Mapping,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
)

__all__ = (
    "PORTAL_IDS",
    "SPEED_IDS",
    "SPEEDS",
    "Object",
    "ColorChannel",
    "Channel",
    "Header",
    "LevelAPI",
    "ColorCollection",
    "DEFAULT_COLORS",
)

if TYPE_CHECKING:
    from gd.api.editor import Editor

IntoColor = Union[Color, Tuple[int, int, int], str, int]

SPEEDS = {}

for speed in Speed:
    name = speed.name.casefold()

    magic = SpeedMagic.from_name(name)
    speed_change = SpeedChange.from_name(name)

    SPEEDS.update({speed.value: magic.value, speed_change.value: magic.value})

del speed, name, magic, speed_change

PORTAL_IDS = {portal.value for portal in PortalType}
SPEED_IDS = {speed.value for speed in SpeedChange}
SPEED_AND_PORTAL_IDS = PORTAL_IDS | SPEED_IDS

T = TypeVar("T")

KT = TypeVar("KT")
VT = TypeVar("VT")
KU = TypeVar("KU")
VU = TypeVar("VU")


def color_from(color: IntoColor) -> Color:
    if isinstance(color, Color):
        return color

    elif isinstance(color, int):
        return Color(color)

    elif isinstance(color, str):
        return Color.from_hex(color)

    elif is_iterable(color):
        return Color.from_rgb(*color)

    else:
        raise ValueError(
            f"Do not know how to convert {color} to color. Known conversions: {IntoColor}."
        )


def map_key_value(
    mapping: Mapping[KT, VT], key_func: Callable[[KT], KU], value_func: Callable[[VT], VU]
) -> Mapping[KU, VU]:
    return {key_func(key): value_func(value) for key, value in mapping.items()}


def enum_from_value(value: T, enum_type: Type[Enum]) -> Enum:
    return enum_type.from_value(value)


def enum_to_value(enum: Enum) -> T:
    return enum.value


class Object(Model):
    PARSER = IndexParser(",", map_like=True)

    id: int = IntField(index=1, default=0)
    x: float = FloatField(index=2, default=0.0)
    y: float = FloatField(index=3, default=0.0)
    h_flipped: bool = BoolField(index=4)
    v_flipped: bool = BoolField(index=5)
    rotation: float = FloatField(index=6)
    red: int = IntField(index=7, aliases=("r",))
    green: int = IntField(index=8, aliases=("g",))
    blue: int = IntField(index=9, aliases=("b",))
    duration: float = FloatField(index=10)
    touch_triggered: bool = BoolField(index=11)
    secret_coin_id: int = IntField(index=12)
    special_checked: bool = BoolField(index=13)
    tint_ground: bool = BoolField(index=14)  # deprecated
    use_player_color_1: bool = BoolField(index=15)
    use_player_color_2: bool = BoolField(index=16)
    blending: bool = BoolField(index=17)
    # index_18: ... = ?Field(index=18)
    # index_19: ... = ?Field(index=19)
    editor_layer_1: int = IntField(index=20)
    color_1_id: int = IntField(index=21, aliases=("color_1",))
    color_2_id: int = IntField(index=22, aliases=("color_2",))
    target_color_id: int = IntField(index=23)
    z_layer: ZLayer = EnumField(index=24, enum_type=ZLayer, from_field=IntField)
    z_order: int = IntField(index=25)
    # index_26: ... = ?Field(index=26)
    # index_27: ... = ?Field(index=27)
    move_x: float = FloatField(index=28)
    move_y: float = FloatField(index=29)
    easing: Easing = EnumField(index=30, enum_type=Easing, from_field=IntField)
    text: str = Base64Field(index=31)
    scale: float = FloatField(index=32)
    # index_33: ... = ?Field(index=33)
    group_parent: bool = BoolField(index=34)
    opacity: float = FloatField(index=35)
    trigger: bool = BoolField(index=36)
    # index_37: ... = ?Field(index=37)
    # index_38: ... = ?Field(index=38)
    # index_39: ... = ?Field(index=39)
    # index_40: ... = ?Field(index=40)
    color_1_hsv_enabled: bool = BoolField(index=41)
    color_2_hsv_enabled: bool = BoolField(index=42)
    color_1_hsv: HSV = ModelField(index=43, model=HSV)
    color_2_hsv: HSV = ModelField(index=44, model=HSV)
    fade_in_time: float = FloatField(index=45)
    hold_time: float = FloatField(index=46)
    fade_out_time: float = FloatField(index=47)
    pulse_mode: PulseMode = EnumField(index=48, enum_type=PulseMode, from_field=IntField)
    copied_color_hsv: HSV = ModelField(index=49, model=HSV)
    copied_color_id: int = IntField(index=50)
    target_group_id: int = IntField(index=51)
    pulse_type: PulseType = EnumField(index=52, enum_type=PulseType, from_field=IntField)
    # index_53: ... = ?Field(index=53)
    teleport_portal_distance: float = FloatField(index=54)
    # index_55: ... = ?Field(index=53)
    activate_group: bool = BoolField(index=56)
    groups: Set[int] = IterableField(index=57, delim=".", transform=set, from_field=IntField)
    lock_to_player_x: bool = BoolField(index=58)
    lock_to_player_y: bool = BoolField(index=59)
    copy_opacity: bool = BoolField(index=60)
    editor_layer_2: int = IntField(index=61)
    spawn_triggered: bool = BoolField(index=62)
    spawn_duration: float = FloatField(index=63)
    do_not_fade: bool = BoolField(index=64)
    main_only: bool = BoolField(index=65)
    detail_only: bool = BoolField(index=66)
    do_not_enter: bool = BoolField(index=67)
    degrees: int = IntField(index=68)
    full_rotation_times: int = IntField(index=69)
    lock_object_rotation: bool = BoolField(index=70)
    other_id: int = IntField(
        index=71, aliases=("follow_group_id", "target_pos_id", "center_id", "secondary_id"),
    )
    x_mod: float = FloatField(index=72)
    y_mod: float = FloatField(index=73)
    # index_74: ... = ?Field(index=74)
    strength: float = FloatField(index=75)
    animation_id: int = IntField(index=76)
    count: int = IntField(index=77)
    subtract_count: bool = BoolField(index=78)
    pickup_item_mode: PickupItemMode = EnumField(
        index=79, enum_type=PickupItemMode, from_field=IntField
    )
    item_or_block_id: int = IntField(index=80, aliases=("item_id", "block_id", "block_a_id"))
    hold_mode: bool = BoolField(index=81)
    touch_toggle_mode: TouchToggleMode = EnumField(
        index=82, enum_type=TouchToggleMode, from_field=IntField
    )
    # index_83: ... = ?Field(index=83)
    interval: float = FloatField(index=84)
    easing_rate: float = FloatField(index=85)
    exclusive: bool = BoolField(index=86)
    multi_trigger: bool = BoolField(index=87)
    comparison: InstantCountComparison = EnumField(
        index=88, enum_type=InstantCountComparison, from_field=IntField
    )
    dual_mode: bool = BoolField(index=89)
    speed: float = FloatField(index=90)
    follow_y_delay: float = FloatField(index=91)
    follow_y_offset: float = FloatField(index=92)
    trigger_on_exit: bool = BoolField(index=93)
    dynamic_block: bool = BoolField(index=94)
    block_b_id: int = IntField(index=95)
    disable_glow: bool = BoolField(index=96)
    custom_rotation_speed: float = FloatField(index=97)
    disable_rotation: float = FloatField(index=98)
    multi_activate: bool = BoolField(index=99)
    use_target: bool = BoolField(index=100)
    target_pos_coordinates: TargetPosCoordinates = EnumField(
        index=101, enum_type=TargetPosCoordinates, from_field=IntField
    )
    editor_disable: bool = BoolField(index=102)
    high_detail: bool = BoolField(index=103)
    # index_104: ... = ?Field(index=104)
    follow_y_max_speed: float = FloatField(index=105)
    randomize_start: bool = BoolField(index=106)
    animation_speed: float = FloatField(index=107)
    linked_group_id: int = IntField(index=108)

    ...  # 2.2 future proofing fields will be added when it gets released

    def h_flip(self) -> "Object":
        self.h_flipped = not self.h_flipped

    def v_flip(self) -> "Object":
        self.v_flipped = not self.v_flipped

    def set_id(self, directive: str) -> "Object":
        self.id = get_id(directive)
        return self

    def set_z_layer(self, directive: str) -> "Object":
        self.z_layer = get_id(get_dir(directive, "layer"), into_enum=True)
        return self

    def set_easing(self, directive: str) -> "Object":
        self.easing = get_id(get_dir(directive, "easing"), into_enum=True)
        return self

    def add_groups(self, *groups: int) -> "Object":
        if self.groups is None:
            self.groups = set(groups)

        else:
            self.groups |= set(groups)

        return self

    def remove_groups(self, *groups: int) -> "Object":
        if self.groups is not None:
            self.groups -= set(groups)

        return self

    def get_pos(self) -> Tuple[float, float]:
        return (self.x, self.y)

    def set_pos(self, x: float, y: float) -> "Object":
        self.x = x
        self.y = y
        return self

    def move(self, x: float = 0.0, y: float = 0.0) -> "Object":
        self.x += x
        self.y += y
        return self

    def rotate(self, degrees: float = 0.0) -> "Object":
        if self.rotation is None:
            self.rotation = degrees

        else:
            self.rotation += degrees

        return self

    def is_checked(self) -> bool:
        return self.special_checked

    def is_portal(self) -> bool:
        return self.id in PORTAL_IDS

    def is_speed(self) -> bool:
        return self.id in SPEED_IDS

    def is_speed_or_portal(self) -> bool:
        return self.id in SPEED_AND_PORTAL_IDS


class ColorChannel(Model):
    PARSER = IndexParser("_", map_like=True)

    red: int = IntField(index=1, default=255, aliases=("r",))
    green: int = IntField(index=2, default=255, aliases=("g",))
    blue: int = IntField(index=3, default=255, aliases=("b",))
    player_color: PlayerColor = EnumField(
        index=4, enum_type=PlayerColor, from_field=IntField, default=PlayerColor.NotUsed
    )
    blending: bool = BoolField(index=5, default=False)
    id: int = IntField(index=6, default=0)
    opacity: float = FloatField(index=7, default=1.0)
    index_8: bool = BoolField(index=8, default=True)
    copied_id: int = IntField(index=9)
    hsv: HSV = ModelField(index=10, model=HSV)
    unknown_red: int = IntField(index=11, default=255, aliases=("unknown_r",))
    unknown_green: int = IntField(index=12, default=255, aliases=("unknown_g",))
    unknown_blue: int = IntField(index=13, default=255, aliases=("unknown_b",))
    index_15: bool = BoolField(index=15, default=True)
    copy_opacity: bool = BoolField(index=17)
    index_18: bool = BoolField(index=18, default=False)

    def __init__(self, directive: Optional[str] = None, **kwargs) -> None:
        super().__init__(**kwargs)

        if directive is not None:
            self.set_id(directive)

    def set_id(self, directive: str) -> "ColorChannel":
        self.id = get_id(get_dir(directive, "color"))

        return self

    def get_color(self) -> Color:
        return Color.from_rgb(self.r, self.g, self.b)

    def set_color(self, color: IntoColor) -> "ColorChannel":
        new = color_from(color)
        self.r = new.r
        self.g = new.g
        self.b = new.b
        return self

    color = property(get_color, set_color)


DEFAULT_COLORS = (
    ColorChannel("BG").set_color(0x287DFF),
    ColorChannel("G").set_color(0x0066FF),
    ColorChannel("Line").set_color(0xFFFFFF),
    ColorChannel("P1").set_color(0x7DFF00),
    ColorChannel("P2").set_color(0x00FFFF),
    ColorChannel("G2").set_color(0x0066FF),
)

Channel = ColorChannel


class ColorCollection(set):
    def __init__(
        self, iterable: Optional[Iterable[ColorChannel]] = None, use_default: bool = True,
    ) -> None:
        if use_default:
            super().__init__(DEFAULT_COLORS)
        else:
            super().__init__()

        if iterable is not None:
            super().update(iterable)

    @classmethod
    def new(cls, *args: ColorChannel, use_default: bool = True) -> "ColorCollection":
        return cls(args, use_default=use_default)

    def remove(self, directive_or_id: Union[int, str]) -> None:
        self.discard(self.get(directive_or_id))

    def copy(self) -> "ColorCollection":
        return self.__class__(channel.copy() for channel in self)

    def clone(self) -> "ColorCollection":
        return self.__class__(channel.clone() for channel in self)

    def difference(self, other: Iterable[ColorChannel]) -> "ColorCollection":
        return self.__class__(super().difference(other))

    def intersection(self, other: Iterable[ColorChannel]) -> "ColorCollection":
        return self.__class__(super().intersection(other))

    def symmetric_difference(self, other: Iterable[ColorChannel]) -> "ColorCollection":
        return self.__class__(super().symmetric_difference(other))

    def union(self, other: Iterable[ColorChannel]) -> "ColorCollection":
        return self.__class__(super().union(other))

    def update(self, other: Iterable[ColorChannel]) -> "ColorCollection":
        super().update(other)
        return self

    def get(self, directive_or_id: Union[int, str]) -> Optional[ColorChannel]:
        if isinstance(directive_or_id, str):
            id = get_id(get_dir(directive_or_id, "color"))

        else:
            id = directive_or_id

        return iter(self).get(id=id)

    def __or__(self, other: Set[ColorChannel]) -> "ColorCollection":
        return self.__class__(super().__or__(other))

    def __xor__(self, other: Set[ColorChannel]) -> "ColorCollection":
        return self.__class__(super().__xor__(other))

    def __sub__(self, other: Set[ColorChannel]) -> "ColorCollection":
        return self.__class__(super().__sub__(other))

    def __and__(self, other: Set[ColorChannel]) -> "ColorCollection":
        return self.__class__(super().__and__(other))

    def __ror__(self, other: Set[ColorChannel]) -> "ColorCollection":
        return self.__class__(super().__ror__(other))

    def __rxor__(self, other: Set[ColorChannel]) -> "ColorCollection":
        return self.__class__(super().__rxor__(other))

    def __rsub__(self, other: Set[ColorChannel]) -> "ColorCollection":
        return self.__class__(super().__rsub__(other))

    def __rand__(self, other: Set[ColorChannel]) -> "ColorCollection":
        return self.__class__(super().__rand__(other))


class Header(Model):
    PARSER = IndexParser(",", map_like=True)

    audio_track: int = IntField(index="kA1")
    gamemode: Gamemode = EnumField(
        index="kA2", enum_type=Gamemode, from_field=IntField, default=Gamemode.CUBE
    )
    minimode: bool = BoolField(index="kA3", default=False)
    speed: Speed = EnumField(
        index="kA4", enum_type=Speed, from_field=IntField, default=Speed.NORMAL
    )
    index_kA5: str = StrField(index="kA5")  # need to check this, something to do with blending
    background: int = IntField(index="kA6", default=0)
    ground: int = IntField(index="kA7", default=0)
    dual_mode: bool = BoolField(index="kA8", default=False)
    has_start_pos: bool = BoolField(index="kA9", default=False)
    two_player_mode: bool = BoolField(index="kA10", default=False)
    flip_gravity: bool = BoolField(index="kA11", default=False)
    song_offset: float = FloatField(index="kA13", default=0.0)
    guidelines: Guidelines = MappingField(
        index="kA14",
        delim="~",
        transform=Guidelines,
        key_from_field=FloatField,
        value_from_field=FloatField,
        skip_empty=True,
    )
    song_fade_in: bool = BoolField(index="kA15", default=False)
    song_fade_out: bool = BoolField(index="kA16", default=False)
    ground_line: int = IntField(index="kA17", default=0)
    font: int = IntField(index="kA18", default=0)
    colors: Set[ColorChannel] = ModelIterField(
        index="kS38",
        model=ColorChannel,
        delim="|",
        transform=partial(ColorCollection, use_default=False),
        factory=ColorCollection,
    )
    color_pages: int = IntField(index="kS39", default=0)

    background_r: int = IntField(index="kS1")
    background_b: int = IntField(index="kS2")
    background_g: int = IntField(index="kS3")
    ground_r: int = IntField(index="kS4")
    ground_b: int = IntField(index="kS5")
    ground_g: int = IntField(index="kS6")
    line_r: int = IntField(index="kS7")
    line_g: int = IntField(index="kS8")
    line_b: int = IntField(index="kS9")
    object_r: int = IntField(index="kS10")
    object_g: int = IntField(index="kS11")
    object_b: int = IntField(index="kS12")
    color_1_r: int = IntField(index="kS13")
    color_1_g: int = IntField(index="kS14")
    color_1_b: int = IntField(index="kS15")

    background_player_color: PlayerColor = EnumField(
        index="kS16", enum_type=PlayerColor, from_field=IntField
    )
    ground_player_color: PlayerColor = EnumField(
        index="kS17", enum_type=PlayerColor, from_field=IntField
    )
    line_player_color: PlayerColor = EnumField(
        index="kS18", enum_type=PlayerColor, from_field=IntField
    )
    object_player_color: PlayerColor = EnumField(
        index="kS19", enum_type=PlayerColor, from_field=IntField
    )
    color_1_player_color: PlayerColor = EnumField(
        index="kS20", enum_type=PlayerColor, from_field=IntField
    )

    background_color: ColorChannel = ModelField(index="kS29", model=ColorChannel)
    ground_color: ColorChannel = ModelField(index="kS30", model=ColorChannel)
    line_color: ColorChannel = ModelField(index="kS31", model=ColorChannel)
    object_color: ColorChannel = ModelField(index="kS32", model=ColorChannel)
    color_1: ColorChannel = ModelField(index="kS33", model=ColorChannel)
    color_2: ColorChannel = ModelField(index="kS34", model=ColorChannel)
    color_3: ColorChannel = ModelField(index="kS35", model=ColorChannel)
    color_4: ColorChannel = ModelField(index="kS36", model=ColorChannel)
    color_3dl: ColorChannel = ModelField(index="kS37", model=ColorChannel)


class LevelAPI(Model):
    ENFORCE_STR = False
    REPR_IGNORE = {"unprocessed_data", "recording_string"}

    id: int = BaseField(index="k1", de=int, ser=int, default=0)
    name: str = BaseField(index="k2", de=str, ser=str, default="Unnamed")
    description: str = BaseField(index="k3", de=decode_base64_str, ser=encode_base64_str)
    unprocessed_data: str = BaseField(index="k4", de=str, ser=str)
    creator: str = BaseField(index="k5", de=str, ser=str)
    track_id: int = BaseField(index="k8", de=int, ser=int)
    downloads: int = BaseField(index="k11", de=int, ser=int)
    index_k13: bool = BaseField(index="k13", de=bool, ser=bool, default=True)
    verified: bool = BaseField(index="k14", de=bool, ser=bool)
    uploaded: bool = BaseField(index="k15", de=bool, ser=bool)
    version: int = BaseField(index="k16", de=int, ser=int, default=1)
    attempts: int = BaseField(index="k18", de=int, ser=int)
    normal_mode_percentage: int = BaseField(index="k19", de=int, ser=int)
    practice_mode_percentage: int = BaseField(index="k20", de=int, ser=int)
    level_type: LevelType = BaseField(
        index="k21", de=partial(enum_from_value, enum_type=LevelType), ser=enum_to_value
    )
    likes: int = BaseField(index="k22", de=int, ser=int)
    length: LevelLength = BaseField(
        index="k23", de=partial(enum_from_value, enum_type=LevelLength), ser=enum_to_value,
    )
    stars: int = BaseField(index="k26", de=int, ser=int)
    recording_string: str = BaseField(index="k34", de=str, ser=str)
    jumps: int = BaseField(index="k36", de=int, ser=int)
    password_field: Password = BaseField(
        index="k41", de=Password.from_robtop_number, ser=Password.to_robtop_number
    )
    original_id: int = BaseField(index="k42", de=int, ser=int)
    song_id: int = BaseField(index="k45", de=int, ser=int)
    revision: int = BaseField(index="k46", de=int, ser=int)
    index_k47: bool = BaseField(index="k47", de=bool, ser=bool, default=True)
    object_count: int = BaseField(index="k48", de=int, ser=int)
    binary_version: Version = BaseField(
        index="k50", de=Version.from_number, ser=Version.to_number, default=Version(3, 5),
    )
    first_coint_acquired: bool = BaseField(index="k61", de=bool, ser=bool)
    second_coin_acquired: bool = BaseField(index="k62", de=bool, ser=bool)
    third_coin_acquired: bool = BaseField(index="k63", de=bool, ser=bool)
    requested_stars: int = BaseField(index="k66", de=int, ser=int)
    extra_string: str = BaseField(index="k67", de=str, ser=str)
    timely_id: int = BaseField(index="k74", de=int, ser=int)
    unlisted: bool = BaseField(index="k79", de=bool, ser=bool)
    editor_seconds: int = BaseField(index="k80", de=int, ser=int)
    copies_seconds: int = BaseField(index="k81", de=int, ser=int)
    folder: int = BaseField(index="k84", de=int, ser=int)

    x: float = BaseField(index="kI1", de=float, ser=float)
    y: float = BaseField(index="kI2", de=float, ser=float)
    zoom: float = BaseField(index="kI3", de=float, ser=float)
    build_tab_page: int = BaseField(index="kI4", de=int, ser=int)
    build_tab: int = BaseField(index="kI5", de=int, ser=int)
    build_tab_pages_dict: Dict[int, int] = BaseField(
        index="kI6",
        de=partial(map_key_value, key_func=int, value_func=int),
        ser=partial(map_key_value, key_func=str, value_func=str),
    )
    editor_layer: int = BaseField(index="kI7", de=int, ser=int)

    internal_type: InternalType = BaseField(
        index="kCEK",
        de=partial(enum_from_value, enum_type=InternalType),
        ser=enum_to_value,
        default=InternalType.LEVEL,
    )

    def get_password(self) -> Optional[int]:
        if self.password_field is None:
            return None

        return self.password_field.password

    def set_password(self, password: Optional[int]) -> None:
        if self.password_field is None:
            self.password_field = Password(password)

        else:
            self.password_field.password = password

    password = property(get_password, set_password)

    def get_copyable(self) -> bool:
        if self.password_field is None:
            return False

        return self.password_field.copyable

    def set_copyable(self, copyable: bool) -> None:
        if self.password_field is None:
            self.password_field = Password(None, copyable)

        else:
            self.password_field.copyable = copyable

    copyable = property(get_copyable, set_copyable)

    @cache_by("unprocessed_data")
    def get_data(self) -> str:
        unprocessed_data = self.unprocessed_data

        if unprocessed_data is None:
            return ""

        if is_level_probably_decoded(unprocessed_data):
            return unprocessed_data

        else:
            return unzip_level_str(unprocessed_data)

    def set_data(self, data: str) -> None:
        if is_level_probably_decoded(data):
            self.unprocessed_data = zip_level_str(data)

        else:
            self.unprocessed_data = data

    data = property(get_data, set_data)

    @cache_by("recording_string")
    def get_recording(self) -> Recording:
        if self.recording_string is None:
            return Recording()

        return Recording.from_string(unzip_level_str(self.recording_string))

    def set_recording(self, recording: Iterable[RecordingEntry]) -> None:
        self.recording_string = zip_level_str(Recording.collect_string(recording))

    recording = property(get_recording, set_recording)

    @cache_by("recording_string")
    def iter_recording(self) -> Iterator[RecordingEntry]:
        if self.recording_string is None:
            return std_iter(())

        return Recording.iter_string(unzip_level_str(self.recording_string))

    def open_editor(self) -> "Editor":
        from gd.api.editor import Editor

        return Editor.load_from(self, "data")

    def to_dict(self) -> Dict[str, T]:
        result = super().to_dict()
        result.update(password=self.password, copyable=self.copyable)

        return result
