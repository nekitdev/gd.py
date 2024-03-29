from __future__ import annotations

from abc import abstractmethod as required
from builtins import hasattr as has_attribute
from typing import (
    TYPE_CHECKING,
    Dict,
    Iterable,
    Iterator,
    Literal,
    Optional,
    Protocol,
    Tuple,
    Type,
    Union,
    runtime_checkable,
)

from attrs import define, field
from iters.iters import iter
from iters.ordered_set import OrderedSet
from named import get_type_name
from typing_aliases import is_instance
from typing_extensions import Never, TypeGuard

from gd.api.color_channels import (
    BACKGROUND_COLOR_CHANNEL_ID,
    COLOR_1_CHANNEL_ID,
    COLOR_2_CHANNEL_ID,
    COLOR_3_CHANNEL_ID,
    COLOR_4_CHANNEL_ID,
    GROUND_COLOR_CHANNEL_ID,
    LINE_3D_COLOR_CHANNEL_ID,
    LINE_COLOR_CHANNEL_ID,
    OBJECT_COLOR_CHANNEL_ID,
    SECONDARY_GROUND_COLOR_CHANNEL_ID,
)
from gd.api.hsv import HSV
from gd.color import Color
from gd.constants import BYTE, DEFAULT_ID, EMPTY
from gd.encoding import decode_base64_string_url_safe, encode_base64_string_url_safe
from gd.enums import (
    CoinType,
    Easing,
    GameMode,
    InstantCountComparison,
    ItemMode,
    ItemType,
    LegacyColorChannelID,
    LockedToPlayerType,
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
from gd.models_constants import GROUP_IDS_SEPARATOR, OBJECT_SEPARATOR
from gd.models_utils import (
    bool_str,
    concat_any_object,
    concat_group_ids,
    concat_object,
    float_str,
    int_bool,
    split_any_object,
    split_group_ids,
    split_object,
)
from gd.robtop import RobTop
from gd.robtop_view import RobTopView

if TYPE_CHECKING:
    from typing_extensions import Self

__all__ = (
    # group IDs
    "GroupIDs",
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
    "has_target_group",
    "is_start_position",
    "is_trigger",
    "has_additional_group",
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
LEGACY_COLOR_CHANNEL_ID = 19
BASE_EDITOR_LAYER = 20
BASE_COLOR_CHANNEL_ID = 21
DETAIL_COLOR_CHANNEL_ID = 22
TARGET_COLOR_CHANNEL_ID = 23
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
BASE_HSV_MODIFIED = 41
DETAIL_HSV_MODIFIED = 42
BASE_HSV = 43
DETAIL_HSV = 44
FADE_IN = 45
HOLD = 46
FADE_OUT = 47
PULSE_MODE = 48
COPIED_HSV = 49
COPIED_COLOR_CHANNEL_ID = 50
TARGET_GROUP_ID = 51
PULSE_TARGET_TYPE = 52
PORTAL_OFFSET = 54
SMOOTH = 55
ACTIVATE_GROUP = 56
GROUP_IDS = 57
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


class GroupIDs(OrderedSet[int], RobTop):
    @classmethod
    def from_robtop(cls, string: str) -> Self:
        return iter(split_group_ids(string)).map(int).collect(cls)

    def to_robtop(self) -> str:
        return iter(self).map(str).collect(concat_group_ids)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return GROUP_IDS_SEPARATOR in string


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


OBJECT_STRING = "{object_type} (ID: {object.id}) at ({object.x}, {object.y})"
object_string = OBJECT_STRING.format


def check_object_id_present(id: Optional[int]) -> int:
    if id is None:
        raise ValueError(OBJECT_ID_NOT_PRESENT)

    return id


@define()
class Object(RobTop):
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

    base_color_channel_id: int = field(default=DEFAULT_ID)
    detail_color_channel_id: int = field(default=DEFAULT_ID)

    base_hsv: HSV = field(factory=HSV)
    detail_hsv: HSV = field(factory=HSV)

    group_ids: GroupIDs = field(factory=GroupIDs)

    group_parent: bool = field(default=DEFAULT_GROUP_PARENT)

    high_detail: bool = field(default=DEFAULT_HIGH_DETAIL)

    disable_glow: bool = field(default=DEFAULT_DISABLE_GLOW)

    special_checked: bool = field(default=DEFAULT_SPECIAL_CHECKED)

    link_id: int = field(default=DEFAULT_ID)

    unknown: bool = field(default=DEFAULT_UNKNOWN)

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        return cls.from_robtop_view(RobTopView(split_object(string)))

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        id = check_object_id_present(view.get_option(ID).map(int).extract())

        x = view.get_option(X).map(float).unwrap_or(DEFAULT_X)
        y = view.get_option(Y).map(float).unwrap_or(DEFAULT_Y)

        rotation = view.get_option(ROTATION).map(float).unwrap_or(DEFAULT_ROTATION)

        scale = view.get_option(SCALE).map(float).unwrap_or(DEFAULT_SCALE)

        h_flipped = view.get_option(H_FLIPPED).map(int_bool).unwrap_or(DEFAULT_H_FLIPPED)
        v_flipped = view.get_option(V_FLIPPED).map(int_bool).unwrap_or(DEFAULT_V_FLIPPED)

        do_not_fade = view.get_option(DO_NOT_FADE).map(int_bool).unwrap_or(DEFAULT_DO_NOT_FADE)
        do_not_enter = view.get_option(DO_NOT_ENTER).map(int_bool).unwrap_or(DEFAULT_DO_NOT_ENTER)

        z_layer = view.get_option(Z_LAYER).map(int).unwrap_or(DEFAULT_Z_LAYER)
        z_order = view.get_option(Z_ORDER).map(int).unwrap_or(DEFAULT_Z_ORDER)

        base_editor_layer = (
            view.get_option(BASE_EDITOR_LAYER).map(int).unwrap_or(DEFAULT_BASE_EDITOR_LAYER)
        )
        additional_editor_layer = (
            view.get_option(ADDITIONAL_EDITOR_LAYER)
            .map(int)
            .unwrap_or(DEFAULT_ADDITIONAL_EDITOR_LAYER)
        )

        legacy_color_channel_id = (
            view.get_option(LEGACY_COLOR_CHANNEL_ID)
            .map(int)
            .map(LegacyColorChannelID)
            .unwrap_or(LegacyColorChannelID.DEFAULT)
        )

        migrated_color_channel_id = legacy_color_channel_id.migrate()

        if migrated_color_channel_id:
            base_color_channel_id = migrated_color_channel_id
            detail_color_channel_id = migrated_color_channel_id

        else:
            base_color_channel_id = (
                view.get_option(BASE_COLOR_CHANNEL_ID).map(int).unwrap_or(DEFAULT_ID)
            )
            detail_color_channel_id = (
                view.get_option(DETAIL_COLOR_CHANNEL_ID).map(int).unwrap_or(DEFAULT_ID)
            )

        base_hsv = view.get_option(BASE_HSV).map(HSV.from_robtop).unwrap_or_else(HSV)
        detail_hsv = view.get_option(DETAIL_HSV).map(HSV.from_robtop).unwrap_or_else(HSV)

        single_group_id = view.get_option(SINGLE_GROUP_ID).map(int).unwrap_or(DEFAULT_ID)

        group_ids = view.get_option(GROUP_IDS).map(GroupIDs.from_robtop).unwrap_or_else(GroupIDs)

        if single_group_id:
            group_ids.append(single_group_id)

        group_parent = view.get_option(GROUP_PARENT).map(int_bool).unwrap_or(DEFAULT_GROUP_PARENT)
        high_detail = view.get_option(HIGH_DETAIL).map(int_bool).unwrap_or(DEFAULT_HIGH_DETAIL)
        disable_glow = view.get_option(DISABLE_GLOW).map(int_bool).unwrap_or(DEFAULT_DISABLE_GLOW)
        special_checked = (
            view.get_option(SPECIAL_CHECKED).map(int_bool).unwrap_or(DEFAULT_SPECIAL_CHECKED)
        )

        link_id = view.get_option(LINK_ID).map(int).unwrap_or(DEFAULT_ID)

        unknown = view.get_option(UNKNOWN).map(int_bool).unwrap_or(DEFAULT_UNKNOWN)

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
            base_color_channel_id=base_color_channel_id,
            detail_color_channel_id=detail_color_channel_id,
            base_hsv=base_hsv,
            detail_hsv=detail_hsv,
            group_ids=group_ids,
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

        base_color_channel_id = self.base_color_channel_id

        if base_color_channel_id:
            data[BASE_COLOR_CHANNEL_ID] = str(base_color_channel_id)

        detail_color_channel_id = self.detail_color_channel_id

        if detail_color_channel_id:
            data[DETAIL_COLOR_CHANNEL_ID] = str(detail_color_channel_id)

        base_hsv = self.base_hsv

        base_hsv_modified = not base_hsv.is_default()

        if base_hsv_modified:
            data[BASE_HSV] = base_hsv.to_robtop()
            data[BASE_HSV_MODIFIED] = bool_str(base_hsv_modified)

        detail_hsv = self.detail_hsv

        detail_hsv_modified = not detail_hsv.is_default()

        if detail_hsv_modified:
            data[DETAIL_HSV] = detail_hsv.to_robtop()
            data[DETAIL_HSV_MODIFIED] = bool_str(detail_hsv_modified)

        group_ids = self.group_ids

        if group_ids:
            data[GROUP_IDS] = group_ids.to_robtop()

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

    def is_unknown(self) -> bool:
        return self.unknown

    def add_group_ids(self, *group_ids: int) -> Self:
        self.group_ids.update(group_ids)

        return self

    def add_group_ids_from_iterable(self, iterable: Iterable[int]) -> Self:
        self.group_ids.update(iterable)

        return self

    def remove_group_ids(self, *group_ids: int) -> Self:
        self.group_ids.difference_update(group_ids)

        return self

    def remove_group_ids_from_iterable(self, iterable: Iterable[int]) -> Self:
        self.group_ids.difference_update(iterable)

        return self

    def move(self, x: float = 0.0, y: float = 0.0) -> Self:
        self.x += x
        self.y += y

        return self

    def h_flip(self) -> Self:
        self.h_flipped = not self.h_flipped

        return self

    def v_flip(self) -> Self:
        self.v_flipped = not self.v_flipped

        return self

    def rotate(self, angle: float) -> Self:
        self.rotation += angle

        return self

    def scale_by(self, scale: float) -> Self:
        self.scale *= scale

        return self

    def scale_to(self, scale: float) -> Self:
        self.scale = scale

        return self

    def scale_to_default(self) -> Self:
        return self.scale_to(DEFAULT_SCALE)

    def is_trigger(self) -> bool:
        return False

    def is_start_position(self) -> bool:
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
    def from_robtop(cls, string: str) -> Self:
        view = RobTopView(split_any_object(string))

        id = check_object_id_present(view.get_option(ID_STRING).map(int).extract())

        x = view.get_option(X_STRING).map(float).unwrap_or(DEFAULT_X)
        y = view.get_option(Y_STRING).map(float).unwrap_or(DEFAULT_Y)

        game_mode = (
            view.get_option(START_POSITION_GAME_MODE)
            .map(int)
            .map(GameMode)
            .unwrap_or(GameMode.DEFAULT)
        )

        mini_mode = (
            view.get_option(START_POSITION_MINI_MODE)
            .map(int_bool)
            .unwrap_or(DEFAULT_START_POSITION_MINI_MODE)
        )

        speed = view.get_option(START_POSITION_SPEED).map(int).map(Speed).unwrap_or(Speed.DEFAULT)

        dual_mode = (
            view.get_option(START_POSITION_DUAL_MODE)
            .map(int_bool)
            .unwrap_or(DEFAULT_START_POSITION_DUAL_MODE)
        )

        flip_gravity = (
            view.get_option(START_POSITION_FLIP_GRAVITY)
            .map(int_bool)
            .unwrap_or(DEFAULT_START_POSITION_FLIP_GRAVITY)
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
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Never:
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


@define()
class SecretCoin(Object):
    coin_id: int = DEFAULT_ID

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        coin = super().from_robtop_view(view)

        coin_id = view.get_option(COIN_ID).map(int).unwrap_or(DEFAULT_ID)

        coin.coin_id = coin_id

        return coin

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        data[COIN_ID] = str(self.coin_id)

        return data


DEFAULT_ROTATION_SPEED = 0.0
DEFAULT_DISABLE_ROTATION = False


@define()
class RotatingObject(Object):
    rotation_speed: float = DEFAULT_ROTATION_SPEED
    disable_rotation: bool = DEFAULT_DISABLE_ROTATION

    def is_disable_rotation(self) -> bool:
        return self.disable_rotation

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        rotating_object = super().from_robtop_view(view)

        rotation_speed = (
            view.get_option(ROTATION_SPEED).map(float).unwrap_or(DEFAULT_ROTATION_SPEED)
        )

        disable_rotation = (
            view.get_option(DISABLE_ROTATION).map(int_bool).unwrap_or(DEFAULT_DISABLE_ROTATION)
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


@define()
class Text(Object):
    content: str = EMPTY

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        text = super().from_robtop_view(view)

        content = view.get_option(CONTENT).map(decode_base64_string_url_safe).unwrap_or(EMPTY)

        text.content = content

        return text

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        data[CONTENT] = encode_base64_string_url_safe(self.content)

        return data


DEFAULT_SMOOTH = False
DEFAULT_PORTAL_OFFSET = 100.0


@define()
class Teleport(Object):
    portal_offset: float = DEFAULT_PORTAL_OFFSET
    smooth: bool = DEFAULT_SMOOTH

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        teleport = super().from_robtop_view(view)

        portal_offset = view.get_option(PORTAL_OFFSET).map(float).unwrap_or(DEFAULT_PORTAL_OFFSET)

        smooth = view.get_option(SMOOTH).map(int_bool).unwrap_or(DEFAULT_SMOOTH)

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


@define()
class PulsatingObject(Object):
    randomize_start: bool = DEFAULT_RANDOMIZE_START
    animation_speed: float = DEFAULT_ANIMATION_SPEED

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        pulsating_object = super().from_robtop_view(view)

        randomize_start = (
            view.get_option(RANDOMIZE_START).map(int_bool).unwrap_or(DEFAULT_RANDOMIZE_START)
        )

        animation_speed = (
            view.get_option(ANIMATION_SPEED).map(float).unwrap_or(DEFAULT_ANIMATION_SPEED)
        )

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


DEFAULT_DYNAMIC = False


@define()
class CollisionBlock(Object):
    block_id: int = DEFAULT_ID
    dynamic: bool = DEFAULT_DYNAMIC

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        collision_block = super().from_robtop_view(view)

        block_id = view.get_option(BLOCK_ID).map(int).unwrap_or(DEFAULT_ID)

        dynamic = view.get_option(DYNAMIC).map(int_bool).unwrap_or(DEFAULT_DYNAMIC)

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


DEFAULT_MULTI_ACTIVATE = False


@define()
class Orb(Object):
    multi_activate: bool = DEFAULT_MULTI_ACTIVATE

    def is_multi_activate(self) -> bool:
        return self.multi_activate

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        orb = super().from_robtop_view(view)

        multi_activate = (
            view.get_option(ORB_MULTI_ACTIVATE).map(int_bool).unwrap_or(DEFAULT_MULTI_ACTIVATE)
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


@define()
class TriggerOrb(Orb):
    target_group_id: int = DEFAULT_ID

    activate_group: bool = DEFAULT_ACTIVATE_GROUP

    def is_activate_group(self) -> bool:
        return self.activate_group

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        trigger_orb = super().from_robtop_view(view)

        activate_group = (
            view.get_option(ACTIVATE_GROUP).map(int_bool).unwrap_or(DEFAULT_ACTIVATE_GROUP)
        )

        target_group_id = view.get_option(TARGET_GROUP_ID).map(int).unwrap_or(DEFAULT_ID)

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


@define()
class ItemCounter(Object):
    item_id: int = DEFAULT_ID

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        item_counter = super().from_robtop_view(view)

        item_id = view.get_option(ITEM_ID).map(int).unwrap_or(DEFAULT_ID)

        item_counter.item_id = item_id

        return item_counter

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        item_id = self.item_id

        if item_id:
            data[ITEM_ID] = str(item_id)

        return data


@define()
class ToggleItem(Object):
    target_group_id: int = DEFAULT_ID

    activate_group: bool = DEFAULT_ACTIVATE_GROUP

    def is_activate_group(self) -> bool:
        return self.activate_group

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        toggle_item = super().from_robtop_view(view)

        target_group_id = view.get_option(TARGET_GROUP_ID).map(int).unwrap_or(DEFAULT_ID)

        toggle_item.target_group_id = target_group_id

        return toggle_item

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        data[TARGET_GROUP_ID] = str(self.target_group_id)

        data[ITEM_MODE] = str(ItemMode.TOGGLE.value)

        return data


DEFAULT_SUBTRACT_COUNT = False


@define()
class PickupItem(Object):
    item_id: int = DEFAULT_ID

    subtract_count: bool = DEFAULT_SUBTRACT_COUNT

    def is_subtract_count(self) -> bool:
        return self.subtract_count

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        pickup_item = super().from_robtop_view(view)

        item_id = view.get_option(ITEM_ID).map(int).unwrap_or(DEFAULT_ID)

        subtract_count = (
            view.get_option(SUBTRACT_COUNT).map(int_bool).unwrap_or(DEFAULT_SUBTRACT_COUNT)
        )

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


DEFAULT_TOUCH_TRIGGERED = False
DEFAULT_SPAWN_TRIGGERED = False
DEFAULT_MULTI_TRIGGER = False


@define()
class Trigger(Object):
    touch_triggered: bool = DEFAULT_TOUCH_TRIGGERED
    spawn_triggered: bool = DEFAULT_SPAWN_TRIGGERED
    multi_trigger: bool = DEFAULT_MULTI_TRIGGER

    def is_trigger(self) -> Literal[True]:
        return True

    def is_touch_triggered(self) -> bool:
        return self.touch_triggered

    def is_spawn_triggered(self) -> bool:
        return self.spawn_triggered

    def is_multi_trigger(self) -> bool:
        return self.multi_trigger

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        trigger = super().from_robtop_view(view)

        touch_triggered = (
            view.get_option(TOUCH_TRIGGERED).map(int_bool).unwrap_or(DEFAULT_TOUCH_TRIGGERED)
        )
        spawn_triggered = (
            view.get_option(SPAWN_TRIGGERED).map(int_bool).unwrap_or(DEFAULT_SPAWN_TRIGGERED)
        )
        multi_trigger = (
            view.get_option(MULTI_TRIGGER).map(int_bool).unwrap_or(DEFAULT_MULTI_TRIGGER)
        )

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

DEFAULT_BLENDING = False


@define()
class BaseColorTrigger(Trigger):
    target_color_channel_id: int = DEFAULT_ID

    duration: float = DEFAULT_DURATION

    blending: bool = DEFAULT_BLENDING

    def is_blending(self) -> bool:
        return self.blending

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        base_color_trigger = super().from_robtop_view(view)

        target_color_channel_id = (
            view.get_option(TARGET_COLOR_CHANNEL_ID).map(int).unwrap_or(DEFAULT_ID)
        )

        duration = view.get_option(DURATION).map(float).unwrap_or(DEFAULT_DURATION)

        blending = view.get_option(BLENDING).map(int_bool).unwrap_or(DEFAULT_BLENDING)

        base_color_trigger.target_color_channel_id = target_color_channel_id

        base_color_trigger.duration = duration

        base_color_trigger.blending = blending

        return base_color_trigger

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        data[TARGET_COLOR_CHANNEL_ID] = str(self.target_color_channel_id)

        data[DURATION] = float_str(self.duration)

        blending = self.is_blending()

        if blending:
            data[BLENDING] = bool_str(blending)

        return data


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


DEFAULT_OPACITY = 1.0


@define()
class PlayerColorTrigger(BaseColorTrigger):
    player_color: PlayerColor = PlayerColor.DEFAULT

    opacity: float = DEFAULT_OPACITY

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        player_color_trigger = super().from_robtop_view(view)

        player_color_1 = (
            view.get_option(PLAYER_COLOR_1).map(int_bool).unwrap_or(DEFAULT_PLAYER_COLOR_1)
        )
        player_color_2 = (
            view.get_option(PLAYER_COLOR_2).map(int_bool).unwrap_or(DEFAULT_PLAYER_COLOR_2)
        )

        player_color = compute_player_color(player_color_1, player_color_2)

        opacity = view.get_option(OPACITY).map(float).unwrap_or(DEFAULT_OPACITY)

        player_color_trigger.player_color = player_color

        player_color_trigger.opacity = opacity

        return player_color_trigger

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

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


@define()
class NormalColorTrigger(BaseColorTrigger):
    color: Color = field(factory=Color.default)

    opacity: float = field(default=DEFAULT_OPACITY)

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        normal_color_trigger = super().from_robtop_view(view)

        red = view.get_option(RED).map(int).unwrap_or(DEFAULT_RED)
        green = view.get_option(GREEN).map(int).unwrap_or(DEFAULT_GREEN)
        blue = view.get_option(BLUE).map(int).unwrap_or(DEFAULT_BLUE)

        color = Color.from_rgb(red, green, blue)

        opacity = view.get_option(OPACITY).map(float).unwrap_or(DEFAULT_OPACITY)

        normal_color_trigger.color = color

        normal_color_trigger.opacity = opacity

        return normal_color_trigger

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        color = self.color

        here = {
            RED: str(color.red),
            GREEN: str(color.green),
            BLUE: str(color.blue),
            OPACITY: float_str(self.opacity),
        }

        data.update(here)

        return data


DEFAULT_COPY_OPACITY = False

COPIED_OPACITY = "opacity is copied"


@define()
class CopiedColorTrigger(BaseColorTrigger):
    blending: bool = field(default=DEFAULT_BLENDING)

    copied_color_channel_id: int = field(default=DEFAULT_ID)
    copied_hsv: HSV = field(factory=HSV)

    opacity: Optional[float] = field(default=None)

    def copy_opacity(self) -> Self:
        self.opacity = None

        return self

    def is_blending(self) -> bool:
        return self.blending

    def is_copy_opacity(self) -> bool:
        return self.opacity is None

    @property
    def opacity_checked(self) -> float:
        opacity = self.opacity

        if opacity is None:
            raise ValueError(COPIED_OPACITY)

        return opacity

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        copied_color_trigger = super().from_robtop_view(view)

        copied_color_channel_id = (
            view.get_option(COPIED_COLOR_CHANNEL_ID).map(int).unwrap_or(DEFAULT_ID)
        )

        copied_hsv = view.get_option(COPIED_HSV).map(HSV.from_robtop).unwrap_or_else(HSV)

        copy_opacity = view.get_option(COPY_OPACITY).map(int_bool).unwrap_or(DEFAULT_COPY_OPACITY)

        if copy_opacity:
            opacity = None

        else:
            opacity = view.get_option(OPACITY).map(float).unwrap_or(DEFAULT_OPACITY)

        copied_color_trigger.copied_color_channel_id = copied_color_channel_id
        copied_color_trigger.copied_hsv = copied_hsv

        copied_color_trigger.opacity = opacity

        return copied_color_trigger

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        copy_opacity = self.is_copy_opacity()

        here = {
            COPIED_COLOR_CHANNEL_ID: str(self.copied_color_channel_id),
            COPIED_HSV: self.copied_hsv.to_robtop(),
            COPY_OPACITY: bool_str(copy_opacity),
        }

        data.update(here)

        if not copy_opacity:
            data[OPACITY] = float_str(self.opacity_checked)

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


class BaseCompatibilityColorTrigger(Compatibility, Trigger):
    duration: float = DEFAULT_DURATION

    blending: bool = DEFAULT_BLENDING

    def is_blending(self) -> bool:
        return self.blending

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        base_compatibility_color_trigger = super().from_robtop_view(view)

        duration = view.get_option(DURATION).map(float).unwrap_or(DEFAULT_DURATION)

        blending = view.get_option(BLENDING).map(int_bool).unwrap_or(DEFAULT_BLENDING)

        base_compatibility_color_trigger.duration = duration

        base_compatibility_color_trigger.blending = blending

        return base_compatibility_color_trigger

    def to_robtop_data(self) -> Never:
        raise NotImplementedError(MIGRATE)


@define()
class PlayerCompatibilityColorTrigger(BaseCompatibilityColorTrigger):
    player_color: PlayerColor = PlayerColor.DEFAULT

    opacity: float = DEFAULT_OPACITY

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        player_compatibility_color_trigger = super().from_robtop_view(view)

        opacity = view.get_option(OPACITY).map(float).unwrap_or(DEFAULT_OPACITY)

        player_color_1 = (
            view.get_option(PLAYER_COLOR_1).map(int_bool).unwrap_or(DEFAULT_PLAYER_COLOR_1)
        )
        player_color_2 = (
            view.get_option(PLAYER_COLOR_2).map(int_bool).unwrap_or(DEFAULT_PLAYER_COLOR_2)
        )

        player_color = compute_player_color(player_color_1, player_color_2)

        player_compatibility_color_trigger.player_color = player_color

        player_compatibility_color_trigger.opacity = opacity

        return player_compatibility_color_trigger

    def generate_migration(self, target_color_channel_id: int) -> PlayerColorTrigger:
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
            base_color_channel_id=self.base_color_channel_id,
            detail_color_channel_id=self.detail_color_channel_id,
            base_hsv=self.base_hsv,
            detail_hsv=self.detail_hsv,
            group_ids=self.group_ids,
            group_parent=self.is_group_parent(),
            high_detail=self.is_high_detail(),
            disable_glow=self.has_disable_glow(),
            special_checked=self.is_special_checked(),
            link_id=self.link_id,
            unknown=self.is_unknown(),
            touch_triggered=self.is_touch_triggered(),
            spawn_triggered=self.is_spawn_triggered(),
            multi_trigger=self.is_multi_trigger(),
            target_color_channel_id=target_color_channel_id,  # NOTE: here is the main difference :p
            duration=self.duration,
            blending=self.is_blending(),
            opacity=self.opacity,
            player_color=self.player_color,
        )


@define()
class NormalCompatibilityColorTrigger(BaseCompatibilityColorTrigger):
    color: Color = field(factory=Color.default)

    opacity: float = field(default=DEFAULT_OPACITY)

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        normal_compatibility_color_trigger = super().from_robtop_view(view)

        red = view.get_option(RED).map(int).unwrap_or(DEFAULT_RED)
        green = view.get_option(GREEN).map(int).unwrap_or(DEFAULT_GREEN)
        blue = view.get_option(BLUE).map(int).unwrap_or(DEFAULT_BLUE)

        color = Color.from_rgb(red, green, blue)

        opacity = view.get_option(OPACITY).map(float).unwrap_or(DEFAULT_OPACITY)

        normal_compatibility_color_trigger.color = color

        normal_compatibility_color_trigger.opacity = opacity

        return normal_compatibility_color_trigger

    def generate_migration(self, target_color_channel_id: int) -> NormalColorTrigger:
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
            base_color_channel_id=self.base_color_channel_id,
            detail_color_channel_id=self.detail_color_channel_id,
            base_hsv=self.base_hsv,
            detail_hsv=self.detail_hsv,
            group_ids=self.group_ids,
            group_parent=self.is_group_parent(),
            high_detail=self.is_high_detail(),
            disable_glow=self.has_disable_glow(),
            special_checked=self.is_special_checked(),
            link_id=self.link_id,
            unknown=self.is_unknown(),
            touch_triggered=self.is_touch_triggered(),
            spawn_triggered=self.is_spawn_triggered(),
            multi_trigger=self.is_multi_trigger(),
            target_color_channel_id=target_color_channel_id,  # NOTE: here is the main difference :p
            duration=self.duration,
            blending=self.is_blending(),
            opacity=self.opacity,
            color=self.color,
        )


@define()
class CopiedCompatibilityColorTrigger(BaseCompatibilityColorTrigger):
    copied_color_channel_id: int = field(default=DEFAULT_ID)
    copied_hsv: HSV = field(factory=HSV)

    opacity: Optional[float] = field(default=None)

    def is_copy_opacity(self) -> bool:
        return self.opacity is None

    def copy_opacity(self) -> Self:
        self.opacity = None

        return self

    @property
    def opacity_checked(self) -> float:
        opacity = self.opacity

        if opacity is None:
            raise ValueError(COPIED_OPACITY)

        return opacity

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        copied_compatibility_color_trigger = super().from_robtop_view(view)

        copied_color_channel_id = (
            view.get_option(COPIED_COLOR_CHANNEL_ID).map(int).unwrap_or(DEFAULT_ID)
        )

        copied_hsv = view.get_option(COPIED_HSV).map(HSV.from_robtop).unwrap_or_else(HSV)

        copy_opacity = view.get_option(COPY_OPACITY).map(int_bool).unwrap_or(DEFAULT_COPY_OPACITY)

        if copy_opacity:
            opacity = None

        else:
            opacity = view.get_option(OPACITY).map(float).unwrap_or(DEFAULT_OPACITY)

        copied_compatibility_color_trigger.copied_color_channel_id = copied_color_channel_id
        copied_compatibility_color_trigger.copied_hsv = copied_hsv

        copied_compatibility_color_trigger.opacity = opacity

        return copied_compatibility_color_trigger

    def generate_migration(self, target_color_channel_id: int) -> CopiedColorTrigger:
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
            base_color_channel_id=self.base_color_channel_id,
            detail_color_channel_id=self.detail_color_channel_id,
            base_hsv=self.base_hsv,
            detail_hsv=self.detail_hsv,
            group_ids=self.group_ids,
            group_parent=self.is_group_parent(),
            high_detail=self.is_high_detail(),
            disable_glow=self.has_disable_glow(),
            special_checked=self.is_special_checked(),
            link_id=self.link_id,
            unknown=self.is_unknown(),
            touch_triggered=self.is_touch_triggered(),
            spawn_triggered=self.is_spawn_triggered(),
            multi_trigger=self.is_multi_trigger(),
            target_color_channel_id=target_color_channel_id,  # NOTE: here is the main difference :p
            duration=self.duration,
            blending=self.is_blending(),
            copied_color_channel_id=self.copied_color_channel_id,
            copied_hsv=self.copied_hsv,
            opacity=self.opacity,
        )


CompatibilityColorTrigger = Union[
    PlayerCompatibilityColorTrigger,
    NormalCompatibilityColorTrigger,
    CopiedCompatibilityColorTrigger,
]


DEFAULT_TINT_GROUND = False


@define()
class PlayerBackgroundColorTrigger(PlayerCompatibilityColorTrigger):
    tint_ground: bool = DEFAULT_TINT_GROUND

    def is_tint_ground(self) -> bool:
        return self.tint_ground

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        player_background_color_trigger = super().from_robtop_view(view)

        tint_ground = view.get_option(TINT_GROUND).map(int_bool).unwrap_or(DEFAULT_TINT_GROUND)

        player_background_color_trigger.tint_ground = tint_ground

        return player_background_color_trigger

    def migrate(self) -> PlayerColorTrigger:
        return self.generate_migration(BACKGROUND_COLOR_CHANNEL_ID)

    def migrate_additional(self) -> Optional[PlayerColorTrigger]:
        return self.generate_migration(GROUND_COLOR_CHANNEL_ID) if self.is_tint_ground() else None


@define()
class NormalBackgroundColorTrigger(NormalCompatibilityColorTrigger):
    tint_ground: bool = DEFAULT_TINT_GROUND

    def is_tint_ground(self) -> bool:
        return self.tint_ground

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        normal_background_color_trigger = super().from_robtop_view(view)

        tint_ground = view.get_option(TINT_GROUND).map(int_bool).unwrap_or(DEFAULT_TINT_GROUND)

        normal_background_color_trigger.tint_ground = tint_ground

        return normal_background_color_trigger

    def migrate(self) -> NormalColorTrigger:
        return self.generate_migration(BACKGROUND_COLOR_CHANNEL_ID)

    def migrate_additional(self) -> Optional[NormalColorTrigger]:
        return self.generate_migration(GROUND_COLOR_CHANNEL_ID) if self.is_tint_ground() else None


@define()
class CopiedBackgroundColorTrigger(CopiedCompatibilityColorTrigger):
    tint_ground: bool = DEFAULT_TINT_GROUND

    def is_tint_ground(self) -> bool:
        return self.tint_ground

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        copied_background_color_trigger = super().from_robtop_view(view)

        tint_ground = view.get_option(TINT_GROUND).map(int_bool).unwrap_or(DEFAULT_TINT_GROUND)

        copied_background_color_trigger.tint_ground = tint_ground

        return copied_background_color_trigger

    def migrate(self) -> CopiedColorTrigger:
        return self.generate_migration(BACKGROUND_COLOR_CHANNEL_ID)

    def migrate_additional(self) -> Optional[CopiedColorTrigger]:
        return self.generate_migration(GROUND_COLOR_CHANNEL_ID) if self.is_tint_ground() else None


@define()
class PlayerGroundColorTrigger(PlayerCompatibilityColorTrigger):
    def migrate(self) -> PlayerColorTrigger:
        return self.generate_migration(GROUND_COLOR_CHANNEL_ID)


@define()
class NormalGroundColorTrigger(NormalCompatibilityColorTrigger):
    def migrate(self) -> NormalColorTrigger:
        return self.generate_migration(GROUND_COLOR_CHANNEL_ID)


@define()
class CopiedGroundColorTrigger(CopiedCompatibilityColorTrigger):
    def migrate(self) -> CopiedColorTrigger:
        return self.generate_migration(GROUND_COLOR_CHANNEL_ID)


@define()
class PlayerLineColorTrigger(PlayerCompatibilityColorTrigger):
    def migrate(self) -> PlayerColorTrigger:
        return self.generate_migration(LINE_COLOR_CHANNEL_ID)


@define()
class NormalLineColorTrigger(NormalCompatibilityColorTrigger):
    def migrate(self) -> NormalColorTrigger:
        return self.generate_migration(LINE_COLOR_CHANNEL_ID)


@define()
class CopiedLineColorTrigger(CopiedCompatibilityColorTrigger):
    def migrate(self) -> CopiedColorTrigger:
        return self.generate_migration(LINE_COLOR_CHANNEL_ID)


@define()
class PlayerObjectColorTrigger(PlayerCompatibilityColorTrigger):
    def migrate(self) -> PlayerColorTrigger:
        return self.generate_migration(OBJECT_COLOR_CHANNEL_ID)


@define()
class NormalObjectColorTrigger(NormalCompatibilityColorTrigger):
    def migrate(self) -> NormalColorTrigger:
        return self.generate_migration(OBJECT_COLOR_CHANNEL_ID)


@define()
class CopiedObjectColorTrigger(CopiedCompatibilityColorTrigger):
    def migrate(self) -> CopiedColorTrigger:
        return self.generate_migration(OBJECT_COLOR_CHANNEL_ID)


@define()
class PlayerLine3DColorTrigger(PlayerCompatibilityColorTrigger):
    def migrate(self) -> PlayerColorTrigger:
        return self.generate_migration(LINE_3D_COLOR_CHANNEL_ID)


@define()
class NormalLine3DColorTrigger(NormalCompatibilityColorTrigger):
    def migrate(self) -> NormalColorTrigger:
        return self.generate_migration(LINE_3D_COLOR_CHANNEL_ID)


@define()
class CopiedLine3DColorTrigger(CopiedCompatibilityColorTrigger):
    def migrate(self) -> CopiedColorTrigger:
        return self.generate_migration(LINE_3D_COLOR_CHANNEL_ID)


@define()
class PlayerSecondaryGroundColorTrigger(PlayerCompatibilityColorTrigger):
    def migrate(self) -> PlayerColorTrigger:
        return self.generate_migration(SECONDARY_GROUND_COLOR_CHANNEL_ID)


@define()
class NormalSecondaryGroundColorTrigger(NormalCompatibilityColorTrigger):
    def migrate(self) -> NormalColorTrigger:
        return self.generate_migration(SECONDARY_GROUND_COLOR_CHANNEL_ID)


@define()
class CopiedSecondaryGroundColorTrigger(CopiedCompatibilityColorTrigger):
    def migrate(self) -> CopiedColorTrigger:
        return self.generate_migration(SECONDARY_GROUND_COLOR_CHANNEL_ID)


@define()
class PlayerColor1Trigger(PlayerCompatibilityColorTrigger):
    def migrate(self) -> PlayerColorTrigger:
        return self.generate_migration(COLOR_1_CHANNEL_ID)


@define()
class NormalColor1Trigger(NormalCompatibilityColorTrigger):
    def migrate(self) -> NormalColorTrigger:
        return self.generate_migration(COLOR_1_CHANNEL_ID)


@define()
class CopiedColor1Trigger(CopiedCompatibilityColorTrigger):
    def migrate(self) -> CopiedColorTrigger:
        return self.generate_migration(COLOR_1_CHANNEL_ID)


@define()
class PlayerColor2Trigger(PlayerCompatibilityColorTrigger):
    def migrate(self) -> PlayerColorTrigger:
        return self.generate_migration(COLOR_2_CHANNEL_ID)


@define()
class NormalColor2Trigger(NormalCompatibilityColorTrigger):
    def migrate(self) -> NormalColorTrigger:
        return self.generate_migration(COLOR_2_CHANNEL_ID)


@define()
class CopiedColor2Trigger(CopiedCompatibilityColorTrigger):
    def migrate(self) -> CopiedColorTrigger:
        return self.generate_migration(COLOR_2_CHANNEL_ID)


@define()
class PlayerColor3Trigger(PlayerCompatibilityColorTrigger):
    def migrate(self) -> PlayerColorTrigger:
        return self.generate_migration(COLOR_3_CHANNEL_ID)


@define()
class NormalColor3Trigger(NormalCompatibilityColorTrigger):
    def migrate(self) -> NormalColorTrigger:
        return self.generate_migration(COLOR_3_CHANNEL_ID)


@define()
class CopiedColor3Trigger(CopiedCompatibilityColorTrigger):
    def migrate(self) -> CopiedColorTrigger:
        return self.generate_migration(COLOR_3_CHANNEL_ID)


@define()
class PlayerColor4Trigger(PlayerCompatibilityColorTrigger):
    def migrate(self) -> PlayerColorTrigger:
        return self.generate_migration(COLOR_4_CHANNEL_ID)


@define()
class NormalColor4Trigger(NormalCompatibilityColorTrigger):
    def migrate(self) -> NormalColorTrigger:
        return self.generate_migration(COLOR_4_CHANNEL_ID)


@define()
class CopiedColor4Trigger(CopiedCompatibilityColorTrigger):
    def migrate(self) -> CopiedColorTrigger:
        return self.generate_migration(COLOR_4_CHANNEL_ID)


@define()
class AlphaTrigger(Trigger):
    target_group_id: int = DEFAULT_ID
    duration: float = DEFAULT_DURATION
    opacity: float = DEFAULT_OPACITY

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        alpha_trigger = super().from_robtop_view(view)

        target_group_id = view.get_option(TARGET_GROUP_ID).map(int).unwrap_or(DEFAULT_ID)

        duration = view.get_option(DURATION).map(float).unwrap_or(DEFAULT_DURATION)

        opacity = view.get_option(OPACITY).map(float).unwrap_or(DEFAULT_OPACITY)

        alpha_trigger.target_group_id = target_group_id
        alpha_trigger.duration = duration
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

DEFAULT_EXCLUSIVE = False


@define()
class BasePulseTrigger(Trigger):
    fade_in: float = DEFAULT_FADE_IN
    hold: float = DEFAULT_HOLD
    fade_out: float = DEFAULT_FADE_OUT

    exclusive: bool = field(default=DEFAULT_EXCLUSIVE)

    def is_exclusive(self) -> bool:
        return self.exclusive

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        base_pulse_trigger = super().from_robtop_view(view)

        fade_in = view.get_option(FADE_IN).map(float).unwrap_or(DEFAULT_FADE_IN)
        hold = view.get_option(HOLD).map(float).unwrap_or(DEFAULT_HOLD)
        fade_out = view.get_option(FADE_OUT).map(float).unwrap_or(DEFAULT_FADE_OUT)

        exclusive = view.get_option(EXCLUSIVE).map(int_bool).unwrap_or(DEFAULT_EXCLUSIVE)

        base_pulse_trigger.fade_in = fade_in
        base_pulse_trigger.hold = hold
        base_pulse_trigger.fade_out = fade_out

        base_pulse_trigger.exclusive = exclusive

        return base_pulse_trigger

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        here = {
            FADE_IN: float_str(self.fade_in),
            HOLD: float_str(self.hold),
            FADE_OUT: float_str(self.fade_out),
        }

        data.update(here)

        exclusive = self.is_exclusive()

        if exclusive:
            data[EXCLUSIVE] = bool_str(exclusive)

        return data


@define()
class PulseColorTrigger(BasePulseTrigger):
    color: Color = field(factory=Color.default)

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        pulse_color_trigger = super().from_robtop_view(view)

        red = view.get_option(RED).map(int).unwrap_or(DEFAULT_RED)
        green = view.get_option(GREEN).map(int).unwrap_or(DEFAULT_GREEN)
        blue = view.get_option(BLUE).map(int).unwrap_or(DEFAULT_BLUE)

        color = Color.from_rgb(red, green, blue)

        pulse_color_trigger.color = color

        return pulse_color_trigger

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        color = self.color

        here = {
            RED: str(color.red),
            GREEN: str(color.green),
            BLUE: str(color.blue),
            PULSE_MODE: str(PulseMode.COLOR.value),
        }

        data.update(here)

        return data


@define()
class PulseHSVTrigger(BasePulseTrigger):
    copied_color_channel_id: int = field(default=DEFAULT_ID)
    copied_hsv: HSV = field(factory=HSV)

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        pulse_hsv_trigger = super().from_robtop_view(view)

        copied_color_channel_id = (
            view.get_option(COPIED_COLOR_CHANNEL_ID).map(int).unwrap_or(DEFAULT_ID)
        )
        copied_hsv = view.get_option(COPIED_HSV).map(HSV.from_robtop).unwrap_or_else(HSV)

        pulse_hsv_trigger.copied_color_channel_id = copied_color_channel_id
        pulse_hsv_trigger.copied_hsv = copied_hsv

        return pulse_hsv_trigger

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        here = {
            COPIED_COLOR_CHANNEL_ID: str(self.copied_color_channel_id),
            COPIED_HSV: self.copied_hsv.to_robtop(),
            PULSE_MODE: str(PulseMode.HSV.value),
        }

        data.update(here)

        return data


@define()
class PulseColorChannelTrigger(PulseColorTrigger):
    target_color_channel_id: int = DEFAULT_ID

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        pulse_color_channel_trigger = super().from_robtop_view(view)

        # XXX: why `TARGET_GROUP_ID` here?

        target_color_channel_id = view.get_option(TARGET_GROUP_ID).map(int).unwrap_or(DEFAULT_ID)

        pulse_color_channel_trigger.target_color_channel_id = target_color_channel_id

        return pulse_color_channel_trigger

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        data[TARGET_GROUP_ID] = str(self.target_color_channel_id)  # XXX: why?
        data[PULSE_TARGET_TYPE] = str(PulseTargetType.COLOR_CHANNEL.value)

        return data


@define()
class PulseHSVChannelTrigger(PulseHSVTrigger):
    target_color_channel_id: int = DEFAULT_ID

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        pulse_hsv_channel_trigger = super().from_robtop_view(view)

        # XXX: uwu

        target_color_channel_id = view.get_option(TARGET_GROUP_ID).map(int).unwrap_or(DEFAULT_ID)

        pulse_hsv_channel_trigger.target_color_channel_id = target_color_channel_id

        return pulse_hsv_channel_trigger

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        data[TARGET_GROUP_ID] = str(self.target_color_channel_id)  # XXX: why?
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


@define()
class PulseColorGroupTrigger(PulseColorTrigger):
    target_group_id: int = DEFAULT_ID
    pulse_type: PulseType = PulseType.DEFAULT

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        pulse_color_group_trigger = super().from_robtop_view(view)

        target_group_id = view.get_option(TARGET_GROUP_ID).map(int).unwrap_or(DEFAULT_ID)

        main_only = view.get_option(MAIN_ONLY).map(int_bool).unwrap_or(DEFAULT_MAIN_ONLY)
        detail_only = view.get_option(DETAIL_ONLY).map(int_bool).unwrap_or(DEFAULT_DETAIL_ONLY)

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


@define()
class PulseHSVGroupTrigger(PulseHSVTrigger):
    target_group_id: int = DEFAULT_ID

    pulse_type: PulseType = PulseType.DEFAULT

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        pulse_hsv_group_trigger = super().from_robtop_view(view)

        target_group_id = view.get_option(TARGET_GROUP_ID).map(int).unwrap_or(DEFAULT_ID)

        main_only = view.get_option(MAIN_ONLY).map(int_bool).unwrap_or(DEFAULT_MAIN_ONLY)
        detail_only = view.get_option(DETAIL_ONLY).map(int_bool).unwrap_or(DEFAULT_DETAIL_ONLY)

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


@define()
class BaseMoveTrigger(Trigger):
    target_group_id: int = DEFAULT_ID

    easing: Easing = Easing.DEFAULT
    easing_rate: float = DEFAULT_EASING_RATE

    duration: float = DEFAULT_DURATION

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        base_move_trigger = super().from_robtop_view(view)

        target_group_id = view.get_option(TARGET_GROUP_ID).map(int).unwrap_or(DEFAULT_ID)

        easing = view.get_option(EASING).map(int).map(Easing).unwrap_or(Easing.DEFAULT)
        easing_rate = view.get_option(EASING_RATE).map(float).unwrap_or(DEFAULT_EASING_RATE)

        duration = view.get_option(DURATION).map(float).unwrap_or(DEFAULT_DURATION)

        base_move_trigger.target_group_id = target_group_id

        base_move_trigger.easing = easing
        base_move_trigger.easing_rate = easing_rate

        base_move_trigger.duration = duration

        return base_move_trigger

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        here = {
            DURATION: float_str(self.duration),
            EASING: str(self.easing.value),
            EASING_RATE: float_str(self.easing_rate),
            TARGET_GROUP_ID: str(self.target_group_id),
        }

        data.update(here)

        return data

    def is_normal(self) -> bool:
        return False

    def is_target(self) -> bool:
        return False


DEFAULT_X_OFFSET = 0.0
DEFAULT_Y_OFFSET = 0.0

DEFAULT_LOCKED_TO_PLAYER_X = False
DEFAULT_LOCKED_TO_PLAYER_Y = False


def compute_locked_type(locked_to_x: bool, locked_to_y: bool) -> LockedToPlayerType:
    locked_type = LockedToPlayerType.NONE

    if locked_to_x:
        locked_type |= LockedToPlayerType.X

    if locked_to_y:
        locked_type |= LockedToPlayerType.Y

    return locked_type


@define()
class NormalMoveTrigger(BaseMoveTrigger):
    x_offset: float = DEFAULT_X_OFFSET
    y_offset: float = DEFAULT_Y_OFFSET

    locked_to_player: LockedToPlayerType = LockedToPlayerType.DEFAULT

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        normal_move_trigger = super().from_robtop_view(view)

        x_offset = view.get_option(X_OFFSET).map(float).unwrap_or(DEFAULT_X_OFFSET)
        y_offset = view.get_option(Y_OFFSET).map(float).unwrap_or(DEFAULT_Y_OFFSET)

        locked_to_player_x = (
            view.get_option(LOCKED_TO_PLAYER_X).map(int_bool).unwrap_or(DEFAULT_LOCKED_TO_PLAYER_X)
        )
        locked_to_player_y = (
            view.get_option(LOCKED_TO_PLAYER_Y).map(int_bool).unwrap_or(DEFAULT_LOCKED_TO_PLAYER_Y)
        )

        locked_to_player = compute_locked_type(locked_to_player_x, locked_to_player_y)

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
        self, x_offset: float = DEFAULT_X_OFFSET, y_offset: float = DEFAULT_Y_OFFSET
    ) -> Self:
        self.x_offset += x_offset
        self.y_offset += y_offset

        return self

    def lock_to_player_x(self) -> Self:
        self.locked_to_player |= LockedToPlayerType.X

        return self

    def lock_to_player_y(self) -> Self:
        self.locked_to_player |= LockedToPlayerType.Y

        return self

    def lock_to_player(self) -> Self:
        self.locked_to_player = LockedToPlayerType.BOTH

        return self

    def unlock_from_player(self) -> Self:
        self.locked_to_player = LockedToPlayerType.NONE

        return self


USE_TARGET_TRUE = True


@define()
class TargetMoveTrigger(BaseMoveTrigger):
    additional_group_id: int = DEFAULT_ID

    target_type: TargetType = TargetType.DEFAULT

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        target_move_trigger = super().from_robtop_view(view)

        additional_group_id = view.get_option(ADDITIONAL_GROUP_ID).map(int).unwrap_or(DEFAULT_ID)

        simple_target_type = (
            view.get_option(TARGET_TYPE)
            .map(int)
            .map(SimpleTargetType)
            .unwrap_or(SimpleTargetType.DEFAULT)
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

    def target_x(self) -> Self:
        self.target_type |= TargetType.X

        return self

    def target_y(self) -> Self:
        self.target_type |= TargetType.Y

        return self

    def target_both(self) -> Self:
        self.target_type = TargetType.BOTH

        return self

    def target_none(self) -> Self:
        self.target_type = TargetType.NONE

        return self


MoveTrigger = Union[NormalMoveTrigger, TargetMoveTrigger]


DEFAULT_DELAY = 0.0
DEFAULT_EDITOR_DISABLE = False


@define()
class SpawnTrigger(Trigger):
    target_group_id: int = DEFAULT_ID

    delay: float = DEFAULT_DELAY

    editor_disable: bool = DEFAULT_EDITOR_DISABLE

    def is_editor_disable(self) -> bool:
        return self.editor_disable

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        spawn_trigger = super().from_robtop_view(view)

        target_group_id = view.get_option(TARGET_GROUP_ID).map(int).unwrap_or(DEFAULT_ID)

        delay = view.get_option(SPAWN_DELAY).map(float).unwrap_or(DEFAULT_DELAY)

        editor_disable = (
            view.get_option(EDITOR_DISABLE).map(int_bool).unwrap_or(DEFAULT_EDITOR_DISABLE)
        )

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


@define()
class StopTrigger(Trigger):
    target_group_id: int = DEFAULT_ID

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        stop_trigger = super().from_robtop_view(view)

        target_group_id = view.get_option(TARGET_GROUP_ID).map(int).unwrap_or(DEFAULT_ID)

        stop_trigger.target_group_id = target_group_id

        return stop_trigger

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        data[TARGET_GROUP_ID] = str(self.target_group_id)

        return data


DEFAULT_TOGGLED = False


@define()
class ToggleTrigger(Trigger):
    target_group_id: int = DEFAULT_ID

    activate_group: bool = DEFAULT_ACTIVATE_GROUP

    def is_activate_group(self) -> bool:
        return self.activate_group

    def toggle(self) -> Self:
        self.activate_group = not self.activate_group

        return self

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        toggle_trigger = super().from_robtop_view(view)

        target_group_id = view.get_option(TARGET_GROUP_ID).map(int).unwrap_or(DEFAULT_ID)

        activate_group = (
            view.get_option(ACTIVATE_GROUP).map(int_bool).unwrap_or(DEFAULT_ACTIVATE_GROUP)
        )

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


DEFAULT_ROTATIONS = 0.0
DEFAULT_DEGREES = 0.0


DEFAULT_TARGET_ROTATION = 0.0
DEFAULT_ROTATION_LOCKED = False


@define()
class RotateTrigger(Trigger):
    target_group_id: int = DEFAULT_ID
    additional_group_id: int = DEFAULT_ID

    duration: float = DEFAULT_DURATION

    easing: Easing = Easing.DEFAULT
    easing_rate: float = DEFAULT_EASING_RATE

    target_rotation: float = DEFAULT_TARGET_ROTATION
    rotation_locked: bool = DEFAULT_ROTATION_LOCKED

    def target_rotate(self, angle: float) -> Self:
        self.target_rotation += angle

        return self

    def is_rotation_locked(self) -> bool:
        return self.rotation_locked

    def lock_rotation(self) -> Self:
        self.rotation_locked = True

        return self

    def unlock_rotation(self) -> Self:
        self.rotation_locked = False

        return self

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        rotate_trigger = super().from_robtop_view(view)

        target_group_id = view.get_option(TARGET_GROUP_ID).map(int).unwrap_or(DEFAULT_ID)
        additional_group_id = view.get_option(ADDITIONAL_GROUP_ID).map(int).unwrap_or(DEFAULT_ID)

        duration = view.get_option(DURATION).map(float).unwrap_or(DEFAULT_DURATION)

        easing = view.get_option(EASING).map(int).map(Easing).unwrap_or(Easing.DEFAULT)
        easing_rate = view.get_option(EASING_RATE).map(float).unwrap_or(DEFAULT_EASING_RATE)

        rotations = view.get_option(ROTATIONS).map(float).unwrap_or(DEFAULT_ROTATIONS)
        degrees = view.get_option(DEGREES).map(float).unwrap_or(DEFAULT_DEGREES)

        target_rotation = rotations * FULL_ROTATION + degrees

        rotation_locked = (
            view.get_option(ROTATION_LOCKED).map(int_bool).unwrap_or(DEFAULT_ROTATION_LOCKED)
        )

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
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        follow_trigger = super().from_robtop_view(view)

        target_group_id = view.get_option(TARGET_GROUP_ID).map(int).unwrap_or(DEFAULT_ID)
        additional_group_id = view.get_option(ADDITIONAL_GROUP_ID).map(int).unwrap_or(DEFAULT_ID)

        duration = view.get_option(DURATION).map(float).unwrap_or(DEFAULT_DURATION)

        easing = view.get_option(EASING).map(int).map(Easing).unwrap_or(Easing.DEFAULT)
        easing_rate = view.get_option(EASING_RATE).map(float).unwrap_or(DEFAULT_EASING_RATE)

        x_modifier = view.get_option(X_MODIFIER).map(float).unwrap_or(DEFAULT_X_MODIFIER)
        y_modifier = view.get_option(Y_MODIFIER).map(float).unwrap_or(DEFAULT_Y_MODIFIER)

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


@define()
class ShakeTrigger(Trigger):
    duration: float = DEFAULT_DURATION
    strength: float = DEFAULT_STRENGTH
    interval: float = DEFAULT_INTERVAL

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        shake_trigger = super().from_robtop_view(view)

        duration = view.get_option(DURATION).map(float).unwrap_or(DEFAULT_DURATION)
        strength = view.get_option(STRENGTH).map(float).unwrap_or(DEFAULT_STRENGTH)
        interval = view.get_option(INTERVAL).map(float).unwrap_or(DEFAULT_INTERVAL)

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


@define()
class AnimateTrigger(Trigger):
    target_group_id: int = DEFAULT_ID

    animation_id: int = DEFAULT_ID

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        animate_trigger = super().from_robtop_view(view)

        target_group_id = view.get_option(TARGET_GROUP_ID).map(int).unwrap_or(DEFAULT_ID)

        animation_id = view.get_option(ANIMATION_ID).map(int).unwrap_or(DEFAULT_ID)

        animate_trigger.target_group_id = target_group_id

        animate_trigger.animation_id = animation_id

        return animate_trigger

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        data[TARGET_GROUP_ID] = str(self.target_group_id)

        data[ANIMATION_ID] = str(self.animation_id)

        return data


DEFAULT_HOLD_MODE = False
DEFAULT_DUAL_MODE = False


@define()
class TouchTrigger(Trigger):
    target_group_id: int = DEFAULT_ID

    hold_mode: bool = DEFAULT_HOLD_MODE
    dual_mode: bool = DEFAULT_DUAL_MODE
    toggle_type: ToggleType = ToggleType.DEFAULT

    def is_hold_mode(self) -> bool:
        return self.hold_mode

    def is_dual_mode(self) -> bool:
        return self.dual_mode

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        touch_trigger = super().from_robtop_view(view)

        target_group_id = view.get_option(TARGET_GROUP_ID).map(int).unwrap_or(DEFAULT_ID)

        hold_mode = view.get_option(HOLD_MODE).map(int_bool).unwrap_or(DEFAULT_HOLD_MODE)
        dual_mode = view.get_option(DUAL_MODE).map(int_bool).unwrap_or(DEFAULT_DUAL_MODE)

        toggle_type = (
            view.get_option(TOGGLE_TYPE).map(int).map(ToggleType).unwrap_or(ToggleType.DEFAULT)
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
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        count_trigger = super().from_robtop_view(view)

        item_id = view.get_option(ITEM_ID).map(int).unwrap_or(DEFAULT_ID)

        count = view.get_option(COUNT).map(int).unwrap_or(DEFAULT_COUNT)

        subtract_count = (
            view.get_option(SUBTRACT_COUNT).map(int_bool).unwrap_or(DEFAULT_SUBTRACT_COUNT)
        )

        if subtract_count:
            count = -count

        activate_group = (
            view.get_option(ACTIVATE_GROUP).map(int_bool).unwrap_or(DEFAULT_ACTIVATE_GROUP)
        )
        multi_activate = (
            view.get_option(TRIGGER_MULTI_ACTIVATE).map(int_bool).unwrap_or(DEFAULT_MULTI_ACTIVATE)
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


@define()
class InstantCountTrigger(Trigger):
    item_id: int = DEFAULT_ID
    count: int = DEFAULT_COUNT

    activate_group: bool = DEFAULT_ACTIVATE_GROUP

    comparison: InstantCountComparison = InstantCountComparison.DEFAULT

    def is_activate_group(self) -> bool:
        return self.activate_group

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        instant_count_trigger = super().from_robtop_view(view)

        item_id = view.get_option(ITEM_ID).map(int).unwrap_or(DEFAULT_ID)

        count = view.get_option(COUNT).map(int).unwrap_or(DEFAULT_COUNT)

        activate_group = (
            view.get_option(ACTIVATE_GROUP).map(int_bool).unwrap_or(DEFAULT_ACTIVATE_GROUP)
        )

        comparison = (
            view.get_option(COMPARISON)
            .map(int)
            .map(InstantCountComparison)
            .unwrap_or(InstantCountComparison.DEFAULT)
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


@define()
class PickupTrigger(Trigger):
    item_id: int = DEFAULT_ID
    count: int = DEFAULT_COUNT

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        pickup_trigger = super().from_robtop_view(view)

        item_id = view.get_option(ITEM_ID).map(int).unwrap_or(DEFAULT_ID)

        count = view.get_option(COUNT).map(int).unwrap_or(DEFAULT_COUNT)

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


@define()
class FollowPlayerYTrigger(Trigger):
    target_group_id: int = DEFAULT_ID

    duration: float = DEFAULT_DURATION
    delay: float = DEFAULT_DELAY

    speed: float = DEFAULT_SPEED
    max_speed: float = DEFAULT_MAX_SPEED
    offset: float = DEFAULT_OFFSET

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        follow_player_y_trigger = super().from_robtop_view(view)

        target_group_id = view.get_option(TARGET_GROUP_ID).map(int).unwrap_or(DEFAULT_ID)

        duration = view.get_option(DURATION).map(float).unwrap_or(DEFAULT_DURATION)

        delay = view.get_option(FOLLOW_DELAY).map(float).unwrap_or(DEFAULT_DELAY)

        speed = view.get_option(SPEED).map(float).unwrap_or(DEFAULT_SPEED)
        max_speed = view.get_option(MAX_SPEED).map(float).unwrap_or(DEFAULT_MAX_SPEED)
        offset = view.get_option(OFFSET).map(float).unwrap_or(DEFAULT_OFFSET)

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


@define()
class OnDeathTrigger(Trigger):
    target_group_id: int = DEFAULT_ID

    activate_group: bool = DEFAULT_ACTIVATE_GROUP

    def is_activate_group(self) -> bool:
        return self.activate_group

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        on_death_trigger = super().from_robtop_view(view)

        target_group_id = view.get_option(TARGET_GROUP_ID).map(int).unwrap_or(DEFAULT_ID)

        activate_group = (
            view.get_option(ACTIVATE_GROUP).map(int_bool).unwrap_or(DEFAULT_ACTIVATE_GROUP)
        )

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


DEFAULT_TRIGGER_ON_EXIT = False


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
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        collision_trigger = super().from_robtop_view(view)

        target_group_id = view.get_option(TARGET_GROUP_ID).map(int).unwrap_or(DEFAULT_ID)

        activate_group = (
            view.get_option(ACTIVATE_GROUP).map(int_bool).unwrap_or(DEFAULT_ACTIVATE_GROUP)
        )

        block_a_id = view.get_option(BLOCK_A_ID).map(int).unwrap_or(DEFAULT_ID)
        block_b_id = view.get_option(BLOCK_B_ID).map(int).unwrap_or(DEFAULT_ID)

        trigger_on_exit = (
            view.get_option(TRIGGER_ON_EXIT).map(int_bool).unwrap_or(DEFAULT_TRIGGER_ON_EXIT)
        )

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
    BACKGROUND_TRIGGER_ID: PlayerBackgroundColorTrigger,
    GROUND_TRIGGER_ID: PlayerGroundColorTrigger,
    LINE_TRIGGER_ID: PlayerLineColorTrigger,
    OBJECT_TRIGGER_ID: PlayerObjectColorTrigger,
    COLOR_1_TRIGGER_ID: PlayerColor1Trigger,
    COLOR_2_TRIGGER_ID: PlayerColor2Trigger,
    COLOR_3_TRIGGER_ID: PlayerColor3Trigger,
    COLOR_4_TRIGGER_ID: PlayerColor4Trigger,
    LINE_3D_TRIGGER_ID: PlayerLine3DColorTrigger,
    SECONDARY_GROUND_TRIGGER_ID: PlayerSecondaryGroundColorTrigger,
    COLOR_TRIGGER_ID: PlayerColorTrigger,
}

NORMAL_COLOR_TRIGGER_MAPPING = {
    BACKGROUND_TRIGGER_ID: NormalBackgroundColorTrigger,
    GROUND_TRIGGER_ID: NormalGroundColorTrigger,
    LINE_TRIGGER_ID: NormalLineColorTrigger,
    OBJECT_TRIGGER_ID: NormalObjectColorTrigger,
    COLOR_1_TRIGGER_ID: NormalColor1Trigger,
    COLOR_2_TRIGGER_ID: NormalColor2Trigger,
    COLOR_3_TRIGGER_ID: NormalColor3Trigger,
    COLOR_4_TRIGGER_ID: NormalColor4Trigger,
    LINE_3D_TRIGGER_ID: NormalLine3DColorTrigger,
    SECONDARY_GROUND_TRIGGER_ID: NormalSecondaryGroundColorTrigger,
    COLOR_TRIGGER_ID: NormalColorTrigger,
}

COPIED_COLOR_TRIGGER_MAPPING = {
    BACKGROUND_TRIGGER_ID: CopiedBackgroundColorTrigger,
    GROUND_TRIGGER_ID: CopiedGroundColorTrigger,
    LINE_TRIGGER_ID: CopiedLineColorTrigger,
    OBJECT_TRIGGER_ID: CopiedObjectColorTrigger,
    COLOR_1_TRIGGER_ID: CopiedColor1Trigger,
    COLOR_2_TRIGGER_ID: CopiedColor2Trigger,
    COLOR_3_TRIGGER_ID: CopiedColor3Trigger,
    COLOR_4_TRIGGER_ID: CopiedColor4Trigger,
    LINE_3D_TRIGGER_ID: CopiedLine3DColorTrigger,
    SECONDARY_GROUND_TRIGGER_ID: CopiedSecondaryGroundColorTrigger,
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

COPIED_COLOR_CHANNEL_ID_STRING = str(COPIED_COLOR_CHANNEL_ID)

PULSE_TARGET_TYPE_STRING = str(PULSE_TARGET_TYPE)

ITEM_MODE_STRING = str(ITEM_MODE)

USE_TARGET_STRING = str(USE_TARGET)


DEFAULT_USE_TARGET = False


def object_from_robtop(string: str) -> Object:
    view = RobTopView(split_any_object(string))

    object_id = check_object_id_present(view.get_option(ID_STRING).map(int).extract())

    object_type: Type[Object]

    if object_id in COLOR_TRIGGER_IDS:
        player_color_1 = (
            view.get_option(PLAYER_COLOR_1_STRING).map(int_bool).unwrap_or(DEFAULT_PLAYER_COLOR_1)
        )
        player_color_2 = (
            view.get_option(PLAYER_COLOR_2_STRING).map(int_bool).unwrap_or(DEFAULT_PLAYER_COLOR_2)
        )

        player_color = compute_player_color(player_color_1, player_color_2)

        if player_color.is_used():
            object_type = PLAYER_COLOR_TRIGGER_MAPPING[object_id]  # type: ignore[assignment]

        else:
            copied_color_channel_id = (
                view.get_option(COPIED_COLOR_CHANNEL_ID_STRING).map(int).extract()
            )

            if copied_color_channel_id is None:
                object_type = COPIED_COLOR_TRIGGER_MAPPING[object_id]  # type: ignore

            else:
                object_type = NORMAL_COLOR_TRIGGER_MAPPING[object_id]  # type: ignore

    elif object_id == MOVE_TRIGGER_ID:
        use_target = view.get_option(USE_TARGET_STRING).map(int_bool).unwrap_or(DEFAULT_USE_TARGET)

        if use_target:
            object_type = TargetMoveTrigger

        else:
            object_type = NormalMoveTrigger

    elif object_id == PULSE_TRIGGER_ID:
        pulse_mode = (
            view.get_option(PULSE_MODE_STRING).map(int).map(PulseMode).unwrap_or(PulseMode.DEFAULT)
        )

        pulse_target_type = (
            view.get_option(PULSE_TARGET_TYPE_STRING)
            .map(int)
            .map(PulseTargetType)
            .unwrap_or(PulseTargetType.DEFAULT)
        )

        object_type = PULSE_TRIGGER_MAPPING[pulse_mode, pulse_target_type]

    elif object_id in ITEM_IDS:
        item_mode = (
            view.get_option(ITEM_MODE_STRING).map(int).map(ItemMode).unwrap_or(ItemMode.DEFAULT)
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
