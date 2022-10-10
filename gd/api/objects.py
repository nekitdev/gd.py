from io import BytesIO
from typing import BinaryIO, Dict, Iterable, Mapping, Type, TypeVar

from attrs import define, field
from typing_extensions import Literal, TypeGuard

from gd.api.hsv import HSV
from gd.api.objects_constants import TEXT_ID
from gd.api.ordered_set import OrderedSet
from gd.binary import VERSION, Binary
from gd.binary_constants import BITS
from gd.binary_utils import Reader, Writer
from gd.color import Color
from gd.constants import DEFAULT_ENCODING, DEFAULT_ERRORS, DEFAULT_ID, EMPTY
from gd.encoding import decode_base64_string_url_safe, encode_base64_string_url_safe
from gd.enum_extensions import Enum, Flag
from gd.enums import (
    ByteOrder,
    Easing,
    InstantCountComparison,
    PickupItemMode,
    PlayerColor,
    PortalType,
    PulseMode,
    PulseTargetType,
    PulseType,
    SpeedChange,
    TargetType,
    ToggleType,
    ZLayer,
)
from gd.models import Model
from gd.models_constants import GROUPS_SEPARATOR, OBJECT_SEPARATOR
from gd.models_utils import (
    concat_groups,
    concat_object,
    float_str,
    int_bool,
    parse_get_or,
    partial_parse_enum,
    split_groups,
    split_object,
)
from gd.robtop import RobTop
from gd.typing import is_instance

__all__ = (
    "Groups",
    "Object",
    "AnimatedObject",
    "Orb",
    "Coin",
    "Text",
    "Teleport",
    "PickupItem",
    "CollisionBlock",
    "ColorTrigger",
    "PulseTrigger",
    "AlphaTrigger",
    "MoveTrigger",
    "SpawnTrigger",
    "StopTrigger",
    "ToggleTrigger",
    "RotateTrigger",
    "FollowTrigger",
    "ShakeTrigger",
    "AnimateTrigger",
    "TouchTrigger",
    "CountTrigger",
    "InstantCountTrigger",
    "PickupTrigger",
    "FollowPlayerYTrigger",
    "OnDeathTrigger",
    "CollisionTrigger",
    "object_from_binary",
    "object_to_binary",
    "object_from_bytes",
    "object_to_bytes",
)

H_FLIPPED_BIT = 0b00000001
V_FLIPPED_BIT = 0b00000010
DO_NOT_FADE_BIT = 0b00000100
DO_NOT_ENTER_BIT = 0b00001000
GROUP_PARENT_BIT = 0b00010000
HIGH_DETAIL_BIT = 0b00100000
DISABLE_GLOW_BIT = 0b01000000
SPECIAL_CHECKED_BIT = 0b10000000

Z_ORDER_MASK = 0b00011111_11111111

Z_LAYER_SHIFT = Z_ORDER_MASK.bit_length()


class ObjectFlag(Flag):
    SIMPLE = 0

    HAS_ROTATION_AND_SCALE = 1
    HAS_EDITOR_LAYER = 2
    HAS_COLORS = 4
    HAS_GROUPS = 8
    HAS_LINK = 16
    HAS_Z = 32

    def has_rotation_and_scale(self) -> bool:
        return type(self).HAS_ROTATION_AND_SCALE in self

    def has_editor_layer(self) -> bool:
        return type(self).HAS_EDITOR_LAYER in self

    def has_colors(self) -> bool:
        return type(self).HAS_COLORS in self

    def has_groups(self) -> bool:
        return type(self).HAS_GROUPS in self

    def has_link(self) -> bool:
        return type(self).HAS_LINK in self

    def has_z(self) -> bool:
        return type(self).HAS_Z in self


DEFAULT_X = 0.0
DEFAULT_Y = 0.0

DEFAULT_ROTATION = 0.0

DEFAULT_H_FLIPPED = False
DEFAULT_V_FLIPPED = False

DEFAULT_SCALE = 1.0

DEFAULT_DO_NOT_FADE = False
DEFAULT_DO_NOT_ENTER = False

DEFAULT_Z_ORDER = 0

DEFAULT_BASE_EDITOR_LAYER = 0
DEFAULT_ADDITIONAL_EDITOR_LAYER = 0

DEFAULT_BASE_COLOR_ID = 0
DEFAULT_DETAIL_COLOR_ID = 0

DEFAULT_GROUP_PARENT = False

DEFAULT_HIGH_DETAIL = False

DEFAULT_DISABLE_GLOW = False

DEFAULT_SPECIAL_CHECKED = False


G = TypeVar("G", bound="Groups")


class Groups(RobTop, OrderedSet[int]):
    @classmethod
    def from_robtop(cls: Type[G], string: str) -> G:
        return cls(map(int, split_groups(string)))

    def to_robtop(self) -> str:
        return concat_groups(map(str, self))

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return GROUPS_SEPARATOR in string


ID = 1
X = 2
Y = 3
H_FLIPPED = 4
V_FLIPPED = 5
ROTATION = 6
SCALE = 32
DO_NOT_FADE = 64
DO_NOT_ENTER = 67
Z_LAYER = 24
Z_ORDER = 25
BASE_EDITOR_LAYER = 20
ADDITIONAL_EDITOR_LAYER = 61
BASE_COLOR_ID = 21
DETAIL_COLOR_ID = 22
BASE_COLOR_HSV_MODIFIED = 41
DETAIL_COLOR_HSV_MODIFIED = 42
BASE_COLOR_HSV = 43
DETAIL_COLOR_HSV = 44
GROUPS = 57
GROUP_PARENT = 34
HIGH_DETAIL = 103
DISABLE_GLOW = 96
SPECIAL_CHECKED = 13
LINK_ID = 108


O = TypeVar("O", bound="Object")


@define()
class Object(Model, Binary):
    id: int = field()
    x: float = field(default=DEFAULT_X)
    y: float = field(default=DEFAULT_Y)

    h_flipped: bool = field(default=DEFAULT_H_FLIPPED)
    v_flipped: bool = field(default=DEFAULT_V_FLIPPED)

    rotation: float = field(default=DEFAULT_ROTATION)

    scale: float = field(default=DEFAULT_SCALE)

    do_not_fade: bool = field(default=DEFAULT_DO_NOT_FADE)
    do_not_enter: bool = field(default=DEFAULT_DO_NOT_ENTER)

    z_layer: ZLayer = field(default=ZLayer.DEFAULT)
    z_order: int = field(default=DEFAULT_Z_ORDER)

    base_editor_layer: int = field(default=DEFAULT_BASE_EDITOR_LAYER)
    additional_editor_layer: int = field(default=DEFAULT_ADDITIONAL_EDITOR_LAYER)

    base_color_id: int = field(default=DEFAULT_BASE_COLOR_ID)
    detail_color_id: int = field(default=DEFAULT_DETAIL_COLOR_ID)

    base_color_hsv: HSV = field(factory=HSV)
    detail_color_hsv: HSV = field(factory=HSV)

    groups: Groups = field(factory=Groups)

    group_parent: bool = field(default=DEFAULT_GROUP_PARENT)

    high_detail: bool = field(default=DEFAULT_HIGH_DETAIL)

    disable_glow: bool = field(default=DEFAULT_DISABLE_GLOW)

    special_checked: bool = field(default=DEFAULT_SPECIAL_CHECKED)

    link_id: int = field(default=DEFAULT_ID)

    @classmethod
    def from_binary(
        cls: Type[O], binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> O:
        h_flipped_bit = H_FLIPPED_BIT
        v_flipped_bit = V_FLIPPED_BIT
        do_not_fade_bit = DO_NOT_FADE_BIT
        do_not_enter_bit = DO_NOT_ENTER_BIT
        group_parent_bit = GROUP_PARENT_BIT
        high_detail_bit = HIGH_DETAIL_BIT
        disable_glow_bit = DISABLE_GLOW_BIT
        special_checked_bit = SPECIAL_CHECKED_BIT

        reader = Reader(binary)

        flag_value = reader.read_u8(order)

        flag = ObjectFlag(flag_value)

        id = reader.read_u16(order)

        x = reader.read_f32(order)
        y = reader.read_f32(order)

        value = reader.read_u8(order)

        h_flipped = value & h_flipped_bit == h_flipped_bit
        v_flipped = value & v_flipped_bit == v_flipped_bit
        do_not_fade = value & do_not_fade_bit == do_not_fade_bit
        do_not_enter = value & do_not_enter_bit == do_not_enter_bit
        group_parent = value & group_parent_bit == group_parent_bit
        high_detail = value & high_detail_bit == high_detail_bit
        disable_glow = value & disable_glow_bit == disable_glow_bit
        special_checked = value & special_checked_bit == special_checked_bit

        if flag.has_rotation_and_scale():
            rotation = reader.read_f32(order)
            scale = reader.read_f32(order)

        else:
            rotation = DEFAULT_ROTATION
            scale = DEFAULT_SCALE

        if flag.has_z():
            z_layer_order = reader.read_u16(order)

            z_layer_value = z_layer_order >> Z_LAYER_SHIFT
            z_order = z_layer_order & Z_ORDER_MASK

            z_layer = ZLayer(z_layer_value)

        else:
            z_layer = ZLayer.DEFAULT
            z_order = 0

        if flag.has_editor_layer():
            base_editor_layer = reader.read_u16(order)
            additional_editor_layer = reader.read_u16(order)

        else:
            base_editor_layer = 0
            additional_editor_layer = 0

        if flag.has_colors():
            base_color_id = reader.read_u16(order)
            detail_color_id = reader.read_u16(order)

            base_color_hsv = HSV.from_binary(binary, order, version)
            detail_color_hsv = HSV.from_binary(binary, order, version)

        else:
            base_color_id = 0
            detail_color_id = 0

            base_color_hsv = HSV()
            detail_color_hsv = HSV()

        groups: Groups

        if flag.has_groups():
            length = reader.read_u16(order)

            groups = Groups(reader.read_u16(order) for _ in range(length))

        else:
            groups = Groups()

        if flag.has_link():
            link_id = reader.read_u16(order)

        else:
            link_id = 0

        return cls(
            id=id,
            x=x,
            y=y,
            rotation=rotation,
            scale=scale,
            h_flipped=h_flipped,
            v_flipped=v_flipped,
            do_not_fade=do_not_fade,
            do_not_enter=do_not_enter,
            z_layer=z_layer,
            z_order=z_order,
            base_editor_layer=base_editor_layer,
            additional_editor_layer=additional_editor_layer,
            base_color_id=base_color_id,
            detail_color_id=detail_color_id,
            base_color_hsv=base_color_hsv,
            detail_color_hsv=detail_color_hsv,
            groups=groups,
            group_parent=group_parent,
            high_detail=high_detail,
            disable_glow=disable_glow,
            special_checked=special_checked,
            link_id=link_id,
        )

    def to_binary(
        self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        writer = Writer(binary)

        flag = ObjectFlag.SIMPLE

        rotation = self.rotation
        scale = self.scale

        if rotation or scale != DEFAULT_SCALE:
            flag |= ObjectFlag.HAS_ROTATION_AND_SCALE

        z_layer = self.z_layer
        z_order = self.z_order

        if not z_layer.is_default() or z_order:
            flag |= ObjectFlag.HAS_Z

        base_editor_layer = self.base_editor_layer
        additional_editor_layer = self.additional_editor_layer

        if base_editor_layer or additional_editor_layer:
            flag |= ObjectFlag.HAS_EDITOR_LAYER

        base_color_id = self.base_color_id
        detail_color_id = self.detail_color_id

        base_color_hsv = self.base_color_hsv
        detail_color_hsv = self.detail_color_hsv

        if (
            base_color_id
            or detail_color_id
            or not base_color_hsv.is_default()
            or not detail_color_hsv.is_default()
        ):
            flag |= ObjectFlag.HAS_COLORS

        groups = self.groups

        if groups:
            flag |= ObjectFlag.HAS_GROUPS

        link_id = self.link_id

        if link_id:
            flag |= ObjectFlag.HAS_LINK

        writer.write_u8(flag.value, order)

        writer.write_u16(self.id, order)

        writer.write_f32(self.x, order)
        writer.write_f32(self.y, order)

        value = 0

        if self.is_h_flipped():
            value |= H_FLIPPED_BIT

        if self.is_v_flipped():
            value |= V_FLIPPED_BIT

        if self.is_do_not_fade():
            value |= DO_NOT_FADE_BIT

        if self.is_do_not_enter():
            value |= DO_NOT_ENTER_BIT

        if self.is_group_parent():
            value |= GROUP_PARENT_BIT

        if self.is_high_detail():
            value |= HIGH_DETAIL_BIT

        if self.is_disable_glow():
            value |= DISABLE_GLOW_BIT

        if self.is_special_checked():
            value |= SPECIAL_CHECKED_BIT

        writer.write_u8(value, order)

        if flag.has_rotation_and_scale():
            writer.write_f32(self.rotation, order)
            writer.write_f32(self.scale, order)

        if flag.has_z():
            z_layer_order = z_order & Z_ORDER_MASK
            z_layer_order |= z_layer.value << Z_LAYER_SHIFT

            writer.write_u16(z_layer_order, order)

        if flag.has_editor_layer():
            writer.write_u16(base_editor_layer, order)
            writer.write_u16(additional_editor_layer, order)

        if flag.has_colors():
            writer.write_u16(base_color_id, order)
            writer.write_u16(detail_color_id, order)

            base_color_hsv.to_binary(binary, order, version)
            detail_color_hsv.to_binary(binary, order, version)

        if flag.has_groups():
            writer.write_u16(len(groups), order)

            for group in sorted(groups):
                writer.write_u16(group, order)

        if flag.has_link():
            writer.write_u16(link_id, order)

    @classmethod
    def from_robtop(cls: Type[O], string: str) -> O:
        return cls.from_robtop_mapping(split_object(string))

    @classmethod
    def from_robtop_mapping(cls: Type[O], mapping: Mapping[int, str]) -> O:
        id = int(mapping[ID])

        x = parse_get_or(float, DEFAULT_X, mapping.get(X))
        y = parse_get_or(float, DEFAULT_Y, mapping.get(Y))

        rotation = parse_get_or(float, DEFAULT_ROTATION, mapping.get(ROTATION))

        scale = parse_get_or(float, DEFAULT_SCALE, mapping.get(SCALE))

        h_flipped = parse_get_or(int_bool, DEFAULT_H_FLIPPED, mapping.get(H_FLIPPED))
        v_flipped = parse_get_or(int_bool, DEFAULT_V_FLIPPED, mapping.get(V_FLIPPED))

        do_not_fade = parse_get_or(int_bool, DEFAULT_DO_NOT_FADE, mapping.get(DO_NOT_FADE))
        do_not_enter = parse_get_or(int_bool, DEFAULT_DO_NOT_ENTER, mapping.get(DO_NOT_ENTER))

        z_layer = parse_get_or(
            partial_parse_enum(int, ZLayer), ZLayer.DEFAULT, mapping.get(Z_LAYER)
        )
        z_order = parse_get_or(int, DEFAULT_Z_ORDER, mapping.get(Z_ORDER))

        base_editor_layer = parse_get_or(
            int, DEFAULT_BASE_EDITOR_LAYER, mapping.get(BASE_EDITOR_LAYER)
        )
        additional_editor_layer = parse_get_or(
            int, DEFAULT_ADDITIONAL_EDITOR_LAYER, mapping.get(ADDITIONAL_EDITOR_LAYER)
        )

        base_color_id = parse_get_or(int, DEFAULT_BASE_COLOR_ID, mapping.get(BASE_COLOR_ID))
        detail_color_id = parse_get_or(int, DEFAULT_DETAIL_COLOR_ID, mapping.get(DETAIL_COLOR_ID))

        base_color_hsv = parse_get_or(HSV.from_robtop, HSV(), mapping.get(BASE_COLOR_HSV))
        detail_color_hsv = parse_get_or(HSV.from_robtop, HSV(), mapping.get(DETAIL_COLOR_HSV))

        groups = parse_get_or(Groups.from_robtop, Groups(), mapping.get(GROUPS))

        group_parent = parse_get_or(int_bool, DEFAULT_GROUP_PARENT, mapping.get(GROUP_PARENT))
        high_detail = parse_get_or(int_bool, DEFAULT_HIGH_DETAIL, mapping.get(HIGH_DETAIL))
        disable_glow = parse_get_or(int_bool, DEFAULT_DISABLE_GLOW, mapping.get(DISABLE_GLOW))
        special_checked = parse_get_or(
            int_bool, DEFAULT_SPECIAL_CHECKED, mapping.get(SPECIAL_CHECKED)
        )

        link_id = parse_get_or(int, DEFAULT_ID, mapping.get(LINK_ID))

        return cls(
            id=id,
            x=x,
            y=y,
            rotation=rotation,
            scale=scale,
            h_flipped=h_flipped,
            v_flipped=v_flipped,
            do_not_fade=do_not_fade,
            do_not_enter=do_not_enter,
            z_layer=z_layer,
            z_order=z_order,
            base_editor_layer=base_editor_layer,
            additional_editor_layer=additional_editor_layer,
            base_color_id=base_color_id,
            detail_color_id=detail_color_id,
            base_color_hsv=base_color_hsv,
            detail_color_hsv=detail_color_hsv,
            groups=groups,
            group_parent=group_parent,
            high_detail=high_detail,
            disable_glow=disable_glow,
            special_checked=special_checked,
            link_id=link_id,
        )

    def to_robtop(self) -> str:
        return concat_object(self.to_robtop_mapping())

    def to_robtop_mapping(self) -> Dict[int, str]:
        mapping = {ID: str(self.id), X: float_str(self.x), Y: float_str(self.y)}

        rotation = self.rotation

        if rotation:
            mapping[ROTATION] = float_str(rotation)

        scale = self.scale

        if scale != DEFAULT_SCALE:
            mapping[SCALE] = float_str(scale)

        h_flipped = self.h_flipped

        if h_flipped:
            mapping[H_FLIPPED] = str(int(h_flipped))

        v_flipped = self.v_flipped

        if v_flipped:
            mapping[V_FLIPPED] = str(int(v_flipped))

        do_not_fade = self.do_not_fade

        if do_not_fade:
            mapping[DO_NOT_FADE] = str(int(do_not_fade))

        do_not_enter = self.do_not_enter

        if do_not_enter:
            mapping[DO_NOT_ENTER] = str(int(do_not_enter))

        z_layer = self.z_layer

        if not z_layer.is_default():
            mapping[Z_LAYER] = str(z_layer.into_simple_z_layer().value)

        z_order = self.z_order

        if z_order:
            mapping[Z_ORDER] = str(z_order)

        base_editor_layer = self.base_editor_layer

        if base_editor_layer:
            mapping[BASE_EDITOR_LAYER] = str(base_editor_layer)

        additional_editor_layer = self.additional_editor_layer

        if additional_editor_layer:
            mapping[ADDITIONAL_EDITOR_LAYER] = str(additional_editor_layer)

        base_color_id = self.base_color_id

        if base_color_id:
            mapping[BASE_COLOR_ID] = str(base_color_id)

        detail_color_id = self.detail_color_id

        if detail_color_id:
            mapping[DETAIL_COLOR_ID] = str(detail_color_id)

        base_color_hsv = self.base_color_hsv

        if not base_color_hsv.is_default():
            mapping[BASE_COLOR_HSV] = base_color_hsv.to_robtop()

        detail_color_hsv = self.detail_color_hsv

        if not detail_color_hsv.is_default():
            mapping[DETAIL_COLOR_HSV] = detail_color_hsv.to_robtop()

        groups = self.groups

        if groups:
            mapping[GROUPS] = groups.to_robtop()

        group_parent = self.group_parent

        if group_parent:
            mapping[GROUP_PARENT] = str(int(group_parent))

        high_detail = self.high_detail

        if high_detail:
            mapping[HIGH_DETAIL] = str(int(high_detail))

        disable_glow = self.disable_glow

        if disable_glow:
            mapping[DISABLE_GLOW] = str(int(disable_glow))

        special_checked = self.special_checked

        if special_checked:
            mapping[SPECIAL_CHECKED] = str(int(special_checked))

        link_id = self.link_id

        if link_id:
            mapping[LINK_ID] = str(link_id)

        return mapping

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return OBJECT_SEPARATOR in string

    def is_h_flipped(self) -> bool:
        return self.h_flipped

    def is_v_flipped(self) -> bool:
        return self.v_flipped

    def is_do_not_fade(self) -> bool:
        return self.do_not_fade

    def is_do_not_enter(self) -> bool:
        return self.do_not_enter

    def is_group_parent(self) -> bool:
        return self.group_parent

    def is_high_detail(self) -> bool:
        return self.high_detail

    def is_disable_glow(self) -> bool:
        return self.disable_glow

    def is_special_checked(self) -> bool:
        return self.special_checked

    def add_groups(self: O, *groups: int) -> O:
        self.groups.update(groups)

        return self

    def add_groups_from_iterable(self: O, iterable: Iterable[int]) -> O:
        self.groups.update(iterable)

        return self

    def remove_groups(self: O, *groups: int) -> O:
        self.groups.difference_update(groups)

        return self

    def remove_groups_from_iterable(self: O, iterable: Iterable[int]) -> O:
        self.groups.difference_update(iterable)

        return self

    def move(self: O, x: float = 0.0, y: float = 0.0) -> O:
        self.x += x
        self.y += y

        return self

    def h_flip(self: O) -> O:
        self.h_flipped = not self.h_flipped

        return self

    def v_flip(self: O) -> O:
        self.v_flipped = not self.v_flipped

        return self

    def rotate(self: O, angle: float) -> O:
        self.rotation += angle

        return self

    def scale_by(self: O, scale: float) -> O:
        self.scale *= scale

        return self

    def scale_to(self: O, scale: float) -> O:
        self.scale = scale

        return self

    def scale_to_default(self: O) -> O:
        return self.scale_to(DEFAULT_SCALE)

    def is_trigger(self) -> bool:
        return False

    def has_target_group(self) -> bool:
        return False

    def has_additional_group(self) -> bool:
        return False

    def is_portal(self) -> bool:
        return self.id in PORTAL_IDS

    def is_speed_change(self) -> bool:
        return self.id in SPEED_CHANGE_IDS


PORTAL_IDS = {portal.value for portal in PortalType}
SPEED_CHANGE_IDS = {speed_change.value for speed_change in SpeedChange}


COIN_ID = 12


C = TypeVar("C", bound="Coin")


@define()
class Coin(Object):
    coin_id: int = DEFAULT_ID

    @classmethod
    def from_binary(
        cls: Type[C], binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> C:
        coin = super().from_binary(binary, order, version)

        reader = Reader(binary)

        coin_id = reader.read_u8(order)

        coin.coin_id = coin_id

        return coin

    def to_binary(
        self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        writer.write_u8(self.coin_id, order)

    @classmethod
    def from_robtop_mapping(cls: Type[C], mapping: Mapping[int, str]) -> C:
        coin = super().from_robtop_mapping(mapping)

        coin_id = parse_get_or(int, DEFAULT_ID, mapping.get(COIN_ID))

        coin.coin_id = coin_id

        return coin

    def to_robtop_mapping(self) -> Dict[int, str]:
        mapping = super().to_robtop_mapping()

        mapping[COIN_ID] = str(self.coin_id)

        return mapping


S = TypeVar("S", bound="Text")

CONTENT = 31


@define()
class Text(Object):
    content: str = EMPTY

    @classmethod
    def from_binary(
        cls: Type[S],
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
    ) -> S:
        text = super().from_binary(binary, order, version)

        reader = Reader(binary)

        length = reader.read_u16(order)

        content = reader.read(length).decode(encoding, errors)

        text.content = content

        return text

    def to_binary(
        self,
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        data = self.content.encode(encoding, errors)

        writer.write_u16(len(data), order)

        writer.write(data)

    @classmethod
    def from_robtop_mapping(cls: Type[S], mapping: Mapping[int, str]) -> S:
        text = super().from_robtop_mapping(mapping)

        content = parse_get_or(decode_base64_string_url_safe, EMPTY, mapping.get(CONTENT))

        text.content = content

        return text

    def to_robtop_mapping(self) -> Dict[int, str]:
        mapping = super().to_robtop_mapping()

        mapping[CONTENT] = encode_base64_string_url_safe(self.content)

        return mapping


DEFAULT_OFFSET = 0.0


@define(slots=False)
class HasOffset:
    offset: float = DEFAULT_OFFSET


DEFAULT_SMOOTH = False

SMOOTH_BIT = 0b00000001

P = TypeVar("P", bound="Teleport")


@define()
class Teleport(HasOffset, Object):
    smooth: bool = DEFAULT_SMOOTH

    @classmethod
    def from_binary(
        cls: Type[P], binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> P:
        smooth_bit = SMOOTH_BIT

        teleport = super().from_binary(binary, order, version)

        reader = Reader(binary)

        offset = reader.read_f32(order)

        value = reader.read_u8(order)

        smooth = value & smooth_bit == smooth_bit

        teleport.offset = offset
        teleport.smooth = smooth

        return teleport

    def to_binary(
        self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        writer.write_f32(self.offset, order)

        value = 0

        if self.is_smooth():
            value |= SMOOTH_BIT

        writer.write_u8(value, order)

    def is_smooth(self) -> bool:
        return self.smooth


DEFAULT_RANDOMIZE_START = False
DEFAULT_ANIMATION_SPEED = 1.0

RANDOMIZE_START_BIT = 0b00000001


AO = TypeVar("AO", bound="AnimatedObject")


@define()
class AnimatedObject(Object):
    randomize_start: bool = DEFAULT_RANDOMIZE_START
    animation_speed: float = DEFAULT_ANIMATION_SPEED

    @classmethod
    def from_binary(
        cls: Type[AO],
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> AO:
        randomize_start_bit = RANDOMIZE_START_BIT

        animated_object = super().from_binary(binary, order, version)

        reader = Reader(binary)

        animation_speed = reader.read_f32(order)

        value = reader.read_u8(order)

        randomize_start = value & randomize_start_bit == randomize_start_bit

        animated_object.randomize_start = randomize_start

        animated_object.animation_speed = animation_speed

        return animated_object

    def to_binary(
        self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        writer.write_f32(self.animation_speed, order)

        value = 0

        if self.is_randomize_start():
            value |= RANDOMIZE_START_BIT

        writer.write_u8(value, order)

    def is_randomize_start(self) -> bool:
        return self.randomize_start


DYNAMIC_BIT = 0b10000000_00000000
BLOCK_ID_MASK = 0b01111111_11111111


DEFAULT_DYNAMIC = False


CB = TypeVar("CB", bound="CollisionBlock")


@define()
class CollisionBlock(Object):
    block_id: int = DEFAULT_ID
    dynamic: bool = DEFAULT_DYNAMIC

    @classmethod
    def from_binary(
        cls: Type[CB],
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> CB:
        dynamic_bit = DYNAMIC_BIT

        collision_block = super().from_binary(binary, order, version)

        reader = Reader(binary)

        value = reader.read_u16(order)

        block_id = value & BLOCK_ID_MASK
        dynamic = value & dynamic_bit == dynamic_bit

        collision_block.block_id = block_id
        collision_block.dynamic = dynamic

        return collision_block

    def to_binary(
        self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        value = self.block_id & BLOCK_ID_MASK

        if self.is_dynamic():
            value |= DYNAMIC_BIT

        writer.write_u16(value, order)

    def is_dynamic(self) -> bool:
        return self.dynamic


@define(slots=False)
class HasItem:
    item_id: int = DEFAULT_ID


DEFAULT_COUNT = 0


@define(slots=False)
class HasCount:
    count: int = DEFAULT_COUNT


@define(slots=False)
class HasTargetGroup:
    target_group_id: int = DEFAULT_ID


@define(slots=False)
class HasAdditionalGroup:
    additional_group_id: int = DEFAULT_ID


DEFAULT_ACTIVATE_GROUP = False


@define(slots=False)
class HasActivateGroup:
    activate_group: bool = DEFAULT_ACTIVATE_GROUP

    def is_activate_group(self) -> bool:
        return self.activate_group


DEFAULT_DURATION = 0.0


@define(slots=False)
class HasDuration:
    duration: float = DEFAULT_DURATION


DEFAULT_DELAY = 0.0


@define(slots=False)
class HasDelay:
    delay: float = DEFAULT_DELAY


DEFAULT_EASING_RATE = 2.0


@define(slots=False)
class HasEasing:
    easing: Easing = Easing.DEFAULT
    easing_rate: float = DEFAULT_EASING_RATE


DEFAULT_MULTI_ACTIVATE = False


@define(slots=False)
class HasMultiActivate:
    multi_activate: bool = DEFAULT_MULTI_ACTIVATE

    def is_multi_activate(self) -> bool:
        return self.multi_activate


@define(slots=False)
class HasColor:
    color: Color = field(factory=Color.default)


MULTI_ACTIVATE_BIT = 0b00000010


OP = TypeVar("OP", bound="Orb")


@define()
class Orb(HasMultiActivate, Object):
    @classmethod
    def from_binary(
        cls: Type[OP],
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> OP:
        orb = super().from_binary(binary, order, version)

        multi_activate_bit = MULTI_ACTIVATE_BIT

        reader = Reader(binary)

        value = reader.read_u8(order)

        multi_activate = value & multi_activate_bit == multi_activate_bit

        orb.multi_activate = multi_activate

        return orb

    def to_binary(
        self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        value = 0

        if self.is_multi_activate():
            value |= MULTI_ACTIVATE_BIT

        writer.write_u8(value, order)


IC = TypeVar("IC", bound="ItemCounter")


@define()
class ItemCounter(HasItem, Object):
    @classmethod
    def from_binary(
        cls: Type[IC],
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> IC:
        item_counter = super().from_binary(binary, order, version)

        reader = Reader(binary)

        item_id = reader.read_u16(order)

        item_counter.item_id = item_id

        return item_counter

    def to_binary(
        self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        writer.write_u16(self.item_id, order)


PI = TypeVar("PI", bound="PickupItem")


@define()
class PickupItem(HasTargetGroup, HasItem, Object):
    mode: PickupItemMode = PickupItemMode.DEFAULT

    @classmethod
    def from_binary(
        cls: Type[PI],
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> PI:
        pickup_item = super().from_binary(binary, order, version)

        reader = Reader(binary)

        target_group_id = reader.read_u16(order)
        item_id = reader.read_u16(order)

        mode_value = reader.read_u8(order)

        mode = PickupItemMode(mode_value)

        pickup_item.target_group_id = target_group_id

        pickup_item.item_id = item_id

        pickup_item.mode = mode

        return pickup_item

    def to_binary(
        self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        writer.write_u16(self.target_group_id, order)
        writer.write_u16(self.item_id, order)

        writer.write_u8(self.mode.value, order)


TOUCH_TRIGGERED_BIT = 0b00000001
SPAWN_TRIGGERED_BIT = 0b00000010
MULTI_TRIGGER_BIT = 0b00000100


DEFAULT_TOUCH_TRIGGERED = False
DEFAULT_SPAWN_TRIGGERED = False
DEFAULT_MULTI_TRIGGER = False


T = TypeVar("T", bound="Trigger")


@define()
class Trigger(Object):
    touch_triggered: bool = DEFAULT_TOUCH_TRIGGERED
    spawn_triggered: bool = DEFAULT_SPAWN_TRIGGERED
    multi_trigger: bool = DEFAULT_MULTI_TRIGGER

    @classmethod
    def from_binary(
        cls: Type[T], binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> T:
        touch_triggered_bit = TOUCH_TRIGGERED_BIT
        spawn_triggered_bit = SPAWN_TRIGGERED_BIT
        multi_trigger_bit = MULTI_TRIGGER_BIT

        trigger = super().from_binary(binary, order, version)

        reader = Reader(binary)

        value = reader.read_u8(order)

        touch_triggered = value & touch_triggered_bit == touch_triggered_bit
        spawn_triggered = value & spawn_triggered_bit == spawn_triggered_bit
        multi_trigger = value & multi_trigger_bit == multi_trigger_bit

        trigger.touch_triggered = touch_triggered
        trigger.spawn_triggered = spawn_triggered
        trigger.multi_trigger = multi_trigger

        return trigger

    def to_binary(
        self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        value = 0

        if self.is_touch_triggered():
            value |= TOUCH_TRIGGERED_BIT

        if self.is_spawn_triggered():
            value |= SPAWN_TRIGGERED_BIT

        if self.is_multi_trigger():
            value |= MULTI_TRIGGER_BIT

        writer.write_u8(value, order)

    def is_trigger(self) -> Literal[True]:
        return True

    def is_touch_triggered(self) -> bool:
        return self.touch_triggered

    def is_spawn_triggered(self) -> bool:
        return self.spawn_triggered

    def is_multi_trigger(self) -> bool:
        return self.multi_trigger


PLAYER_COLOR_MASK = 0b00000011
BLENDING_BIT = 0b00000100
COPY_OPACITY_BIT = 0b00001000


DEFAULT_BLENDING = False
DEFAULT_COPY_OPACITY = False


CLT = TypeVar("CLT", bound="ColorTrigger")


@define()
class ColorTrigger(HasColor, HasDuration, Trigger):
    blending: bool = field(default=DEFAULT_BLENDING)
    target_color_id: int = field(default=DEFAULT_ID)

    copied_color_id: int = field(default=DEFAULT_ID)
    copied_color_hsv: HSV = field(factory=HSV)

    copy_opacity: bool = field(default=False)

    player_color: PlayerColor = field(default=PlayerColor.DEFAULT)

    def is_blending(self) -> bool:
        return self.blending

    def is_copy_opacity(self) -> bool:
        return self.copy_opacity

    @classmethod
    def from_binary(
        cls: Type[CLT],
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> CLT:
        color_trigger = super().from_binary(binary, order, version)

        blending_bit = BLENDING_BIT
        copy_opacity_bit = COPY_OPACITY_BIT
        player_color_mask = PLAYER_COLOR_MASK

        reader = Reader(binary)

        value = reader.read_u32(order)

        blending = value & blending_bit == blending_bit
        copy_opacity = value & copy_opacity_bit == copy_opacity_bit

        player_color_value = value & player_color_mask

        if player_color_value == player_color_mask:
            player_color = PlayerColor.NOT_USED

        else:
            player_color = PlayerColor(player_color_value)

        value >>= BITS

        color = Color(value)

        duration = reader.read_f32(order)

        target_color_id = reader.read_u16(order)
        copied_color_id = reader.read_u16(order)

        copied_color_hsv = HSV.from_binary(binary, order, version)

        color_trigger.blending = blending
        color_trigger.copy_opacity = copy_opacity

        color_trigger.player_color = player_color

        color_trigger.color = color

        color_trigger.duration = duration

        color_trigger.target_color_id = target_color_id
        color_trigger.copied_color_id = copied_color_id

        color_trigger.copied_color_hsv = copied_color_hsv

        return color_trigger

    def to_binary(
        self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        player_color = self.player_color

        if player_color.is_not_used():
            value = PLAYER_COLOR_MASK

        else:
            value = player_color.value

        if self.is_blending():
            value |= BLENDING_BIT

        if self.is_copy_opacity():
            value |= COPY_OPACITY_BIT

        value |= self.color.value << BITS

        writer.write_u32(value, order)

        writer.write_f32(self.duration, order)

        writer.write_u16(self.target_color_id, order)
        writer.write_u16(self.copied_color_id, order)

        self.copied_color_hsv.to_binary(binary, order, version)


DEFAULT_OPACITY = 1.0


ALT = TypeVar("ALT", bound="AlphaTrigger")


@define()
class AlphaTrigger(HasTargetGroup, HasDuration, Trigger):
    opacity: float = DEFAULT_OPACITY

    @classmethod
    def from_binary(
        cls: Type[ALT],
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> ALT:
        alpha_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary)

        duration = reader.read_f32(order)

        target_group_id = reader.read_u16(order)

        opacity = reader.read_f32(order)

        alpha_trigger.duration = duration
        alpha_trigger.target_group_id = target_group_id
        alpha_trigger.opacity = opacity

        return alpha_trigger

    def to_binary(
        self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        writer.write_f32(self.duration, order)
        writer.write_u16(self.target_group_id, order)
        writer.write_f32(self.opacity, order)


PULSE_TARGET_TYPE_BIT = 0b00000001
PULSE_TYPE_MASK = 0b00000110
PULSE_MODE_BIT = 0b00001000
EXCLUSIVE_BIT = 0b00010000

PULSE_TYPE_SHIFT = PULSE_TARGET_TYPE_BIT.bit_length()
PULSE_MODE_SHIFT = PULSE_TYPE_MASK.bit_length()


DEFAULT_FADE_IN = 0.0
DEFAULT_HOLD = 0.0
DEFAULT_FADE_OUT = 0.0

DEFAULT_EXCLUSIVE = False


PLT = TypeVar("PLT", bound="PulseTrigger")


@define()
class PulseTrigger(Trigger):
    fade_in: float = field(default=DEFAULT_FADE_IN)
    hold: float = field(default=DEFAULT_HOLD)
    fade_out: float = field(default=DEFAULT_FADE_OUT)

    color: Color = field(factory=Color.default)
    hsv: HSV = field(factory=HSV)

    target_type: PulseTargetType = field(default=PulseTargetType.DEFAULT)
    type: PulseType = field(default=PulseType.DEFAULT)
    mode: PulseMode = field(default=PulseMode.DEFAULT)

    exclusive: bool = field(default=DEFAULT_EXCLUSIVE)

    def is_exclusive(self) -> bool:
        return self.exclusive

    @classmethod
    def from_binary(
        cls: Type[PLT],
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> PLT:
        exclusive_bit = EXCLUSIVE_BIT

        pulse_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary)

        fade_in = reader.read_f32(order)
        hold = reader.read_f32(order)
        fade_out = reader.read_f32(order)

        value = reader.read_u32(order)

        exclusive = value & exclusive_bit == exclusive_bit

        target_type_value = value & PULSE_TARGET_TYPE_BIT

        type_value = (value & PULSE_TYPE_MASK) >> PULSE_TYPE_SHIFT

        mode_value = (value & PULSE_MODE_BIT) >> PULSE_MODE_SHIFT

        target_type = PulseTargetType(target_type_value)
        type = PulseType(type_value)
        mode = PulseMode(mode_value)

        value >>= BITS

        color = Color(value)

        hsv = HSV.from_binary(binary, order, version)

        pulse_trigger.fade_in = fade_in
        pulse_trigger.hold = hold
        pulse_trigger.fade_out = fade_out

        pulse_trigger.exclusive = exclusive

        pulse_trigger.target_type = target_type
        pulse_trigger.type = type
        pulse_trigger.mode = mode

        pulse_trigger.color = color
        pulse_trigger.hsv = hsv

        return pulse_trigger

    def to_binary(
        self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        writer = Writer(binary)

        writer.write_f32(self.fade_in, order)
        writer.write_f32(self.hold, order)
        writer.write_f32(self.fade_out, order)

        value = self.target_type.value

        value |= self.type.value << PULSE_TYPE_SHIFT
        value |= self.mode.value << PULSE_MODE_SHIFT

        if self.is_exclusive():
            value |= EXCLUSIVE_BIT

        value |= self.color.value << BITS

        writer.write_u32(value, order)

        self.hsv.to_binary(binary, order, version)


TARGET_TYPE_MASK = 0b00000011
LOCKED_TO_PLAYER_X_BIT = 0b00000100
LOCKED_TO_PLAYER_Y_BIT = 0b00001000


DEFAULT_X_OFFSET = 0.0
DEFAULT_Y_OFFSET = 0.0

DEFAULT_LOCKED_TO_PLAYER_X = False
DEFAULT_LOCKED_TO_PLAYER_Y = False


MT = TypeVar("MT", bound="MoveTrigger")


@define()
class MoveTrigger(HasTargetGroup, HasEasing, HasDuration, Trigger):
    x_offset: float = DEFAULT_X_OFFSET
    y_offset: float = DEFAULT_Y_OFFSET

    locked_to_player_x: bool = DEFAULT_LOCKED_TO_PLAYER_X
    locked_to_player_y: bool = DEFAULT_LOCKED_TO_PLAYER_Y

    target_type: TargetType = TargetType.DEFAULT

    @classmethod
    def from_binary(
        cls: Type[MT],
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> MT:
        locked_to_player_x_bit = LOCKED_TO_PLAYER_X_BIT
        locked_to_player_y_bit = LOCKED_TO_PLAYER_Y_BIT

        move_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary)

        duration = reader.read_f32(order)

        easing_value = reader.read_u8(order)

        easing = Easing(easing_value)

        easing_rate = reader.read_f32(order)

        target_group_id = reader.read_u16(order)

        x_offset = reader.read_f32(order)
        y_offset = reader.read_f32(order)

        value = reader.read_u8(order)

        target_type_value = value & TARGET_TYPE_MASK
        target_type = TargetType(target_type_value)

        locked_to_player_x = value & locked_to_player_x_bit == locked_to_player_x_bit
        locked_to_player_y = value & locked_to_player_y_bit == locked_to_player_y_bit

        move_trigger.duration = duration

        move_trigger.easing = easing
        move_trigger.easing_rate = easing_rate

        move_trigger.target_group_id = target_group_id

        move_trigger.x_offset = x_offset
        move_trigger.y_offset = y_offset

        move_trigger.target_type = target_type

        move_trigger.locked_to_player_x = locked_to_player_x
        move_trigger.locked_to_player_y = locked_to_player_y

        return move_trigger

    def to_binary(
        self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        writer.write_f32(self.duration, order)

        writer.write_u8(self.easing.value, order)

        writer.write_f32(self.easing_rate, order)

        writer.write_u16(self.target_group_id, order)

        writer.write_f32(self.x_offset, order)
        writer.write_f32(self.y_offset, order)

        value = self.target_type.value

        if self.is_locked_to_player_x():
            value |= LOCKED_TO_PLAYER_X_BIT

        if self.is_locked_to_player_y():
            value |= LOCKED_TO_PLAYER_Y_BIT

        writer.write_u8(value, order)

    def is_locked_to_player_x(self) -> bool:
        return self.locked_to_player_x

    def is_locked_to_player_y(self) -> bool:
        return self.locked_to_player_y

    def lock_to_player_x(self: MT) -> MT:
        self.locked_to_player_x = True

        return self

    def lock_to_player_y(self: MT) -> MT:
        self.locked_to_player_y = True

        return self

    def unlock_from_player_x(self: MT) -> MT:
        self.locked_to_player_x = False

        return self

    def unlock_from_player_y(self: MT) -> MT:
        self.locked_to_player_y = False

        return self

    def move_offset(self: MT, x_offset: float = 0.0, y_offset: float = 0.0) -> MT:
        self.x_offset += x_offset
        self.y_offset += y_offset

        return self


EDITOR_DISABLE_BIT = 0b00000001


DEFAULT_EDITOR_DISABLE = False


SPT = TypeVar("SPT", bound="SpawnTrigger")


@define()
class SpawnTrigger(HasDelay, HasTargetGroup, Trigger):
    editor_disable: bool = DEFAULT_EDITOR_DISABLE

    @classmethod
    def from_binary(
        cls: Type[SPT],
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> SPT:
        editor_disable_bit = EDITOR_DISABLE_BIT

        spawn_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary)

        target_group_id = reader.read_u16(order)

        delay = reader.read_f32(order)

        value = reader.read_u8(order)

        editor_disable = value & editor_disable_bit == editor_disable_bit

        spawn_trigger.target_group_id = target_group_id

        spawn_trigger.delay = delay

        spawn_trigger.editor_disable = editor_disable

    def to_binary(
        self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        writer.write_u16(self.target_group_id, order)

        writer.write_f32(self.delay, order)

        value = 0

        if self.is_editor_disable():
            value |= EDITOR_DISABLE_BIT

        writer.write_u8(value, order)

    def is_editor_disable(self) -> bool:
        return self.editor_disable


ST = TypeVar("ST", bound="StopTrigger")


@define()
class StopTrigger(HasTargetGroup, Trigger):
    @classmethod
    def from_binary(
        cls: Type[ST],
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> ST:
        stop_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary)

        target_group_id = reader.read_u16(order)

        stop_trigger.target_group_id = target_group_id

        return stop_trigger

    def to_binary(
        self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        writer.write_u16(self.target_group_id, order)


TOGGLED_BIT = 0b10000000
ACTIVATE_GROUP_BIT = 0b00000001


DEFAULT_TOGGLED = False


TT = TypeVar("TT", bound="ToggleTrigger")


@define()
class ToggleTrigger(HasActivateGroup, HasTargetGroup, Trigger):
    toggled: bool = DEFAULT_TOGGLED

    @classmethod
    def from_binary(
        cls: Type[TT],
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> TT:
        toggled_bit = TOGGLED_BIT
        activate_group_bit = ACTIVATE_GROUP_BIT

        toggle_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary)

        target_group_id = reader.read_u16(order)

        value = reader.read_u8(order)

        activate_group = value & activate_group_bit == activate_group_bit

        toggled = value & toggled_bit == toggled_bit

        toggle_trigger.target_group_id = target_group_id

        toggle_trigger.activate_group = activate_group

        toggle_trigger.toggled = toggled

        return toggle_trigger

    def to_binary(
        self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        writer.write_u16(self.target_group_id, order)

        value = 0

        if self.is_activate_group():
            value |= ACTIVATE_GROUP_BIT

        if self.is_toggled():
            value |= TOGGLED_BIT

        writer.write_u8(value, order)

    def is_toggled(self) -> bool:
        return self.toggled

    def toggle(self: TT) -> TT:
        self.toggled = not self.toggled

        return self


ROTATION_LOCKED_BIT = 0b00000001


DEFAULT_TARGET_ROTATION = 0.0
DEFAULT_ROTATION_LOCKED = False


RT = TypeVar("RT", bound="RotateTrigger")


@define()
class RotateTrigger(HasEasing, HasAdditionalGroup, HasTargetGroup, HasDuration, Trigger):
    target_rotation: float = DEFAULT_TARGET_ROTATION
    rotation_locked: bool = DEFAULT_ROTATION_LOCKED

    @classmethod
    def from_binary(
        cls: Type[RT],
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> RT:
        rotation_locked_bit = ROTATION_LOCKED_BIT

        rotate_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary)

        duration = reader.read_f32(order)

        target_group_id = reader.read_u16(order)
        additional_group_id = reader.read_u16(order)

        easing_value = reader.read_u8(order)

        easing = Easing(easing_value)

        easing_rate = reader.read_f32(order)

        target_rotation = reader.read_f32(order)

        value = reader.read_u8(order)

        rotation_locked = value & rotation_locked_bit == rotation_locked_bit

        rotate_trigger.duration = duration

        rotate_trigger.target_group_id = target_group_id
        rotate_trigger.additional_group_id = additional_group_id

        rotate_trigger.easing = easing
        rotate_trigger.easing_rate = easing_rate

        rotate_trigger.target_rotation = target_rotation

        rotate_trigger.rotation_locked = rotation_locked

    def to_binary(
        self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        writer.write_f32(self.duration, order)

        writer.write_u16(self.target_group_id, order)
        writer.write_u16(self.additional_group_id, order)

        writer.write_u8(self.easing.value, order)
        writer.write_f32(self.easing_rate, order)

        writer.write_f32(self.target_rotation, order)

        value = 0

        if self.is_rotation_locked():
            value |= ROTATION_LOCKED_BIT

        writer.write_u8(value, order)

    def target_rotate(self: RT, angle: float) -> RT:
        self.target_rotation += angle

        return self

    def is_rotation_locked(self) -> bool:
        return self.rotation_locked

    def lock_rotation(self: RT) -> RT:
        self.rotation_locked = True

        return self

    def unlock_rotation(self: RT) -> RT:
        self.rotation_locked = False

        return self


DEFAULT_X_MODIFIER = 1.0
DEFAULT_Y_MODIFIER = 1.0


FT = TypeVar("FT", bound="FollowTrigger")


@define()
class FollowTrigger(HasEasing, HasAdditionalGroup, HasTargetGroup, HasDuration, Trigger):
    x_modifier: float = DEFAULT_X_MODIFIER
    y_modifier: float = DEFAULT_Y_MODIFIER

    @classmethod
    def from_binary(
        cls: Type[FT],
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> FT:
        follow_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary)

        duration = reader.read_f32(order)

        target_group_id = reader.read_u16(order)
        additional_group_id = reader.read_u16(order)

        easing_value = reader.read_u8(order)

        easing = Easing(easing_value)

        easing_rate = reader.read_f32(order)

        x_modifier = reader.read_f32(order)
        y_modifier = reader.read_f32(order)

        follow_trigger.duration = duration

        follow_trigger.target_group_id = target_group_id
        follow_trigger.additional_group_id = additional_group_id

        follow_trigger.easing = easing
        follow_trigger.easing_rate = easing_rate

        follow_trigger.x_modifier = x_modifier
        follow_trigger.y_modifier = y_modifier

        return follow_trigger

    def to_binary(
        self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        writer.write_f32(self.duration, order)

        writer.write_u16(self.target_group_id, order)
        writer.write_u16(self.additional_group_id, order)

        writer.write_u8(self.easing.value, order)
        writer.write_f32(self.easing_rate, order)

        writer.write_f32(self.x_modifier, order)
        writer.write_f32(self.y_modifier, order)


DEFAULT_STRENGTH = 0.0
DEFAULT_INTERVAL = 0.0


SHT = TypeVar("SHT", bound="ShakeTrigger")


@define()
class ShakeTrigger(HasDuration, Trigger):
    strength: float = DEFAULT_STRENGTH
    interval: float = DEFAULT_INTERVAL

    @classmethod
    def from_binary(
        cls: Type[SHT],
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> SHT:
        shake_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary)

        duration = reader.read_f32(order)
        strength = reader.read_f32(order)
        interval = reader.read_f32(order)

        shake_trigger.duration = duration
        shake_trigger.strength = strength
        shake_trigger.interval = interval

    def to_binary(
        self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        writer.write_f32(self.duration, order)
        writer.write_f32(self.strength, order)
        writer.write_f32(self.interval, order)


AT = TypeVar("AT", bound="AnimateTrigger")


@define()
class AnimateTrigger(HasTargetGroup, Trigger):
    animation_id: int = DEFAULT_ID

    @classmethod
    def from_binary(
        cls: Type[AT],
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> AT:
        animate_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary)

        target_group_id = reader.read_u16(order)

        animation_id = reader.read_u8(order)

        animate_trigger.target_group_id = target_group_id

        animate_trigger.animation_id = animation_id

        return animate_trigger

    def to_binary(
        self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        writer.write_u16(self.target_group_id, order)

        writer.write_u8(self.animation_id, order)



TOGGLE_TYPE_MASK = 0b00000011
HOLD_MODE_BIT = 0b00000100
DUAL_MODE_BIT = 0b00001000


DEFAULT_HOLD_MODE = False
DEFAULT_DUAL_MODE = False


THT = TypeVar("THT", bound="TouchTrigger")


@define()
class TouchTrigger(HasTargetGroup, Trigger):
    hold_mode: bool = DEFAULT_HOLD_MODE
    dual_mode: bool = DEFAULT_DUAL_MODE
    toggle_type: ToggleType = ToggleType.DEFAULT

    @classmethod
    def from_binary(
        cls: Type[THT],
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> THT:
        hold_mode_bit = HOLD_MODE_BIT
        dual_mode_bit = DUAL_MODE_BIT

        touch_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary)

        target_group_id = reader.read_u16(order)

        value = reader.read_u8(order)

        toggle_type_value = value & TOGGLE_TYPE_MASK

        toggle_type = ToggleType(toggle_type_value)

        hold_mode = value & hold_mode_bit == hold_mode_bit
        dual_mode = value & dual_mode_bit == dual_mode_bit

        touch_trigger.target_group_id = target_group_id

        touch_trigger.hold_mode = hold_mode
        touch_trigger.dual_mode = dual_mode

        touch_trigger.toggle_type = toggle_type

        return touch_trigger

    def to_binary(
        self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        writer.write_u16(self.target_group_id, order)

        value = self.toggle_type.value

        if self.is_hold_mode():
            value |= HOLD_MODE_BIT

        if self.is_dual_mode():
            value |= DUAL_MODE_BIT

        writer.write_u8(value, order)

    def is_hold_mode(self) -> bool:
        return self.hold_mode

    def is_dual_mode(self) -> bool:
        return self.dual_mode


CT = TypeVar("CT", bound="CountTrigger")


@define()
class CountTrigger(HasMultiActivate, HasActivateGroup, HasCount, HasItem, Trigger):
    @classmethod
    def from_binary(
        cls: Type[CT],
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> CT:
        activate_group_bit = ACTIVATE_GROUP_BIT
        multi_activate_bit = MULTI_ACTIVATE_BIT

        count_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary)

        item_id = reader.read_u16(order)

        count = reader.read_i32(order)

        value = reader.read_u8(order)

        activate_group = value & activate_group_bit == activate_group_bit
        multi_activate = value & multi_activate_bit == multi_activate_bit

        count_trigger.item_id = item_id

        count_trigger.count = count

        count_trigger.activate_group = activate_group
        count_trigger.multi_activate = multi_activate

    def to_binary(
        self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        writer.write_u16(self.item_id, order)

        writer.write_i32(self.count, order)

        value = 0

        if self.is_activate_group():
            value |= ACTIVATE_GROUP_BIT

        if self.is_multi_activate():
            value |= MULTI_ACTIVATE_BIT

        writer.write_u8(value, order)


ICT = TypeVar("ICT", bound="InstantCountTrigger")

COMPARISON_MASK = 0b00000110
COMPARISON_SHIFT = ACTIVATE_GROUP_BIT.bit_length()


@define()
class InstantCountTrigger(HasActivateGroup, HasCount, HasItem, Trigger):
    comparison: InstantCountComparison = InstantCountComparison.DEFAULT

    @classmethod
    def from_binary(
        cls: Type[ICT],
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> ICT:
        activate_group_bit = ACTIVATE_GROUP_BIT

        instant_count_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary)

        item_id = reader.read_u16(order)

        count = reader.read_i32(order)

        value = reader.read_u8(order)

        activate_group = value & activate_group_bit == activate_group_bit

        comparison_value = (value & COMPARISON_MASK) >> COMPARISON_SHIFT

        comparison = InstantCountComparison(comparison_value)

        instant_count_trigger.item_id = item_id

        instant_count_trigger.count = count

        instant_count_trigger.activate_group = activate_group

        instant_count_trigger.comparison = comparison

        return instant_count_trigger

    def to_binary(
        self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        writer.write_u16(self.item_id, order)

        writer.write_i32(self.count, order)

        value = 0

        if self.is_activate_group():
            value |= ACTIVATE_GROUP_BIT

        value |= self.comparison.value << COMPARISON_SHIFT

        writer.write_u8(value, order)


PT = TypeVar("PT", bound="PickupTrigger")


@define()
class PickupTrigger(HasCount, HasItem, Trigger):
    @classmethod
    def from_binary(
        cls: Type[PT],
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> PT:
        pickup_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary)

        item_id = reader.read_u16(order)

        count = reader.read_i32(order)

        pickup_trigger.item_id = item_id

        pickup_trigger.count = count

        return pickup_trigger

    def to_binary(
        self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        writer.write_u16(self.item_id, order)

        writer.write_i32(self.count, order)


DEFAULT_SPEED = 1.0
DEFAULT_MAX_SPEED = 0.0


FPYT = TypeVar("FPYT", bound="FollowPlayerYTrigger")


@define()
class FollowPlayerYTrigger(HasOffset, HasDelay, HasTargetGroup, Trigger):
    speed: float = DEFAULT_SPEED
    max_speed: float = DEFAULT_MAX_SPEED

    @classmethod
    def from_binary(
        cls: Type[FPYT],
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> FPYT:
        follow_player_y_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary)

        target_group_id = reader.read_u16(order)

        delay = reader.read_f32(order)

        speed = reader.read_f32(order)
        max_speed = reader.read_f32(order)
        offset = reader.read_f32(order)

        follow_player_y_trigger.target_group_id = target_group_id

        follow_player_y_trigger.delay = delay

        follow_player_y_trigger.speed = speed
        follow_player_y_trigger.max_speed = max_speed
        follow_player_y_trigger.offset = offset

        return follow_player_y_trigger

    def to_binary(
        self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        writer.write_u16(self.target_group_id, order)

        writer.write_f32(self.delay, order)

        writer.write_f32(self.speed, order)
        writer.write_f32(self.max_speed, order)
        writer.write_f32(self.offset, order)


ODT = TypeVar("ODT", bound="OnDeathTrigger")


@define()
class OnDeathTrigger(HasActivateGroup, HasTargetGroup, Trigger):
    @classmethod
    def from_binary(
        cls: Type[ODT],
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> ODT:
        activate_group_bit = ACTIVATE_GROUP_BIT

        on_death_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary)

        target_group_id = reader.read_u16(order)

        value = reader.read_u8(order)

        activate_group = value & activate_group_bit == activate_group_bit

        on_death_trigger.target_group_id = target_group_id

        on_death_trigger.activate_group = activate_group

        return on_death_trigger

    def to_binary(
        self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        writer.write_u16(self.target_group_id, order)

        value = 0

        if self.is_activate_group():
            value |= ACTIVATE_GROUP_BIT

        writer.write_u8(value, order)


TRIGGER_ON_EXIT_BIT = 0b10000000_00000000


DEFAULT_TRIGGER_ON_EXIT = False


CBT = TypeVar("CBT", bound="CollisionTrigger")


@define()
class CollisionTrigger(HasActivateGroup, HasTargetGroup, Trigger):
    block_a_id: int = DEFAULT_ID
    block_b_id: int = DEFAULT_ID

    trigger_on_exit: bool = DEFAULT_TRIGGER_ON_EXIT

    @classmethod
    def from_binary(
        cls: Type[CBT],
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> CBT:
        block_id_mask = BLOCK_ID_MASK
        trigger_on_exit_bit = TRIGGER_ON_EXIT_BIT

        collision_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary)

        value = reader.read_u16(order)

        block_a_id = value & block_id_mask

        value = reader.read_u16(order)

        block_b_id = value & block_id_mask

        trigger_on_exit = value & trigger_on_exit_bit == trigger_on_exit_bit

        collision_trigger.block_a_id = block_a_id
        collision_trigger.block_b_id = block_b_id
        collision_trigger.trigger_on_exit = trigger_on_exit

        return collision_trigger

    def to_binary(
        self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        block_id_mask = BLOCK_ID_MASK

        super().to_binary(binary, order, version)

        writer = Writer(binary)

        writer.write_u16(self.block_a_id & block_id_mask, order)

        value = self.block_b_id & block_id_mask

        if self.is_trigger_on_exit():
            value |= TRIGGER_ON_EXIT_BIT

        writer.write_u16(value, order)

    def is_trigger_on_exit(self) -> bool:
        return self.trigger_on_exit


def is_trigger(object: Object) -> TypeGuard[Trigger]:
    return object.is_trigger()


def has_target_group(object: Object) -> TypeGuard[HasTargetGroup]:
    return is_instance(object, HasTargetGroup)


def has_additional_group(object: Object) -> TypeGuard[HasAdditionalGroup]:
    return is_instance(object, HasAdditionalGroup)


class ObjectType(Enum):
    OBJECT = 1
    ANIMATED_OBJECT = 2
    ORB = 3
    COIN = 4
    TEXT = 5
    TELEPORT = 6
    ITEM_COUNTER = 7
    PICKUP_ITEM = 8
    COLLISION_BLOCK = 9
    COLOR_TRIGGER = 10
    PULSE_TRIGGER = 11
    ALPHA_TRIGGER = 12
    MOVE_TRIGGER = 13
    SPAWN_TRIGGER = 14
    STOP_TRIGGER = 15
    TOGGLE_TRIGGER = 16
    ROTATE_TRIGGER = 17
    FOLLOW_TRIGGER = 18
    SHAKE_TRIGGER = 19
    ANIMATE_TRIGGER = 20
    TOUCH_TRIGGER = 21
    COUNT_TRIGGER = 22
    INSTANT_COUNT_TRIGGER = 23
    PICKUP_TRIGGER = 24
    FOLLOW_PLAYER_Y_TRIGGER = 25
    ON_DEATH_TRIGGER = 26
    COLLISION_TRIGGER = 27


OBJECT_TYPE_TO_TYPE = {
    ObjectType.OBJECT: Object,
    ObjectType.ANIMATED_OBJECT: AnimatedObject,
    ObjectType.ORB: Orb,
    ObjectType.COIN: Coin,
    ObjectType.TEXT: Text,
    ObjectType.TELEPORT: Teleport,
    ObjectType.ITEM_COUNTER: ItemCounter,
    ObjectType.PICKUP_ITEM: PickupItem,
    ObjectType.COLLISION_BLOCK: CollisionBlock,
    ObjectType.COLOR_TRIGGER: ColorTrigger,
    ObjectType.PULSE_TRIGGER: PulseTrigger,
    ObjectType.ALPHA_TRIGGER: AlphaTrigger,
    ObjectType.MOVE_TRIGGER: MoveTrigger,
    ObjectType.SPAWN_TRIGGER: SpawnTrigger,
    ObjectType.STOP_TRIGGER: StopTrigger,
    ObjectType.TOGGLE_TRIGGER: ToggleTrigger,
    ObjectType.ROTATE_TRIGGER: RotateTrigger,
    ObjectType.FOLLOW_TRIGGER: FollowTrigger,
    ObjectType.SHAKE_TRIGGER: ShakeTrigger,
    ObjectType.ANIMATE_TRIGGER: AnimateTrigger,
    ObjectType.TOUCH_TRIGGER: TouchTrigger,
    ObjectType.COUNT_TRIGGER: CountTrigger,
    ObjectType.INSTANT_COUNT_TRIGGER: InstantCountTrigger,
    ObjectType.PICKUP_TRIGGER: PickupTrigger,
    ObjectType.FOLLOW_PLAYER_Y_TRIGGER: FollowPlayerYTrigger,
    ObjectType.ON_DEATH_TRIGGER: OnDeathTrigger,
    ObjectType.COLLISION_TRIGGER: CollisionTrigger,
}

TYPE_TO_OBJECT_TYPE = {type: object_type for object_type, type in OBJECT_TYPE_TO_TYPE.items()}


def object_from_binary(
    binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
) -> Object:
    reader = Reader(binary)

    object_type_value = reader.read_u8(order)
    object_type = ObjectType(object_type_value)

    return OBJECT_TYPE_TO_TYPE[object_type].from_binary(binary, order, version)


def object_from_bytes(
    data: bytes, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
) -> Object:
    return object_from_binary(BytesIO(data), order, version)


def object_to_binary(
    object: Object, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
) -> None:
    object_type = TYPE_TO_OBJECT_TYPE[type(object)]

    writer = Writer(binary)

    writer.write_u8(object_type.value, order)

    object.to_binary(binary, order, version)


def object_to_bytes(
    object: Object, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
) -> bytes:
    binary = BytesIO()

    object_to_binary(object, binary, order, version)

    binary.seek(0)

    return binary.read()


OBJECT_ID_NOT_PRESENT = "object id is not present"


def object_from_robtop(string: str) -> Object:  # TODO: extend this function
    mapping = split_object(string)

    object_id_string = mapping.get(ID)

    if object_id_string is None:
        raise ValueError(OBJECT_ID_NOT_PRESENT)

    object_id = int(object_id_string)

    if object_id == TEXT_ID:
        return Text.from_robtop_mapping(mapping)

    return Object.from_robtop_mapping(mapping)


def object_to_robtop(object: Object) -> str:
    return object.to_robtop()
