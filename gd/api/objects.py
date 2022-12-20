from io import BytesIO
from typing import Dict, Iterable, Mapping, Type, TypeVar

from attrs import define, field
from typing_extensions import Literal, TypeGuard

from gd.api.hsv import HSV
from gd.api.ordered_set import OrderedSet
from gd.binary import VERSION, Binary, BinaryReader, BinaryWriter
from gd.binary_constants import BITS, BYTE
from gd.binary_utils import Reader, Writer
from gd.color import Color
from gd.constants import DEFAULT_ENCODING, DEFAULT_ERRORS, DEFAULT_ID, EMPTY
from gd.encoding import decode_base64_string_url_safe, encode_base64_string_url_safe
from gd.enum_extensions import Enum, Flag
from gd.enums import (
    ByteOrder,
    CoinType,
    Easing,
    InstantCountComparison,
    MiscType,
    OrbType,
    PickupItemMode,
    PickupItemType,
    PlayerColor,
    PortalType,
    PulsatingObjectType,
    PulseMode,
    PulseTargetType,
    PulseType,
    RotatingObjectType,
    SimpleTargetType,
    SimpleZLayer,
    SpeedChangeType,
    TargetType,
    ToggleType,
    TriggerType,
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

__all__ = (
    "Groups",
    "Object",
    "PulsatingObject",
    "RotatingObject",
    "Orb",
    "TriggerOrb",
    "ItemCounter",
    "SecretCoin",
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

GRID_UNITS = 30.0


H_FLIPPED_BIT = 0b00000001
V_FLIPPED_BIT = 0b00000010
DO_NOT_FADE_BIT = 0b00000100
DO_NOT_ENTER_BIT = 0b00001000
GROUP_PARENT_BIT = 0b00010000
HIGH_DETAIL_BIT = 0b00100000
DISABLE_GLOW_BIT = 0b01000000
SPECIAL_CHECKED_BIT = 0b10000000


class ObjectFlag(Flag):
    SIMPLE = 0

    HAS_ROTATION_AND_SCALE = 1 << 0
    HAS_EDITOR_LAYER = 1 << 1
    HAS_COLORS = 1 << 2
    HAS_GROUPS = 1 << 3
    HAS_LINK = 1 << 4
    HAS_Z = 1 << 5

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
LEGACY_COLOR_ID = 19
BASE_COLOR_ID = 21
DETAIL_COLOR_ID = 22
BASE_COLOR_HSV_MODIFIED = 41
DETAIL_COLOR_HSV_MODIFIED = 42
BASE_COLOR_HSV = 43
DETAIL_COLOR_HSV = 44
SINGLE_GROUP_ID = 33
GROUPS = 57
GROUP_PARENT = 34
HIGH_DETAIL = 103
DISABLE_GLOW = 96
SPECIAL_CHECKED = 13
LINK_ID = 108

OBJECT_STRING = "Object (ID: {object.id}) at ({object.x}, {object.y})"

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

    base_color_id: int = field(default=DEFAULT_ID)
    detail_color_id: int = field(default=DEFAULT_ID)

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
        cls: Type[O],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
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
            z_layer_value = reader.read_u8(order)

            z_order = reader.read_i16(order)

            z_layer = ZLayer(z_layer_value)

        else:
            z_layer = ZLayer.DEFAULT
            z_order = DEFAULT_Z_ORDER

        if flag.has_editor_layer():
            base_editor_layer = reader.read_u16(order)
            additional_editor_layer = reader.read_u16(order)

        else:
            base_editor_layer = DEFAULT_BASE_EDITOR_LAYER
            additional_editor_layer = DEFAULT_ADDITIONAL_EDITOR_LAYER

        if flag.has_colors():
            base_color_id = reader.read_u16(order)
            detail_color_id = reader.read_u16(order)

            base_color_hsv = HSV.from_binary(binary, order, version)
            detail_color_hsv = HSV.from_binary(binary, order, version)

        else:
            base_color_id = DEFAULT_ID
            detail_color_id = DEFAULT_ID

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
            link_id = DEFAULT_ID

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
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
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

        if self.has_do_not_fade():
            value |= DO_NOT_FADE_BIT

        if self.has_do_not_enter():
            value |= DO_NOT_ENTER_BIT

        if self.is_group_parent():
            value |= GROUP_PARENT_BIT

        if self.is_high_detail():
            value |= HIGH_DETAIL_BIT

        if self.has_disable_glow():
            value |= DISABLE_GLOW_BIT

        if self.is_special_checked():
            value |= SPECIAL_CHECKED_BIT

        writer.write_u8(value, order)

        if flag.has_rotation_and_scale():
            writer.write_f32(self.rotation, order)
            writer.write_f32(self.scale, order)

        if flag.has_z():
            writer.write_u8(self.z_layer.value, order)

            writer.write_i16(self.z_order, order)

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
        id_option = mapping.get(ID)

        if id_option is None:
            raise ValueError(OBJECT_ID_NOT_PRESENT)

        id = int(id_option)

        x = parse_get_or(float, DEFAULT_X, mapping.get(X))
        y = parse_get_or(float, DEFAULT_Y, mapping.get(Y))

        rotation = parse_get_or(float, DEFAULT_ROTATION, mapping.get(ROTATION))

        scale = parse_get_or(float, DEFAULT_SCALE, mapping.get(SCALE))

        h_flipped = parse_get_or(int_bool, DEFAULT_H_FLIPPED, mapping.get(H_FLIPPED))
        v_flipped = parse_get_or(int_bool, DEFAULT_V_FLIPPED, mapping.get(V_FLIPPED))

        do_not_fade = parse_get_or(int_bool, DEFAULT_DO_NOT_FADE, mapping.get(DO_NOT_FADE))
        do_not_enter = parse_get_or(int_bool, DEFAULT_DO_NOT_ENTER, mapping.get(DO_NOT_ENTER))

        z_layer = parse_get_or(
            partial_parse_enum(int, SimpleZLayer), SimpleZLayer.DEFAULT, mapping.get(Z_LAYER)
        ).into_z_layer()
        z_order = parse_get_or(int, DEFAULT_Z_ORDER, mapping.get(Z_ORDER))

        base_editor_layer = parse_get_or(
            int, DEFAULT_BASE_EDITOR_LAYER, mapping.get(BASE_EDITOR_LAYER)
        )
        additional_editor_layer = parse_get_or(
            int, DEFAULT_ADDITIONAL_EDITOR_LAYER, mapping.get(ADDITIONAL_EDITOR_LAYER)
        )

        legacy_color_id = parse_get_or(int, DEFAULT_ID, mapping.get(LEGACY_COLOR_ID))

        if legacy_color_id:
            base_color_id = legacy_color_id
            detail_color_id = legacy_color_id

        else:
            base_color_id = parse_get_or(int, DEFAULT_ID, mapping.get(BASE_COLOR_ID))
            detail_color_id = parse_get_or(int, DEFAULT_ID, mapping.get(DETAIL_COLOR_ID))

        base_color_hsv = parse_get_or(HSV.from_robtop, HSV(), mapping.get(BASE_COLOR_HSV))
        detail_color_hsv = parse_get_or(HSV.from_robtop, HSV(), mapping.get(DETAIL_COLOR_HSV))

        single_group_id = parse_get_or(int, DEFAULT_ID, mapping.get(SINGLE_GROUP_ID))

        groups = parse_get_or(Groups.from_robtop, Groups(), mapping.get(GROUPS))

        if single_group_id:
            groups.append(single_group_id)

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

        h_flipped = self.is_h_flipped()

        if h_flipped:
            mapping[H_FLIPPED] = str(int(h_flipped))

        v_flipped = self.is_v_flipped()

        if v_flipped:
            mapping[V_FLIPPED] = str(int(v_flipped))

        do_not_fade = self.has_do_not_fade()

        if do_not_fade:
            mapping[DO_NOT_FADE] = str(int(do_not_fade))

        do_not_enter = self.has_do_not_enter()

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

        base_color_hsv_modified = not base_color_hsv.is_default()

        if base_color_hsv_modified:
            mapping[BASE_COLOR_HSV] = base_color_hsv.to_robtop()
            mapping[BASE_COLOR_HSV_MODIFIED] = str(int(base_color_hsv_modified))

        detail_color_hsv = self.detail_color_hsv

        detail_color_hsv_modified = not detail_color_hsv.is_default()

        if detail_color_hsv_modified:
            mapping[DETAIL_COLOR_HSV] = detail_color_hsv.to_robtop()
            mapping[DETAIL_COLOR_HSV_MODIFIED] = str(int(detail_color_hsv_modified))

        groups = self.groups

        if groups:
            mapping[GROUPS] = groups.to_robtop()

        group_parent = self.is_group_parent()

        if group_parent:
            mapping[GROUP_PARENT] = str(int(group_parent))

        high_detail = self.is_high_detail()

        if high_detail:
            mapping[HIGH_DETAIL] = str(int(high_detail))

        disable_glow = self.has_disable_glow()

        if disable_glow:
            mapping[DISABLE_GLOW] = str(int(disable_glow))

        special_checked = self.is_special_checked()

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

    def has_do_not_fade(self) -> bool:
        return self.do_not_fade

    def has_do_not_enter(self) -> bool:
        return self.do_not_enter

    def is_group_parent(self) -> bool:
        return self.group_parent

    def is_high_detail(self) -> bool:
        return self.high_detail

    def has_disable_glow(self) -> bool:
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

    def __str__(self) -> str:
        return OBJECT_STRING.format(object=self)


PORTAL_IDS = {portal.id for portal in PortalType}
SPEED_CHANGE_IDS = {speed_change.id for speed_change in SpeedChangeType}


COIN_ID = 12


SC = TypeVar("SC", bound="SecretCoin")


@define()
class SecretCoin(Object):
    coin_id: int = DEFAULT_ID

    @classmethod
    def from_binary(
        cls: Type[SC],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> SC:
        coin = super().from_binary(binary, order, version)

        reader = Reader(binary)

        coin_id = reader.read_u8(order)

        coin.coin_id = coin_id

        return coin

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        writer.write_u8(self.coin_id, order)

    @classmethod
    def from_robtop_mapping(cls: Type[SC], mapping: Mapping[int, str]) -> SC:
        coin = super().from_robtop_mapping(mapping)

        coin_id = parse_get_or(int, DEFAULT_ID, mapping.get(COIN_ID))

        coin.coin_id = coin_id

        return coin

    def to_robtop_mapping(self) -> Dict[int, str]:
        mapping = super().to_robtop_mapping()

        mapping[COIN_ID] = str(self.coin_id)

        return mapping


ROTATION_SPEED = 97
DISABLE_ROTATION = 98


DISABLE_ROTATION_BIT = 0b00000001


DEFAULT_ROTATION_SPEED = 0.0
DEFAULT_DISABLE_ROTATION = False


RO = TypeVar("RO", bound="RotatingObject")


@define()
class RotatingObject(Object):
    rotation_speed: float = DEFAULT_ROTATION_SPEED
    disable_rotation: bool = DEFAULT_DISABLE_ROTATION

    @classmethod
    def from_binary(
        cls: Type[RO],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> RO:
        rotating_object = super().from_binary(binary, order, version)

        disable_rotation_bit = DISABLE_ROTATION_BIT

        reader = Reader(binary)

        rotation_speed = reader.read_f32(order)

        value = reader.read_u8(order)

        disable_rotation = value & disable_rotation_bit == disable_rotation_bit

        rotating_object.rotation_speed = rotation_speed
        rotating_object.disable_rotation = disable_rotation

        return rotating_object

    def to_binary(
        self,
        binary: BinaryWriter,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        writer.write_f32(self.rotation_speed, order)

        value = 0

        if self.is_disable_rotation():
            value |= DISABLE_ROTATION_BIT

        writer.write_u8(value, order)

    def is_disable_rotation(self) -> bool:
        return self.disable_rotation

    @classmethod
    def from_robtop_mapping(cls: Type[RO], mapping: Mapping[int, str]) -> RO:
        rotating_object = super().from_robtop_mapping(mapping)

        rotation_speed = parse_get_or(float, DEFAULT_ROTATION_SPEED, mapping.get(ROTATION_SPEED))

        disable_rotation = parse_get_or(
            bool, DEFAULT_DISABLE_ROTATION, mapping.get(DISABLE_ROTATION)
        )

        rotating_object.rotation_speed = rotation_speed
        rotating_object.disable_rotation = disable_rotation

        return rotating_object

    def to_robtop_mapping(self) -> Dict[int, str]:
        mapping = super().to_robtop_mapping()

        rotation_speed = self.rotation_speed

        if self.rotation_speed:
            mapping[ROTATION_SPEED] = float_str(rotation_speed)

        disable_rotation = self.is_disable_rotation()

        if disable_rotation:
            mapping[DISABLE_ROTATION] = str(int(disable_rotation))

        return mapping


CONTENT = 31


S = TypeVar("S", bound="Text")


@define()
class Text(Object):
    content: str = EMPTY

    @classmethod
    def from_binary(
        cls: Type[S],
        binary: BinaryReader,
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
        binary: BinaryWriter,
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


SMOOTH_BIT = 0b00000001


DEFAULT_SMOOTH = False
DEFAULT_PORTAL_OFFSET = 100.0


PORTAL_OFFSET = 54
SMOOTH = 55


P = TypeVar("P", bound="Teleport")


@define()
class Teleport(Object):
    portal_offset: float = DEFAULT_PORTAL_OFFSET
    smooth: bool = DEFAULT_SMOOTH

    @classmethod
    def from_binary(
        cls: Type[P],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> P:
        smooth_bit = SMOOTH_BIT

        teleport = super().from_binary(binary, order, version)

        reader = Reader(binary)

        portal_offset = reader.read_f32(order)

        value = reader.read_u8(order)

        smooth = value & smooth_bit == smooth_bit

        teleport.portal_offset = portal_offset
        teleport.smooth = smooth

        return teleport

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        writer.write_f32(self.portal_offset, order)

        value = 0

        if self.is_smooth():
            value |= SMOOTH_BIT

        writer.write_u8(value, order)

    @classmethod
    def from_robtop_mapping(cls: Type[P], mapping: Mapping[int, str]) -> P:
        teleport = super().from_robtop_mapping(mapping)

        portal_offset = parse_get_or(float, DEFAULT_PORTAL_OFFSET, mapping.get(PORTAL_OFFSET))

        smooth = parse_get_or(int_bool, DEFAULT_SMOOTH, mapping.get(SMOOTH))

        teleport.portal_offset = portal_offset
        teleport.smooth = smooth

        return teleport

    def to_robtop_mapping(self) -> Dict[int, str]:
        mapping = super().to_robtop_mapping()

        mapping[PORTAL_OFFSET] = float_str(self.portal_offset)

        smooth = self.smooth

        if smooth:
            mapping[SMOOTH] = str(int(smooth))

        return mapping

    def is_smooth(self) -> bool:
        return self.smooth


DEFAULT_RANDOMIZE_START = False
DEFAULT_ANIMATION_SPEED = 1.0

RANDOMIZE_START_BIT = 0b00000001

RANDOMIZE_START = 106
ANIMATION_SPEED = 107

PO = TypeVar("PO", bound="PulsatingObject")


@define()
class PulsatingObject(Object):
    randomize_start: bool = DEFAULT_RANDOMIZE_START
    animation_speed: float = DEFAULT_ANIMATION_SPEED

    @classmethod
    def from_binary(
        cls: Type[PO],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> PO:
        randomize_start_bit = RANDOMIZE_START_BIT

        pulsating_object = super().from_binary(binary, order, version)

        reader = Reader(binary)

        animation_speed = reader.read_f32(order)

        value = reader.read_u8(order)

        randomize_start = value & randomize_start_bit == randomize_start_bit

        pulsating_object.randomize_start = randomize_start

        pulsating_object.animation_speed = animation_speed

        return pulsating_object

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        writer.write_f32(self.animation_speed, order)

        value = 0

        if self.is_randomize_start():
            value |= RANDOMIZE_START_BIT

        writer.write_u8(value, order)

    @classmethod
    def from_robtop_mapping(cls: Type[PO], mapping: Mapping[int, str]) -> PO:
        pulsating_object = super().from_robtop_mapping(mapping)

        randomize_start = parse_get_or(
            int_bool, DEFAULT_RANDOMIZE_START, mapping.get(RANDOMIZE_START)
        )

        animation_speed = parse_get_or(float, DEFAULT_ANIMATION_SPEED, mapping.get(ANIMATION_SPEED))

        pulsating_object.randomize_start = randomize_start
        pulsating_object.animation_speed = animation_speed

        return pulsating_object

    def to_robtop_mapping(self) -> Dict[int, str]:
        mapping = super().to_robtop_mapping()

        mapping[ANIMATION_SPEED] = str(self.animation_speed)

        randomize_start = self.is_randomize_start()

        if randomize_start:
            mapping[RANDOMIZE_START] = str(int(randomize_start))

        return mapping

    def is_randomize_start(self) -> bool:
        return self.randomize_start


DYNAMIC_BIT = 0b10000000_00000000
BLOCK_ID_MASK = 0b01111111_11111111


DEFAULT_DYNAMIC = False


BLOCK_ID = 80
DYNAMIC = 94

CB = TypeVar("CB", bound="CollisionBlock")


@define()
class CollisionBlock(Object):
    block_id: int = DEFAULT_ID
    dynamic: bool = DEFAULT_DYNAMIC

    @classmethod
    def from_binary(
        cls: Type[CB],
        binary: BinaryReader,
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
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        value = self.block_id & BLOCK_ID_MASK

        if self.is_dynamic():
            value |= DYNAMIC_BIT

        writer.write_u16(value, order)

    @classmethod
    def from_robtop_mapping(cls: Type[CB], mapping: Mapping[int, str]) -> CB:
        collision_block = super().from_robtop_mapping(mapping)

        block_id = parse_get_or(int, DEFAULT_ID, mapping.get(BLOCK_ID))

        dynamic = parse_get_or(int_bool, DEFAULT_DYNAMIC, mapping.get(DYNAMIC))

        collision_block.block_id = block_id
        collision_block.dynamic = dynamic

        return collision_block

    def to_robtop_mapping(self) -> Dict[int, str]:
        mapping = super().to_robtop_mapping()

        mapping[BLOCK_ID] = str(self.block_id)

        dynamic = self.is_dynamic()

        if dynamic:
            mapping[DYNAMIC] = str(int(dynamic))

        return mapping

    def is_dynamic(self) -> bool:
        return self.dynamic


ITEM_ID = 80


@define(slots=False)
class HasItem:
    item_id: int = DEFAULT_ID


COUNT = 77


DEFAULT_COUNT = 0


@define(slots=False)
class HasCount:
    count: int = DEFAULT_COUNT


TARGET_GROUP_ID = 51


@define(slots=False)
class HasTargetGroup:
    target_group_id: int = DEFAULT_ID

    def has_target_group(self) -> bool:
        return True


TARGET_COLOR_ID = 23


@define(slots=False)
class HasTargetColor:
    target_color_id: int = DEFAULT_ID


ADDITIONAL_GROUP_ID = 71


@define(slots=False)
class HasAdditionalGroup:
    additional_group_id: int = DEFAULT_ID

    def has_additional_group(self) -> bool:
        return True


ACTIVATE_GROUP = 56


DEFAULT_ACTIVATE_GROUP = False


@define(slots=False)
class HasActivateGroup:
    activate_group: bool = DEFAULT_ACTIVATE_GROUP

    def is_activate_group(self) -> bool:
        return self.activate_group


DURATION = 10


DEFAULT_DURATION = 0.0


@define(slots=False)
class HasDuration:
    duration: float = DEFAULT_DURATION


SPAWN_DELAY = 63
FOLLOW_DELAY = 91


DEFAULT_DELAY = 0.0


@define(slots=False)
class HasDelay:
    delay: float = DEFAULT_DELAY


EASING = 30
EASING_RATE = 85


DEFAULT_EASING_RATE = 2.0


@define(slots=False)
class HasEasing:
    easing: Easing = Easing.DEFAULT
    easing_rate: float = DEFAULT_EASING_RATE


ORB_MULTI_ACTIVATE = 99
TRIGGER_MULTI_ACTIVATE = 104


DEFAULT_MULTI_ACTIVATE = False


@define(slots=False)
class HasMultiActivate:
    multi_activate: bool = DEFAULT_MULTI_ACTIVATE

    def is_multi_activate(self) -> bool:
        return self.multi_activate


OPACITY = 35


DEFAULT_OPACITY = 1.0


@define(slots=False)
class HasOpacity:
    opacity: float = DEFAULT_OPACITY


RED = 7
GREEN = 8
BLUE = 9

DEFAULT_RED = BYTE
DEFAULT_GREEN = BYTE
DEFAULT_BLUE = BYTE


@define(slots=False)
class HasColor:
    color: Color = field(factory=Color.default)


MULTI_ACTIVATE_BIT = 0b00000010


OP = TypeVar("OP", bound="Orb")


@define()
class Orb(HasMultiActivate, Object):  # type: ignore
    @classmethod
    def from_binary(
        cls: Type[OP],
        binary: BinaryReader,
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
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        value = 0

        if self.is_multi_activate():
            value |= MULTI_ACTIVATE_BIT

        writer.write_u8(value, order)

    @classmethod
    def from_robtop_mapping(cls: Type[OP], mapping: Mapping[int, str]) -> OP:
        orb = super().from_robtop_mapping(mapping)

        multi_activate = parse_get_or(
            int_bool, DEFAULT_MULTI_ACTIVATE, mapping.get(ORB_MULTI_ACTIVATE)
        )

        orb.multi_activate = multi_activate

        return orb

    def to_robtop_mapping(self) -> Dict[int, str]:
        mapping = super().to_robtop_mapping()

        multi_activate = self.is_multi_activate()

        if multi_activate:
            mapping[ORB_MULTI_ACTIVATE] = str(int(multi_activate))

        return mapping


TO = TypeVar("TO", bound="TriggerOrb")


@define()
class TriggerOrb(HasTargetGroup, HasActivateGroup, Orb):
    @classmethod
    def from_binary(
        cls: Type[TO],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> TO:
        activate_group_bit = ACTIVATE_GROUP_BIT
        multi_activate_bit = MULTI_ACTIVATE_BIT

        trigger_orb = super().from_binary(binary, order, version)

        reader = Reader(binary)

        value = reader.read_u8(order)

        activate_group = value & activate_group_bit == activate_group_bit
        multi_activate = value & multi_activate_bit == multi_activate_bit

        target_group_id = reader.read_u16(order)

        trigger_orb.activate_group = activate_group
        trigger_orb.multi_activate = multi_activate

        trigger_orb.target_group_id = target_group_id

        return trigger_orb

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        value = 0

        if self.is_activate_group():
            value |= ACTIVATE_GROUP_BIT

        if self.is_multi_activate():
            value |= MULTI_ACTIVATE_BIT

        writer.write_u8(value, order)

        writer.write_u16(self.target_group_id, order)

    @classmethod
    def from_robtop_mapping(cls: Type[TO], mapping: Mapping[int, str]) -> TO:
        trigger_orb = super().from_robtop_mapping(mapping)

        activate_group = parse_get_or(int_bool, DEFAULT_ACTIVATE_GROUP, mapping.get(ACTIVATE_GROUP))

        target_group_id = parse_get_or(int, DEFAULT_ID, mapping.get(TARGET_GROUP_ID))

        trigger_orb.activate_group = activate_group

        trigger_orb.target_group_id = target_group_id

        return trigger_orb

    def to_robtop_mapping(self) -> Dict[int, str]:
        mapping = super().to_robtop_mapping()

        activate_group = self.is_activate_group()

        if activate_group:
            mapping[ACTIVATE_GROUP] = str(int(activate_group))

        mapping[TARGET_GROUP_ID] = str(self.target_group_id)

        return mapping


IC = TypeVar("IC", bound="ItemCounter")


@define()
class ItemCounter(HasItem, Object):  # type: ignore
    @classmethod
    def from_binary(
        cls: Type[IC],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> IC:
        item_counter = super().from_binary(binary, order, version)

        reader = Reader(binary)

        item_id = reader.read_u16(order)

        item_counter.item_id = item_id

        return item_counter

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        writer.write_u16(self.item_id, order)

    @classmethod
    def from_robtop_mapping(cls: Type[IC], mapping: Mapping[int, str]) -> IC:
        item_counter = super().from_robtop_mapping(mapping)

        item_id = parse_get_or(int, DEFAULT_ID, mapping.get(ITEM_ID))

        item_counter.item_id = item_id

        return item_counter

    def to_robtop_mapping(self) -> Dict[int, str]:
        mapping = super().to_robtop_mapping()

        item_id = self.item_id

        if item_id:
            mapping[ITEM_ID] = str(item_id)

        return mapping


SUBTRACT_COUNT = 78
PICKUP_MODE = 79

SUBTRACT_COUNT_BIT = 0b10000000
PICKUP_MODE_MASK = 0b00000011


PI = TypeVar("PI", bound="PickupItem")


DEFAULT_SUBTRACT_COUNT = False


@define()
class PickupItem(HasTargetGroup, HasItem, Object):  # type: ignore
    subtract_count: bool = DEFAULT_SUBTRACT_COUNT
    mode: PickupItemMode = PickupItemMode.DEFAULT

    @classmethod
    def from_binary(
        cls: Type[PI],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> PI:
        pickup_mode_mask = PICKUP_MODE_MASK
        subtract_count_bit = SUBTRACT_COUNT_BIT

        pickup_item = super().from_binary(binary, order, version)

        reader = Reader(binary)

        value = reader.read_u8(order)

        mode_value = value & pickup_mode_mask

        mode = PickupItemMode(mode_value)

        if mode.is_toggle_trigger():
            target_group_id = reader.read_u16(order)
            item_id = DEFAULT_ID

        else:
            target_group_id = DEFAULT_ID
            item_id = reader.read_u16(order)

        subtract_count = value & subtract_count_bit == subtract_count_bit

        pickup_item.target_group_id = target_group_id

        pickup_item.subtract_count = subtract_count

        pickup_item.item_id = item_id

        pickup_item.mode = mode

        return pickup_item

    def is_subtract_count(self) -> bool:
        return self.subtract_count

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        mode = self.mode

        value = mode.value

        if self.is_subtract_count():
            value |= SUBTRACT_COUNT_BIT

        writer.write_u8(value, order)

        if mode.is_toggle_trigger():
            writer.write_u16(self.target_group_id, order)

        else:
            writer.write_u16(self.item_id, order)

    def to_robtop_mapping(self) -> Dict[int, str]:
        mapping = super().to_robtop_mapping()

        mode = self.mode

        if mode.is_toggle_trigger():
            mapping[TARGET_GROUP_ID] = str(self.target_group_id)

        else:
            subtract_count = self.subtract_count

            if subtract_count:
                mapping[SUBTRACT_COUNT] = str(int(subtract_count))

            mapping[ITEM_ID] = str(self.item_id)

        mapping[PICKUP_MODE] = str(mode.value)

        return mapping


TOUCH_TRIGGERED = 11
SPAWN_TRIGGERED = 62
MULTI_TRIGGER = 87


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
        cls: Type[T],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
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
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
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

    @classmethod
    def from_robtop_mapping(cls: Type[T], mapping: Mapping[int, str]) -> T:
        trigger = super().from_robtop_mapping(mapping)

        touch_triggered = parse_get_or(
            int_bool, DEFAULT_TOUCH_TRIGGERED, mapping.get(TOUCH_TRIGGERED)
        )
        spawn_triggered = parse_get_or(
            int_bool, DEFAULT_SPAWN_TRIGGERED, mapping.get(SPAWN_TRIGGERED)
        )
        multi_trigger = parse_get_or(int_bool, DEFAULT_MULTI_TRIGGER, mapping.get(MULTI_TRIGGER))

        trigger.touch_triggered = touch_triggered
        trigger.spawn_triggered = spawn_triggered
        trigger.multi_trigger = multi_trigger

        return trigger

    def to_robtop_mapping(self) -> Dict[int, str]:
        mapping = super().to_robtop_mapping()

        touch_triggered = self.is_touch_triggered()

        if touch_triggered:
            mapping[TOUCH_TRIGGERED] = str(int(touch_triggered))

        spawn_triggered = self.is_spawn_triggered()

        if spawn_triggered:
            mapping[SPAWN_TRIGGERED] = str(int(spawn_triggered))

        multi_trigger = self.is_multi_trigger()

        if touch_triggered:
            mapping[MULTI_TRIGGER] = str(int(multi_trigger))

        return mapping


BLENDING = 17
COPIED_COLOR_ID = 50
COPIED_COLOR_HSV = 49
COPY_OPACITY = 60
PLAYER_COLOR_1 = 15
PLAYER_COLOR_2 = 16

PLAYER_COLOR_MASK = 0b00000011
BLENDING_BIT = 0b00000100
COPY_OPACITY_BIT = 0b00001000


DEFAULT_BLENDING = False
DEFAULT_COPY_OPACITY = False
DEFAULT_PLAYER_COLOR_1 = False
DEFAULT_PLAYER_COLOR_2 = False


CLT = TypeVar("CLT", bound="ColorTrigger")


@define()
class ColorTrigger(HasTargetColor, HasColor, HasDuration, HasOpacity, Trigger):  # type: ignore
    blending: bool = field(default=DEFAULT_BLENDING)

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
        binary: BinaryReader,
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

        opacity = reader.read_f32(order)

        color_trigger.blending = blending
        color_trigger.copy_opacity = copy_opacity

        color_trigger.player_color = player_color

        color_trigger.color = color

        color_trigger.duration = duration

        color_trigger.target_color_id = target_color_id
        color_trigger.copied_color_id = copied_color_id

        color_trigger.copied_color_hsv = copied_color_hsv

        color_trigger.opacity = opacity

        return color_trigger

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        value = self.player_color.value

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

        writer.write_f32(self.opacity, order)

    @classmethod
    def from_robtop_mapping(cls: Type[CLT], mapping: Mapping[int, str]) -> CLT:
        color_trigger = super().from_robtop_mapping(mapping)

        blending = parse_get_or(int_bool, DEFAULT_BLENDING, mapping.get(BLENDING))

        copy_opacity = parse_get_or(int_bool, DEFAULT_COPY_OPACITY, mapping.get(COPY_OPACITY))

        player_color_1 = parse_get_or(int_bool, DEFAULT_PLAYER_COLOR_1, mapping.get(PLAYER_COLOR_1))
        player_color_2 = parse_get_or(int_bool, DEFAULT_PLAYER_COLOR_2, mapping.get(PLAYER_COLOR_2))

        if player_color_1 and player_color_2:
            player_color = PlayerColor.DEFAULT

        else:
            if player_color_1:
                player_color = PlayerColor.COLOR_1

            elif player_color_2:
                player_color = PlayerColor.COLOR_2

            else:
                player_color = PlayerColor.NOT_USED

        red, green, blue = (
            parse_get_or(int, DEFAULT_RED, mapping.get(RED)),
            parse_get_or(int, DEFAULT_GREEN, mapping.get(GREEN)),
            parse_get_or(int, DEFAULT_BLUE, mapping.get(BLUE)),
        )

        color = Color.from_rgb(red, green, blue)

        duration = parse_get_or(float, DEFAULT_DURATION, mapping.get(DURATION))

        target_color_id = parse_get_or(int, DEFAULT_ID, mapping.get(TARGET_COLOR_ID))
        copied_color_id = parse_get_or(int, DEFAULT_ID, mapping.get(COPIED_COLOR_ID))

        copied_color_hsv = parse_get_or(HSV.from_robtop, HSV(), mapping.get(COPIED_COLOR_HSV))

        opacity = parse_get_or(float, DEFAULT_OPACITY, mapping.get(OPACITY))

        color_trigger.blending = blending
        color_trigger.copy_opacity = copy_opacity

        color_trigger.player_color = player_color

        color_trigger.color = color

        color_trigger.duration = duration

        color_trigger.target_color_id = target_color_id
        color_trigger.copied_color_id = copied_color_id

        color_trigger.copied_color_hsv = copied_color_hsv

        color_trigger.opacity = opacity

        return color_trigger

    def to_robtop_mapping(self) -> Dict[int, str]:
        mapping = super().to_robtop_mapping()

        blending = self.is_blending()

        if blending:
            mapping[BLENDING] = str(int(blending))

        copy_opacity = self.is_copy_opacity()

        if copy_opacity:
            mapping[COPY_OPACITY] = str(int(copy_opacity))

        player_color = self.player_color

        player_color_1 = player_color.is_color_1()
        player_color_2 = player_color.is_color_2()

        if player_color_1:
            mapping[PLAYER_COLOR_1] = str(int(player_color_1))

        if player_color_2:
            mapping[PLAYER_COLOR_2] = str(int(player_color_2))

        red, green, blue = self.color.to_rgb()

        mapping[RED] = str(red)
        mapping[GREEN] = str(green)
        mapping[BLUE] = str(blue)

        mapping[DURATION] = float_str(self.duration)

        mapping[TARGET_COLOR_ID] = str(self.target_color_id)

        copied_color_id = self.copied_color_id

        if copied_color_id:
            mapping[COPIED_COLOR_ID] = str(self.copied_color_id)

        copied_color_hsv = self.copied_color_hsv

        if not copied_color_hsv.is_default():
            mapping[COPIED_COLOR_HSV] = copied_color_hsv.to_robtop()

        mapping[OPACITY] = float_str(self.opacity)

        return mapping


ALT = TypeVar("ALT", bound="AlphaTrigger")


@define()
class AlphaTrigger(HasTargetGroup, HasDuration, HasOpacity, Trigger):  # type: ignore
    @classmethod
    def from_binary(
        cls: Type[ALT],
        binary: BinaryReader,
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
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        writer.write_f32(self.duration, order)
        writer.write_u16(self.target_group_id, order)
        writer.write_f32(self.opacity, order)

    @classmethod
    def from_robtop_mapping(cls: Type[ALT], mapping: Mapping[int, str]) -> ALT:
        alpha_trigger = super().from_robtop_mapping(mapping)

        duration = parse_get_or(float, DEFAULT_DURATION, mapping.get(DURATION))

        target_group_id = parse_get_or(int, DEFAULT_ID, mapping.get(TARGET_GROUP_ID))

        opacity = parse_get_or(float, DEFAULT_OPACITY, mapping.get(OPACITY))

        alpha_trigger.duration = duration
        alpha_trigger.target_group_id = target_group_id
        alpha_trigger.opacity = opacity

        return alpha_trigger

    def to_robtop_mapping(self) -> Dict[int, str]:
        mapping = super().to_robtop_mapping()

        mapping[DURATION] = float_str(self.duration)

        mapping[TARGET_GROUP_ID] = str(self.target_group_id)

        mapping[OPACITY] = float_str(self.opacity)

        return mapping


FADE_IN = 45
HOLD = 46
FADE_OUT = 47
EXCLUSIVE = 86
PULSE_MODE = 48
PULSE_TARGET_TYPE = 52
MAIN_ONLY = 65
DETAIL_ONLY = 66


PULSE_TARGET_TYPE_BIT = 0b00000001
PULSE_TYPE_MASK = 0b00000110
PULSE_MODE_BIT = 0b00001000
EXCLUSIVE_BIT = 0b00010000

PULSE_TYPE_SHIFT = PULSE_TARGET_TYPE_BIT.bit_length()
PULSE_MODE_SHIFT = PULSE_TYPE_MASK.bit_length()


DEFAULT_FADE_IN = 0.0
DEFAULT_HOLD = 0.0
DEFAULT_FADE_OUT = 0.0

DEFAULT_MAIN_ONLY = False
DEFAULT_DETAIL_ONLY = False

DEFAULT_EXCLUSIVE = False


PLT = TypeVar("PLT", bound="PulseTrigger")


@define()
class PulseTrigger(HasTargetColor, HasTargetGroup, HasColor, Trigger):  # type: ignore
    fade_in: float = field(default=DEFAULT_FADE_IN)
    hold: float = field(default=DEFAULT_HOLD)
    fade_out: float = field(default=DEFAULT_FADE_OUT)

    color_id: int = field(default=DEFAULT_ID)
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
        binary: BinaryReader,
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

        if mode.is_hsv():
            color_id = reader.read_u16(order)
            hsv = HSV.from_binary(binary, order, version)

        else:
            color_id = DEFAULT_ID
            hsv = HSV()

        if target_type.is_color_channel():
            target_color_id = reader.read_u16(order)
            target_group_id = DEFAULT_ID

        else:
            target_color_id = DEFAULT_ID
            target_group_id = reader.read_u16(order)

        pulse_trigger.fade_in = fade_in
        pulse_trigger.hold = hold
        pulse_trigger.fade_out = fade_out

        pulse_trigger.target_color_id = target_color_id
        pulse_trigger.target_group_id = target_group_id

        pulse_trigger.exclusive = exclusive

        pulse_trigger.target_type = target_type
        pulse_trigger.type = type
        pulse_trigger.mode = mode

        pulse_trigger.color = color
        pulse_trigger.color_id = color_id
        pulse_trigger.hsv = hsv

        return pulse_trigger

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        writer.write_f32(self.fade_in, order)
        writer.write_f32(self.hold, order)
        writer.write_f32(self.fade_out, order)

        target_type = self.target_type

        value = target_type.value

        mode = self.mode

        value |= self.type.value << PULSE_TYPE_SHIFT
        value |= mode.value << PULSE_MODE_SHIFT

        if self.is_exclusive():
            value |= EXCLUSIVE_BIT

        value |= self.color.value << BITS

        writer.write_u32(value, order)

        if mode.is_hsv():
            writer.write_u16(self.color_id, order)
            self.hsv.to_binary(binary, order, version)

        if target_type.is_color_channel():
            writer.write_u16(self.target_color_id, order)

        else:
            writer.write_u16(self.target_group_id, order)

    @classmethod
    def from_robtop_mapping(cls: Type[PLT], mapping: Mapping[int, str]) -> PLT:
        pulse_trigger = super().from_robtop_mapping(mapping)

        fade_in = parse_get_or(float, DEFAULT_FADE_IN, mapping.get(FADE_IN))
        hold = parse_get_or(float, DEFAULT_HOLD, mapping.get(HOLD))
        fade_out = parse_get_or(float, DEFAULT_FADE_OUT, mapping.get(FADE_OUT))

        exclusive = parse_get_or(int_bool, DEFAULT_EXCLUSIVE, mapping.get(EXCLUSIVE))

        target_type = parse_get_or(
            partial_parse_enum(int, PulseTargetType),
            PulseTargetType.DEFAULT,
            mapping.get(PULSE_TARGET_TYPE),
        )

        if target_type.is_color_channel():
            target_color_id = parse_get_or(int, DEFAULT_ID, mapping.get(TARGET_GROUP_ID))  # why
            target_group_id = DEFAULT_ID

        else:
            target_color_id = DEFAULT_ID
            target_group_id = parse_get_or(int, DEFAULT_ID, mapping.get(TARGET_GROUP_ID))

        mode = parse_get_or(
            partial_parse_enum(int, PulseMode), PulseMode.DEFAULT, mapping.get(PULSE_MODE)
        )

        if mode.is_color():
            red, green, blue = (
                parse_get_or(int, DEFAULT_RED, mapping.get(RED)),
                parse_get_or(int, DEFAULT_GREEN, mapping.get(GREEN)),
                parse_get_or(int, DEFAULT_BLUE, mapping.get(BLUE)),
            )

            color = Color.from_rgb(red, green, blue)

            color_id = DEFAULT_ID
            hsv = HSV()

        else:
            color = Color.default()

            color_id = parse_get_or(int, DEFAULT_ID, mapping.get(COPIED_COLOR_ID))
            hsv = parse_get_or(HSV.from_robtop, HSV(), mapping.get(COPIED_COLOR_HSV))

        main_only = parse_get_or(int_bool, DEFAULT_MAIN_ONLY, mapping.get(MAIN_ONLY))
        detail_only = parse_get_or(int_bool, DEFAULT_DETAIL_ONLY, mapping.get(DETAIL_ONLY))

        if main_only ^ detail_only:
            if main_only:
                type = PulseType.MAIN

            if detail_only:
                type = PulseType.DETAIL

        else:
            type = PulseType.BOTH

        pulse_trigger.fade_in = fade_in
        pulse_trigger.hold = hold
        pulse_trigger.fade_out = fade_out

        pulse_trigger.target_color_id = target_color_id
        pulse_trigger.target_group_id = target_group_id

        pulse_trigger.exclusive = exclusive

        pulse_trigger.target_type = target_type
        pulse_trigger.mode = mode
        pulse_trigger.type = type

        pulse_trigger.color = color
        pulse_trigger.color_id = color_id
        pulse_trigger.hsv = hsv

        return pulse_trigger

    def to_robtop_mapping(self) -> Dict[int, str]:
        mapping = super().to_robtop_mapping()

        fade_in = self.fade_in

        if fade_in:
            mapping[FADE_IN] = float_str(fade_in)

        hold = self.hold

        if hold:
            mapping[HOLD] = float_str(hold)

        fade_out = self.fade_out

        if fade_out:
            mapping[FADE_OUT] = float_str(fade_out)

        exclusive = self.is_exclusive()

        if exclusive:
            mapping[EXCLUSIVE] = str(int(exclusive))

        target_type = self.target_type

        if target_type.is_color_channel():
            mapping[TARGET_GROUP_ID] = str(self.target_color_id)  # why

        else:
            mapping[TARGET_GROUP_ID] = str(self.target_group_id)

        mapping[PULSE_TARGET_TYPE] = str(target_type.value)

        mode = self.mode

        if mode.is_color():
            red, green, blue = self.color.to_rgb()

            mapping[RED] = str(red)
            mapping[GREEN] = str(green)
            mapping[BLUE] = str(blue)

        else:
            mapping[COPIED_COLOR_ID] = str(self.color_id)
            mapping[COPIED_COLOR_HSV] = self.hsv.to_robtop()

        mapping[PULSE_MODE] = str(mode.value)

        type = self.type

        main_only = type.is_main_only()
        detail_only = type.is_detail_only()

        if main_only:
            mapping[MAIN_ONLY] = str(int(main_only))

        if detail_only:
            mapping[DETAIL_ONLY] = str(int(detail_only))

        return mapping


X_OFFSET = 28
Y_OFFSET = 29
LOCKED_TO_PLAYER_X = 58
LOCKED_TO_PLAYER_Y = 59
USE_TARGET = 100
TARGET_TYPE = 101

TARGET_TYPE_MASK = 0b00000011
LOCKED_TO_PLAYER_X_BIT = 0b00000100
LOCKED_TO_PLAYER_Y_BIT = 0b00001000


DEFAULT_X_OFFSET = 0.0
DEFAULT_Y_OFFSET = 0.0

DEFAULT_LOCKED_TO_PLAYER_X = False
DEFAULT_LOCKED_TO_PLAYER_Y = False


MT = TypeVar("MT", bound="MoveTrigger")


@define()
class MoveTrigger(HasAdditionalGroup, HasTargetGroup, HasEasing, HasDuration, Trigger):  # type: ignore
    x_offset: float = DEFAULT_X_OFFSET
    y_offset: float = DEFAULT_Y_OFFSET

    locked_to_player_x: bool = DEFAULT_LOCKED_TO_PLAYER_X
    locked_to_player_y: bool = DEFAULT_LOCKED_TO_PLAYER_Y

    target_type: TargetType = TargetType.DEFAULT

    @classmethod
    def from_binary(
        cls: Type[MT],
        binary: BinaryReader,
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

        value = reader.read_u8(order)

        target_type_value = value & TARGET_TYPE_MASK
        target_type = TargetType(target_type_value)

        locked_to_player_x = value & locked_to_player_x_bit == locked_to_player_x_bit
        locked_to_player_y = value & locked_to_player_y_bit == locked_to_player_y_bit

        if target_type.is_none():
            x_offset = reader.read_f32(order)
            y_offset = reader.read_f32(order)

            additional_group_id = DEFAULT_ID

        else:
            x_offset = DEFAULT_X_OFFSET
            y_offset = DEFAULT_Y_OFFSET

            additional_group_id = reader.read_u16(order)

        move_trigger.duration = duration

        move_trigger.easing = easing
        move_trigger.easing_rate = easing_rate

        move_trigger.target_group_id = target_group_id

        move_trigger.x_offset = x_offset
        move_trigger.y_offset = y_offset

        move_trigger.target_type = target_type

        move_trigger.locked_to_player_x = locked_to_player_x
        move_trigger.locked_to_player_y = locked_to_player_y

        move_trigger.additional_group_id = additional_group_id

        return move_trigger

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        writer.write_f32(self.duration, order)

        writer.write_u8(self.easing.value, order)

        writer.write_f32(self.easing_rate, order)

        writer.write_u16(self.target_group_id, order)

        target_type = self.target_type

        value = target_type.value

        if self.is_locked_to_player_x():
            value |= LOCKED_TO_PLAYER_X_BIT

        if self.is_locked_to_player_y():
            value |= LOCKED_TO_PLAYER_Y_BIT

        writer.write_u8(value, order)

        if target_type.is_none():
            writer.write_f32(self.x_offset, order)
            writer.write_f32(self.y_offset, order)

        else:
            writer.write_u16(self.additional_group_id, order)

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

    @classmethod
    def from_robtop_mapping(cls: Type[MT], mapping: Mapping[int, str]) -> MT:
        move_trigger = super().from_robtop_mapping(mapping)

        duration = parse_get_or(float, DEFAULT_DURATION, mapping.get(DURATION))

        easing = parse_get_or(partial_parse_enum(int, Easing), Easing.DEFAULT, mapping.get(EASING))
        easing_rate = parse_get_or(float, DEFAULT_EASING_RATE, mapping.get(EASING_RATE))

        target_group_id = parse_get_or(int, DEFAULT_ID, mapping.get(TARGET_GROUP_ID))

        target_type_option = mapping.get(TARGET_TYPE)

        if target_type_option is None:
            target_type = TargetType.NONE

        else:
            target_type = SimpleTargetType(int(target_type_option)).into_target_type()

        if target_type.is_none():
            locked_to_player_x = parse_get_or(
                int_bool, DEFAULT_LOCKED_TO_PLAYER_X, mapping.get(LOCKED_TO_PLAYER_X)
            )
            locked_to_player_y = parse_get_or(
                int_bool, DEFAULT_LOCKED_TO_PLAYER_Y, mapping.get(LOCKED_TO_PLAYER_Y)
            )

            x_offset = parse_get_or(float, DEFAULT_X_OFFSET, mapping.get(X_OFFSET))
            y_offset = parse_get_or(float, DEFAULT_Y_OFFSET, mapping.get(Y_OFFSET))

            additional_group_id = DEFAULT_ID

        else:
            locked_to_player_x = DEFAULT_LOCKED_TO_PLAYER_X
            locked_to_player_y = DEFAULT_LOCKED_TO_PLAYER_Y

            x_offset = DEFAULT_X_OFFSET
            y_offset = DEFAULT_Y_OFFSET

            additional_group_id = parse_get_or(int, DEFAULT_ID, mapping.get(ADDITIONAL_GROUP_ID))

        move_trigger.duration = duration

        move_trigger.easing = easing
        move_trigger.easing_rate = easing_rate

        move_trigger.target_group_id = target_group_id

        move_trigger.target_type = target_type

        move_trigger.locked_to_player_x = locked_to_player_x
        move_trigger.locked_to_player_y = locked_to_player_y

        move_trigger.x_offset = x_offset
        move_trigger.y_offset = y_offset

        move_trigger.additional_group_id = additional_group_id

        return move_trigger

    def to_robtop_mapping(self) -> Dict[int, str]:
        mapping = super().to_robtop_mapping()

        mapping[DURATION] = float_str(self.duration)

        mapping[EASING] = str(self.easing.value)

        mapping[EASING_RATE] = float_str(self.easing_rate)

        mapping[TARGET_GROUP_ID] = str(self.target_group_id)

        target_type = self.target_type

        if target_type.is_none():
            mapping[LOCKED_TO_PLAYER_X] = str(int(self.is_locked_to_player_x()))
            mapping[LOCKED_TO_PLAYER_Y] = str(int(self.is_locked_to_player_y()))

            mapping[X_OFFSET] = float_str(self.x_offset)
            mapping[Y_OFFSET] = float_str(self.y_offset)

        else:
            mapping[TARGET_TYPE] = str(target_type.into_simple_target_type().value)

            mapping[ADDITIONAL_GROUP_ID] = str(self.additional_group_id)

        return mapping


EDITOR_DISABLE = 102


EDITOR_DISABLE_BIT = 0b00000001

DEFAULT_EDITOR_DISABLE = False


SPT = TypeVar("SPT", bound="SpawnTrigger")


@define()
class SpawnTrigger(HasDelay, HasTargetGroup, Trigger):  # type: ignore
    editor_disable: bool = DEFAULT_EDITOR_DISABLE

    @classmethod
    def from_binary(
        cls: Type[SPT],
        binary: BinaryReader,
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

        return spawn_trigger

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
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

    @classmethod
    def from_robtop_mapping(cls: Type[SPT], mapping: Mapping[int, str]) -> SPT:
        spawn_trigger = super().from_robtop_mapping(mapping)

        target_group_id = parse_get_or(int, DEFAULT_ID, mapping.get(TARGET_GROUP_ID))

        delay = parse_get_or(float, DEFAULT_DELAY, mapping.get(SPAWN_DELAY))

        editor_disable = parse_get_or(int_bool, DEFAULT_EDITOR_DISABLE, mapping.get(EDITOR_DISABLE))

        spawn_trigger.target_group_id = target_group_id

        spawn_trigger.delay = delay

        spawn_trigger.editor_disable = editor_disable

        return spawn_trigger

    def to_robtop_mapping(self) -> Dict[int, str]:
        mapping = super().to_robtop_mapping()

        mapping[TARGET_GROUP_ID] = str(self.target_group_id)

        mapping[SPAWN_DELAY] = float_str(self.delay)

        editor_disable = self.is_editor_disable()

        if editor_disable:
            mapping[EDITOR_DISABLE] = str(int(editor_disable))

        return mapping


ST = TypeVar("ST", bound="StopTrigger")


@define()
class StopTrigger(HasTargetGroup, Trigger):  # type: ignore
    @classmethod
    def from_binary(
        cls: Type[ST],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> ST:
        stop_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary)

        target_group_id = reader.read_u16(order)

        stop_trigger.target_group_id = target_group_id

        return stop_trigger

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        writer.write_u16(self.target_group_id, order)

    @classmethod
    def from_robtop_mapping(cls: Type[ST], mapping: Mapping[int, str]) -> ST:
        stop_trigger = super().from_robtop_mapping(mapping)

        target_group_id = parse_get_or(int, DEFAULT_ID, mapping.get(TARGET_GROUP_ID))

        stop_trigger.target_group_id = target_group_id

        return stop_trigger

    def to_robtop_mapping(self) -> Dict[int, str]:
        mapping = super().to_robtop_mapping()

        mapping[TARGET_GROUP_ID] = str(self.target_group_id)

        return mapping


ACTIVATE_GROUP_BIT = 0b00000001


DEFAULT_TOGGLED = False


TT = TypeVar("TT", bound="ToggleTrigger")


@define()
class ToggleTrigger(HasActivateGroup, HasTargetGroup, Trigger):  # type: ignore
    @classmethod
    def from_binary(
        cls: Type[TT],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> TT:
        activate_group_bit = ACTIVATE_GROUP_BIT

        toggle_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary)

        target_group_id = reader.read_u16(order)

        value = reader.read_u8(order)

        activate_group = value & activate_group_bit == activate_group_bit

        toggle_trigger.target_group_id = target_group_id

        toggle_trigger.activate_group = activate_group

        return toggle_trigger

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        writer.write_u16(self.target_group_id, order)

        value = 0

        if self.is_activate_group():
            value |= ACTIVATE_GROUP_BIT

        writer.write_u8(value, order)

    def toggle(self: TT) -> TT:
        self.activate_group = not self.activate_group

        return self

    @classmethod
    def from_robtop_mapping(cls: Type[TT], mapping: Mapping[int, str]) -> TT:
        toggle_trigger = super().from_robtop_mapping(mapping)

        target_group_id = parse_get_or(int, DEFAULT_ID, mapping.get(TARGET_GROUP_ID))

        activate_group = parse_get_or(int_bool, DEFAULT_ACTIVATE_GROUP, mapping.get(ACTIVATE_GROUP))

        toggle_trigger.target_group_id = target_group_id

        toggle_trigger.activate_group = activate_group

        return toggle_trigger

    def to_robtop_mapping(self) -> Dict[int, str]:
        mapping = super().to_robtop_mapping()

        mapping[TARGET_GROUP_ID] = str(self.target_group_id)

        activate_group = self.is_activate_group()

        if activate_group:
            mapping[ACTIVATE_GROUP] = str(int(activate_group))

        return mapping


DEGREES = 68
ROTATIONS = 69
ROTATION_LOCKED = 70


FULL_ROTATION = 360.0

ROTATION_LOCKED_BIT = 0b00000001


DEFAULT_ROTATIONS = 0.0
DEFAULT_DEGREES = 0.0


DEFAULT_TARGET_ROTATION = 0.0
DEFAULT_ROTATION_LOCKED = False


RT = TypeVar("RT", bound="RotateTrigger")


@define()
class RotateTrigger(  # type: ignore
    HasEasing, HasAdditionalGroup, HasTargetGroup, HasDuration, Trigger
):
    target_rotation: float = DEFAULT_TARGET_ROTATION
    rotation_locked: bool = DEFAULT_ROTATION_LOCKED

    @classmethod
    def from_binary(
        cls: Type[RT],
        binary: BinaryReader,
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

        return rotate_trigger

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
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

    @classmethod
    def from_robtop_mapping(cls: Type[RT], mapping: Mapping[int, str]) -> RT:
        rotate_trigger = super().from_robtop_mapping(mapping)

        duration = parse_get_or(float, DEFAULT_DURATION, mapping.get(DURATION))

        target_group_id = parse_get_or(int, DEFAULT_ID, mapping.get(TARGET_GROUP_ID))
        additional_group_id = parse_get_or(int, DEFAULT_ID, mapping.get(ADDITIONAL_GROUP_ID))

        easing = parse_get_or(partial_parse_enum(int, Easing), Easing.DEFAULT, mapping.get(EASING))
        easing_rate = parse_get_or(float, DEFAULT_EASING_RATE, mapping.get(EASING_RATE))

        rotations = parse_get_or(float, DEFAULT_ROTATIONS, mapping.get(ROTATIONS))

        degrees = parse_get_or(float, DEFAULT_DEGREES, mapping.get(DEGREES))

        target_rotation = rotations * FULL_ROTATION + degrees

        rotation_locked = parse_get_or(int_bool, DEFAULT_ROTATION_LOCKED, mapping.get(ROTATION_LOCKED))

        rotate_trigger.duration = duration

        rotate_trigger.target_group_id = target_group_id
        rotate_trigger.additional_group_id = additional_group_id

        rotate_trigger.easing = easing
        rotate_trigger.easing_rate = easing_rate

        rotate_trigger.target_rotation = target_rotation

        rotate_trigger.rotation_locked = rotation_locked

        return rotate_trigger

    def to_robtop_mapping(self) -> Dict[int, str]:
        mapping = super().to_robtop_mapping()

        mapping[DURATION] = float_str(self.duration)

        mapping[TARGET_GROUP_ID] = str(self.target_group_id)
        mapping[ADDITIONAL_GROUP_ID] = str(self.additional_group_id)

        mapping[EASING] = str(self.easing.value)
        mapping[EASING_RATE] = float_str(self.easing_rate)

        rotations, degrees = divmod(self.target_rotation, FULL_ROTATION)

        mapping[ROTATIONS] = str(rotations)
        mapping[DEGREES] = str(degrees)

        rotation_locked = self.is_rotation_locked()

        if rotation_locked:
            mapping[ROTATION_LOCKED] = str(int(rotation_locked))

        return mapping


X_MODIFIER = 72
Y_MODIFIER = 73


DEFAULT_X_MODIFIER = 1.0
DEFAULT_Y_MODIFIER = 1.0


FT = TypeVar("FT", bound="FollowTrigger")


@define()
class FollowTrigger(HasEasing, HasAdditionalGroup, HasTargetGroup, HasDuration, Trigger):  # type: ignore
    x_modifier: float = DEFAULT_X_MODIFIER
    y_modifier: float = DEFAULT_Y_MODIFIER

    @classmethod
    def from_binary(
        cls: Type[FT],
        binary: BinaryReader,
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
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
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

    @classmethod
    def from_robtop_mapping(cls: Type[FT], mapping: Mapping[int, str]) -> FT:
        follow_trigger = super().from_robtop_mapping(mapping)

        duration = parse_get_or(float, DEFAULT_DURATION, mapping.get(DURATION))

        target_group_id = parse_get_or(int, DEFAULT_ID, mapping.get(TARGET_GROUP_ID))
        additional_group_id = parse_get_or(int, DEFAULT_ID, mapping.get(ADDITIONAL_GROUP_ID))

        easing = parse_get_or(partial_parse_enum(int, Easing), Easing.DEFAULT, mapping.get(EASING))
        easing_rate = parse_get_or(float, DEFAULT_EASING_RATE, mapping.get(EASING_RATE))

        x_modifier = parse_get_or(float, DEFAULT_X_MODIFIER, mapping.get(X_MODIFIER))
        y_modifier = parse_get_or(float, DEFAULT_Y_MODIFIER, mapping.get(Y_MODIFIER))

        follow_trigger.duration = duration

        follow_trigger.target_group_id = target_group_id
        follow_trigger.additional_group_id = additional_group_id

        follow_trigger.easing = easing
        follow_trigger.easing_rate = easing_rate

        follow_trigger.x_modifier = x_modifier
        follow_trigger.y_modifier = y_modifier

        return follow_trigger

    def to_robtop_mapping(self) -> Dict[int, str]:
        mapping = super().to_robtop_mapping()

        mapping[DURATION] = float_str(self.duration)

        mapping[TARGET_GROUP_ID] = str(self.target_group_id)
        mapping[ADDITIONAL_GROUP_ID] = str(self.additional_group_id)

        mapping[EASING] = str(self.easing.value)
        mapping[EASING_RATE] = float_str(self.easing_rate)

        mapping[X_MODIFIER] = float_str(self.x_modifier)
        mapping[Y_MODIFIER] = float_str(self.y_modifier)

        return mapping


STRENGTH = 75
INTERVAL = 84


DEFAULT_STRENGTH = 0.0
DEFAULT_INTERVAL = 0.0


SHT = TypeVar("SHT", bound="ShakeTrigger")


@define()
class ShakeTrigger(HasDuration, Trigger):  # type: ignore
    strength: float = DEFAULT_STRENGTH
    interval: float = DEFAULT_INTERVAL

    @classmethod
    def from_binary(
        cls: Type[SHT],
        binary: BinaryReader,
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

        return shake_trigger

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        writer.write_f32(self.duration, order)
        writer.write_f32(self.strength, order)
        writer.write_f32(self.interval, order)

    @classmethod
    def from_robtop_mapping(cls: Type[SHT], mapping: Mapping[int, str]) -> SHT:
        shake_trigger = super().from_robtop_mapping(mapping)

        duration = parse_get_or(float, DEFAULT_DURATION, mapping.get(DURATION))
        strength = parse_get_or(float, DEFAULT_STRENGTH, mapping.get(STRENGTH))
        interval = parse_get_or(float, DEFAULT_INTERVAL, mapping.get(INTERVAL))

        shake_trigger.duration = duration
        shake_trigger.strength = strength
        shake_trigger.interval = interval

        return shake_trigger

    def to_robtop_mapping(self) -> Dict[int, str]:
        mapping = super().to_robtop_mapping()

        mapping[DURATION] = float_str(self.duration)
        mapping[STRENGTH] = float_str(self.strength)
        mapping[INTERVAL] = float_str(self.interval)

        return mapping


ANIMATION_ID = 76


AT = TypeVar("AT", bound="AnimateTrigger")


@define()
class AnimateTrigger(HasTargetGroup, Trigger):  # type: ignore
    animation_id: int = DEFAULT_ID

    @classmethod
    def from_binary(
        cls: Type[AT],
        binary: BinaryReader,
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
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        writer.write_u16(self.target_group_id, order)

        writer.write_u8(self.animation_id, order)

    @classmethod
    def from_robtop_mapping(cls: Type[AT], mapping: Mapping[int, str]) -> AT:
        animate_trigger = super().from_robtop_mapping(mapping)

        target_group_id = parse_get_or(int, DEFAULT_ID, mapping.get(TARGET_GROUP_ID))

        animation_id = parse_get_or(int, DEFAULT_ID, mapping.get(ANIMATION_ID))

        animate_trigger.target_group_id = target_group_id

        animate_trigger.animation_id = animation_id

        return animate_trigger

    def to_robtop_mapping(self) -> Dict[int, str]:
        mapping = super().to_robtop_mapping()

        mapping[TARGET_GROUP_ID] = str(self.target_group_id)

        mapping[ANIMATION_ID] = str(self.animation_id)

        return mapping


HOLD_MODE = 81
TOGGLE_TYPE = 82
DUAL_MODE = 89

TOGGLE_TYPE_MASK = 0b00000011
HOLD_MODE_BIT = 0b00000100
DUAL_MODE_BIT = 0b00001000


DEFAULT_HOLD_MODE = False
DEFAULT_DUAL_MODE = False


THT = TypeVar("THT", bound="TouchTrigger")


@define()
class TouchTrigger(HasTargetGroup, Trigger):  # type: ignore
    hold_mode: bool = DEFAULT_HOLD_MODE
    dual_mode: bool = DEFAULT_DUAL_MODE
    toggle_type: ToggleType = ToggleType.DEFAULT

    @classmethod
    def from_binary(
        cls: Type[THT],
        binary: BinaryReader,
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
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
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

    @classmethod
    def from_robtop_mapping(cls: Type[THT], mapping: Mapping[int, str]) -> THT:
        touch_trigger = super().from_robtop_mapping(mapping)

        target_group_id = parse_get_or(int, DEFAULT_ID, mapping.get(TARGET_GROUP_ID))

        hold_mode = parse_get_or(int_bool, DEFAULT_HOLD_MODE, mapping.get(HOLD_MODE))
        dual_mode = parse_get_or(int_bool, DEFAULT_DUAL_MODE, mapping.get(DUAL_MODE))

        toggle_type = parse_get_or(
            partial_parse_enum(int, ToggleType), ToggleType.DEFAULT, mapping.get(TOGGLE_TYPE)
        )

        touch_trigger.target_group_id = target_group_id

        touch_trigger.hold_mode = hold_mode
        touch_trigger.dual_mode = dual_mode

        touch_trigger.toggle_type = toggle_type

        return touch_trigger

    def to_robtop_mapping(self) -> Dict[int, str]:
        mapping = super().to_robtop_mapping()

        mapping[TARGET_GROUP_ID] = str(self.target_group_id)

        hold_mode = self.is_hold_mode()

        if hold_mode:
            mapping[HOLD_MODE] = str(int(hold_mode))

        dual_mode = self.is_dual_mode()

        if dual_mode:
            mapping[DUAL_MODE] = str(int(dual_mode))

        mapping[TOGGLE_TYPE] = str(self.toggle_type.value)

        return mapping


CT = TypeVar("CT", bound="CountTrigger")


@define()
class CountTrigger(HasMultiActivate, HasActivateGroup, HasCount, HasItem, Trigger):  # type: ignore
    @classmethod
    def from_binary(
        cls: Type[CT],
        binary: BinaryReader,
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

        return count_trigger

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
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

    @classmethod
    def from_robtop_mapping(cls: Type[CT], mapping: Mapping[int, str]) -> CT:
        count_trigger = super().from_robtop_mapping(mapping)

        item_id = parse_get_or(int, DEFAULT_ID, mapping.get(ITEM_ID))

        count = parse_get_or(int, DEFAULT_COUNT, mapping.get(COUNT))

        activate_group = parse_get_or(int_bool, DEFAULT_ACTIVATE_GROUP, mapping.get(ACTIVATE_GROUP))
        multi_activate = parse_get_or(
            int_bool, DEFAULT_MULTI_ACTIVATE, mapping.get(TRIGGER_MULTI_ACTIVATE)
        )

        count_trigger.item_id = item_id

        count_trigger.count = count

        count_trigger.activate_group = activate_group
        count_trigger.multi_activate = multi_activate

        return count_trigger

    def to_robtop_mapping(self) -> Dict[int, str]:
        mapping = super().to_robtop_mapping()

        mapping[ITEM_ID] = str(self.item_id)

        count = self.count

        if count < 0:
            mapping[SUBTRACT_COUNT] = str(-count)

        else:
            mapping[COUNT] = str(count)

        activate_group = self.is_activate_group()

        if activate_group:
            mapping[ACTIVATE_GROUP] = str(int(activate_group))

        multi_activate = self.is_multi_activate()

        if multi_activate:
            mapping[TRIGGER_MULTI_ACTIVATE] = str(int(multi_activate))

        return mapping


COMPARISON = 88


ICT = TypeVar("ICT", bound="InstantCountTrigger")

COMPARISON_MASK = 0b00000110
COMPARISON_SHIFT = ACTIVATE_GROUP_BIT.bit_length()


@define()
class InstantCountTrigger(HasActivateGroup, HasCount, HasItem, Trigger):  # type: ignore
    comparison: InstantCountComparison = InstantCountComparison.DEFAULT

    @classmethod
    def from_binary(
        cls: Type[ICT],
        binary: BinaryReader,
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
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
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

    @classmethod
    def from_robtop_mapping(cls: Type[ICT], mapping: Mapping[int, str]) -> ICT:
        instant_count_trigger = super().from_robtop_mapping(mapping)

        item_id = parse_get_or(int, DEFAULT_ID, mapping.get(ITEM_ID))

        count = parse_get_or(int, DEFAULT_COUNT, mapping.get(COUNT))

        activate_group = parse_get_or(int_bool, DEFAULT_ACTIVATE_GROUP, mapping.get(ACTIVATE_GROUP))

        comparison = parse_get_or(
            partial_parse_enum(int, InstantCountComparison),
            InstantCountComparison.DEFAULT,
            mapping.get(COMPARISON),
        )

        instant_count_trigger.item_id = item_id

        instant_count_trigger.count = count

        instant_count_trigger.activate_group = activate_group

        instant_count_trigger.comparison = comparison

        return instant_count_trigger

    def to_robtop_mapping(self) -> Dict[int, str]:
        mapping = super().to_robtop_mapping()

        mapping[ITEM_ID] = str(self.item_id)

        mapping[COUNT] = str(self.count)

        activate_group = self.is_activate_group()

        if activate_group:
            mapping[ACTIVATE_GROUP] = str(int(activate_group))

        mapping[COMPARISON] = str(self.comparison.value)

        return mapping


PT = TypeVar("PT", bound="PickupTrigger")


@define()
class PickupTrigger(HasCount, HasItem, Trigger):  # type: ignore
    @classmethod
    def from_binary(
        cls: Type[PT],
        binary: BinaryReader,
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
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        writer.write_u16(self.item_id, order)

        writer.write_i32(self.count, order)

    @classmethod
    def from_robtop_mapping(cls: Type[PT], mapping: Mapping[int, str]) -> PT:
        pickup_trigger = super().from_robtop_mapping(mapping)

        item_id = parse_get_or(int, DEFAULT_ID, mapping.get(ITEM_ID))

        count = parse_get_or(int, DEFAULT_COUNT, mapping.get(COUNT))

        pickup_trigger.item_id = item_id

        pickup_trigger.count = count

        return pickup_trigger

    def to_robtop_mapping(self) -> Dict[int, str]:
        mapping = super().to_robtop_mapping()

        mapping[ITEM_ID] = str(self.item_id)

        mapping[COUNT] = str(self.count)

        return mapping


OFFSET = 92
MAX_SPEED = 105
SPEED = 90

DEFAULT_SPEED = 1.0
DEFAULT_MAX_SPEED = 0.0
DEFAULT_OFFSET = 0.0


FPYT = TypeVar("FPYT", bound="FollowPlayerYTrigger")


@define()
class FollowPlayerYTrigger(HasDelay, HasTargetGroup, Trigger):  # type: ignore
    speed: float = DEFAULT_SPEED
    max_speed: float = DEFAULT_MAX_SPEED
    offset: float = DEFAULT_OFFSET

    @classmethod
    def from_binary(
        cls: Type[FPYT],
        binary: BinaryReader,
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
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        writer.write_u16(self.target_group_id, order)

        writer.write_f32(self.delay, order)

        writer.write_f32(self.speed, order)
        writer.write_f32(self.max_speed, order)
        writer.write_f32(self.offset, order)

    @classmethod
    def from_robtop_mapping(cls: Type[FPYT], mapping: Mapping[int, str]) -> FPYT:
        follow_player_y_trigger = super().from_robtop_mapping(mapping)

        target_group_id = parse_get_or(int, DEFAULT_ID, mapping.get(TARGET_GROUP_ID))

        delay = parse_get_or(float, DEFAULT_DELAY, mapping.get(FOLLOW_DELAY))

        speed = parse_get_or(float, DEFAULT_SPEED, mapping.get(SPEED))
        max_speed = parse_get_or(float, DEFAULT_MAX_SPEED, mapping.get(MAX_SPEED))
        offset = parse_get_or(float, DEFAULT_OFFSET, mapping.get(OFFSET))

        follow_player_y_trigger.target_group_id = target_group_id

        follow_player_y_trigger.delay = delay

        follow_player_y_trigger.speed = speed
        follow_player_y_trigger.max_speed = max_speed
        follow_player_y_trigger.offset = offset

        return follow_player_y_trigger

    def to_robtop_mapping(self) -> Dict[int, str]:
        mapping = super().to_robtop_mapping()

        mapping[TARGET_GROUP_ID] = str(self.target_group_id)

        mapping[FOLLOW_DELAY] = float_str(self.delay)

        mapping[SPEED] = float_str(self.speed)
        mapping[MAX_SPEED] = float_str(self.max_speed)
        mapping[OFFSET] = float_str(self.offset)

        return mapping


ODT = TypeVar("ODT", bound="OnDeathTrigger")


@define()
class OnDeathTrigger(HasActivateGroup, HasTargetGroup, Trigger):  # type: ignore
    @classmethod
    def from_binary(
        cls: Type[ODT],
        binary: BinaryReader,
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
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary)

        writer.write_u16(self.target_group_id, order)

        value = 0

        if self.is_activate_group():
            value |= ACTIVATE_GROUP_BIT

        writer.write_u8(value, order)

    @classmethod
    def from_robtop_mapping(cls: Type[ODT], mapping: Mapping[int, str]) -> ODT:
        on_death_trigger = super().from_robtop_mapping(mapping)

        target_group_id = parse_get_or(int, DEFAULT_ID, mapping.get(TARGET_GROUP_ID))

        activate_group = parse_get_or(int_bool, DEFAULT_ACTIVATE_GROUP, mapping.get(ACTIVATE_GROUP))

        on_death_trigger.target_group_id = target_group_id

        on_death_trigger.activate_group = activate_group

        return on_death_trigger

    def to_robtop_mapping(self) -> Dict[int, str]:
        mapping = super().to_robtop_mapping()

        mapping[TARGET_GROUP_ID] = str(self.target_group_id)

        activate_group = self.is_activate_group()

        if activate_group:
            mapping[ACTIVATE_GROUP] = str(int(activate_group))

        return mapping


BLOCK_A_ID = 80
BLOCK_B_ID = 95
TRIGGER_ON_EXIT = 93


TRIGGER_ON_EXIT_BIT = 0b10000000_00000000


DEFAULT_TRIGGER_ON_EXIT = False


CBT = TypeVar("CBT", bound="CollisionTrigger")


@define()
class CollisionTrigger(HasActivateGroup, HasTargetGroup, Trigger):  # type: ignore
    block_a_id: int = DEFAULT_ID
    block_b_id: int = DEFAULT_ID

    trigger_on_exit: bool = DEFAULT_TRIGGER_ON_EXIT

    @classmethod
    def from_binary(
        cls: Type[CBT],
        binary: BinaryReader,
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
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
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

    @classmethod
    def from_robtop_mapping(cls: Type[CBT], mapping: Mapping[int, str]) -> CBT:
        collision_trigger = super().from_robtop_mapping(mapping)

        block_a_id = parse_get_or(int, DEFAULT_ID, mapping.get(BLOCK_A_ID))
        block_b_id = parse_get_or(int, DEFAULT_ID, mapping.get(BLOCK_B_ID))

        trigger_on_exit = parse_get_or(
            int_bool, DEFAULT_TRIGGER_ON_EXIT, mapping.get(TRIGGER_ON_EXIT)
        )

        collision_trigger.block_a_id = block_a_id
        collision_trigger.block_b_id = block_b_id

        collision_trigger.trigger_on_exit = trigger_on_exit

        return collision_trigger

    def to_robtop_mapping(self) -> Dict[int, str]:
        mapping = super().to_robtop_mapping()

        mapping[BLOCK_A_ID] = str(self.block_a_id)
        mapping[BLOCK_B_ID] = str(self.block_b_id)

        trigger_on_exit = self.is_trigger_on_exit()

        if trigger_on_exit:
            mapping[TRIGGER_ON_EXIT] = str(int(trigger_on_exit))

        return mapping


def is_trigger(object: Object) -> TypeGuard[Trigger]:
    return object.is_trigger()


def has_target_group(object: Object) -> TypeGuard[HasTargetGroup]:
    return object.has_target_group()


def has_additional_group(object: Object) -> TypeGuard[HasAdditionalGroup]:
    return object.has_additional_group()


class ObjectType(Enum):
    OBJECT = 1
    PULSATING_OBJECT = 2
    ROTATING_OBJECT = 3
    ORB = 4
    TRIGGER_ORB = 5
    SECRET_COIN = 6
    TEXT = 7
    TELEPORT = 8
    ITEM_COUNTER = 9
    PICKUP_ITEM = 10
    COLLISION_BLOCK = 11
    COLOR_TRIGGER = 12
    PULSE_TRIGGER = 13
    ALPHA_TRIGGER = 14
    MOVE_TRIGGER = 15
    SPAWN_TRIGGER = 16
    STOP_TRIGGER = 17
    TOGGLE_TRIGGER = 18
    ROTATE_TRIGGER = 19
    FOLLOW_TRIGGER = 20
    SHAKE_TRIGGER = 21
    ANIMATE_TRIGGER = 22
    TOUCH_TRIGGER = 23
    COUNT_TRIGGER = 24
    INSTANT_COUNT_TRIGGER = 25
    PICKUP_TRIGGER = 26
    FOLLOW_PLAYER_Y_TRIGGER = 27
    ON_DEATH_TRIGGER = 28
    COLLISION_TRIGGER = 29


OBJECT_TYPE_TO_TYPE: Dict[ObjectType, Type[Object]] = {
    ObjectType.OBJECT: Object,
    ObjectType.PULSATING_OBJECT: PulsatingObject,
    ObjectType.ROTATING_OBJECT: RotatingObject,
    ObjectType.ORB: Orb,
    ObjectType.TRIGGER_ORB: TriggerOrb,
    ObjectType.SECRET_COIN: SecretCoin,
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
    binary: BinaryReader, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
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
    object: Object,
    binary: BinaryWriter,
    order: ByteOrder = ByteOrder.DEFAULT,
    version: int = VERSION,
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


OBJECT_ID_TO_TYPE: Dict[int, Type[Object]] = {
    MiscType.TEXT.id: Text,
    CoinType.SECRET.id: SecretCoin,
    PortalType.BLUE_TELEPORT.id: Teleport,
    OrbType.TRIGGER.id: TriggerOrb,
    MiscType.ITEM_COUNTER.id: ItemCounter,
    MiscType.COLLISION_BLOCK.id: CollisionBlock,
    TriggerType.COLOR.id: ColorTrigger,
    TriggerType.ALPHA.id: AlphaTrigger,
    TriggerType.PULSE.id: PulseTrigger,
    TriggerType.MOVE.id: MoveTrigger,
    TriggerType.SPAWN.id: SpawnTrigger,
    TriggerType.STOP.id: StopTrigger,
    TriggerType.TOGGLE.id: ToggleTrigger,
    TriggerType.ROTATE.id: RotateTrigger,
    TriggerType.FOLLOW.id: FollowTrigger,
    TriggerType.SHAKE.id: ShakeTrigger,
    TriggerType.ANIMATE.id: AnimateTrigger,
    TriggerType.TOUCH.id: TouchTrigger,
    TriggerType.COUNT.id: CountTrigger,
    TriggerType.INSTANT_COUNT.id: InstantCountTrigger,
    TriggerType.PICKUP.id: PickupTrigger,
    TriggerType.FOLLOW_PLAYER_Y.id: FollowPlayerYTrigger,
    TriggerType.ON_DEATH.id: OnDeathTrigger,
    TriggerType.COLLISION.id: CollisionTrigger,
}

OBJECT_ID_TO_TYPE.update({orb.id: Orb for orb in OrbType if not orb.is_trigger()})
OBJECT_ID_TO_TYPE.update({pickup_item.id: PickupItem for pickup_item in PickupItemType})
OBJECT_ID_TO_TYPE.update(
    {rotating_object.id: RotatingObject for rotating_object in RotatingObjectType}
)
OBJECT_ID_TO_TYPE.update(
    {pulsating_object.id: PulsatingObject for pulsating_object in PulsatingObjectType}
)


def object_from_robtop(string: str) -> Object:
    mapping = split_object(string)

    object_id_string = mapping.get(ID)

    if object_id_string is None:
        raise ValueError(OBJECT_ID_NOT_PRESENT)

    object_id = int(object_id_string)

    object_type = OBJECT_ID_TO_TYPE.get(object_id, Object)

    return object_type.from_robtop_mapping(mapping)


def object_to_robtop(object: Object) -> str:
    return object.to_robtop()


# TODO: compatibility?
