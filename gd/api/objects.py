from abc import abstractmethod as required
from builtins import hasattr as has_attribute
from enum import Enum, Flag
from io import BytesIO
from typing import Dict, Iterable, Iterator, Mapping, Optional, Tuple, Type, TypeVar, Union

from attrs import define, field
from iters.iters import iter
from iters.ordered_set import OrderedSet
from named import get_type_name
from typing_aliases import is_instance
from typing_extensions import Literal, Never, Protocol, TypeGuard, runtime_checkable

from gd.api.color_channels import (
    BACKGROUND_COLOR_ID,
    COLOR_1_ID,
    COLOR_2_ID,
    COLOR_3_ID,
    COLOR_4_ID,
    GROUND_COLOR_ID,
    LINE_3D_COLOR_ID,
    LINE_COLOR_ID,
    OBJECT_COLOR_ID,
    SECONDARY_GROUND_COLOR_ID,
)
from gd.api.hsv import HSV
from gd.binary import VERSION, Binary, BinaryReader, BinaryWriter
from gd.binary_constants import BITS, BYTE, HALF_BITS, HALF_BYTE
from gd.binary_utils import Reader, Writer
from gd.color import Color
from gd.constants import DEFAULT_ENCODING, DEFAULT_ERRORS, DEFAULT_ID, DEFAULT_ROUNDING, EMPTY
from gd.encoding import decode_base64_string_url_safe, encode_base64_string_url_safe
from gd.enums import (
    ByteOrder,
    CoinType,
    Easing,
    GameMode,
    InstantCountComparison,
    ItemMode,
    ItemType,
    LegacyColorID,
    LockedType,
    MiscType,
    OrbType,
    PlayerColor,
    PortalType,
    PulsatingObjectType,
    PulseMode,
    PulseTargetType,
    PulseType,
    RotatingObjectType,
    SimpleTargetType,
    Speed,
    SpeedChangeType,
    TargetType,
    ToggleType,
    TriggerType,
)
from gd.models_constants import GROUPS_SEPARATOR, OBJECT_SEPARATOR
from gd.models_utils import (
    bool_str,
    concat_any_object,
    concat_groups,
    concat_object,
    float_str,
    int_bool,
    parse_get_or,
    parse_get_or_else,
    partial_parse_enum,
    split_any_object,
    split_groups,
    split_object,
)
from gd.robtop import RobTop

__all__ = (
    # groups
    "Groups",
    # objects
    "Object",
    "PulsatingObject",
    "RotatingObject",
    "Orb",
    "TriggerOrb",
    "ItemCounter",
    "SecretCoin",
    "Text",
    "Teleport",
    "ToggleItem",
    "PickupItem",
    "CollisionBlock",
    "PlayerColorTrigger",
    "NormalColorTrigger",
    "CopiedColorTrigger",
    "PulseColorChannelTrigger",
    "PulseHSVChannelTrigger",
    "PulseColorGroupTrigger",
    "PulseHSVGroupTrigger",
    "AlphaTrigger",
    "NormalMoveTrigger",
    "TargetMoveTrigger",
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
    # unions
    "Item",
    "ColorTrigger",
    "PulseTrigger",
    "MoveTrigger",
    # type guards
    "is_start_position",
    "is_trigger",
    "has_target_group",
    "has_additional_group",
    # conversion
    "object_from_binary",
    "object_to_binary",
    "object_from_bytes",
    "object_to_bytes",
    # migration
    "migrate_objects",
)

GRID_UNITS = 30.0

ID = 1
X = 2
Y = 3
H_FLIPPED = 4
V_FLIPPED = 5
ROTATION = 6
RED = 7
GREEN = 8
BLUE = 9
DURATION = 10
TOUCH_TRIGGERED = 11
COIN_ID = 12
SPECIAL_CHECKED = 13
TINT_GROUND = 14
PLAYER_COLOR_1 = 15
PLAYER_COLOR_2 = 16
BLENDING = 17
LEGACY_COLOR_ID = 19
BASE_EDITOR_LAYER = 20
BASE_COLOR_ID = 21
DETAIL_COLOR_ID = 22
TARGET_COLOR_ID = 23
Z_LAYER = 24
Z_ORDER = 25
X_OFFSET = 28
Y_OFFSET = 29
EASING = 30
CONTENT = 31
SCALE = 32
SINGLE_GROUP_ID = 33
GROUP_PARENT = 34
OPACITY = 35
UNKNOWN = 36
BASE_COLOR_HSV_MODIFIED = 41
DETAIL_COLOR_HSV_MODIFIED = 42
BASE_COLOR_HSV = 43
DETAIL_COLOR_HSV = 44
FADE_IN = 45
HOLD = 46
FADE_OUT = 47
PULSE_MODE = 48
COPIED_COLOR_HSV = 49
COPIED_COLOR_ID = 50
TARGET_GROUP_ID = 51
PULSE_TARGET_TYPE = 52
PORTAL_OFFSET = 54
SMOOTH = 55
ACTIVATE_GROUP = 56
GROUPS = 57
LOCKED_TO_PLAYER_X = 58
LOCKED_TO_PLAYER_Y = 59
COPY_OPACITY = 60
ADDITIONAL_EDITOR_LAYER = 61
SPAWN_TRIGGERED = 62
SPAWN_DELAY = 63
DO_NOT_FADE = 64
MAIN_ONLY = 65
DETAIL_ONLY = 66
DO_NOT_ENTER = 67
DEGREES = 68
ROTATIONS = 69
ROTATION_LOCKED = 70
ADDITIONAL_GROUP_ID = 71
X_MODIFIER = 72
Y_MODIFIER = 73
STRENGTH = 75
ANIMATION_ID = 76
COUNT = 77
SUBTRACT_COUNT = 78
ITEM_MODE = 79
ITEM_ID = 80
BLOCK_ID = 80
BLOCK_A_ID = 80
HOLD_MODE = 81
TOGGLE_TYPE = 82
INTERVAL = 84
EASING_RATE = 85
EXCLUSIVE = 86
MULTI_TRIGGER = 87
COMPARISON = 88
DUAL_MODE = 89
SPEED = 90
FOLLOW_DELAY = 91
OFFSET = 92
TRIGGER_ON_EXIT = 93
DYNAMIC = 94
BLOCK_B_ID = 95
DISABLE_GLOW = 96
ROTATION_SPEED = 97
DISABLE_ROTATION = 98
ORB_MULTI_ACTIVATE = 99
USE_TARGET = 100
TARGET_TYPE = 101
EDITOR_DISABLE = 102
HIGH_DETAIL = 103
TRIGGER_MULTI_ACTIVATE = 104
MAX_SPEED = 105
RANDOMIZE_START = 106
ANIMATION_SPEED = 107
LINK_ID = 108


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


G = TypeVar("G", bound="Groups")


class Groups(OrderedSet[int], Binary, RobTop):
    @classmethod
    def from_robtop(cls: Type[G], string: str) -> G:
        return iter(split_groups(string)).map(int).collect(cls)

    def to_robtop(self) -> str:
        return iter(self).map(str).collect(concat_groups)

    @classmethod
    def from_binary(
        cls: Type[G],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> G:
        reader = Reader(binary, order)

        length = reader.read_u16()

        return iter.repeat_exactly_with(reader.read_u16, length).collect(cls)

    def to_binary(
        self,
        binary: BinaryWriter,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> None:
        writer = Writer(binary, order)

        writer.write_u16(len(self))

        iter(self).for_each(writer.write_u16)

    @staticmethod
    def can_be_in(string: str) -> bool:
        return GROUPS_SEPARATOR in string


DEFAULT_X = 0.0
DEFAULT_Y = 0.0

DEFAULT_ROTATION = 0.0

DEFAULT_H_FLIPPED = False
DEFAULT_V_FLIPPED = False

DEFAULT_SCALE = 1.0

DEFAULT_DO_NOT_FADE = False
DEFAULT_DO_NOT_ENTER = False

DEFAULT_Z_LAYER = 0
DEFAULT_Z_ORDER = 0

DEFAULT_BASE_EDITOR_LAYER = 0
DEFAULT_ADDITIONAL_EDITOR_LAYER = 0

DEFAULT_GROUP_PARENT = False

DEFAULT_HIGH_DETAIL = False

DEFAULT_DISABLE_GLOW = False

DEFAULT_SPECIAL_CHECKED = False

DEFAULT_UNKNOWN = False


H_FLIPPED_BIT = 0b00000001
V_FLIPPED_BIT = 0b00000010
DO_NOT_FADE_BIT = 0b00000100
DO_NOT_ENTER_BIT = 0b00001000
GROUP_PARENT_BIT = 0b00010000
HIGH_DETAIL_BIT = 0b00100000
DISABLE_GLOW_BIT = 0b01000000
SPECIAL_CHECKED_BIT = 0b10000000

UNKNOWN_BIT = 0b00000001


OBJECT_STRING = "{object_type} (ID: {object.id}) at ({object.x}, {object.y})"
object_string = OBJECT_STRING.format

O = TypeVar("O", bound="Object")


@define()
class Object(Binary, RobTop):
    id: int = field()
    x: float = field(default=DEFAULT_X)
    y: float = field(default=DEFAULT_Y)

    h_flipped: bool = field(default=DEFAULT_H_FLIPPED)
    v_flipped: bool = field(default=DEFAULT_V_FLIPPED)

    rotation: float = field(default=DEFAULT_ROTATION)

    scale: float = field(default=DEFAULT_SCALE)

    do_not_fade: bool = field(default=DEFAULT_DO_NOT_FADE)
    do_not_enter: bool = field(default=DEFAULT_DO_NOT_ENTER)

    z_layer: int = field(default=DEFAULT_Z_LAYER)
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

    unknown: bool = field(default=DEFAULT_UNKNOWN)

    @classmethod
    def from_binary(
        cls: Type[O],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> O:
        rounding = DEFAULT_ROUNDING

        h_flipped_bit = H_FLIPPED_BIT
        v_flipped_bit = V_FLIPPED_BIT
        do_not_fade_bit = DO_NOT_FADE_BIT
        do_not_enter_bit = DO_NOT_ENTER_BIT
        group_parent_bit = GROUP_PARENT_BIT
        high_detail_bit = HIGH_DETAIL_BIT
        disable_glow_bit = DISABLE_GLOW_BIT
        special_checked_bit = SPECIAL_CHECKED_BIT

        unknown_bit = UNKNOWN_BIT

        reader = Reader(binary, order)

        flag_value = reader.read_u8()

        flag = ObjectFlag(flag_value)

        id = reader.read_u16()

        x = round(reader.read_f32(), rounding)
        y = round(reader.read_f32(), rounding)

        value = reader.read_u8()

        h_flipped = value & h_flipped_bit == h_flipped_bit
        v_flipped = value & v_flipped_bit == v_flipped_bit
        do_not_fade = value & do_not_fade_bit == do_not_fade_bit
        do_not_enter = value & do_not_enter_bit == do_not_enter_bit
        group_parent = value & group_parent_bit == group_parent_bit
        high_detail = value & high_detail_bit == high_detail_bit
        disable_glow = value & disable_glow_bit == disable_glow_bit
        special_checked = value & special_checked_bit == special_checked_bit

        if flag.has_rotation_and_scale():
            rotation = round(reader.read_f32(), rounding)
            scale = round(reader.read_f32(), rounding)

        else:
            rotation = DEFAULT_ROTATION
            scale = DEFAULT_SCALE

        if flag.has_z():
            z_layer = reader.read_i8()
            z_order = reader.read_i16()

        else:
            z_layer = DEFAULT_Z_LAYER
            z_order = DEFAULT_Z_ORDER

        if flag.has_editor_layer():
            base_editor_layer = reader.read_u16()
            additional_editor_layer = reader.read_u16()

        else:
            base_editor_layer = DEFAULT_BASE_EDITOR_LAYER
            additional_editor_layer = DEFAULT_ADDITIONAL_EDITOR_LAYER

        if flag.has_colors():
            base_color_id = reader.read_u16()
            detail_color_id = reader.read_u16()

            base_color_hsv = HSV.from_binary(binary, order, version)
            detail_color_hsv = HSV.from_binary(binary, order, version)

        else:
            base_color_id = DEFAULT_ID
            detail_color_id = DEFAULT_ID

            base_color_hsv = HSV()
            detail_color_hsv = HSV()

        if flag.has_groups():
            groups = Groups.from_binary(binary, order, version)

        else:
            groups = Groups()

        if flag.has_link():
            link_id = reader.read_u16()

        else:
            link_id = DEFAULT_ID

        value = reader.read_u8()

        unknown = value & unknown_bit == unknown_bit

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
            unknown=unknown,
        )

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        writer = Writer(binary, order)

        flag = ObjectFlag.SIMPLE

        rotation = self.rotation
        scale = self.scale

        if rotation or scale != DEFAULT_SCALE:
            flag |= ObjectFlag.HAS_ROTATION_AND_SCALE

        z_layer = self.z_layer
        z_order = self.z_order

        if z_layer or z_order:
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

        writer.write_u8(flag.value)

        writer.write_u16(self.id)

        writer.write_f32(self.x)
        writer.write_f32(self.y)

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

        writer.write_u8(value)

        if flag.has_rotation_and_scale():
            writer.write_f32(self.rotation)
            writer.write_f32(self.scale)

        if flag.has_z():
            writer.write_i8(self.z_layer)

            writer.write_i16(self.z_order)

        if flag.has_editor_layer():
            writer.write_u16(base_editor_layer)
            writer.write_u16(additional_editor_layer)

        if flag.has_colors():
            writer.write_u16(base_color_id)
            writer.write_u16(detail_color_id)

            base_color_hsv.to_binary(binary, order, version)
            detail_color_hsv.to_binary(binary, order, version)

        if flag.has_groups():
            self.groups.to_binary(binary, order, version)

        if flag.has_link():
            writer.write_u16(link_id)

        value = 0

        if self.is_unknown():
            value |= UNKNOWN_BIT

        writer.write_u8(value)

    @classmethod
    def from_robtop(cls: Type[O], string: str) -> O:
        return cls.from_robtop_data(split_object(string))

    @classmethod
    def from_robtop_data(cls: Type[O], data: Mapping[int, str]) -> O:
        id_option = data.get(ID)

        if id_option is None:
            raise ValueError(OBJECT_ID_NOT_PRESENT)

        id = int(id_option)

        x = parse_get_or(float, DEFAULT_X, data.get(X))
        y = parse_get_or(float, DEFAULT_Y, data.get(Y))

        rotation = parse_get_or(float, DEFAULT_ROTATION, data.get(ROTATION))

        scale = parse_get_or(float, DEFAULT_SCALE, data.get(SCALE))

        h_flipped = parse_get_or(int_bool, DEFAULT_H_FLIPPED, data.get(H_FLIPPED))
        v_flipped = parse_get_or(int_bool, DEFAULT_V_FLIPPED, data.get(V_FLIPPED))

        do_not_fade = parse_get_or(int_bool, DEFAULT_DO_NOT_FADE, data.get(DO_NOT_FADE))
        do_not_enter = parse_get_or(int_bool, DEFAULT_DO_NOT_ENTER, data.get(DO_NOT_ENTER))

        z_layer = parse_get_or(int, DEFAULT_Z_LAYER, data.get(Z_LAYER))
        z_order = parse_get_or(int, DEFAULT_Z_ORDER, data.get(Z_ORDER))

        base_editor_layer = parse_get_or(
            int, DEFAULT_BASE_EDITOR_LAYER, data.get(BASE_EDITOR_LAYER)
        )
        additional_editor_layer = parse_get_or(
            int, DEFAULT_ADDITIONAL_EDITOR_LAYER, data.get(ADDITIONAL_EDITOR_LAYER)
        )

        legacy_color_id = parse_get_or(
            partial_parse_enum(int, LegacyColorID),
            LegacyColorID.DEFAULT,
            data.get(LEGACY_COLOR_ID),
        )

        migrated_color_id = legacy_color_id.migrate()

        if migrated_color_id:
            base_color_id = migrated_color_id
            detail_color_id = migrated_color_id

        else:
            base_color_id = parse_get_or(int, DEFAULT_ID, data.get(BASE_COLOR_ID))
            detail_color_id = parse_get_or(int, DEFAULT_ID, data.get(DETAIL_COLOR_ID))

        base_color_hsv = parse_get_or_else(HSV.from_robtop, HSV, data.get(BASE_COLOR_HSV))
        detail_color_hsv = parse_get_or_else(HSV.from_robtop, HSV, data.get(DETAIL_COLOR_HSV))

        single_group_id = parse_get_or(int, DEFAULT_ID, data.get(SINGLE_GROUP_ID))

        groups = parse_get_or_else(Groups.from_robtop, Groups, data.get(GROUPS))

        if single_group_id:
            groups.append(single_group_id)

        group_parent = parse_get_or(int_bool, DEFAULT_GROUP_PARENT, data.get(GROUP_PARENT))
        high_detail = parse_get_or(int_bool, DEFAULT_HIGH_DETAIL, data.get(HIGH_DETAIL))
        disable_glow = parse_get_or(int_bool, DEFAULT_DISABLE_GLOW, data.get(DISABLE_GLOW))
        special_checked = parse_get_or(int_bool, DEFAULT_SPECIAL_CHECKED, data.get(SPECIAL_CHECKED))

        link_id = parse_get_or(int, DEFAULT_ID, data.get(LINK_ID))

        unknown = parse_get_or(int_bool, DEFAULT_UNKNOWN, data.get(UNKNOWN))

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
            unknown=unknown,
        )

    def to_robtop(self) -> str:
        return concat_object(self.to_robtop_data())

    def to_robtop_data(self) -> Dict[int, str]:
        data = {ID: str(self.id), X: float_str(self.x), Y: float_str(self.y)}

        rotation = self.rotation

        if rotation:
            data[ROTATION] = float_str(rotation)

        scale = self.scale

        if scale != DEFAULT_SCALE:
            data[SCALE] = float_str(scale)

        h_flipped = self.is_h_flipped()

        if h_flipped:
            data[H_FLIPPED] = bool_str(h_flipped)

        v_flipped = self.is_v_flipped()

        if v_flipped:
            data[V_FLIPPED] = bool_str(v_flipped)

        do_not_fade = self.has_do_not_fade()

        if do_not_fade:
            data[DO_NOT_FADE] = bool_str(do_not_fade)

        do_not_enter = self.has_do_not_enter()

        if do_not_enter:
            data[DO_NOT_ENTER] = bool_str(do_not_enter)

        z_layer = self.z_layer

        if z_layer:
            data[Z_LAYER] = str(z_layer)

        z_order = self.z_order

        if z_order:
            data[Z_ORDER] = str(z_order)

        base_editor_layer = self.base_editor_layer

        if base_editor_layer:
            data[BASE_EDITOR_LAYER] = str(base_editor_layer)

        additional_editor_layer = self.additional_editor_layer

        if additional_editor_layer:
            data[ADDITIONAL_EDITOR_LAYER] = str(additional_editor_layer)

        base_color_id = self.base_color_id

        if base_color_id:
            data[BASE_COLOR_ID] = str(base_color_id)

        detail_color_id = self.detail_color_id

        if detail_color_id:
            data[DETAIL_COLOR_ID] = str(detail_color_id)

        base_color_hsv = self.base_color_hsv

        base_color_hsv_modified = not base_color_hsv.is_default()

        if base_color_hsv_modified:
            data[BASE_COLOR_HSV] = base_color_hsv.to_robtop()
            data[BASE_COLOR_HSV_MODIFIED] = bool_str(base_color_hsv_modified)

        detail_color_hsv = self.detail_color_hsv

        detail_color_hsv_modified = not detail_color_hsv.is_default()

        if detail_color_hsv_modified:
            data[DETAIL_COLOR_HSV] = detail_color_hsv.to_robtop()
            data[DETAIL_COLOR_HSV_MODIFIED] = bool_str(detail_color_hsv_modified)

        groups = self.groups

        if groups:
            data[GROUPS] = groups.to_robtop()

        group_parent = self.is_group_parent()

        if group_parent:
            data[GROUP_PARENT] = bool_str(group_parent)

        high_detail = self.is_high_detail()

        if high_detail:
            data[HIGH_DETAIL] = bool_str(high_detail)

        disable_glow = self.has_disable_glow()

        if disable_glow:
            data[DISABLE_GLOW] = bool_str(disable_glow)

        special_checked = self.is_special_checked()

        if special_checked:
            data[SPECIAL_CHECKED] = bool_str(special_checked)

        link_id = self.link_id

        if link_id:
            data[LINK_ID] = str(link_id)

        unknown = self.is_unknown()

        if unknown:
            data[UNKNOWN] = bool_str(unknown)

        return data

    @staticmethod
    def can_be_in(string: str) -> bool:
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

    def is_unknown(self) -> bool:
        return self.unknown

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

    def is_start_position(self) -> bool:
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
        return object_string(object_type=get_type_name(self), object=self)


PORTAL_IDS = {portal.id for portal in PortalType}
SPEED_CHANGE_IDS = {speed_change.id for speed_change in SpeedChangeType}


ID_STRING = str(ID)
X_STRING = str(X)
Y_STRING = str(Y)

START_POSITION_GAME_MODE = "kA2"
START_POSITION_MINI_MODE = "kA3"
START_POSITION_SPEED = "kA4"
START_POSITION_DUAL_MODE = "kA8"
START_POSITION = "kA9"
START_POSITION_FLIP_GRAVITY = "kA11"

DEFAULT_START_POSITION_MINI_MODE = False
DEFAULT_START_POSITION_DUAL_MODE = False
DEFAULT_START_POSITION_FLIP_GRAVITY = False


START_POSITION_MINI_MODE_BIT = 0b00000001
START_POSITION_DUAL_MODE_BIT = 0b00000010
START_POSITION_FLIP_GRAVITY_BIT = 0b00000100


SP = TypeVar("SP", bound="StartPosition")

SPECIAL_HANDLING = (
    "special handling is required for start positions; consider using `from_robtop` and `to_robtop`"
)


@define()
class StartPosition(Object):
    game_mode: GameMode = field(default=GameMode.DEFAULT)
    mini_mode: bool = field(default=DEFAULT_START_POSITION_MINI_MODE)
    speed: Speed = field(default=Speed.DEFAULT)
    dual_mode: bool = field(default=DEFAULT_START_POSITION_DUAL_MODE)
    flip_gravity: bool = field(default=DEFAULT_START_POSITION_FLIP_GRAVITY)

    @classmethod
    def from_binary(
        cls: Type[SP],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> SP:
        start_position = super().from_binary(binary, order, version)

        start_position_mini_mode_bit = START_POSITION_MINI_MODE_BIT
        start_position_dual_mode_bit = START_POSITION_DUAL_MODE_BIT
        start_position_flip_gravity_bit = START_POSITION_FLIP_GRAVITY_BIT

        reader = Reader(binary, order)

        value = reader.read_u8()

        speed = Speed(value & HALF_BYTE)

        value >>= HALF_BITS

        game_mode = GameMode(value)

        value = reader.read_u8()

        mini_mode = value & start_position_mini_mode_bit == start_position_mini_mode_bit
        dual_mode = value & start_position_dual_mode_bit == start_position_dual_mode_bit
        flip_gravity = value & start_position_flip_gravity_bit == start_position_flip_gravity_bit

        start_position.game_mode = game_mode
        start_position.mini_mode = mini_mode
        start_position.speed = speed
        start_position.dual_mode = dual_mode
        start_position.flip_gravity = flip_gravity

        return start_position

    def to_binary(
        self,
        binary: BinaryWriter,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary, order)

        value = (self.game_mode.value << HALF_BITS) | self.speed.value

        writer.write_u8(value)

        value = 0

        if self.is_mini_mode():
            value |= START_POSITION_MINI_MODE_BIT

        if self.is_dual_mode():
            value |= START_POSITION_DUAL_MODE_BIT

        if self.is_flip_gravity():
            value |= START_POSITION_FLIP_GRAVITY_BIT

        writer.write_u8(value)

    @classmethod
    def from_robtop(cls: Type[SP], string: str) -> SP:
        data = split_any_object(string)

        id_option = data.get(ID_STRING)

        if id_option is None:
            raise ValueError(OBJECT_ID_NOT_PRESENT)

        id = int(id_option)

        x = parse_get_or(float, DEFAULT_X, data.get(X_STRING))
        y = parse_get_or(float, DEFAULT_Y, data.get(Y_STRING))

        game_mode = parse_get_or(
            partial_parse_enum(int, GameMode),
            GameMode.DEFAULT,
            data.get(START_POSITION_GAME_MODE),
        )

        mini_mode = parse_get_or(
            int_bool, DEFAULT_START_POSITION_MINI_MODE, data.get(START_POSITION_MINI_MODE)
        )

        speed = parse_get_or(
            partial_parse_enum(int, Speed), Speed.DEFAULT, data.get(START_POSITION_SPEED)
        )

        dual_mode = parse_get_or(
            int_bool, DEFAULT_START_POSITION_DUAL_MODE, data.get(START_POSITION_DUAL_MODE)
        )

        flip_gravity = parse_get_or(
            int_bool, DEFAULT_START_POSITION_FLIP_GRAVITY, data.get(START_POSITION_FLIP_GRAVITY)
        )

        return cls(
            id=id,
            x=x,
            y=y,
            game_mode=game_mode,
            mini_mode=mini_mode,
            speed=speed,
            dual_mode=dual_mode,
            flip_gravity=flip_gravity,
        )

    def to_robtop(self) -> str:
        data = {
            ID_STRING: str(self.id),
            X_STRING: float_str(self.x),
            Y_STRING: float_str(self.y),
            START_POSITION_GAME_MODE: str(self.game_mode.value),
            START_POSITION_MINI_MODE: bool_str(self.is_mini_mode()),
            START_POSITION_SPEED: str(self.speed.value),
            START_POSITION_DUAL_MODE: bool_str(self.is_dual_mode()),
            START_POSITION: bool_str(self.is_start_position()),
            START_POSITION_FLIP_GRAVITY: bool_str(self.is_flip_gravity()),
        }

        return concat_any_object(data)

    @classmethod
    def from_robtop_data(cls, data: Mapping[int, str]) -> Never:
        raise NotImplementedError(SPECIAL_HANDLING)

    def to_robtop_data(self) -> Never:
        raise NotImplementedError(SPECIAL_HANDLING)

    def is_start_position(self) -> bool:
        return True

    def is_mini_mode(self) -> bool:
        return self.mini_mode

    def is_dual_mode(self) -> bool:
        return self.dual_mode

    def is_flip_gravity(self) -> bool:
        return self.flip_gravity


def is_start_position(object: Object) -> TypeGuard[StartPosition]:
    return object.is_start_position()


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

        reader = Reader(binary, order)

        coin_id = reader.read_u8()

        coin.coin_id = coin_id

        return coin

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary, order)

        writer.write_u8(self.coin_id)

    @classmethod
    def from_robtop_data(cls: Type[SC], data: Mapping[int, str]) -> SC:
        coin = super().from_robtop_data(data)

        coin_id = parse_get_or(int, DEFAULT_ID, data.get(COIN_ID))

        coin.coin_id = coin_id

        return coin

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        data[COIN_ID] = str(self.coin_id)

        return data


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
        rounding = DEFAULT_ROUNDING

        rotating_object = super().from_binary(binary, order, version)

        disable_rotation_bit = DISABLE_ROTATION_BIT

        reader = Reader(binary, order)

        rotation_speed = round(reader.read_f32(), rounding)

        value = reader.read_u8()

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

        writer = Writer(binary, order)

        writer.write_f32(self.rotation_speed)

        value = 0

        if self.is_disable_rotation():
            value |= DISABLE_ROTATION_BIT

        writer.write_u8(value)

    def is_disable_rotation(self) -> bool:
        return self.disable_rotation

    @classmethod
    def from_robtop_data(cls: Type[RO], data: Mapping[int, str]) -> RO:
        rotating_object = super().from_robtop_data(data)

        rotation_speed = parse_get_or(float, DEFAULT_ROTATION_SPEED, data.get(ROTATION_SPEED))

        disable_rotation = parse_get_or(
            int_bool, DEFAULT_DISABLE_ROTATION, data.get(DISABLE_ROTATION)
        )

        rotating_object.rotation_speed = rotation_speed
        rotating_object.disable_rotation = disable_rotation

        return rotating_object

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        rotation_speed = self.rotation_speed

        if self.rotation_speed:
            data[ROTATION_SPEED] = float_str(rotation_speed)

        disable_rotation = self.is_disable_rotation()

        if disable_rotation:
            data[DISABLE_ROTATION] = bool_str(disable_rotation)

        return data


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

        reader = Reader(binary, order)

        length = reader.read_u16()

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

        writer = Writer(binary, order)

        data = self.content.encode(encoding, errors)

        writer.write_u16(len(data))

        writer.write(data)

    @classmethod
    def from_robtop_data(cls: Type[S], data: Mapping[int, str]) -> S:
        text = super().from_robtop_data(data)

        content = parse_get_or(
            decode_base64_string_url_safe, EMPTY, data.get(CONTENT), ignore_errors=True
        )

        text.content = content

        return text

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        data[CONTENT] = encode_base64_string_url_safe(self.content)

        return data


SMOOTH_BIT = 0b00000001


DEFAULT_SMOOTH = False
DEFAULT_PORTAL_OFFSET = 100.0


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
        rounding = DEFAULT_ROUNDING

        smooth_bit = SMOOTH_BIT

        teleport = super().from_binary(binary, order, version)

        reader = Reader(binary, order)

        portal_offset = round(reader.read_f32(), rounding)

        value = reader.read_u8()

        smooth = value & smooth_bit == smooth_bit

        teleport.portal_offset = portal_offset
        teleport.smooth = smooth

        return teleport

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary, order)

        writer.write_f32(self.portal_offset)

        value = 0

        if self.is_smooth():
            value |= SMOOTH_BIT

        writer.write_u8(value)

    @classmethod
    def from_robtop_data(cls: Type[P], data: Mapping[int, str]) -> P:
        teleport = super().from_robtop_data(data)

        portal_offset = parse_get_or(float, DEFAULT_PORTAL_OFFSET, data.get(PORTAL_OFFSET))

        smooth = parse_get_or(int_bool, DEFAULT_SMOOTH, data.get(SMOOTH))

        teleport.portal_offset = portal_offset
        teleport.smooth = smooth

        return teleport

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        data[PORTAL_OFFSET] = float_str(self.portal_offset)

        smooth = self.smooth

        if smooth:
            data[SMOOTH] = bool_str(smooth)

        return data

    def is_smooth(self) -> bool:
        return self.smooth


DEFAULT_RANDOMIZE_START = False
DEFAULT_ANIMATION_SPEED = 1.0

RANDOMIZE_START_BIT = 0b00000001


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
        rounding = DEFAULT_ROUNDING

        randomize_start_bit = RANDOMIZE_START_BIT

        pulsating_object = super().from_binary(binary, order, version)

        reader = Reader(binary, order)

        animation_speed = round(reader.read_f32(), rounding)

        value = reader.read_u8()

        randomize_start = value & randomize_start_bit == randomize_start_bit

        pulsating_object.randomize_start = randomize_start

        pulsating_object.animation_speed = animation_speed

        return pulsating_object

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary, order)

        writer.write_f32(self.animation_speed)

        value = 0

        if self.is_randomize_start():
            value |= RANDOMIZE_START_BIT

        writer.write_u8(value)

    @classmethod
    def from_robtop_data(cls: Type[PO], data: Mapping[int, str]) -> PO:
        pulsating_object = super().from_robtop_data(data)

        randomize_start = parse_get_or(int_bool, DEFAULT_RANDOMIZE_START, data.get(RANDOMIZE_START))

        animation_speed = parse_get_or(float, DEFAULT_ANIMATION_SPEED, data.get(ANIMATION_SPEED))

        pulsating_object.randomize_start = randomize_start
        pulsating_object.animation_speed = animation_speed

        return pulsating_object

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        data[ANIMATION_SPEED] = str(self.animation_speed)

        randomize_start = self.is_randomize_start()

        if randomize_start:
            data[RANDOMIZE_START] = bool_str(randomize_start)

        return data

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
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> CB:
        dynamic_bit = DYNAMIC_BIT

        collision_block = super().from_binary(binary, order, version)

        reader = Reader(binary, order)

        value = reader.read_u16()

        block_id = value & BLOCK_ID_MASK
        dynamic = value & dynamic_bit == dynamic_bit

        collision_block.block_id = block_id
        collision_block.dynamic = dynamic

        return collision_block

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary, order)

        value = self.block_id & BLOCK_ID_MASK

        if self.is_dynamic():
            value |= DYNAMIC_BIT

        writer.write_u16(value)

    @classmethod
    def from_robtop_data(cls: Type[CB], data: Mapping[int, str]) -> CB:
        collision_block = super().from_robtop_data(data)

        block_id = parse_get_or(int, DEFAULT_ID, data.get(BLOCK_ID))

        dynamic = parse_get_or(int_bool, DEFAULT_DYNAMIC, data.get(DYNAMIC))

        collision_block.block_id = block_id
        collision_block.dynamic = dynamic

        return collision_block

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        data[BLOCK_ID] = str(self.block_id)

        dynamic = self.is_dynamic()

        if dynamic:
            data[DYNAMIC] = bool_str(dynamic)

        return data

    def is_dynamic(self) -> bool:
        return self.dynamic


MULTI_ACTIVATE_BIT = 0b00000010


DEFAULT_MULTI_ACTIVATE = False


OP = TypeVar("OP", bound="Orb")


@define()
class Orb(Object):
    multi_activate: bool = DEFAULT_MULTI_ACTIVATE

    def is_multi_activate(self) -> bool:
        return self.multi_activate

    @classmethod
    def from_binary(
        cls: Type[OP],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> OP:
        orb = super().from_binary(binary, order, version)

        multi_activate_bit = MULTI_ACTIVATE_BIT

        reader = Reader(binary, order)

        value = reader.read_u8()

        multi_activate = value & multi_activate_bit == multi_activate_bit

        orb.multi_activate = multi_activate

        return orb

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary, order)

        value = 0

        if self.is_multi_activate():
            value |= MULTI_ACTIVATE_BIT

        writer.write_u8(value)

    @classmethod
    def from_robtop_data(cls: Type[OP], data: Mapping[int, str]) -> OP:
        orb = super().from_robtop_data(data)

        multi_activate = parse_get_or(
            int_bool, DEFAULT_MULTI_ACTIVATE, data.get(ORB_MULTI_ACTIVATE)
        )

        orb.multi_activate = multi_activate

        return orb

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        multi_activate = self.is_multi_activate()

        if multi_activate:
            data[ORB_MULTI_ACTIVATE] = bool_str(multi_activate)

        return data


DEFAULT_ACTIVATE_GROUP = False


TO = TypeVar("TO", bound="TriggerOrb")


@define()
class TriggerOrb(Orb):
    target_group_id: int = DEFAULT_ID

    activate_group: bool = DEFAULT_ACTIVATE_GROUP

    def is_activate_group(self) -> bool:
        return self.activate_group

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

        reader = Reader(binary, order)

        value = reader.read_u8()

        activate_group = value & activate_group_bit == activate_group_bit
        multi_activate = value & multi_activate_bit == multi_activate_bit

        target_group_id = reader.read_u16()

        trigger_orb.activate_group = activate_group
        trigger_orb.multi_activate = multi_activate

        trigger_orb.target_group_id = target_group_id

        return trigger_orb

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary, order)

        value = 0

        if self.is_activate_group():
            value |= ACTIVATE_GROUP_BIT

        if self.is_multi_activate():
            value |= MULTI_ACTIVATE_BIT

        writer.write_u8(value)

        writer.write_u16(self.target_group_id)

    @classmethod
    def from_robtop_data(cls: Type[TO], data: Mapping[int, str]) -> TO:
        trigger_orb = super().from_robtop_data(data)

        activate_group = parse_get_or(int_bool, DEFAULT_ACTIVATE_GROUP, data.get(ACTIVATE_GROUP))

        target_group_id = parse_get_or(int, DEFAULT_ID, data.get(TARGET_GROUP_ID))

        trigger_orb.activate_group = activate_group

        trigger_orb.target_group_id = target_group_id

        return trigger_orb

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        activate_group = self.is_activate_group()

        if activate_group:
            data[ACTIVATE_GROUP] = bool_str(activate_group)

        data[TARGET_GROUP_ID] = str(self.target_group_id)

        return data


IC = TypeVar("IC", bound="ItemCounter")


@define()
class ItemCounter(Object):
    item_id: int = DEFAULT_ID

    @classmethod
    def from_binary(
        cls: Type[IC],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> IC:
        item_counter = super().from_binary(binary, order, version)

        reader = Reader(binary, order)

        item_id = reader.read_u16()

        item_counter.item_id = item_id

        return item_counter

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary, order)

        writer.write_u16(self.item_id)

    @classmethod
    def from_robtop_data(cls: Type[IC], data: Mapping[int, str]) -> IC:
        item_counter = super().from_robtop_data(data)

        item_id = parse_get_or(int, DEFAULT_ID, data.get(ITEM_ID))

        item_counter.item_id = item_id

        return item_counter

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        item_id = self.item_id

        if item_id:
            data[ITEM_ID] = str(item_id)

        return data


TI = TypeVar("TI", bound="ToggleItem")


@define()
class ToggleItem(Object):
    target_group_id: int = DEFAULT_ID

    activate_group: bool = DEFAULT_ACTIVATE_GROUP

    def is_activate_group(self) -> bool:
        return self.activate_group

    @classmethod
    def from_binary(
        cls: Type[TI],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> TI:
        activate_group_bit = ACTIVATE_GROUP_BIT

        toggle_item = super().from_binary(binary, order, version)

        reader = Reader(binary, order)

        value = reader.read_u8()

        activate_group = value & activate_group_bit == activate_group_bit

        target_group_id = reader.read_u16()

        toggle_item.activate_group = activate_group

        toggle_item.target_group_id = target_group_id

        return toggle_item

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary, order)

        value = 0

        if self.is_activate_group():
            value |= ACTIVATE_GROUP_BIT

        writer.write_u8(value)

        writer.write_u16(self.target_group_id)

    @classmethod
    def from_robtop_data(cls: Type[TI], data: Mapping[int, str]) -> TI:
        toggle_item = super().from_robtop_data(data)

        target_group_id = parse_get_or(int, DEFAULT_ID, data.get(TARGET_GROUP_ID))

        toggle_item.target_group_id = target_group_id

        return toggle_item

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        data[TARGET_GROUP_ID] = str(self.target_group_id)

        data[ITEM_MODE] = str(ItemMode.TOGGLE.value)

        return data


SUBTRACT_COUNT_BIT = 0b00000001

DEFAULT_SUBTRACT_COUNT = False


PI = TypeVar("PI", bound="PickupItem")


@define()
class PickupItem(Object):
    item_id: int = DEFAULT_ID

    subtract_count: bool = DEFAULT_SUBTRACT_COUNT

    def is_subtract_count(self) -> bool:
        return self.subtract_count

    @classmethod
    def from_binary(
        cls: Type[PI],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> PI:
        subtract_count_bit = SUBTRACT_COUNT_BIT

        pickup_item = super().from_binary(binary, order, version)

        reader = Reader(binary, order)

        value = reader.read_u8()

        subtract_count = value & subtract_count_bit == subtract_count_bit

        item_id = reader.read_u16()

        pickup_item.subtract_count = subtract_count

        pickup_item.item_id = item_id

        return pickup_item

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary, order)

        value = 0

        if self.is_subtract_count():
            value |= SUBTRACT_COUNT_BIT

        writer.write_u8(value)

        writer.write_u16(self.item_id)

    @classmethod
    def from_robtop_data(cls: Type[PI], data: Mapping[int, str]) -> PI:
        pickup_item = super().from_robtop_data(data)

        item_id = parse_get_or(int, DEFAULT_ID, data.get(ITEM_ID))

        subtract_count = parse_get_or(int_bool, DEFAULT_SUBTRACT_COUNT, data.get(SUBTRACT_COUNT))

        pickup_item.item_id = item_id

        pickup_item.subtract_count = subtract_count

        return pickup_item

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        subtract_count = self.is_subtract_count()

        if subtract_count:
            data[SUBTRACT_COUNT] = bool_str(subtract_count)

        data[ITEM_ID] = str(self.item_id)

        data[ITEM_MODE] = str(ItemMode.PICKUP.value)

        return data


Item = Union[PickupItem, ToggleItem]


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

        reader = Reader(binary, order)

        value = reader.read_u8()

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

        writer = Writer(binary, order)

        value = 0

        if self.is_touch_triggered():
            value |= TOUCH_TRIGGERED_BIT

        if self.is_spawn_triggered():
            value |= SPAWN_TRIGGERED_BIT

        if self.is_multi_trigger():
            value |= MULTI_TRIGGER_BIT

        writer.write_u8(value)

    def is_trigger(self) -> Literal[True]:
        return True

    def is_touch_triggered(self) -> bool:
        return self.touch_triggered

    def is_spawn_triggered(self) -> bool:
        return self.spawn_triggered

    def is_multi_trigger(self) -> bool:
        return self.multi_trigger

    @classmethod
    def from_robtop_data(cls: Type[T], data: Mapping[int, str]) -> T:
        trigger = super().from_robtop_data(data)

        touch_triggered = parse_get_or(int_bool, DEFAULT_TOUCH_TRIGGERED, data.get(TOUCH_TRIGGERED))
        spawn_triggered = parse_get_or(int_bool, DEFAULT_SPAWN_TRIGGERED, data.get(SPAWN_TRIGGERED))
        multi_trigger = parse_get_or(int_bool, DEFAULT_MULTI_TRIGGER, data.get(MULTI_TRIGGER))

        trigger.touch_triggered = touch_triggered
        trigger.spawn_triggered = spawn_triggered
        trigger.multi_trigger = multi_trigger

        return trigger

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        touch_triggered = self.is_touch_triggered()

        if touch_triggered:
            data[TOUCH_TRIGGERED] = bool_str(touch_triggered)

        spawn_triggered = self.is_spawn_triggered()

        if spawn_triggered:
            data[SPAWN_TRIGGERED] = bool_str(spawn_triggered)

        multi_trigger = self.is_multi_trigger()

        if multi_trigger:
            data[MULTI_TRIGGER] = bool_str(multi_trigger)

        return data


DEFAULT_DURATION = 0.0


BCT = TypeVar("BCT", bound="BaseColorTrigger")


@define()
class BaseColorTrigger(Trigger):
    target_color_id: int = DEFAULT_ID

    duration: float = DEFAULT_DURATION

    @classmethod
    def from_binary(
        cls: Type[BCT],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> BCT:
        rounding = DEFAULT_ROUNDING

        base_color_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary, order)

        target_color_id = reader.read_u16()

        duration = round(reader.read_f32(), rounding)

        base_color_trigger.target_color_id = target_color_id

        base_color_trigger.duration = duration

        return base_color_trigger

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary, order)

        writer.write_u16(self.target_color_id)

        writer.write_f32(self.duration)

    @classmethod
    def from_robtop_data(cls: Type[BCT], data: Mapping[int, str]) -> BCT:
        base_color_trigger = super().from_robtop_data(data)

        target_color_id = parse_get_or(int, DEFAULT_ID, data.get(TARGET_COLOR_ID))

        duration = parse_get_or(float, DEFAULT_DURATION, data.get(DURATION))

        base_color_trigger.target_color_id = target_color_id

        base_color_trigger.duration = duration

        return base_color_trigger

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        data[TARGET_COLOR_ID] = str(self.target_color_id)

        data[DURATION] = float_str(self.duration)

        return data


BLENDING_BIT = 0b00000001
PLAYER_COLOR_MASK = 0b00000110
PLAYER_COLOR_SHIFT = BLENDING_BIT.bit_length()


DEFAULT_PLAYER_COLOR_1 = False
DEFAULT_PLAYER_COLOR_2 = False


def compute_player_color(player_color_1: bool, player_color_2: bool) -> PlayerColor:
    if player_color_1 and player_color_2:
        return PlayerColor.NOT_USED

    if player_color_1:
        return PlayerColor.COLOR_1

    if player_color_2:
        return PlayerColor.COLOR_2

    return PlayerColor.NOT_USED


DEFAULT_BLENDING = False
DEFAULT_OPACITY = 1.0


PLCT = TypeVar("PLCT", bound="PlayerColorTrigger")


@define()
class PlayerColorTrigger(BaseColorTrigger):
    blending: bool = DEFAULT_BLENDING
    opacity: float = DEFAULT_OPACITY

    player_color: PlayerColor = PlayerColor.DEFAULT

    def is_blending(self) -> bool:
        return self.blending

    @classmethod
    def from_binary(
        cls: Type[PLCT],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> PLCT:
        rounding = DEFAULT_ROUNDING

        blending_bit = BLENDING_BIT

        player_color_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary, order)

        value = reader.read_u8()

        blending = value & blending_bit == blending_bit

        player_color_value = (value & PLAYER_COLOR_MASK) >> PLAYER_COLOR_SHIFT

        player_color = PlayerColor(player_color_value)

        opacity = round(reader.read_f32(), rounding)

        player_color_trigger.blending = blending

        player_color_trigger.player_color = player_color

        player_color_trigger.opacity = opacity

        return player_color_trigger

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary, order)

        value = 0

        if self.is_blending():
            value |= BLENDING_BIT

        value |= self.player_color.value << PLAYER_COLOR_SHIFT

        writer.write_u8(value)

        writer.write_f32(self.opacity)

    @classmethod
    def from_robtop_data(cls: Type[PLCT], data: Mapping[int, str]) -> PLCT:
        player_color_trigger = super().from_robtop_data(data)

        blending = parse_get_or(int_bool, DEFAULT_BLENDING, data.get(BLENDING))

        player_color_1 = parse_get_or(int_bool, DEFAULT_PLAYER_COLOR_1, data.get(PLAYER_COLOR_1))
        player_color_2 = parse_get_or(int_bool, DEFAULT_PLAYER_COLOR_2, data.get(PLAYER_COLOR_2))

        player_color = compute_player_color(player_color_1, player_color_2)

        opacity = parse_get_or(float, DEFAULT_OPACITY, data.get(OPACITY))

        player_color_trigger.blending = blending

        player_color_trigger.player_color = player_color

        player_color_trigger.opacity = opacity

        return player_color_trigger

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        blending = self.is_blending()

        if blending:
            data[BLENDING] = bool_str(blending)

        player_color = self.player_color

        player_color_1 = player_color.is_color_1()
        player_color_2 = player_color.is_color_2()

        if player_color_1:
            data[PLAYER_COLOR_1] = bool_str(player_color_1)

        if player_color_2:
            data[PLAYER_COLOR_2] = bool_str(player_color_2)

        data[OPACITY] = float_str(self.opacity)

        return data


DEFAULT_RED = BYTE
DEFAULT_GREEN = BYTE
DEFAULT_BLUE = BYTE


NCT = TypeVar("NCT", bound="NormalColorTrigger")


@define()
class NormalColorTrigger(BaseColorTrigger):
    blending: bool = field(default=DEFAULT_BLENDING)
    opacity: float = field(default=DEFAULT_OPACITY)
    color: Color = field(factory=Color.default)

    def is_blending(self) -> bool:
        return self.blending

    @classmethod
    def from_binary(
        cls: Type[NCT],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> NCT:
        rounding = DEFAULT_ROUNDING

        blending_bit = BLENDING_BIT

        normal_color_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary, order)

        value = reader.read_u32()

        blending = value & blending_bit == blending_bit

        value >>= BITS

        color = Color(value)

        opacity = round(reader.read_f32(), rounding)

        normal_color_trigger.blending = blending
        normal_color_trigger.color = color
        normal_color_trigger.opacity = opacity

        return normal_color_trigger

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary, order)

        value = 0

        if self.is_blending():
            value |= BLENDING_BIT

        value |= self.color.value << BITS

        writer.write_u32(value)

        writer.write_f32(self.opacity)

    @classmethod
    def from_robtop_data(cls: Type[NCT], data: Mapping[int, str]) -> NCT:
        normal_color_trigger = super().from_robtop_data(data)

        blending = parse_get_or(int_bool, DEFAULT_BLENDING, data.get(BLENDING))

        red = parse_get_or(int, DEFAULT_RED, data.get(RED))
        green = parse_get_or(int, DEFAULT_GREEN, data.get(GREEN))
        blue = parse_get_or(int, DEFAULT_BLUE, data.get(BLUE))

        color = Color.from_rgb(red, green, blue)

        opacity = parse_get_or(float, DEFAULT_OPACITY, data.get(OPACITY))

        normal_color_trigger.blending = blending

        normal_color_trigger.color = color

        normal_color_trigger.opacity = opacity

        return normal_color_trigger

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        color = self.color

        actual = {
            RED: str(color.red),
            GREEN: str(color.green),
            BLUE: str(color.blue),
            OPACITY: float_str(self.opacity),
        }

        data.update(actual)

        blending = self.is_blending()

        if blending:
            data[BLENDING] = bool_str(blending)

        return data


COPY_OPACITY_BIT = 0b00000010

DEFAULT_COPY_OPACITY = False


CCT = TypeVar("CCT", bound="CopiedColorTrigger")


@define()
class CopiedColorTrigger(BaseColorTrigger):
    blending: bool = field(default=DEFAULT_BLENDING)

    copied_color_id: int = field(default=DEFAULT_ID)
    copied_color_hsv: HSV = field(factory=HSV)

    opacity: Optional[float] = field(default=None)

    def is_blending(self) -> bool:
        return self.blending

    def is_copy_opacity(self) -> bool:
        return self.opacity is None

    @classmethod
    def from_binary(
        cls: Type[CCT],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> CCT:
        rounding = DEFAULT_ROUNDING

        blending_bit = BLENDING_BIT
        copy_opacity_bit = COPY_OPACITY_BIT

        copied_color_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary, order)

        value = reader.read_u8()

        blending = value & blending_bit == blending_bit
        copy_opacity = value & copy_opacity_bit == copy_opacity_bit

        if copy_opacity:
            opacity = None

        else:
            opacity = round(reader.read_f32(), rounding)

        copied_color_id = reader.read_u16()
        copied_color_hsv = HSV.from_binary(binary, order, version)

        copied_color_trigger.blending = blending
        copied_color_trigger.opacity = opacity

        copied_color_trigger.copied_color_id = copied_color_id
        copied_color_trigger.copied_color_hsv = copied_color_hsv

        return copied_color_trigger

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary, order)

        value = 0

        if self.is_blending():
            value |= BLENDING_BIT

        if self.is_copy_opacity():
            value |= COPY_OPACITY_BIT

        writer.write_u8(value)

        opacity = self.opacity

        if opacity is not None:
            writer.write_f32(opacity)

        writer.write_u16(self.copied_color_id)

        self.copied_color_hsv.to_binary(binary, order, version)

    @classmethod
    def from_robtop_data(cls: Type[CCT], data: Mapping[int, str]) -> CCT:
        copied_color_trigger = super().from_robtop_data(data)

        blending = parse_get_or(int_bool, DEFAULT_BLENDING, data.get(BLENDING))

        copied_color_id = parse_get_or(int, DEFAULT_ID, data.get(COPIED_COLOR_ID))
        copied_color_hsv = parse_get_or_else(HSV.from_robtop, HSV, data.get(COPIED_COLOR_HSV))

        copy_opacity = parse_get_or(int_bool, DEFAULT_COPY_OPACITY, data.get(COPY_OPACITY))

        if copy_opacity:
            opacity = None

        else:
            opacity = parse_get_or(float, DEFAULT_OPACITY, data.get(OPACITY))

        copied_color_trigger.blending = blending

        copied_color_trigger.copied_color_id = copied_color_id
        copied_color_trigger.copied_color_hsv = copied_color_hsv

        copied_color_trigger.opacity = opacity

        return copied_color_trigger

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        actual = {
            COPIED_COLOR_ID: str(self.copied_color_id),
            COPIED_COLOR_HSV: self.copied_color_hsv.to_robtop(),
            COPY_OPACITY: bool_str(self.is_copy_opacity()),
        }

        data.update(actual)

        opacity = self.opacity

        if opacity is not None:
            data[OPACITY] = float_str(opacity)

        blending = self.is_blending()

        if blending:
            data[BLENDING] = bool_str(blending)

        return data


ColorTrigger = Union[PlayerColorTrigger, NormalColorTrigger, CopiedColorTrigger]


# compatibility


@runtime_checkable
class Compatibility(Protocol):
    @required
    def migrate(self) -> Object:
        ...

    def migrate_additional(self) -> Optional[Object]:
        pass


def is_compatibility(object: Object) -> TypeGuard[Compatibility]:
    return is_instance(object, Compatibility)


def migrate_objects(objects: Iterable[Object]) -> Iterator[Object]:
    for object in objects:
        if is_compatibility(object):
            yield object.migrate()

            additional = object.migrate_additional()

            if additional is not None:
                yield additional

        else:
            yield object


MIGRATE = (
    "this is the compatibility color trigger; use `migrate` method to migrate to the newer system"
)


BCMCT = TypeVar("BCMCT", bound="BaseCompatibilityColorTrigger")


class BaseCompatibilityColorTrigger(Compatibility, Trigger):
    duration: float = DEFAULT_DURATION

    @classmethod
    def from_robtop_data(cls: Type[BCMCT], data: Mapping[int, str]) -> BCMCT:
        base_compatibility_color_trigger = super().from_robtop_data(data)

        duration = parse_get_or(float, DEFAULT_DURATION, data.get(DURATION))

        base_compatibility_color_trigger.duration = duration

        return base_compatibility_color_trigger

    def to_robtop_data(self) -> Never:
        raise NotImplementedError(MIGRATE)

    @classmethod
    def from_binary(
        cls: Type[BCMCT],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> Never:
        raise NotImplementedError(MIGRATE)

    def to_binary(
        self,
        binary: BinaryWriter,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> Never:
        raise NotImplementedError(MIGRATE)


PCMCT = TypeVar("PCMCT", bound="PlayerCompatibilityColorTrigger")


@define()
class PlayerCompatibilityColorTrigger(BaseCompatibilityColorTrigger):
    blending: bool = DEFAULT_BLENDING
    opacity: float = DEFAULT_OPACITY

    player_color: PlayerColor = PlayerColor.DEFAULT

    def is_blending(self) -> bool:
        return self.blending

    @classmethod
    def from_robtop_data(cls: Type[PCMCT], data: Mapping[int, str]) -> PCMCT:
        player_compatibility_color_trigger = super().from_robtop_data(data)

        blending = parse_get_or(int_bool, DEFAULT_BLENDING, data.get(BLENDING))
        opacity = parse_get_or(float, DEFAULT_OPACITY, data.get(OPACITY))

        player_color_1 = parse_get_or(int_bool, DEFAULT_PLAYER_COLOR_1, data.get(PLAYER_COLOR_1))
        player_color_2 = parse_get_or(int_bool, DEFAULT_PLAYER_COLOR_2, data.get(PLAYER_COLOR_2))

        player_color = compute_player_color(player_color_1, player_color_2)

        player_compatibility_color_trigger.blending = blending
        player_compatibility_color_trigger.opacity = opacity
        player_compatibility_color_trigger.player_color = player_color

        return player_compatibility_color_trigger

    def generate_migration(self, target_color_id: int) -> PlayerColorTrigger:
        return PlayerColorTrigger(
            id=TriggerType.COLOR.id,  # NOTE: here is the small difference :)
            x=self.x,
            y=self.y,
            h_flipped=self.is_h_flipped(),
            v_flipped=self.is_v_flipped(),
            rotation=self.rotation,
            scale=self.scale,
            do_not_fade=self.has_do_not_fade(),
            do_not_enter=self.has_do_not_enter(),
            z_layer=self.z_layer,
            z_order=self.z_order,
            base_editor_layer=self.base_editor_layer,
            additional_editor_layer=self.additional_editor_layer,
            base_color_id=self.base_color_id,
            detail_color_id=self.detail_color_id,
            base_color_hsv=self.base_color_hsv,
            detail_color_hsv=self.detail_color_hsv,
            groups=self.groups,
            group_parent=self.is_group_parent(),
            high_detail=self.is_high_detail(),
            disable_glow=self.has_disable_glow(),
            special_checked=self.is_special_checked(),
            link_id=self.link_id,
            unknown=self.is_unknown(),
            touch_triggered=self.is_touch_triggered(),
            spawn_triggered=self.is_spawn_triggered(),
            multi_trigger=self.is_multi_trigger(),
            target_color_id=target_color_id,  # NOTE: here is the main difference :p
            duration=self.duration,
            blending=self.is_blending(),
            opacity=self.opacity,
            player_color=self.player_color,
        )


NCMCT = TypeVar("NCMCT", bound="NormalCompatibilityColorTrigger")


@define()
class NormalCompatibilityColorTrigger(BaseCompatibilityColorTrigger):
    blending: bool = field(default=DEFAULT_BLENDING)
    opacity: float = field(default=DEFAULT_OPACITY)
    color: Color = field(factory=Color.default)

    def is_blending(self) -> bool:
        return self.blending

    @classmethod
    def from_robtop_data(cls: Type[NCMCT], data: Mapping[int, str]) -> NCMCT:
        normal_compatibility_color_trigger = super().from_robtop_data(data)

        blending = parse_get_or(int_bool, DEFAULT_BLENDING, data.get(BLENDING))
        opacity = parse_get_or(float, DEFAULT_OPACITY, data.get(OPACITY))

        red = parse_get_or(int, DEFAULT_RED, data.get(RED))
        green = parse_get_or(int, DEFAULT_GREEN, data.get(GREEN))
        blue = parse_get_or(int, DEFAULT_BLUE, data.get(BLUE))

        color = Color.from_rgb(red, green, blue)

        normal_compatibility_color_trigger.blending = blending
        normal_compatibility_color_trigger.opacity = opacity
        normal_compatibility_color_trigger.color = color

        return normal_compatibility_color_trigger

    def generate_migration(self, target_color_id: int) -> NormalColorTrigger:
        return NormalColorTrigger(
            id=TriggerType.COLOR.id,  # NOTE: here is the small difference :)
            x=self.x,
            y=self.y,
            h_flipped=self.is_h_flipped(),
            v_flipped=self.is_v_flipped(),
            rotation=self.rotation,
            scale=self.scale,
            do_not_fade=self.has_do_not_fade(),
            do_not_enter=self.has_do_not_enter(),
            z_layer=self.z_layer,
            z_order=self.z_order,
            base_editor_layer=self.base_editor_layer,
            additional_editor_layer=self.additional_editor_layer,
            base_color_id=self.base_color_id,
            detail_color_id=self.detail_color_id,
            base_color_hsv=self.base_color_hsv,
            detail_color_hsv=self.detail_color_hsv,
            groups=self.groups,
            group_parent=self.is_group_parent(),
            high_detail=self.is_high_detail(),
            disable_glow=self.has_disable_glow(),
            special_checked=self.is_special_checked(),
            link_id=self.link_id,
            unknown=self.is_unknown(),
            touch_triggered=self.is_touch_triggered(),
            spawn_triggered=self.is_spawn_triggered(),
            multi_trigger=self.is_multi_trigger(),
            target_color_id=target_color_id,  # NOTE: here is the main difference :p
            duration=self.duration,
            blending=self.is_blending(),
            opacity=self.opacity,
            color=self.color,
        )


CCMCT = TypeVar("CCMCT", bound="CopiedCompatibilityColorTrigger")


@define()
class CopiedCompatibilityColorTrigger(BaseCompatibilityColorTrigger):
    blending: bool = field(default=DEFAULT_BLENDING)

    copied_color_id: int = field(default=DEFAULT_ID)
    copied_color_hsv: HSV = field(factory=HSV)

    opacity: Optional[float] = field(default=None)

    def is_blending(self) -> bool:
        return self.blending

    def is_copy_opacity(self) -> bool:
        return self.opacity is None

    @classmethod
    def from_robtop_data(cls: Type[CCMCT], data: Mapping[int, str]) -> CCMCT:
        copied_compatibility_color_trigger = super().from_robtop_data(data)

        blending = parse_get_or(int_bool, DEFAULT_BLENDING, data.get(BLENDING))

        copied_color_id = parse_get_or(int, DEFAULT_ID, data.get(COPIED_COLOR_ID))

        copied_color_hsv = parse_get_or_else(HSV.from_robtop, HSV, data.get(COPIED_COLOR_HSV))

        copy_opacity = parse_get_or(int_bool, DEFAULT_COPY_OPACITY, data.get(COPY_OPACITY))

        if copy_opacity:
            opacity = None

        else:
            opacity = parse_get_or(float, DEFAULT_OPACITY, data.get(OPACITY))

        copied_compatibility_color_trigger.blending = blending

        copied_compatibility_color_trigger.copied_color_id = copied_color_id
        copied_compatibility_color_trigger.copied_color_hsv = copied_color_hsv

        copied_compatibility_color_trigger.opacity = opacity

        return copied_compatibility_color_trigger

    def generate_migration(self, target_color_id: int) -> CopiedColorTrigger:
        return CopiedColorTrigger(
            id=TriggerType.COLOR.id,  # NOTE: here is the small difference :)
            x=self.x,
            y=self.y,
            h_flipped=self.is_h_flipped(),
            v_flipped=self.is_v_flipped(),
            rotation=self.rotation,
            scale=self.scale,
            do_not_fade=self.has_do_not_fade(),
            do_not_enter=self.has_do_not_enter(),
            z_layer=self.z_layer,
            z_order=self.z_order,
            base_editor_layer=self.base_editor_layer,
            additional_editor_layer=self.additional_editor_layer,
            base_color_id=self.base_color_id,
            detail_color_id=self.detail_color_id,
            base_color_hsv=self.base_color_hsv,
            detail_color_hsv=self.detail_color_hsv,
            groups=self.groups,
            group_parent=self.is_group_parent(),
            high_detail=self.is_high_detail(),
            disable_glow=self.has_disable_glow(),
            special_checked=self.is_special_checked(),
            link_id=self.link_id,
            unknown=self.is_unknown(),
            touch_triggered=self.is_touch_triggered(),
            spawn_triggered=self.is_spawn_triggered(),
            multi_trigger=self.is_multi_trigger(),
            target_color_id=target_color_id,  # NOTE: here is the main difference :p
            duration=self.duration,
            blending=self.is_blending(),
            copied_color_id=self.copied_color_id,
            copied_color_hsv=self.copied_color_hsv,
            opacity=self.opacity,
        )


CompatibilityColorTrigger = Union[
    PlayerCompatibilityColorTrigger,
    NormalCompatibilityColorTrigger,
    CopiedCompatibilityColorTrigger,
]


DEFAULT_TINT_GROUND = False


PBGT = TypeVar("PBGT", bound="PlayerBackgroundTrigger")


@define()
class PlayerBackgroundTrigger(PlayerCompatibilityColorTrigger):
    tint_ground: bool = DEFAULT_TINT_GROUND

    def is_tint_ground(self) -> bool:
        return self.tint_ground

    @classmethod
    def from_robtop_data(cls: Type[PBGT], data: Mapping[int, str]) -> PBGT:
        player_background_color_trigger = super().from_robtop_data(data)

        tint_ground = parse_get_or(int_bool, DEFAULT_TINT_GROUND, data.get(TINT_GROUND))

        player_background_color_trigger.tint_ground = tint_ground

        return player_background_color_trigger

    def migrate(self) -> PlayerColorTrigger:
        return self.generate_migration(BACKGROUND_COLOR_ID)

    def migrate_additional(self) -> Optional[PlayerColorTrigger]:
        return self.generate_migration(GROUND_COLOR_ID) if self.is_tint_ground() else None


NBGT = TypeVar("NBGT", bound="NormalBackgroundTrigger")


@define()
class NormalBackgroundTrigger(NormalCompatibilityColorTrigger):
    tint_ground: bool = DEFAULT_TINT_GROUND

    def is_tint_ground(self) -> bool:
        return self.tint_ground

    @classmethod
    def from_robtop_data(cls: Type[NBGT], data: Mapping[int, str]) -> NBGT:
        normal_background_color_trigger = super().from_robtop_data(data)

        tint_ground = parse_get_or(int_bool, DEFAULT_TINT_GROUND, data.get(TINT_GROUND))

        normal_background_color_trigger.tint_ground = tint_ground

        return normal_background_color_trigger

    def migrate(self) -> NormalColorTrigger:
        return self.generate_migration(BACKGROUND_COLOR_ID)

    def migrate_additional(self) -> Optional[NormalColorTrigger]:
        return self.generate_migration(GROUND_COLOR_ID) if self.is_tint_ground() else None


CBGT = TypeVar("CBGT", bound="CopiedBackgroundTrigger")


@define()
class CopiedBackgroundTrigger(CopiedCompatibilityColorTrigger):
    tint_ground: bool = DEFAULT_TINT_GROUND

    def is_tint_ground(self) -> bool:
        return self.tint_ground

    @classmethod
    def from_robtop_data(cls: Type[CBGT], data: Mapping[int, str]) -> CBGT:
        copied_background_color_trigger = super().from_robtop_data(data)

        tint_ground = parse_get_or(int_bool, DEFAULT_TINT_GROUND, data.get(TINT_GROUND))

        copied_background_color_trigger.tint_ground = tint_ground

        return copied_background_color_trigger

    def migrate(self) -> CopiedColorTrigger:
        return self.generate_migration(BACKGROUND_COLOR_ID)

    def migrate_additional(self) -> Optional[CopiedColorTrigger]:
        return self.generate_migration(GROUND_COLOR_ID) if self.is_tint_ground() else None


@define()
class PlayerGroundTrigger(PlayerCompatibilityColorTrigger):
    def migrate(self) -> PlayerColorTrigger:
        return self.generate_migration(GROUND_COLOR_ID)


@define()
class NormalGroundTrigger(NormalCompatibilityColorTrigger):
    def migrate(self) -> NormalColorTrigger:
        return self.generate_migration(GROUND_COLOR_ID)


@define()
class CopiedGroundTrigger(CopiedCompatibilityColorTrigger):
    def migrate(self) -> CopiedColorTrigger:
        return self.generate_migration(GROUND_COLOR_ID)


@define()
class PlayerLineTrigger(PlayerCompatibilityColorTrigger):
    def migrate(self) -> PlayerColorTrigger:
        return self.generate_migration(LINE_COLOR_ID)


@define()
class NormalLineTrigger(NormalCompatibilityColorTrigger):
    def migrate(self) -> NormalColorTrigger:
        return self.generate_migration(LINE_COLOR_ID)


@define()
class CopiedLineTrigger(CopiedCompatibilityColorTrigger):
    def migrate(self) -> CopiedColorTrigger:
        return self.generate_migration(LINE_COLOR_ID)


@define()
class PlayerObjectTrigger(PlayerCompatibilityColorTrigger):
    def migrate(self) -> PlayerColorTrigger:
        return self.generate_migration(OBJECT_COLOR_ID)


@define()
class NormalObjectTrigger(NormalCompatibilityColorTrigger):
    def migrate(self) -> NormalColorTrigger:
        return self.generate_migration(OBJECT_COLOR_ID)


@define()
class CopiedObjectTrigger(CopiedCompatibilityColorTrigger):
    def migrate(self) -> CopiedColorTrigger:
        return self.generate_migration(OBJECT_COLOR_ID)


@define()
class PlayerLine3DTrigger(PlayerCompatibilityColorTrigger):
    def migrate(self) -> PlayerColorTrigger:
        return self.generate_migration(LINE_3D_COLOR_ID)


@define()
class NormalLine3DTrigger(NormalCompatibilityColorTrigger):
    def migrate(self) -> NormalColorTrigger:
        return self.generate_migration(LINE_3D_COLOR_ID)


@define()
class CopiedLine3DTrigger(CopiedCompatibilityColorTrigger):
    def migrate(self) -> CopiedColorTrigger:
        return self.generate_migration(LINE_3D_COLOR_ID)


@define()
class PlayerSecondaryGroundTrigger(PlayerCompatibilityColorTrigger):
    def migrate(self) -> PlayerColorTrigger:
        return self.generate_migration(SECONDARY_GROUND_COLOR_ID)


@define()
class NormalSecondaryGroundTrigger(NormalCompatibilityColorTrigger):
    def migrate(self) -> NormalColorTrigger:
        return self.generate_migration(SECONDARY_GROUND_COLOR_ID)


@define()
class CopiedSecondaryGroundTrigger(CopiedCompatibilityColorTrigger):
    def migrate(self) -> CopiedColorTrigger:
        return self.generate_migration(SECONDARY_GROUND_COLOR_ID)


@define()
class PlayerColor1Trigger(PlayerCompatibilityColorTrigger):
    def migrate(self) -> PlayerColorTrigger:
        return self.generate_migration(COLOR_1_ID)


@define()
class NormalColor1Trigger(NormalCompatibilityColorTrigger):
    def migrate(self) -> NormalColorTrigger:
        return self.generate_migration(COLOR_1_ID)


@define()
class CopiedColor1Trigger(CopiedCompatibilityColorTrigger):
    def migrate(self) -> CopiedColorTrigger:
        return self.generate_migration(COLOR_1_ID)


@define()
class PlayerColor2Trigger(PlayerCompatibilityColorTrigger):
    def migrate(self) -> PlayerColorTrigger:
        return self.generate_migration(COLOR_2_ID)


@define()
class NormalColor2Trigger(NormalCompatibilityColorTrigger):
    def migrate(self) -> NormalColorTrigger:
        return self.generate_migration(COLOR_2_ID)


@define()
class CopiedColor2Trigger(CopiedCompatibilityColorTrigger):
    def migrate(self) -> CopiedColorTrigger:
        return self.generate_migration(COLOR_2_ID)


@define()
class PlayerColor3Trigger(PlayerCompatibilityColorTrigger):
    def migrate(self) -> PlayerColorTrigger:
        return self.generate_migration(COLOR_3_ID)


@define()
class NormalColor3Trigger(NormalCompatibilityColorTrigger):
    def migrate(self) -> NormalColorTrigger:
        return self.generate_migration(COLOR_3_ID)


@define()
class CopiedColor3Trigger(CopiedCompatibilityColorTrigger):
    def migrate(self) -> CopiedColorTrigger:
        return self.generate_migration(COLOR_3_ID)


@define()
class PlayerColor4Trigger(PlayerCompatibilityColorTrigger):
    def migrate(self) -> PlayerColorTrigger:
        return self.generate_migration(COLOR_4_ID)


@define()
class NormalColor4Trigger(NormalCompatibilityColorTrigger):
    def migrate(self) -> NormalColorTrigger:
        return self.generate_migration(COLOR_4_ID)


@define()
class CopiedColor4Trigger(CopiedCompatibilityColorTrigger):
    def migrate(self) -> CopiedColorTrigger:
        return self.generate_migration(COLOR_4_ID)


ALT = TypeVar("ALT", bound="AlphaTrigger")


@define()
class AlphaTrigger(Trigger):
    target_group_id: int = DEFAULT_ID
    duration: float = DEFAULT_DURATION
    opacity: float = DEFAULT_OPACITY

    @classmethod
    def from_binary(
        cls: Type[ALT],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> ALT:
        rounding = DEFAULT_ROUNDING

        alpha_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary, order)

        duration = round(reader.read_f32(), rounding)

        target_group_id = reader.read_u16()

        opacity = round(reader.read_f32(), rounding)

        alpha_trigger.duration = duration
        alpha_trigger.target_group_id = target_group_id
        alpha_trigger.opacity = opacity

        return alpha_trigger

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary, order)

        writer.write_f32(self.duration)
        writer.write_u16(self.target_group_id)
        writer.write_f32(self.opacity)

    @classmethod
    def from_robtop_data(cls: Type[ALT], data: Mapping[int, str]) -> ALT:
        alpha_trigger = super().from_robtop_data(data)

        duration = parse_get_or(float, DEFAULT_DURATION, data.get(DURATION))

        target_group_id = parse_get_or(int, DEFAULT_ID, data.get(TARGET_GROUP_ID))

        opacity = parse_get_or(float, DEFAULT_OPACITY, data.get(OPACITY))

        alpha_trigger.duration = duration
        alpha_trigger.target_group_id = target_group_id
        alpha_trigger.opacity = opacity

        return alpha_trigger

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        data[DURATION] = float_str(self.duration)

        data[TARGET_GROUP_ID] = str(self.target_group_id)

        data[OPACITY] = float_str(self.opacity)

        return data


DEFAULT_FADE_IN = 0.0
DEFAULT_HOLD = 0.0
DEFAULT_FADE_OUT = 0.0


BPT = TypeVar("BPT", bound="BasePulseTrigger")


@define()
class BasePulseTrigger(Trigger):
    fade_in: float = DEFAULT_FADE_IN
    hold: float = DEFAULT_HOLD
    fade_out: float = DEFAULT_FADE_OUT

    @classmethod
    def from_binary(
        cls: Type[BPT],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> BPT:
        rounding = DEFAULT_ROUNDING

        pulse_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary, order)

        fade_in = round(reader.read_f32(), rounding)
        hold = round(reader.read_f32(), rounding)
        fade_out = round(reader.read_f32(), rounding)

        pulse_trigger.fade_in = fade_in
        pulse_trigger.hold = hold
        pulse_trigger.fade_out = fade_out

        return pulse_trigger

    def to_binary(
        self,
        binary: BinaryWriter,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary, order)

        writer.write_f32(self.fade_in)
        writer.write_f32(self.hold)
        writer.write_f32(self.fade_out)

    @classmethod
    def from_robtop_data(cls: Type[BPT], data: Mapping[int, str]) -> BPT:
        base_pulse_trigger = super().from_robtop_data(data)

        fade_in = parse_get_or(float, DEFAULT_FADE_IN, data.get(FADE_IN))
        hold = parse_get_or(float, DEFAULT_HOLD, data.get(HOLD))
        fade_out = parse_get_or(float, DEFAULT_FADE_OUT, data.get(FADE_OUT))

        base_pulse_trigger.fade_in = fade_in
        base_pulse_trigger.hold = hold
        base_pulse_trigger.fade_out = fade_out

        return base_pulse_trigger

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        actual = {
            FADE_IN: float_str(self.fade_in),
            HOLD: float_str(self.hold),
            FADE_OUT: float_str(self.fade_out),
        }

        data.update(actual)

        return data


DEFAULT_EXCLUSIVE = False


EXCLUSIVE_BIT = 0b00000001


PCT = TypeVar("PCT", bound="PulseColorTrigger")


@define()
class PulseColorTrigger(BasePulseTrigger):
    exclusive: bool = field(default=DEFAULT_EXCLUSIVE)

    color: Color = field(factory=Color.default)

    def is_exclusive(self) -> bool:
        return self.exclusive

    @classmethod
    def from_binary(
        cls: Type[PCT],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> PCT:
        exclusive_bit = EXCLUSIVE_BIT

        pulse_color_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary, order)

        value = reader.read_u32()

        exclusive = value & exclusive_bit == exclusive_bit

        value >>= BITS

        color = Color(value)

        pulse_color_trigger.color = color
        pulse_color_trigger.exclusive = exclusive

        return pulse_color_trigger

    def to_binary(
        self,
        binary: BinaryWriter,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary, order)

        value = 0

        if self.is_exclusive():
            value |= EXCLUSIVE_BIT

        value |= self.color.value << BITS

        writer.write_u32(value)

    @classmethod
    def from_robtop_data(cls: Type[PCT], data: Mapping[int, str]) -> PCT:
        pulse_color_trigger = super().from_robtop_data(data)

        red = parse_get_or(int, DEFAULT_RED, data.get(RED))
        green = parse_get_or(int, DEFAULT_GREEN, data.get(GREEN))
        blue = parse_get_or(int, DEFAULT_BLUE, data.get(BLUE))

        color = Color.from_rgb(red, green, blue)

        exclusive = parse_get_or(int_bool, DEFAULT_EXCLUSIVE, data.get(EXCLUSIVE))

        pulse_color_trigger.color = color
        pulse_color_trigger.exclusive = exclusive

        return pulse_color_trigger

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        color = self.color

        actual = {
            RED: str(color.red),
            GREEN: str(color.green),
            BLUE: str(color.blue),
            PULSE_MODE: str(PulseMode.COLOR.value),
        }

        data.update(actual)

        exclusive = self.is_exclusive()

        if exclusive:
            data[EXCLUSIVE] = bool_str(exclusive)

        return data


PHT = TypeVar("PHT", bound="PulseHSVTrigger")


@define()
class PulseHSVTrigger(BasePulseTrigger):
    exclusive: bool = field(default=DEFAULT_EXCLUSIVE)

    copied_color_id: int = field(default=DEFAULT_ID)
    copied_color_hsv: HSV = field(factory=HSV)

    def is_exclusive(self) -> bool:
        return self.exclusive

    @classmethod
    def from_binary(
        cls: Type[PHT],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> PHT:
        exclusive_bit = EXCLUSIVE_BIT

        pulse_hsv_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary, order)

        copied_color_id = reader.read_u16()
        copied_color_hsv = HSV.from_binary(binary, order, version)

        value = reader.read_u8()

        exclusive = value & exclusive_bit == exclusive_bit

        pulse_hsv_trigger.copied_color_id = copied_color_id
        pulse_hsv_trigger.copied_color_hsv = copied_color_hsv

        pulse_hsv_trigger.exclusive = exclusive

        return pulse_hsv_trigger

    def to_binary(
        self,
        binary: BinaryWriter,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary, order)

        writer.write_u16(self.copied_color_id)
        self.copied_color_hsv.to_binary(binary, order, version)

        value = 0

        if self.is_exclusive():
            value |= EXCLUSIVE_BIT

        writer.write_u8(value)

    @classmethod
    def from_robtop_data(cls: Type[PHT], data: Mapping[int, str]) -> PHT:
        pulse_hsv_trigger = super().from_robtop_data(data)

        copied_color_id = parse_get_or(int, DEFAULT_ID, data.get(COPIED_COLOR_ID))
        copied_color_hsv = parse_get_or_else(HSV.from_robtop, HSV, data.get(COPIED_COLOR_HSV))

        exclusive = parse_get_or(int_bool, DEFAULT_EXCLUSIVE, data.get(EXCLUSIVE))

        pulse_hsv_trigger.copied_color_id = copied_color_id
        pulse_hsv_trigger.copied_color_hsv = copied_color_hsv

        pulse_hsv_trigger.exclusive = exclusive

        return pulse_hsv_trigger

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        actual = {
            COPIED_COLOR_ID: str(self.copied_color_id),
            COPIED_COLOR_HSV: self.copied_color_hsv.to_robtop(),
            PULSE_MODE: str(PulseMode.HSV.value),
        }

        data.update(actual)

        exclusive = self.is_exclusive()

        if exclusive:
            data[EXCLUSIVE] = bool_str(exclusive)

        return data


PCCT = TypeVar("PCCT", bound="PulseColorChannelTrigger")


@define()
class PulseColorChannelTrigger(PulseColorTrigger):
    target_color_id: int = DEFAULT_ID

    @classmethod
    def from_binary(
        cls: Type[PCCT],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> PCCT:
        pulse_color_channel_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary, order)

        target_color_id = reader.read_u16()

        pulse_color_channel_trigger.target_color_id = target_color_id

        return pulse_color_channel_trigger

    def to_binary(
        self,
        binary: BinaryWriter,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary, order)

        writer.write_u16(self.target_color_id)

    @classmethod
    def from_robtop_data(cls: Type[PCCT], data: Mapping[int, str]) -> PCCT:
        pulse_color_channel_trigger = super().from_robtop_data(data)

        target_color_id = parse_get_or(int, DEFAULT_ID, data.get(TARGET_GROUP_ID))  # XXX: why?

        pulse_color_channel_trigger.target_color_id = target_color_id

        return pulse_color_channel_trigger

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        data[TARGET_GROUP_ID] = str(self.target_color_id)  # XXX: why?
        data[PULSE_TARGET_TYPE] = str(PulseTargetType.COLOR_CHANNEL.value)

        return data


PHCT = TypeVar("PHCT", bound="PulseHSVChannelTrigger")


@define()
class PulseHSVChannelTrigger(PulseHSVTrigger):
    target_color_id: int = DEFAULT_ID

    @classmethod
    def from_binary(
        cls: Type[PHCT],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> PHCT:
        pulse_hsv_channel_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary, order)

        target_color_id = reader.read_u16()

        pulse_hsv_channel_trigger.target_color_id = target_color_id

        return pulse_hsv_channel_trigger

    def to_binary(
        self,
        binary: BinaryWriter,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary, order)

        writer.write_u16(self.target_color_id)

    @classmethod
    def from_robtop_data(cls: Type[PHCT], data: Mapping[int, str]) -> PHCT:
        pulse_hsv_channel_trigger = super().from_robtop_data(data)

        target_color_id = parse_get_or(int, DEFAULT_ID, data.get(TARGET_GROUP_ID))  # XXX: why?

        pulse_hsv_channel_trigger.target_color_id = target_color_id

        return pulse_hsv_channel_trigger

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        data[TARGET_GROUP_ID] = str(self.target_color_id)  # XXX: why?
        data[PULSE_TARGET_TYPE] = str(PulseTargetType.COLOR_CHANNEL.value)

        return data


DEFAULT_MAIN_ONLY = False
DEFAULT_DETAIL_ONLY = False


def compute_pulse_type(main_only: bool, detail_only: bool) -> PulseType:
    if main_only ^ detail_only:
        if main_only:
            return PulseType.MAIN

        return PulseType.DETAIL

    return PulseType.BOTH


PCGT = TypeVar("PCGT", bound="PulseColorGroupTrigger")


@define()
class PulseColorGroupTrigger(PulseColorTrigger):
    target_group_id: int = DEFAULT_ID
    pulse_type: PulseType = PulseType.DEFAULT

    @classmethod
    def from_binary(
        cls: Type[PCGT],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> PCGT:
        pulse_color_group_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary, order)

        target_group_id = reader.read_u16()

        pulse_type_value = reader.read_u8()

        pulse_type = PulseType(pulse_type_value)

        pulse_color_group_trigger.target_group_id = target_group_id

        pulse_color_group_trigger.pulse_type = pulse_type

        return pulse_color_group_trigger

    def to_binary(
        self,
        binary: BinaryWriter,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary, order)

        writer.write_u16(self.target_group_id)

        writer.write_u8(self.pulse_type.value)

    @classmethod
    def from_robtop_data(cls: Type[PCGT], data: Mapping[int, str]) -> PCGT:
        pulse_color_group_trigger = super().from_robtop_data(data)

        target_group_id = parse_get_or(int, DEFAULT_ID, data.get(TARGET_GROUP_ID))

        main_only = parse_get_or(int_bool, DEFAULT_MAIN_ONLY, data.get(MAIN_ONLY))
        detail_only = parse_get_or(int_bool, DEFAULT_DETAIL_ONLY, data.get(DETAIL_ONLY))

        pulse_type = compute_pulse_type(main_only, detail_only)

        pulse_color_group_trigger.target_group_id = target_group_id

        pulse_color_group_trigger.pulse_type = pulse_type

        return pulse_color_group_trigger

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        data[TARGET_GROUP_ID] = str(self.target_group_id)
        data[PULSE_TARGET_TYPE] = str(PulseTargetType.GROUP.value)

        main_only = self.pulse_type.is_main_only()
        detail_only = self.pulse_type.is_detail_only()

        if main_only:
            data[MAIN_ONLY] = bool_str(main_only)

        if detail_only:
            data[DETAIL_ONLY] = bool_str(detail_only)

        return data


PHGT = TypeVar("PHGT", bound="PulseHSVGroupTrigger")


@define()
class PulseHSVGroupTrigger(PulseHSVTrigger):
    target_group_id: int = DEFAULT_ID

    pulse_type: PulseType = PulseType.DEFAULT

    @classmethod
    def from_binary(
        cls: Type[PHGT],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> PHGT:
        pulse_hsv_group_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary, order)

        target_group_id = reader.read_u16()

        pulse_type_value = reader.read_u8()

        pulse_type = PulseType(pulse_type_value)

        pulse_hsv_group_trigger.target_group_id = target_group_id

        pulse_hsv_group_trigger.pulse_type = pulse_type

        return pulse_hsv_group_trigger

    def to_binary(
        self,
        binary: BinaryWriter,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary, order)

        writer.write_u16(self.target_group_id)

        writer.write_u8(self.pulse_type.value)

    @classmethod
    def from_robtop_data(cls: Type[PHGT], data: Mapping[int, str]) -> PHGT:
        pulse_hsv_group_trigger = super().from_robtop_data(data)

        target_group_id = parse_get_or(int, DEFAULT_ID, data.get(TARGET_GROUP_ID))

        main_only = parse_get_or(int_bool, DEFAULT_MAIN_ONLY, data.get(MAIN_ONLY))
        detail_only = parse_get_or(int_bool, DEFAULT_DETAIL_ONLY, data.get(DETAIL_ONLY))

        pulse_type = compute_pulse_type(main_only, detail_only)

        pulse_hsv_group_trigger.target_group_id = target_group_id

        pulse_hsv_group_trigger.pulse_type = pulse_type

        return pulse_hsv_group_trigger

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        data[TARGET_GROUP_ID] = str(self.target_group_id)
        data[PULSE_TARGET_TYPE] = str(PulseTargetType.GROUP.value)

        main_only = self.pulse_type.is_main_only()
        detail_only = self.pulse_type.is_detail_only()

        if main_only:
            data[MAIN_ONLY] = bool_str(main_only)

        if detail_only:
            data[DETAIL_ONLY] = bool_str(detail_only)

        return data


PulseTrigger = Union[
    PulseColorChannelTrigger,
    PulseHSVChannelTrigger,
    PulseColorGroupTrigger,
    PulseHSVGroupTrigger,
]


DEFAULT_EASING_RATE = 2.0


BMT = TypeVar("BMT", bound="BaseMoveTrigger")


@define()
class BaseMoveTrigger(Trigger):
    target_group_id: int = DEFAULT_ID

    easing: Easing = Easing.DEFAULT
    easing_rate: float = DEFAULT_EASING_RATE

    duration: float = DEFAULT_DURATION

    @classmethod
    def from_binary(
        cls: Type[BMT],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> BMT:
        rounding = DEFAULT_ROUNDING

        base_move_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary, order)

        duration = round(reader.read_f32(), rounding)

        easing_value = reader.read_u8()

        easing = Easing(easing_value)

        easing_rate = round(reader.read_f32(), rounding)

        target_group_id = reader.read_u16()

        base_move_trigger.duration = duration

        base_move_trigger.easing = easing
        base_move_trigger.easing_rate = easing_rate

        base_move_trigger.target_group_id = target_group_id

        return base_move_trigger

    def to_binary(
        self,
        binary: BinaryWriter,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary, order)

        writer.write_f32(self.duration)

        writer.write_u8(self.easing.value)
        writer.write_f32(self.easing_rate)

        writer.write_u16(self.target_group_id)

    @classmethod
    def from_robtop_data(cls: Type[BMT], data: Mapping[int, str]) -> BMT:
        base_move_trigger = super().from_robtop_data(data)

        duration = parse_get_or(float, DEFAULT_DURATION, data.get(DURATION))

        easing = parse_get_or(partial_parse_enum(int, Easing), Easing.DEFAULT, data.get(EASING))
        easing_rate = parse_get_or(float, DEFAULT_EASING_RATE, data.get(EASING_RATE))

        target_group_id = parse_get_or(int, DEFAULT_ID, data.get(TARGET_GROUP_ID))

        base_move_trigger.duration = duration

        base_move_trigger.easing = easing
        base_move_trigger.easing_rate = easing_rate

        base_move_trigger.target_group_id = target_group_id

        return base_move_trigger

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        actual = {
            DURATION: float_str(self.duration),
            EASING: str(self.easing.value),
            EASING_RATE: float_str(self.easing_rate),
            TARGET_GROUP_ID: str(self.target_group_id),
        }

        data.update(actual)

        return data

    def is_normal(self) -> bool:
        return False

    def is_target(self) -> bool:
        return False


DEFAULT_X_OFFSET = 0.0
DEFAULT_Y_OFFSET = 0.0

DEFAULT_LOCKED_TO_PLAYER_X = False
DEFAULT_LOCKED_TO_PLAYER_Y = False


NMT = TypeVar("NMT", bound="NormalMoveTrigger")


@define()
class NormalMoveTrigger(BaseMoveTrigger):
    x_offset: float = DEFAULT_X_OFFSET
    y_offset: float = DEFAULT_Y_OFFSET

    locked_to_player: LockedType = LockedType.DEFAULT

    @classmethod
    def from_binary(
        cls: Type[NMT],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> NMT:
        rounding = DEFAULT_ROUNDING

        normal_move_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary, order)

        x_offset = round(reader.read_f32(), rounding)
        y_offset = round(reader.read_f32(), rounding)

        locked_to_player_value = reader.read_u8()

        locked_to_player = LockedType(locked_to_player_value)

        normal_move_trigger.x_offset = x_offset
        normal_move_trigger.y_offset = y_offset

        normal_move_trigger.locked_to_player = locked_to_player

        return normal_move_trigger

    def to_binary(
        self,
        binary: BinaryWriter,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary, order)

        writer.write_f32(self.x_offset)
        writer.write_f32(self.y_offset)

        writer.write_u8(self.locked_to_player.value)

    @classmethod
    def from_robtop_data(cls: Type[NMT], data: Mapping[int, str]) -> NMT:
        normal_move_trigger = super().from_robtop_data(data)

        x_offset = parse_get_or(float, DEFAULT_X_OFFSET, data.get(X_OFFSET))
        y_offset = parse_get_or(float, DEFAULT_Y_OFFSET, data.get(Y_OFFSET))

        locked_to_player_x = parse_get_or(
            bool, DEFAULT_LOCKED_TO_PLAYER_X, data.get(LOCKED_TO_PLAYER_X)
        )

        locked_to_player_y = parse_get_or(
            bool, DEFAULT_LOCKED_TO_PLAYER_Y, data.get(LOCKED_TO_PLAYER_Y)
        )

        locked_to_player = LockedType.NONE

        if locked_to_player_x:
            locked_to_player |= LockedType.X

        if locked_to_player_y:
            locked_to_player |= LockedType.Y

        normal_move_trigger.x_offset = x_offset
        normal_move_trigger.y_offset = y_offset

        normal_move_trigger.locked_to_player = locked_to_player

        return normal_move_trigger

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        data[X_OFFSET] = float_str(self.x_offset)
        data[Y_OFFSET] = float_str(self.y_offset)

        locked_to_player = self.locked_to_player

        locked_to_player_x = locked_to_player.x()

        if locked_to_player_x:
            data[LOCKED_TO_PLAYER_X] = bool_str(locked_to_player_x)

        locked_to_player_y = locked_to_player.y()

        if locked_to_player_y:
            data[LOCKED_TO_PLAYER_Y] = bool_str(locked_to_player_y)

        return data

    def move_offset(
        self: NMT, x_offset: float = DEFAULT_X_OFFSET, y_offset: float = DEFAULT_Y_OFFSET
    ) -> NMT:
        self.x_offset += x_offset
        self.y_offset += y_offset

        return self


USE_TARGET_TRUE = True


TMT = TypeVar("TMT", bound="TargetMoveTrigger")


@define()
class TargetMoveTrigger(BaseMoveTrigger):
    additional_group_id: int = DEFAULT_ID

    target_type: TargetType = TargetType.DEFAULT

    @classmethod
    def from_binary(
        cls: Type[TMT],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> TMT:
        target_move_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary, order)

        additional_group_id = reader.read_u16()

        target_type_value = reader.read_u8()

        target_type = TargetType(target_type_value)

        target_move_trigger.additional_group_id = additional_group_id

        target_move_trigger.target_type = target_type

        return target_move_trigger

    def to_binary(
        self,
        binary: BinaryWriter,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary, order)

        writer.write_u16(self.additional_group_id)

        writer.write_u8(self.target_type.value)

    @classmethod
    def from_robtop_data(cls: Type[TMT], data: Mapping[int, str]) -> TMT:
        target_move_trigger = super().from_robtop_data(data)

        additional_group_id = parse_get_or(int, DEFAULT_ID, data.get(ADDITIONAL_GROUP_ID))

        simple_target_type = parse_get_or(
            partial_parse_enum(int, SimpleTargetType),
            SimpleTargetType.DEFAULT,
            data.get(TARGET_TYPE),
        )

        target_type = simple_target_type.into_target_type()

        target_move_trigger.additional_group_id = additional_group_id

        target_move_trigger.target_type = target_type

        return target_move_trigger

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        data[ADDITIONAL_GROUP_ID] = str(self.additional_group_id)

        simple_target_type = self.target_type.into_simple_target_type()

        data[TARGET_TYPE] = str(simple_target_type.value)

        data[USE_TARGET] = bool_str(USE_TARGET_TRUE)

        return data


MoveTrigger = Union[NormalMoveTrigger, TargetMoveTrigger]


DEFAULT_DELAY = 0.0
DEFAULT_EDITOR_DISABLE = False


EDITOR_DISABLE_BIT = 0b00000001


SPT = TypeVar("SPT", bound="SpawnTrigger")


@define()
class SpawnTrigger(Trigger):
    target_group_id: int = DEFAULT_ID

    delay: float = DEFAULT_DELAY

    editor_disable: bool = DEFAULT_EDITOR_DISABLE

    @classmethod
    def from_binary(
        cls: Type[SPT],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> SPT:
        rounding = DEFAULT_ROUNDING

        editor_disable_bit = EDITOR_DISABLE_BIT

        spawn_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary, order)

        target_group_id = reader.read_u16()

        delay = round(reader.read_f32(), rounding)

        value = reader.read_u8()

        editor_disable = value & editor_disable_bit == editor_disable_bit

        spawn_trigger.target_group_id = target_group_id

        spawn_trigger.delay = delay

        spawn_trigger.editor_disable = editor_disable

        return spawn_trigger

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary, order)

        writer.write_u16(self.target_group_id)

        writer.write_f32(self.delay)

        value = 0

        if self.is_editor_disable():
            value |= EDITOR_DISABLE_BIT

        writer.write_u8(value)

    def is_editor_disable(self) -> bool:
        return self.editor_disable

    @classmethod
    def from_robtop_data(cls: Type[SPT], data: Mapping[int, str]) -> SPT:
        spawn_trigger = super().from_robtop_data(data)

        target_group_id = parse_get_or(int, DEFAULT_ID, data.get(TARGET_GROUP_ID))

        delay = parse_get_or(float, DEFAULT_DELAY, data.get(SPAWN_DELAY))

        editor_disable = parse_get_or(int_bool, DEFAULT_EDITOR_DISABLE, data.get(EDITOR_DISABLE))

        spawn_trigger.target_group_id = target_group_id

        spawn_trigger.delay = delay

        spawn_trigger.editor_disable = editor_disable

        return spawn_trigger

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        data[TARGET_GROUP_ID] = str(self.target_group_id)

        data[SPAWN_DELAY] = float_str(self.delay)

        editor_disable = self.is_editor_disable()

        if editor_disable:
            data[EDITOR_DISABLE] = bool_str(editor_disable)

        return data


ST = TypeVar("ST", bound="StopTrigger")


@define()
class StopTrigger(Trigger):
    target_group_id: int = DEFAULT_ID

    @classmethod
    def from_binary(
        cls: Type[ST],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> ST:
        stop_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary, order)

        target_group_id = reader.read_u16()

        stop_trigger.target_group_id = target_group_id

        return stop_trigger

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary, order)

        writer.write_u16(self.target_group_id)

    @classmethod
    def from_robtop_data(cls: Type[ST], data: Mapping[int, str]) -> ST:
        stop_trigger = super().from_robtop_data(data)

        target_group_id = parse_get_or(int, DEFAULT_ID, data.get(TARGET_GROUP_ID))

        stop_trigger.target_group_id = target_group_id

        return stop_trigger

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        data[TARGET_GROUP_ID] = str(self.target_group_id)

        return data


ACTIVATE_GROUP_BIT = 0b00000001


DEFAULT_TOGGLED = False


TT = TypeVar("TT", bound="ToggleTrigger")


@define()
class ToggleTrigger(Trigger):
    target_group_id: int = DEFAULT_ID

    activate_group: bool = DEFAULT_ACTIVATE_GROUP

    def is_activate_group(self) -> bool:
        return self.activate_group

    @classmethod
    def from_binary(
        cls: Type[TT],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> TT:
        activate_group_bit = ACTIVATE_GROUP_BIT

        toggle_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary, order)

        target_group_id = reader.read_u16()

        value = reader.read_u8()

        activate_group = value & activate_group_bit == activate_group_bit

        toggle_trigger.target_group_id = target_group_id

        toggle_trigger.activate_group = activate_group

        return toggle_trigger

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary, order)

        writer.write_u16(self.target_group_id)

        value = 0

        if self.is_activate_group():
            value |= ACTIVATE_GROUP_BIT

        writer.write_u8(value)

    def toggle(self: TT) -> TT:
        self.activate_group = not self.activate_group

        return self

    @classmethod
    def from_robtop_data(cls: Type[TT], data: Mapping[int, str]) -> TT:
        toggle_trigger = super().from_robtop_data(data)

        target_group_id = parse_get_or(int, DEFAULT_ID, data.get(TARGET_GROUP_ID))

        activate_group = parse_get_or(int_bool, DEFAULT_ACTIVATE_GROUP, data.get(ACTIVATE_GROUP))

        toggle_trigger.target_group_id = target_group_id

        toggle_trigger.activate_group = activate_group

        return toggle_trigger

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        data[TARGET_GROUP_ID] = str(self.target_group_id)

        activate_group = self.is_activate_group()

        if activate_group:
            data[ACTIVATE_GROUP] = bool_str(activate_group)

        return data


FULL_ROTATION = 360.0

ROTATION_LOCKED_BIT = 0b00000001


DEFAULT_ROTATIONS = 0.0
DEFAULT_DEGREES = 0.0


DEFAULT_TARGET_ROTATION = 0.0
DEFAULT_ROTATION_LOCKED = False


RT = TypeVar("RT", bound="RotateTrigger")


@define()
class RotateTrigger(Trigger):
    target_group_id: int = DEFAULT_ID
    additional_group_id: int = DEFAULT_ID

    duration: float = DEFAULT_DURATION

    easing: Easing = Easing.DEFAULT
    easing_rate: float = DEFAULT_EASING_RATE

    target_rotation: float = DEFAULT_TARGET_ROTATION
    rotation_locked: bool = DEFAULT_ROTATION_LOCKED

    @classmethod
    def from_binary(
        cls: Type[RT],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> RT:
        rounding = DEFAULT_ROUNDING

        rotation_locked_bit = ROTATION_LOCKED_BIT

        rotate_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary, order)

        duration = round(reader.read_f32(), rounding)

        target_group_id = reader.read_u16()
        additional_group_id = reader.read_u16()

        easing_value = reader.read_u8()

        easing = Easing(easing_value)

        easing_rate = round(reader.read_f32(), rounding)

        target_rotation = round(reader.read_f32(), rounding)

        value = reader.read_u8()

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

        writer = Writer(binary, order)

        writer.write_f32(self.duration)

        writer.write_u16(self.target_group_id)
        writer.write_u16(self.additional_group_id)

        writer.write_u8(self.easing.value)
        writer.write_f32(self.easing_rate)

        writer.write_f32(self.target_rotation)

        value = 0

        if self.is_rotation_locked():
            value |= ROTATION_LOCKED_BIT

        writer.write_u8(value)

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
    def from_robtop_data(cls: Type[RT], data: Mapping[int, str]) -> RT:
        rotate_trigger = super().from_robtop_data(data)

        duration = parse_get_or(float, DEFAULT_DURATION, data.get(DURATION))

        target_group_id = parse_get_or(int, DEFAULT_ID, data.get(TARGET_GROUP_ID))
        additional_group_id = parse_get_or(int, DEFAULT_ID, data.get(ADDITIONAL_GROUP_ID))

        easing = parse_get_or(partial_parse_enum(int, Easing), Easing.DEFAULT, data.get(EASING))
        easing_rate = parse_get_or(float, DEFAULT_EASING_RATE, data.get(EASING_RATE))

        rotations = parse_get_or(float, DEFAULT_ROTATIONS, data.get(ROTATIONS))

        degrees = parse_get_or(float, DEFAULT_DEGREES, data.get(DEGREES))

        target_rotation = rotations * FULL_ROTATION + degrees

        rotation_locked = parse_get_or(int_bool, DEFAULT_ROTATION_LOCKED, data.get(ROTATION_LOCKED))

        rotate_trigger.duration = duration

        rotate_trigger.target_group_id = target_group_id
        rotate_trigger.additional_group_id = additional_group_id

        rotate_trigger.easing = easing
        rotate_trigger.easing_rate = easing_rate

        rotate_trigger.target_rotation = target_rotation

        rotate_trigger.rotation_locked = rotation_locked

        return rotate_trigger

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        data[DURATION] = float_str(self.duration)

        data[TARGET_GROUP_ID] = str(self.target_group_id)
        data[ADDITIONAL_GROUP_ID] = str(self.additional_group_id)

        data[EASING] = str(self.easing.value)
        data[EASING_RATE] = float_str(self.easing_rate)

        rotations, degrees = divmod(self.target_rotation, FULL_ROTATION)

        data[ROTATIONS] = str(rotations)
        data[DEGREES] = str(degrees)

        rotation_locked = self.is_rotation_locked()

        if rotation_locked:
            data[ROTATION_LOCKED] = bool_str(rotation_locked)

        return data


DEFAULT_X_MODIFIER = 1.0
DEFAULT_Y_MODIFIER = 1.0


FT = TypeVar("FT", bound="FollowTrigger")


@define()
class FollowTrigger(Trigger):
    target_group_id: int = DEFAULT_ID
    additional_group_id: int = DEFAULT_ID

    duration: float = DEFAULT_DURATION

    easing: Easing = Easing.DEFAULT
    easing_rate: float = DEFAULT_EASING_RATE

    x_modifier: float = DEFAULT_X_MODIFIER
    y_modifier: float = DEFAULT_Y_MODIFIER

    @classmethod
    def from_binary(
        cls: Type[FT],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> FT:
        rounding = DEFAULT_ROUNDING

        follow_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary, order)

        duration = round(reader.read_f32(), rounding)

        target_group_id = reader.read_u16()
        additional_group_id = reader.read_u16()

        easing_value = reader.read_u8()

        easing = Easing(easing_value)

        easing_rate = round(reader.read_f32(), rounding)

        x_modifier = round(reader.read_f32(), rounding)
        y_modifier = round(reader.read_f32(), rounding)

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

        writer = Writer(binary, order)

        writer.write_f32(self.duration)

        writer.write_u16(self.target_group_id)
        writer.write_u16(self.additional_group_id)

        writer.write_u8(self.easing.value)
        writer.write_f32(self.easing_rate)

        writer.write_f32(self.x_modifier)
        writer.write_f32(self.y_modifier)

    @classmethod
    def from_robtop_data(cls: Type[FT], data: Mapping[int, str]) -> FT:
        follow_trigger = super().from_robtop_data(data)

        duration = parse_get_or(float, DEFAULT_DURATION, data.get(DURATION))

        target_group_id = parse_get_or(int, DEFAULT_ID, data.get(TARGET_GROUP_ID))
        additional_group_id = parse_get_or(int, DEFAULT_ID, data.get(ADDITIONAL_GROUP_ID))

        easing = parse_get_or(partial_parse_enum(int, Easing), Easing.DEFAULT, data.get(EASING))
        easing_rate = parse_get_or(float, DEFAULT_EASING_RATE, data.get(EASING_RATE))

        x_modifier = parse_get_or(float, DEFAULT_X_MODIFIER, data.get(X_MODIFIER))
        y_modifier = parse_get_or(float, DEFAULT_Y_MODIFIER, data.get(Y_MODIFIER))

        follow_trigger.duration = duration

        follow_trigger.target_group_id = target_group_id
        follow_trigger.additional_group_id = additional_group_id

        follow_trigger.easing = easing
        follow_trigger.easing_rate = easing_rate

        follow_trigger.x_modifier = x_modifier
        follow_trigger.y_modifier = y_modifier

        return follow_trigger

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        data[DURATION] = float_str(self.duration)

        data[TARGET_GROUP_ID] = str(self.target_group_id)
        data[ADDITIONAL_GROUP_ID] = str(self.additional_group_id)

        data[EASING] = str(self.easing.value)
        data[EASING_RATE] = float_str(self.easing_rate)

        data[X_MODIFIER] = float_str(self.x_modifier)
        data[Y_MODIFIER] = float_str(self.y_modifier)

        return data


DEFAULT_STRENGTH = 0.0
DEFAULT_INTERVAL = 0.0


SHT = TypeVar("SHT", bound="ShakeTrigger")


@define()
class ShakeTrigger(Trigger):
    duration: float = DEFAULT_DURATION
    strength: float = DEFAULT_STRENGTH
    interval: float = DEFAULT_INTERVAL

    @classmethod
    def from_binary(
        cls: Type[SHT],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> SHT:
        rounding = DEFAULT_ROUNDING

        shake_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary, order)

        duration = round(reader.read_f32(), rounding)
        strength = round(reader.read_f32(), rounding)
        interval = round(reader.read_f32(), rounding)

        shake_trigger.duration = duration
        shake_trigger.strength = strength
        shake_trigger.interval = interval

        return shake_trigger

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary, order)

        writer.write_f32(self.duration)
        writer.write_f32(self.strength)
        writer.write_f32(self.interval)

    @classmethod
    def from_robtop_data(cls: Type[SHT], data: Mapping[int, str]) -> SHT:
        shake_trigger = super().from_robtop_data(data)

        duration = parse_get_or(float, DEFAULT_DURATION, data.get(DURATION))
        strength = parse_get_or(float, DEFAULT_STRENGTH, data.get(STRENGTH))
        interval = parse_get_or(float, DEFAULT_INTERVAL, data.get(INTERVAL))

        shake_trigger.duration = duration
        shake_trigger.strength = strength
        shake_trigger.interval = interval

        return shake_trigger

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        data[DURATION] = float_str(self.duration)
        data[STRENGTH] = float_str(self.strength)
        data[INTERVAL] = float_str(self.interval)

        return data


AT = TypeVar("AT", bound="AnimateTrigger")


@define()
class AnimateTrigger(Trigger):
    target_group_id: int = DEFAULT_ID

    animation_id: int = DEFAULT_ID

    @classmethod
    def from_binary(
        cls: Type[AT],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> AT:
        animate_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary, order)

        target_group_id = reader.read_u16()

        animation_id = reader.read_u8()

        animate_trigger.target_group_id = target_group_id

        animate_trigger.animation_id = animation_id

        return animate_trigger

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary, order)

        writer.write_u16(self.target_group_id)

        writer.write_u8(self.animation_id)

    @classmethod
    def from_robtop_data(cls: Type[AT], data: Mapping[int, str]) -> AT:
        animate_trigger = super().from_robtop_data(data)

        target_group_id = parse_get_or(int, DEFAULT_ID, data.get(TARGET_GROUP_ID))

        animation_id = parse_get_or(int, DEFAULT_ID, data.get(ANIMATION_ID))

        animate_trigger.target_group_id = target_group_id

        animate_trigger.animation_id = animation_id

        return animate_trigger

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        data[TARGET_GROUP_ID] = str(self.target_group_id)

        data[ANIMATION_ID] = str(self.animation_id)

        return data


TOGGLE_TYPE_MASK = 0b00000011
HOLD_MODE_BIT = 0b00000100
DUAL_MODE_BIT = 0b00001000


DEFAULT_HOLD_MODE = False
DEFAULT_DUAL_MODE = False

THT = TypeVar("THT", bound="TouchTrigger")


@define()
class TouchTrigger(Trigger):
    target_group_id: int = DEFAULT_ID

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

        reader = Reader(binary, order)

        target_group_id = reader.read_u16()

        value = reader.read_u8()

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

        writer = Writer(binary, order)

        writer.write_u16(self.target_group_id)

        value = self.toggle_type.value

        if self.is_hold_mode():
            value |= HOLD_MODE_BIT

        if self.is_dual_mode():
            value |= DUAL_MODE_BIT

        writer.write_u8(value)

    def is_hold_mode(self) -> bool:
        return self.hold_mode

    def is_dual_mode(self) -> bool:
        return self.dual_mode

    @classmethod
    def from_robtop_data(cls: Type[THT], data: Mapping[int, str]) -> THT:
        touch_trigger = super().from_robtop_data(data)

        target_group_id = parse_get_or(int, DEFAULT_ID, data.get(TARGET_GROUP_ID))

        hold_mode = parse_get_or(int_bool, DEFAULT_HOLD_MODE, data.get(HOLD_MODE))
        dual_mode = parse_get_or(int_bool, DEFAULT_DUAL_MODE, data.get(DUAL_MODE))

        toggle_type = parse_get_or(
            partial_parse_enum(int, ToggleType), ToggleType.DEFAULT, data.get(TOGGLE_TYPE)
        )

        touch_trigger.target_group_id = target_group_id

        touch_trigger.hold_mode = hold_mode
        touch_trigger.dual_mode = dual_mode

        touch_trigger.toggle_type = toggle_type

        return touch_trigger

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        data[TARGET_GROUP_ID] = str(self.target_group_id)

        hold_mode = self.is_hold_mode()

        if hold_mode:
            data[HOLD_MODE] = bool_str(hold_mode)

        dual_mode = self.is_dual_mode()

        if dual_mode:
            data[DUAL_MODE] = bool_str(dual_mode)

        data[TOGGLE_TYPE] = str(self.toggle_type.value)

        return data


DEFAULT_COUNT = 0


CT = TypeVar("CT", bound="CountTrigger")


@define()
class CountTrigger(Trigger):
    item_id: int = DEFAULT_ID

    count: int = DEFAULT_COUNT

    activate_group: bool = DEFAULT_ACTIVATE_GROUP
    multi_activate: bool = DEFAULT_MULTI_ACTIVATE

    def is_activate_group(self) -> bool:
        return self.activate_group

    def is_multi_activate(self) -> bool:
        return self.multi_activate

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

        reader = Reader(binary, order)

        item_id = reader.read_u16()

        count = reader.read_i32()

        value = reader.read_u8()

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

        writer = Writer(binary, order)

        writer.write_u16(self.item_id)

        writer.write_i32(self.count)

        value = 0

        if self.is_activate_group():
            value |= ACTIVATE_GROUP_BIT

        if self.is_multi_activate():
            value |= MULTI_ACTIVATE_BIT

        writer.write_u8(value)

    @classmethod
    def from_robtop_data(cls: Type[CT], data: Mapping[int, str]) -> CT:
        count_trigger = super().from_robtop_data(data)

        item_id = parse_get_or(int, DEFAULT_ID, data.get(ITEM_ID))

        count = parse_get_or(int, DEFAULT_COUNT, data.get(COUNT))

        subtract_count = parse_get_or(int_bool, DEFAULT_SUBTRACT_COUNT, data.get(SUBTRACT_COUNT))

        if subtract_count:
            count = -count

        activate_group = parse_get_or(int_bool, DEFAULT_ACTIVATE_GROUP, data.get(ACTIVATE_GROUP))
        multi_activate = parse_get_or(
            int_bool, DEFAULT_MULTI_ACTIVATE, data.get(TRIGGER_MULTI_ACTIVATE)
        )

        count_trigger.item_id = item_id

        count_trigger.count = count

        count_trigger.activate_group = activate_group
        count_trigger.multi_activate = multi_activate

        return count_trigger

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        data[ITEM_ID] = str(self.item_id)

        count = self.count

        subtract_count = count < 0

        if subtract_count:
            data[SUBTRACT_COUNT] = bool_str(subtract_count)

            count = -count

        data[COUNT] = str(count)

        activate_group = self.is_activate_group()

        if activate_group:
            data[ACTIVATE_GROUP] = bool_str(activate_group)

        multi_activate = self.is_multi_activate()

        if multi_activate:
            data[TRIGGER_MULTI_ACTIVATE] = bool_str(multi_activate)

        return data


ICT = TypeVar("ICT", bound="InstantCountTrigger")

COMPARISON_MASK = 0b00000110
COMPARISON_SHIFT = ACTIVATE_GROUP_BIT.bit_length()


@define()
class InstantCountTrigger(Trigger):
    item_id: int = DEFAULT_ID
    count: int = DEFAULT_COUNT

    activate_group: bool = DEFAULT_ACTIVATE_GROUP

    comparison: InstantCountComparison = InstantCountComparison.DEFAULT

    def is_activate_group(self) -> bool:
        return self.activate_group

    @classmethod
    def from_binary(
        cls: Type[ICT],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> ICT:
        activate_group_bit = ACTIVATE_GROUP_BIT

        instant_count_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary, order)

        item_id = reader.read_u16()

        count = reader.read_i32()

        value = reader.read_u8()

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

        writer = Writer(binary, order)

        writer.write_u16(self.item_id)

        writer.write_i32(self.count)

        value = 0

        if self.is_activate_group():
            value |= ACTIVATE_GROUP_BIT

        value |= self.comparison.value << COMPARISON_SHIFT

        writer.write_u8(value)

    @classmethod
    def from_robtop_data(cls: Type[ICT], data: Mapping[int, str]) -> ICT:
        instant_count_trigger = super().from_robtop_data(data)

        item_id = parse_get_or(int, DEFAULT_ID, data.get(ITEM_ID))

        count = parse_get_or(int, DEFAULT_COUNT, data.get(COUNT))

        activate_group = parse_get_or(int_bool, DEFAULT_ACTIVATE_GROUP, data.get(ACTIVATE_GROUP))

        comparison = parse_get_or(
            partial_parse_enum(int, InstantCountComparison),
            InstantCountComparison.DEFAULT,
            data.get(COMPARISON),
        )

        instant_count_trigger.item_id = item_id

        instant_count_trigger.count = count

        instant_count_trigger.activate_group = activate_group

        instant_count_trigger.comparison = comparison

        return instant_count_trigger

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        data[ITEM_ID] = str(self.item_id)

        data[COUNT] = str(self.count)

        activate_group = self.is_activate_group()

        if activate_group:
            data[ACTIVATE_GROUP] = bool_str(activate_group)

        data[COMPARISON] = str(self.comparison.value)

        return data


PT = TypeVar("PT", bound="PickupTrigger")


@define()
class PickupTrigger(Trigger):
    item_id: int = DEFAULT_ID
    count: int = DEFAULT_COUNT

    @classmethod
    def from_binary(
        cls: Type[PT],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> PT:
        pickup_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary, order)

        item_id = reader.read_u16()

        count = reader.read_i32()

        pickup_trigger.item_id = item_id

        pickup_trigger.count = count

        return pickup_trigger

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary, order)

        writer.write_u16(self.item_id)

        writer.write_i32(self.count)

    @classmethod
    def from_robtop_data(cls: Type[PT], data: Mapping[int, str]) -> PT:
        pickup_trigger = super().from_robtop_data(data)

        item_id = parse_get_or(int, DEFAULT_ID, data.get(ITEM_ID))

        count = parse_get_or(int, DEFAULT_COUNT, data.get(COUNT))

        pickup_trigger.item_id = item_id

        pickup_trigger.count = count

        return pickup_trigger

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        data[ITEM_ID] = str(self.item_id)

        data[COUNT] = str(self.count)

        return data


DEFAULT_SPEED = 1.0
DEFAULT_MAX_SPEED = 0.0
DEFAULT_OFFSET = 0.0


FPYT = TypeVar("FPYT", bound="FollowPlayerYTrigger")


@define()
class FollowPlayerYTrigger(Trigger):
    target_group_id: int = DEFAULT_ID

    duration: float = DEFAULT_DURATION
    delay: float = DEFAULT_DELAY

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
        rounding = DEFAULT_ROUNDING

        follow_player_y_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary, order)

        target_group_id = reader.read_u16()

        duration = round(reader.read_f32(), rounding)

        delay = round(reader.read_f32(), rounding)

        speed = round(reader.read_f32(), rounding)
        max_speed = round(reader.read_f32(), rounding)
        offset = round(reader.read_f32(), rounding)

        follow_player_y_trigger.target_group_id = target_group_id

        follow_player_y_trigger.duration = duration

        follow_player_y_trigger.delay = delay

        follow_player_y_trigger.speed = speed
        follow_player_y_trigger.max_speed = max_speed
        follow_player_y_trigger.offset = offset

        return follow_player_y_trigger

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary, order)

        writer.write_u16(self.target_group_id)

        writer.write_f32(self.duration)

        writer.write_f32(self.delay)

        writer.write_f32(self.speed)
        writer.write_f32(self.max_speed)
        writer.write_f32(self.offset)

    @classmethod
    def from_robtop_data(cls: Type[FPYT], data: Mapping[int, str]) -> FPYT:
        follow_player_y_trigger = super().from_robtop_data(data)

        target_group_id = parse_get_or(int, DEFAULT_ID, data.get(TARGET_GROUP_ID))

        duration = parse_get_or(float, DEFAULT_DURATION, data.get(DURATION))

        delay = parse_get_or(float, DEFAULT_DELAY, data.get(FOLLOW_DELAY))

        speed = parse_get_or(float, DEFAULT_SPEED, data.get(SPEED))
        max_speed = parse_get_or(float, DEFAULT_MAX_SPEED, data.get(MAX_SPEED))
        offset = parse_get_or(float, DEFAULT_OFFSET, data.get(OFFSET))

        follow_player_y_trigger.target_group_id = target_group_id

        follow_player_y_trigger.duration = duration

        follow_player_y_trigger.delay = delay

        follow_player_y_trigger.speed = speed
        follow_player_y_trigger.max_speed = max_speed
        follow_player_y_trigger.offset = offset

        return follow_player_y_trigger

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        data[TARGET_GROUP_ID] = str(self.target_group_id)

        data[DURATION] = float_str(self.duration)

        data[FOLLOW_DELAY] = float_str(self.delay)

        data[SPEED] = float_str(self.speed)
        data[MAX_SPEED] = float_str(self.max_speed)
        data[OFFSET] = float_str(self.offset)

        return data


ODT = TypeVar("ODT", bound="OnDeathTrigger")


@define()
class OnDeathTrigger(Trigger):
    target_group_id: int = DEFAULT_ID

    activate_group: bool = DEFAULT_ACTIVATE_GROUP

    def is_activate_group(self) -> bool:
        return self.activate_group

    @classmethod
    def from_binary(
        cls: Type[ODT],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> ODT:
        activate_group_bit = ACTIVATE_GROUP_BIT

        on_death_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary, order)

        target_group_id = reader.read_u16()

        value = reader.read_u8()

        activate_group = value & activate_group_bit == activate_group_bit

        on_death_trigger.target_group_id = target_group_id

        on_death_trigger.activate_group = activate_group

        return on_death_trigger

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary, order)

        writer.write_u16(self.target_group_id)

        value = 0

        if self.is_activate_group():
            value |= ACTIVATE_GROUP_BIT

        writer.write_u8(value)

    @classmethod
    def from_robtop_data(cls: Type[ODT], data: Mapping[int, str]) -> ODT:
        on_death_trigger = super().from_robtop_data(data)

        target_group_id = parse_get_or(int, DEFAULT_ID, data.get(TARGET_GROUP_ID))

        activate_group = parse_get_or(int_bool, DEFAULT_ACTIVATE_GROUP, data.get(ACTIVATE_GROUP))

        on_death_trigger.target_group_id = target_group_id

        on_death_trigger.activate_group = activate_group

        return on_death_trigger

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        data[TARGET_GROUP_ID] = str(self.target_group_id)

        activate_group = self.is_activate_group()

        if activate_group:
            data[ACTIVATE_GROUP] = bool_str(activate_group)

        return data


TRIGGER_ON_EXIT_BIT = 0b10000000_00000000
COLLISION_ACTIVATE_GROUP_BIT = 0b10000000_00000000


DEFAULT_TRIGGER_ON_EXIT = False


CBT = TypeVar("CBT", bound="CollisionTrigger")


@define()
class CollisionTrigger(Trigger):
    target_group_id: int = DEFAULT_ID

    activate_group: bool = DEFAULT_ACTIVATE_GROUP

    block_a_id: int = DEFAULT_ID
    block_b_id: int = DEFAULT_ID

    trigger_on_exit: bool = DEFAULT_TRIGGER_ON_EXIT

    def is_activate_group(self) -> bool:
        return self.activate_group

    def is_trigger_on_exit(self) -> bool:
        return self.trigger_on_exit

    @classmethod
    def from_binary(
        cls: Type[CBT],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> CBT:
        block_id_mask = BLOCK_ID_MASK
        activate_group_bit = COLLISION_ACTIVATE_GROUP_BIT
        trigger_on_exit_bit = TRIGGER_ON_EXIT_BIT

        collision_trigger = super().from_binary(binary, order, version)

        reader = Reader(binary, order)

        value = reader.read_u16()

        block_a_id = value & block_id_mask

        activate_group = value & activate_group_bit == activate_group_bit

        value = reader.read_u16()

        block_b_id = value & block_id_mask

        trigger_on_exit = value & trigger_on_exit_bit == trigger_on_exit_bit

        target_group_id = reader.read_u16()

        collision_trigger.block_a_id = block_a_id
        collision_trigger.block_b_id = block_b_id
        collision_trigger.activate_group = activate_group
        collision_trigger.trigger_on_exit = trigger_on_exit
        collision_trigger.target_group_id = target_group_id

        return collision_trigger

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary, order)

        value = self.block_a_id

        if self.is_activate_group():
            value |= COLLISION_ACTIVATE_GROUP_BIT

        writer.write_u16(value)

        value = self.block_b_id

        if self.is_trigger_on_exit():
            value |= TRIGGER_ON_EXIT_BIT

        writer.write_u16(value)

        writer.write_u16(self.target_group_id)

    @classmethod
    def from_robtop_data(cls: Type[CBT], data: Mapping[int, str]) -> CBT:
        collision_trigger = super().from_robtop_data(data)

        block_a_id = parse_get_or(int, DEFAULT_ID, data.get(BLOCK_A_ID))
        block_b_id = parse_get_or(int, DEFAULT_ID, data.get(BLOCK_B_ID))

        activate_group = parse_get_or(int_bool, DEFAULT_ACTIVATE_GROUP, data.get(ACTIVATE_GROUP))

        trigger_on_exit = parse_get_or(int_bool, DEFAULT_TRIGGER_ON_EXIT, data.get(TRIGGER_ON_EXIT))

        target_group_id = parse_get_or(int, DEFAULT_ID, data.get(TARGET_GROUP_ID))

        collision_trigger.block_a_id = block_a_id
        collision_trigger.block_b_id = block_b_id

        collision_trigger.activate_group = activate_group

        collision_trigger.trigger_on_exit = trigger_on_exit

        collision_trigger.target_group_id = target_group_id

        return collision_trigger

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        data[BLOCK_A_ID] = str(self.block_a_id)
        data[BLOCK_B_ID] = str(self.block_b_id)

        activate_group = self.is_activate_group()

        if activate_group:
            data[ACTIVATE_GROUP] = bool_str(activate_group)

        trigger_on_exit = self.is_trigger_on_exit()

        if trigger_on_exit:
            data[TRIGGER_ON_EXIT] = bool_str(trigger_on_exit)

        data[TARGET_GROUP_ID] = str(self.target_group_id)

        return data


def is_trigger(object: Object) -> TypeGuard[Trigger]:
    return object.is_trigger()


@runtime_checkable
class HasTargetGroup(Protocol):
    target_group_id: int


@runtime_checkable
class HasAdditionalGroup(Protocol):
    additional_group_id: int


TARGET_GROUP_ID_NAME = "target_group_id"
ADDITIONAL_GROUP_ID_NAME = "additional_group_id"


def has_target_group(object: Object) -> TypeGuard[HasTargetGroup]:
    return has_attribute(object, TARGET_GROUP_ID_NAME)


def has_additional_group(object: Object) -> TypeGuard[HasAdditionalGroup]:
    return has_attribute(object, ADDITIONAL_GROUP_ID_NAME)


class ObjectType(Enum):
    OBJECT = 0
    START_POSITION = 1
    PULSATING_OBJECT = 2
    ROTATING_OBJECT = 3
    ORB = 4
    TRIGGER_ORB = 5
    SECRET_COIN = 6
    TEXT = 7
    TELEPORT = 8
    ITEM_COUNTER = 9
    PICKUP_ITEM = 10
    TOGGLE_ITEM = 11
    COLLISION_BLOCK = 12
    PLAYER_COLOR_TRIGGER = 13
    NORMAL_COLOR_TRIGGER = 14
    COPIED_COLOR_TRIGGER = 15
    PULSE_COLOR_CHANNEL_TRIGGER = 16
    PULSE_HSV_CHANNEL_TRIGGER = 17
    PULSE_COLOR_GROUP_TRIGGER = 18
    PULSE_HSV_GROUP_TRIGGER = 19
    ALPHA_TRIGGER = 20
    NORMAL_MOVE_TRIGGER = 21
    TARGET_MOVE_TRIGGER = 22
    SPAWN_TRIGGER = 23
    STOP_TRIGGER = 24
    TOGGLE_TRIGGER = 25
    ROTATE_TRIGGER = 26
    FOLLOW_TRIGGER = 27
    SHAKE_TRIGGER = 28
    ANIMATE_TRIGGER = 29
    TOUCH_TRIGGER = 30
    COUNT_TRIGGER = 31
    INSTANT_COUNT_TRIGGER = 32
    PICKUP_TRIGGER = 33
    FOLLOW_PLAYER_Y_TRIGGER = 34
    ON_DEATH_TRIGGER = 35
    COLLISION_TRIGGER = 36


OBJECT_TYPE_TO_TYPE: Dict[ObjectType, Type[Object]] = {
    ObjectType.OBJECT: Object,
    ObjectType.START_POSITION: StartPosition,
    ObjectType.PULSATING_OBJECT: PulsatingObject,
    ObjectType.ROTATING_OBJECT: RotatingObject,
    ObjectType.ORB: Orb,
    ObjectType.TRIGGER_ORB: TriggerOrb,
    ObjectType.SECRET_COIN: SecretCoin,
    ObjectType.TEXT: Text,
    ObjectType.TELEPORT: Teleport,
    ObjectType.ITEM_COUNTER: ItemCounter,
    ObjectType.PICKUP_ITEM: PickupItem,
    ObjectType.TOGGLE_ITEM: ToggleItem,
    ObjectType.COLLISION_BLOCK: CollisionBlock,
    ObjectType.PLAYER_COLOR_TRIGGER: PlayerColorTrigger,
    ObjectType.NORMAL_COLOR_TRIGGER: NormalColorTrigger,
    ObjectType.COPIED_COLOR_TRIGGER: CopiedColorTrigger,
    ObjectType.PULSE_COLOR_CHANNEL_TRIGGER: PulseColorChannelTrigger,
    ObjectType.PULSE_HSV_CHANNEL_TRIGGER: PulseHSVChannelTrigger,
    ObjectType.PULSE_COLOR_GROUP_TRIGGER: PulseColorGroupTrigger,
    ObjectType.PULSE_HSV_GROUP_TRIGGER: PulseHSVGroupTrigger,
    ObjectType.ALPHA_TRIGGER: AlphaTrigger,
    ObjectType.NORMAL_MOVE_TRIGGER: NormalMoveTrigger,
    ObjectType.TARGET_MOVE_TRIGGER: TargetMoveTrigger,
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
    reader = Reader(binary, order)

    object_type_value = reader.read_u8()
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
    object_type = TYPE_TO_OBJECT_TYPE.get(type(object))

    if object_type is None:
        raise TypeError  # TODO: message?

    writer = Writer(binary, order)

    writer.write_u8(object_type.value)

    object.to_binary(binary, order, version)


def object_to_bytes(
    object: Object, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
) -> bytes:
    binary = BytesIO()

    object_to_binary(object, binary, order, version)

    binary.seek(0)

    return binary.read()


OBJECT_ID_NOT_PRESENT = "object ID is not present"

# miscellaneaous IDs

START_POSITION_ID = MiscType.START_POSITION.id
TEXT_ID = MiscType.TEXT.id
ITEM_COUNTER_ID = MiscType.ITEM_COUNTER.id
COLLISION_BLOCK_ID = MiscType.COLLISION_BLOCK.id

# coin IDs

SECRET_COIN_ID = CoinType.SECRET.id

# portal IDs

TELEPORT_ID = PortalType.BLUE_TELEPORT.id

# orb IDs

TRIGGER_ORB_ID = OrbType.TRIGGER.id

# trigger IDs

BACKGROUND_TRIGGER_ID = TriggerType.BACKGROUND.id
GROUND_TRIGGER_ID = TriggerType.GROUND.id
LINE_TRIGGER_ID = TriggerType.LINE.id
OBJECT_TRIGGER_ID = TriggerType.OBJECT.id
COLOR_1_TRIGGER_ID = TriggerType.COLOR_1.id
COLOR_2_TRIGGER_ID = TriggerType.COLOR_2.id
COLOR_3_TRIGGER_ID = TriggerType.COLOR_3.id
COLOR_4_TRIGGER_ID = TriggerType.COLOR_4.id
LINE_3D_TRIGGER_ID = TriggerType.LINE_3D.id
COLOR_TRIGGER_ID = TriggerType.COLOR.id
SECONDARY_GROUND_TRIGGER_ID = TriggerType.SECONDARY_GROUND.id
MOVE_TRIGGER_ID = TriggerType.MOVE.id
PULSE_TRIGGER_ID = TriggerType.PULSE.id
ALPHA_TRIGGER_ID = TriggerType.ALPHA.id
TOGGLE_TRIGGER_ID = TriggerType.TOGGLE.id
SPAWN_TRIGGER_ID = TriggerType.SPAWN.id
ROTATE_TRIGGER_ID = TriggerType.ROTATE.id
FOLLOW_TRIGGER_ID = TriggerType.FOLLOW.id
SHAKE_TRIGGER_ID = TriggerType.SHAKE.id
ANIMATE_TRIGGER_ID = TriggerType.ANIMATE.id
TOUCH_TRIGGER_ID = TriggerType.TOUCH.id
COUNT_TRIGGER_ID = TriggerType.COUNT.id
STOP_TRIGGER_ID = TriggerType.STOP.id
INSTANT_COUNT_TRIGGER_ID = TriggerType.INSTANT_COUNT.id
ON_DEATH_TRIGGER_ID = TriggerType.ON_DEATH.id
FOLLOW_PLAYER_Y_TRIGGER_ID = TriggerType.FOLLOW_PLAYER_Y.id
COLLISION_TRIGGER_ID = TriggerType.COLLISION.id
PICKUP_TRIGGER_ID = TriggerType.PICKUP.id


OBJECT_ID_TO_TYPE: Dict[int, Type[Object]] = {
    # NOTE: (compatibility) color, pulse and move triggers and items are detected separately
    START_POSITION_ID: StartPosition,
    TEXT_ID: Text,
    SECRET_COIN_ID: SecretCoin,
    TELEPORT_ID: Teleport,
    TRIGGER_ORB_ID: TriggerOrb,
    ITEM_COUNTER_ID: ItemCounter,
    COLLISION_BLOCK_ID: CollisionBlock,
    ALPHA_TRIGGER_ID: AlphaTrigger,
    SPAWN_TRIGGER_ID: SpawnTrigger,
    STOP_TRIGGER_ID: StopTrigger,
    TOGGLE_TRIGGER_ID: ToggleTrigger,
    ROTATE_TRIGGER_ID: RotateTrigger,
    FOLLOW_TRIGGER_ID: FollowTrigger,
    SHAKE_TRIGGER_ID: ShakeTrigger,
    ANIMATE_TRIGGER_ID: AnimateTrigger,
    TOUCH_TRIGGER_ID: TouchTrigger,
    COUNT_TRIGGER_ID: CountTrigger,
    INSTANT_COUNT_TRIGGER_ID: InstantCountTrigger,
    PICKUP_TRIGGER_ID: PickupTrigger,
    FOLLOW_PLAYER_Y_TRIGGER_ID: FollowPlayerYTrigger,
    ON_DEATH_TRIGGER_ID: OnDeathTrigger,
    COLLISION_TRIGGER_ID: CollisionTrigger,
}

OBJECT_ID_TO_TYPE.update({orb.id: Orb for orb in OrbType if not orb.is_trigger()})
OBJECT_ID_TO_TYPE.update(
    {rotating_object.id: RotatingObject for rotating_object in RotatingObjectType}
)
OBJECT_ID_TO_TYPE.update(
    {pulsating_object.id: PulsatingObject for pulsating_object in PulsatingObjectType}
)

PULSE_TRIGGER_MAPPING: Dict[Tuple[PulseMode, PulseTargetType], Type[PulseTrigger]] = {
    (PulseMode.COLOR, PulseTargetType.COLOR_CHANNEL): PulseColorChannelTrigger,
    (PulseMode.HSV, PulseTargetType.COLOR_CHANNEL): PulseHSVChannelTrigger,
    (PulseMode.COLOR, PulseTargetType.GROUP): PulseColorGroupTrigger,
    (PulseMode.HSV, PulseTargetType.GROUP): PulseHSVGroupTrigger,
}

PLAYER_COLOR_TRIGGER_MAPPING = {
    BACKGROUND_TRIGGER_ID: PlayerBackgroundTrigger,
    GROUND_TRIGGER_ID: PlayerGroundTrigger,
    LINE_TRIGGER_ID: PlayerLineTrigger,
    OBJECT_TRIGGER_ID: PlayerObjectTrigger,
    COLOR_1_TRIGGER_ID: PlayerColor1Trigger,
    COLOR_2_TRIGGER_ID: PlayerColor2Trigger,
    COLOR_3_TRIGGER_ID: PlayerColor3Trigger,
    COLOR_4_TRIGGER_ID: PlayerColor4Trigger,
    LINE_3D_TRIGGER_ID: PlayerLine3DTrigger,
    SECONDARY_GROUND_TRIGGER_ID: PlayerSecondaryGroundTrigger,
    COLOR_TRIGGER_ID: PlayerColorTrigger,
}

NORMAL_COLOR_TRIGGER_MAPPING = {
    BACKGROUND_TRIGGER_ID: NormalBackgroundTrigger,
    GROUND_TRIGGER_ID: NormalGroundTrigger,
    LINE_TRIGGER_ID: NormalLineTrigger,
    OBJECT_TRIGGER_ID: NormalObjectTrigger,
    COLOR_1_TRIGGER_ID: NormalColor1Trigger,
    COLOR_2_TRIGGER_ID: NormalColor2Trigger,
    COLOR_3_TRIGGER_ID: NormalColor3Trigger,
    COLOR_4_TRIGGER_ID: NormalColor4Trigger,
    LINE_3D_TRIGGER_ID: NormalLine3DTrigger,
    SECONDARY_GROUND_TRIGGER_ID: NormalSecondaryGroundTrigger,
    COLOR_TRIGGER_ID: NormalColorTrigger,
}

COPIED_COLOR_TRIGGER_MAPPING = {
    BACKGROUND_TRIGGER_ID: CopiedBackgroundTrigger,
    GROUND_TRIGGER_ID: CopiedGroundTrigger,
    LINE_TRIGGER_ID: CopiedLineTrigger,
    OBJECT_TRIGGER_ID: CopiedObjectTrigger,
    COLOR_1_TRIGGER_ID: CopiedColor1Trigger,
    COLOR_2_TRIGGER_ID: CopiedColor2Trigger,
    COLOR_3_TRIGGER_ID: CopiedColor3Trigger,
    COLOR_4_TRIGGER_ID: CopiedColor4Trigger,
    LINE_3D_TRIGGER_ID: CopiedLine3DTrigger,
    SECONDARY_GROUND_TRIGGER_ID: CopiedSecondaryGroundTrigger,
    COLOR_TRIGGER_ID: CopiedColorTrigger,
}

ITEM_IDS = {item.id for item in ItemType}

COLOR_TRIGGER_IDS = {
    BACKGROUND_TRIGGER_ID,
    GROUND_TRIGGER_ID,
    LINE_TRIGGER_ID,
    OBJECT_TRIGGER_ID,
    COLOR_1_TRIGGER_ID,
    COLOR_2_TRIGGER_ID,
    COLOR_3_TRIGGER_ID,
    COLOR_4_TRIGGER_ID,
    LINE_3D_TRIGGER_ID,
    SECONDARY_GROUND_TRIGGER_ID,
    COLOR_TRIGGER_ID,
}

PLAYER_COLOR_1_STRING = str(PLAYER_COLOR_1)
PLAYER_COLOR_2_STRING = str(PLAYER_COLOR_2)

PULSE_MODE_STRING = str(PULSE_MODE)

COPIED_COLOR_ID_STRING = str(COPIED_COLOR_ID)

PULSE_TARGET_TYPE_STRING = str(PULSE_TARGET_TYPE)

ITEM_MODE_STRING = str(ITEM_MODE)

USE_TARGET_STRING = str(USE_TARGET)


DEFAULT_USE_TARGET = False


def object_from_robtop(string: str) -> Object:
    data = split_any_object(string)

    object_id = parse_get_or(int, DEFAULT_ID, data.get(ID_STRING))

    if not object_id:
        raise ValueError(OBJECT_ID_NOT_PRESENT)

    object_type: Type[Object]

    if object_id in COLOR_TRIGGER_IDS:
        player_color_1 = parse_get_or(
            int_bool, DEFAULT_PLAYER_COLOR_1, data.get(PLAYER_COLOR_1_STRING)
        )
        player_color_2 = parse_get_or(
            int_bool, DEFAULT_PLAYER_COLOR_2, data.get(PLAYER_COLOR_2_STRING)
        )

        player_color = compute_player_color(player_color_1, player_color_2)

        if player_color.is_used():
            object_type = PLAYER_COLOR_TRIGGER_MAPPING[object_id]  # type: ignore

        else:
            copied_color_id = parse_get_or(int, DEFAULT_ID, data.get(COPIED_COLOR_ID_STRING))

            if copied_color_id:
                object_type = COPIED_COLOR_TRIGGER_MAPPING[object_id]  # type: ignore

            else:
                object_type = NORMAL_COLOR_TRIGGER_MAPPING[object_id]  # type: ignore

    elif object_id == MOVE_TRIGGER_ID:
        use_target = parse_get_or(int_bool, DEFAULT_USE_TARGET, data.get(USE_TARGET_STRING))

        if use_target:
            object_type = TargetMoveTrigger

        else:
            object_type = NormalMoveTrigger

    elif object_id == PULSE_TRIGGER_ID:
        pulse_mode = parse_get_or(
            partial_parse_enum(int, PulseMode), PulseMode.DEFAULT, data.get(PULSE_MODE_STRING)
        )

        pulse_target_type = parse_get_or(
            partial_parse_enum(int, PulseTargetType),
            PulseTargetType.DEFAULT,
            data.get(PULSE_TARGET_TYPE_STRING),
        )

        object_type = PULSE_TRIGGER_MAPPING[pulse_mode, pulse_target_type]

    elif object_id in ITEM_IDS:
        item_mode = parse_get_or(
            partial_parse_enum(int, ItemMode), ItemMode.DEFAULT, data.get(ITEM_MODE_STRING)
        )

        if item_mode.is_pickup():
            object_type = PickupItem

        else:
            object_type = ToggleItem

    else:
        object_type = OBJECT_ID_TO_TYPE.get(object_id, Object)

    object = object_type.from_robtop(string)

    return object


def object_to_robtop(object: Object) -> str:
    return object.to_robtop()
