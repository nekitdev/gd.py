from io import BytesIO
from typing import BinaryIO, Iterable, Set, Type, TypeVar

from attrs import define, field
from typing_extensions import TypeGuard

from gd.api.hsv import HSV
from gd.binary import Binary
from gd.binary_utils import UTF_8, Reader, Writer
from gd.colors import Color
from gd.constants import EMPTY
from gd.enum_extensions import Enum, Flag
from gd.enums import (
    ByteOrder,
    Easing,
    InstantCountComparison,
    PickupItemMode,
    PlayerColor,
    PulseMode,
    PulseTargetType,
    PulseType,
    TargetType,
    ToggleType,
    ZLayer,
)
from gd.typing import is_instance

O = TypeVar("O", bound="Object")

__all__ = (
    "Object",
    "AnimatedObject",
    "Orb",
    "Coin",
    "Text",
    "Teleport",
    "PickupItem",
    "CollisionBlock",
    "Trigger",
    "ColorTrigger",
    "PulseTrigger",
    "MoveTrigger",
    "SpawnTrigger",
    "StopTrigger",
    "RotateTrigger",
    "FollowTrigger",
    "ShakeTrigger",
    "AnimationTrigger",
    "TouchTrigger",
    "CountTrigger",
    "InstantCountTrigger",
    "PickupTrigger",
    "FollowPlayerYTrigger",
    "OnDeathTrigger",
    "CollisionTrigger",
)

H_FLIPPED_BIT = 0b00000001
V_FLIPPED_BIT = 0b00000010
DO_NOT_FADE_BIT = 0b00000100
DO_NOT_ENTER_BIT = 0b00001000
GROUP_PARENT_BIT = 0b00010000
HIGH_DETAIL_BIT = 0b00100000
GLOW_BIT = 0b01000000
SPECIAL_CHECKED_BIT = 0b10000000

Z_ORDER_MASK = 0b00011111_11111111

Z_ORDER_BITS = Z_ORDER_MASK.bit_length()


class ObjectFlag(Flag):
    SIMPLE = 0

    HAS_EDITOR_LAYER = 1
    HAS_COLORS = 2
    HAS_LINK = 4
    HAS_Z = 8

    def has_editor_layer(self) -> bool:
        return type(self).HAS_EDITOR_LAYER in self

    def has_colors(self) -> bool:
        return type(self).HAS_COLORS in self

    def has_link(self) -> bool:
        return type(self).HAS_LINK in self

    def has_z(self) -> bool:
        return type(self).HAS_Z in self


@define()
class Object(Binary):
    id: int = field()
    x: float = field(default=0.0)
    y: float = field(default=0.0)

    rotation: float = field(default=0.0)

    h_flipped: bool = field(default=False)
    v_flipped: bool = field(default=False)

    scale: float = field(default=1.0)

    do_not_fade: bool = field(default=False)
    do_not_enter: bool = field(default=False)

    z_layer: ZLayer = field(default=ZLayer.DEFAULT)
    z_order: int = field(default=0)

    base_editor_layer: int = field(default=0)
    additional_editor_layer: int = field(default=0)

    base_color_id: int = field(default=0)
    detail_color_id: int = field(default=0)

    base_color_hsv: HSV = field(factory=HSV)
    detail_color_hsv: HSV = field(factory=HSV)

    groups: Set[int] = field(factory=set)

    group_parent: bool = False

    high_detail: bool = False

    glow: bool = True

    special_checked: bool = False

    link_id: int = 0

    @classmethod
    def from_binary(cls: Type[O], binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT) -> O:
        h_flipped_bit = H_FLIPPED_BIT
        v_flipped_bit = V_FLIPPED_BIT
        do_not_fade_bit = DO_NOT_FADE_BIT
        do_not_enter_bit = DO_NOT_ENTER_BIT
        group_parent_bit = GROUP_PARENT_BIT
        high_detail_bit = HIGH_DETAIL_BIT
        glow_bit = GLOW_BIT
        special_checked_bit = SPECIAL_CHECKED_BIT

        reader = Reader(binary)

        flag_value = reader.read_u8(order)

        flag = ObjectFlag(flag_value)

        id = reader.read_u16(order)

        x = reader.read_f32(order)
        y = reader.read_f32(order)

        rotation = reader.read_f32(order)
        scale = reader.read_f32(order)

        value = reader.read_u8(order)

        h_flipped = value & h_flipped_bit == h_flipped_bit
        v_flipped = value & v_flipped_bit == v_flipped_bit
        do_not_fade = value & do_not_fade_bit == do_not_fade_bit
        do_not_enter = value & do_not_enter_bit == do_not_enter_bit
        group_parent = value & group_parent_bit == group_parent_bit
        high_detail = value & high_detail_bit == high_detail_bit
        glow = value & glow_bit == glow_bit
        special_checked = value & special_checked_bit == special_checked_bit

        if flag.has_z():
            z_layer_order = reader.read_u16(order)

            z_layer_value = z_layer_order >> Z_ORDER_BITS
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

            base_color_hsv = HSV.from_binary(binary, order)
            detail_color_hsv = HSV.from_binary(binary, order)

        else:
            base_color_id = 0
            detail_color_id = 0

            base_color_hsv = HSV()
            detail_color_hsv = HSV()

        length = reader.read_u16(order)

        groups = {reader.read_u16(order) for _ in range(length)}

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
            glow=glow,
            special_checked=special_checked,
            link_id=link_id,
        )

    def to_binary(self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT) -> None:
        writer = Writer(binary)

        flag = ObjectFlag.SIMPLE

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

        link_id = self.link_id

        if link_id:
            flag |= ObjectFlag.HAS_LINK

        writer.write_u8(flag.value, order)

        writer.write_u16(self.id, order)

        writer.write_f32(self.x, order)
        writer.write_f32(self.y, order)

        writer.write_f32(self.rotation, order)
        writer.write_f32(self.scale, order)

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

        if self.is_glow():
            value |= GLOW_BIT

        if self.is_special_checked():
            value |= SPECIAL_CHECKED_BIT

        writer.write_u8(value, order)

        if flag.has_z():
            z_layer_order = z_order & Z_ORDER_MASK
            z_layer_order |= z_layer.value << Z_ORDER_BITS

            writer.write_u16(z_layer_order, order)

        if flag.has_editor_layer():
            writer.write_u16(base_editor_layer, order)
            writer.write_u16(additional_editor_layer, order)

        if flag.has_colors():
            writer.write_u16(base_color_id, order)
            writer.write_u16(detail_color_id, order)

            base_color_hsv.to_binary(binary, order)
            detail_color_hsv.to_binary(binary, order)

        writer.write_u16(len(self.groups), order)

        for group in sorted(self.groups):
            writer.write_u16(group, order)

        if flag.has_link():
            writer.write_u16(link_id, order)

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

    def is_glow(self) -> bool:
        return self.glow

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

    def scale_by(self: O, scale: float = 1.0) -> O:
        self.scale *= scale

        return self

    def scale_to(self: O, scale: float = 1.0) -> O:
        self.scale = scale

        return self

    def is_trigger(self) -> bool:
        return False


C = TypeVar("C", bound="Coin")


@define()
class Coin(Object):
    coin_id: int = 0

    @classmethod
    def from_binary(cls: Type[C], binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT) -> C:
        coin = super().from_binary(binary, order)

        reader = Reader(binary)

        coin_id = reader.read_u8(order)

        coin.coin_id = coin_id

        return coin

    def to_binary(self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT) -> None:
        super().to_binary(binary, order)

        writer = Writer(binary)

        writer.write_u8(self.coin_id, order)


S = TypeVar("S", bound="Text")


@define()
class Text(Object):
    content: str = EMPTY

    @classmethod
    def from_binary(
        cls: Type[S], binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, encoding: str = UTF_8
    ) -> S:
        text = super().from_binary(binary, order)

        reader = Reader(binary)

        length = reader.read_u16(order)

        content = reader.read(length).decode(encoding)

        text.content = content

        return text

    def to_binary(
        self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, encoding: str = UTF_8
    ) -> None:
        super().to_binary(binary, order)

        writer = Writer(binary)

        data = self.content.encode(encoding)

        writer.write_u16(len(data), order)

        writer.write(data)


P = TypeVar("P", bound="Teleport")


SMOOTH_BIT = 0b00000001


@define()
class Teleport(Object):
    offset: float = 0.0
    smooth: bool = False

    @classmethod
    def from_binary(cls: Type[P], binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT) -> P:
        smooth_bit = SMOOTH_BIT

        teleport = super().from_binary(binary, order)

        reader = Reader(binary)

        offset = reader.read_f32(order)

        value = reader.read_u8(order)

        smooth = value & smooth_bit == smooth_bit

        teleport.offset = offset
        teleport.smooth = smooth

        return teleport

    def to_binary(self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT) -> None:
        super().to_binary(binary, order)

        writer = Writer(binary)

        writer.write_f32(self.offset, order)

        value = 0

        if self.is_smooth():
            value |= SMOOTH_BIT

        writer.write_u8(value, order)

    def is_smooth(self) -> bool:
        return self.smooth


RANDOMIZE_START_BIT = 0b00000001

AO = TypeVar("AO", bound="AnimatedObject")


@define()
class AnimatedObject(Object):
    randomize_start: bool = False
    animation_speed: float = 0.0

    @classmethod
    def from_binary(cls: Type[AO], binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT) -> AO:
        randomize_start_bit = RANDOMIZE_START_BIT

        animated_object = super().from_binary(binary, order)

        reader = Reader(binary)

        animation_speed = reader.read_f32(order)

        value = reader.read_u8(order)

        randomize_start = value & randomize_start_bit == randomize_start_bit

        animated_object.randomize_start = randomize_start
        animated_object.animation_speed = animation_speed

        return animated_object

    def to_binary(self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT) -> None:
        super().to_binary(binary, order)

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


CB = TypeVar("CB", bound="CollisionBlock")


@define()
class CollisionBlock(Object):
    block_id: int = 0
    dynamic: bool = False

    @classmethod
    def from_binary(cls: Type[CB], binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT) -> CB:
        dynamic_bit = DYNAMIC_BIT

        collision_block = super().from_binary(binary, order)

        reader = Reader(binary)

        value = reader.read_u16(order)

        block_id = value & BLOCK_ID_MASK
        dynamic = value & dynamic_bit == dynamic_bit

        collision_block.block_id = block_id
        collision_block.dynamic = dynamic

        return collision_block

    def to_binary(self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT) -> None:
        super().to_binary(binary, order)

        writer = Writer(binary)

        value = self.block_id & BLOCK_ID_MASK

        if self.is_dynamic():
            value |= DYNAMIC_BIT

        writer.write_u16(value, order)

    def is_dynamic(self) -> bool:
        return self.dynamic


@define(slots=False)
class HasItem:
    item_id: int = 0


@define(slots=False)
class HasCount:
    count: int = 0


@define(slots=False)
class HasTargetGroup:
    target_group_id: int = 0


@define(slots=False)
class HasAdditionalGroup(HasTargetGroup):
    additional_group_id: int = 0


@define(slots=False)
class HasActivateGroup:
    activate_group: bool = False


@define(slots=False)
class HasDuration:
    duration: float = 0.0


@define(slots=False)
class HasDelay:
    delay: float = 0.0


@define(slots=False)
class HasEasing:
    easing: Easing = Easing.DEFAULT
    easing_rate: float = 0.0


@define(slots=False)
class HasMultiActivate:
    multi_activate: bool = False


@define(slots=False)
class HasColor:
    color: Color = field(factory=Color.default)


@define()
class Orb(HasMultiActivate, Object):
    pass


PI = TypeVar("PI", bound="PickupItem")


@define()
class PickupItem(HasTargetGroup, HasItem, Object):
    mode: PickupItemMode = PickupItemMode.DEFAULT

    @classmethod
    def from_binary(cls: Type[PI], binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT) -> PI:
        pickup_item = super().from_binary(binary, order)

        reader = Reader(binary)

        target_group_id = reader.read_u16(order)
        item_id = reader.read_u16(order)

        mode_value = reader.read_u8(order)

        mode = PickupItemMode(mode_value)

        pickup_item.target_group_id = target_group_id
        pickup_item.item_id = item_id

        pickup_item.mode = mode

        return pickup_item

    def to_binary(self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT) -> None:
        super().to_binary(binary, order)

        writer = Writer(binary)

        writer.write_u16(self.target_group_id, order)
        writer.write_u16(self.item_id, order)

        writer.write_u8(self.mode.value, order)


TOUCH_TRIGGERED_BIT = 0b00000001
SPAWN_TRIGGERED_BIT = 0b00000010
MULTI_TRIGGER_BIT = 0b00000100

T = TypeVar("T", bound="Trigger")


@define()
class Trigger(Object):
    touch_triggered: bool = False
    spawn_triggered: bool = False
    multi_trigger: bool = False

    @classmethod
    def from_binary(cls: Type[T], binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT) -> T:
        touch_triggered_bit = TOUCH_TRIGGERED_BIT
        spawn_triggered_bit = SPAWN_TRIGGERED_BIT
        multi_trigger_bit = MULTI_TRIGGER_BIT

        trigger = super().from_binary(binary, order)

        reader = Reader(binary)

        value = reader.read_u8(order)

        touch_triggered = value & touch_triggered_bit == touch_triggered_bit
        spawn_triggered = value & spawn_triggered_bit == spawn_triggered_bit
        multi_trigger = value & multi_trigger_bit == multi_trigger_bit

        trigger.touch_triggered = touch_triggered
        trigger.spawn_triggered = spawn_triggered
        trigger.multi_trigger = multi_trigger

        return trigger

    def to_binary(self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT) -> None:
        super().to_binary(binary, order)

        writer = Writer(binary)

        value = 0

        if self.is_touch_triggered():
            value |= TOUCH_TRIGGERED_BIT

        if self.is_spawn_triggered():
            value |= SPAWN_TRIGGERED_BIT

        if self.is_multi_trigger():
            value |= MULTI_TRIGGER_BIT

        writer.write_u8(value, order)

    def is_trigger(self) -> bool:
        return True

    def is_touch_triggered(self) -> bool:
        return self.touch_triggered

    def is_spawn_triggered(self) -> bool:
        return self.spawn_triggered

    def is_multi_trigger(self) -> bool:
        return self.multi_trigger


@define()
class ColorTrigger(HasColor, HasDuration, Trigger):
    blending: bool = field(default=False)
    target_color_id: int = field(default=0)

    copied_color_id: int = field(default=0)
    copied_color_hsv: HSV = field(factory=HSV)

    copy_opacity: bool = field(default=False)

    player_color: PlayerColor = field(default=PlayerColor.DEFAULT)


@define()
class PulseTrigger(Trigger):
    fade_in: float = field(default=0.0)
    hold: float = field(default=0.0)
    fade_out: float = field(default=0.0)

    color: Color = field(factory=Color.default)
    hsv: HSV = field(factory=HSV)

    target_type: PulseTargetType = PulseTargetType.DEFAULT
    type: PulseType = PulseType.DEFAULT
    mode: PulseMode = PulseMode.DEFAULT

    exclusive: bool = False


M = TypeVar("M", bound="MoveTrigger")


@define()
class MoveTrigger(HasEasing, HasDuration, Trigger):
    x_offset: float = 0.0
    y_offset: float = 0.0

    locked_to_player_x: bool = False
    locked_to_player_y: bool = False

    target_type: TargetType = TargetType.DEFAULT

    def is_locked_to_player_x(self) -> bool:
        return self.locked_to_player_x

    def is_locked_to_player_y(self) -> bool:
        return self.locked_to_player_y

    def lock_to_player_x(self: M) -> M:
        self.locked_to_player_x = True

        return self

    def lock_to_player_y(self: M) -> M:
        self.locked_to_player_y = True

        return self

    def unlock_from_player_x(self: M) -> M:
        self.locked_to_player_x = False

        return self

    def unlock_from_player_y(self: M) -> M:
        self.locked_to_player_y = False

        return self

    def move_offset(self: M, x_offset: float = 0.0, y_offset: float = 0.0) -> M:
        self.x_offset += x_offset
        self.y_offset += y_offset

        return self


@define()
class SpawnTrigger(HasTargetGroup, HasDelay, Trigger):
    editor_disable: bool = False


@define(slots=False)
class StopTrigger(HasTargetGroup, Trigger):
    pass


R = TypeVar("R", bound="RotateTrigger")


@define()
class RotateTrigger(HasEasing, HasAdditionalGroup, HasDuration, Trigger):
    target_rotation: float = 0.0
    rotation_locked: bool = False

    def target_rotate(self: R, angle: float) -> R:
        self.target_rotation += angle

        return self

    def is_rotation_locked(self) -> bool:
        return self.rotation_locked

    def lock_rotation(self: R) -> R:
        self.rotation_locked = True

        return self

    def unlock_rotation(self: R) -> R:
        self.rotation_locked = False

        return self


@define()
class FollowTrigger(HasEasing, HasAdditionalGroup, HasDuration, Trigger):
    x_modifier: float = 1.0
    y_modifier: float = 1.0


@define()
class ShakeTrigger(HasDuration, Trigger):
    strength: float = 0.0
    interval: float = 0.0


@define()
class AnimationTrigger(HasTargetGroup, Trigger):
    animation_id: int = 0


@define()
class TouchTrigger(HasTargetGroup, Trigger):
    hold_mode: bool = False
    dual_mode: bool = False
    toggle: ToggleType = ToggleType.DEFAULT


@define()
class CountTrigger(HasMultiActivate, HasActivateGroup, HasCount, HasItem, Trigger):
    pass


@define()
class InstantCountTrigger(HasActivateGroup, HasCount, HasItem, Trigger):
    comparison: InstantCountComparison = InstantCountComparison.DEFAULT


@define()
class PickupTrigger(HasCount, HasItem, Trigger):
    pass


@define()
class FollowPlayerYTrigger(HasDelay, HasTargetGroup, Trigger):
    speed: float = 1.0
    max_speed: float = 0.0
    offset: float = 0.0


@define()
class OnDeathTrigger(HasActivateGroup, HasTargetGroup, Trigger):
    pass


TRIGGER_ON_EXIT_BIT = 0b10000000_00000000

CT = TypeVar("CT", bound="CollisionTrigger")


@define()
class CollisionTrigger(HasActivateGroup, HasTargetGroup, Trigger):
    block_a_id: int = 0
    block_b_id: int = 0

    trigger_on_exit: bool = False

    @classmethod
    def from_binary(cls: Type[CT], binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT) -> CT:
        block_id_mask = BLOCK_ID_MASK
        trigger_on_exit_bit = TRIGGER_ON_EXIT_BIT

        collision_trigger = super().from_binary(binary, order)

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

    def to_binary(self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT) -> None:
        block_id_mask = BLOCK_ID_MASK

        super().to_binary(binary, order)

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


class ObjectType(Enum):
    OBJECT = 1
    ANIMATED_OBJECT = 2
    ORB = 3
    COIN = 4
    TEXT = 5
    TELEPORT = 6
    PICKUP_ITEM = 7
    COLLISION_BLOCK = 8
    COLOR_TRIGGER = 9
    PULSE_TRIGGER = 10
    MOVE_TRIGGER = 11
    SPAWN_TRIGGER = 12
    STOP_TRIGGER = 13
    ROTATE_TRIGGER = 14
    FOLLOW_TRIGGER = 15
    SHAKE_TRIGGER = 16
    ANIMATION_TRIGGER = 17
    TOUCH_TRIGGER = 18
    COUNT_TRIGGER = 19
    INSTANT_COUNT_TRIGGER = 20
    PICKUP_TRIGGER = 21
    FOLLOW_PLAYER_Y_TRIGGER = 22
    ON_DEATH_TRIGGER = 23
    COLLISION_TRIGGER = 24


OBJECT_TYPE_TO_TYPE = {
    ObjectType.OBJECT: Object,
    ObjectType.ANIMATED_OBJECT: AnimatedObject,
    ObjectType.ORB: Orb,
    ObjectType.COIN: Coin,
    ObjectType.TEXT: Text,
    ObjectType.TELEPORT: Teleport,
    ObjectType.PICKUP_ITEM: PickupItem,
    ObjectType.COLLISION_BLOCK: CollisionBlock,
    ObjectType.COLOR_TRIGGER: ColorTrigger,
    ObjectType.PULSE_TRIGGER: PulseTrigger,
    ObjectType.MOVE_TRIGGER: MoveTrigger,
    ObjectType.SPAWN_TRIGGER: SpawnTrigger,
    ObjectType.STOP_TRIGGER: StopTrigger,
    ObjectType.ROTATE_TRIGGER: RotateTrigger,
    ObjectType.FOLLOW_TRIGGER: FollowTrigger,
    ObjectType.SHAKE_TRIGGER: ShakeTrigger,
    ObjectType.ANIMATION_TRIGGER: AnimationTrigger,
    ObjectType.TOUCH_TRIGGER: TouchTrigger,
    ObjectType.COUNT_TRIGGER: CountTrigger,
    ObjectType.INSTANT_COUNT_TRIGGER: InstantCountTrigger,
    ObjectType.PICKUP_TRIGGER: PickupTrigger,
    ObjectType.FOLLOW_PLAYER_Y_TRIGGER: FollowPlayerYTrigger,
    ObjectType.ON_DEATH_TRIGGER: OnDeathTrigger,
    ObjectType.COLLISION_TRIGGER: CollisionTrigger,
}

TYPE_TO_OBJECT_TYPE = {type: object_type for object_type, type in OBJECT_TYPE_TO_TYPE.items()}


def object_from_binary(binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT) -> Object:
    reader = Reader(binary)

    object_type_value = reader.read_u8(order)
    object_type = ObjectType(object_type_value)

    return OBJECT_TYPE_TO_TYPE[object_type].from_binary(binary, order)


def object_from_bytes(data: bytes, order: ByteOrder = ByteOrder.DEFAULT) -> Object:
    return object_from_binary(BytesIO(data), order)


def object_to_binary(
    object: Object, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT
) -> None:
    object_type = TYPE_TO_OBJECT_TYPE[type(object)]

    writer = Writer(binary)

    writer.write_u8(object_type.value, order)

    object.to_binary(binary, order)


def object_to_bytes(object: Object, order: ByteOrder = ByteOrder.DEFAULT) -> bytes:
    binary = BytesIO()

    object_to_binary(object, binary, order)

    binary.seek(0)

    return binary.read()
