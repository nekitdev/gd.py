from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Iterable, Optional, Union

from attrs import define, field
from iters.iters import iter
from typing_extensions import TypeGuard

from gd.api.hsv import HSV
from gd.color import Color
from gd.constants import BYTE
from gd.enums import PlayerColor, SpecialColorChannelID
from gd.models_utils import (
    bool_str,
    concat_color_channel,
    concat_color_channels,
    float_str,
    int_bool,
    split_color_channel,
    split_color_channels,
)
from gd.robtop import FromRobTop, RobTop
from gd.robtop_view import RobTopView

if TYPE_CHECKING:
    from typing_extensions import Self

__all__ = (
    # cases (variants)
    "PlayerColorChannel",
    "NormalColorChannel",
    "CopiedColorChannel",
    # union
    "ColorChannel",
    # color channels
    "ColorChannels",
)

RED = 1
GREEN = 2
BLUE = 3
PLAYER_COLOR = 4
BLENDING = 5
ID = 6
OPACITY = 7
OPACITY_TOGGLED = 8
COPIED_ID = 9
COLOR_HSV = 10
TO_RED = 11
TO_GREEN = 12
TO_BLUE = 13
DURATION = 14
TO_OPACITY = 15
COPY_OPACITY = 17
UNKNOWN = 18


DEFAULT_OPACITY_TOGGLED = True

DEFAULT_TO_RED = BYTE
DEFAULT_TO_GREEN = BYTE
DEFAULT_TO_BLUE = BYTE

DEFAULT_DURATION = 0.0

DEFAULT_TO_OPACITY = 1.0

DEFAULT_UNKNOWN = False


DEFAULT_RED = BYTE
DEFAULT_GREEN = BYTE
DEFAULT_BLUE = BYTE

DEFAULT_BLENDING = False

DEFAULT_OPACITY = 1.0

DEFAULT_COPY_OPACITY = False


BACKGROUND_COLOR_CHANNEL_ID = SpecialColorChannelID.BACKGROUND.id
GROUND_COLOR_CHANNEL_ID = SpecialColorChannelID.GROUND.id
LINE_COLOR_CHANNEL_ID = SpecialColorChannelID.LINE.id
LINE_3D_COLOR_CHANNEL_ID = SpecialColorChannelID.LINE_3D.id
OBJECT_COLOR_CHANNEL_ID = SpecialColorChannelID.OBJECT.id
SECONDARY_GROUND_COLOR_CHANNEL_ID = SpecialColorChannelID.SECONDARY_GROUND.id

COLOR_1_CHANNEL_ID = 1
COLOR_2_CHANNEL_ID = 2
COLOR_3_CHANNEL_ID = 3
COLOR_4_CHANNEL_ID = 4


COLOR_CHANNEL_ID_NOT_PRESENT = "color channel ID is not present"


def check_color_channel_id_present(id: Optional[int]) -> int:
    if id is None:
        raise ValueError(COLOR_CHANNEL_ID_NOT_PRESENT)

    return id


@define()
class BaseColorChannel(RobTop):
    """Represents base color channels."""

    id: int

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        data = split_color_channel(string)

        view = RobTopView(data)

        return cls.from_robtop_view(view)

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        id = check_color_channel_id_present(view.get_option(ID).map(int).extract())

        return cls(id=id)

    def to_robtop(self) -> str:
        return concat_color_channel(self.to_robtop_data())

    def to_robtop_data(self) -> Dict[int, str]:
        data = {ID: str(self.id)}

        return data

    def is_player(self) -> bool:
        return False

    def is_normal(self) -> bool:
        return False

    def is_copied(self) -> bool:
        return False


@define()
class PlayerColorChannel(BaseColorChannel):
    """Represents player color channels."""

    player_color: PlayerColor

    opacity: float = DEFAULT_OPACITY

    blending: bool = DEFAULT_BLENDING

    def is_blending(self) -> bool:
        return self.blending

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        id = check_color_channel_id_present(view.get_option(ID).map(int).extract())

        player_color = (
            view.get_option(PLAYER_COLOR).map(int).map(PlayerColor).unwrap_or(PlayerColor.DEFAULT)
        )

        opacity = view.get_option(OPACITY).map(float).unwrap_or(DEFAULT_OPACITY)

        blending = view.get_option(BLENDING).map(int_bool).unwrap_or(DEFAULT_BLENDING)

        return cls(id=id, player_color=player_color, opacity=opacity, blending=blending)

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        here = {
            PLAYER_COLOR: str(self.player_color.value),
            OPACITY: float_str(self.opacity),
            OPACITY_TOGGLED: bool_str(DEFAULT_OPACITY_TOGGLED),
        }

        data.update(here)

        blending = self.is_blending()

        if blending:
            data[BLENDING] = bool_str(blending)

        return data

    def is_player(self) -> bool:
        return True


@define()
class NormalColorChannel(BaseColorChannel):
    """Represents normal color channels."""

    color: Color

    opacity: float = DEFAULT_OPACITY

    blending: bool = DEFAULT_BLENDING

    def is_blending(self) -> bool:
        return self.blending

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        id = check_color_channel_id_present(view.get_option(ID).map(int).extract())

        red = view.get_option(RED).map(int).unwrap_or(DEFAULT_RED)
        green = view.get_option(GREEN).map(int).unwrap_or(DEFAULT_GREEN)
        blue = view.get_option(BLUE).map(int).unwrap_or(DEFAULT_BLUE)

        color = Color.from_rgb(red, green, blue)

        opacity = view.get_option(OPACITY).map(float).unwrap_or(DEFAULT_OPACITY)

        blending = view.get_option(BLENDING).map(int_bool).unwrap_or(DEFAULT_BLENDING)

        return cls(id=id, color=color, opacity=opacity, blending=blending)

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        color = self.color

        here = {
            RED: str(color.red),
            GREEN: str(color.green),
            BLUE: str(color.blue),
            OPACITY: float_str(self.opacity),
            OPACITY_TOGGLED: bool_str(DEFAULT_OPACITY_TOGGLED),
        }

        data.update(here)

        blending = self.is_blending()

        if blending:
            data[BLENDING] = bool_str(blending)

        return data

    def is_normal(self) -> bool:
        return True


COLOR_CHANNEL_COPIED_ID_NOT_PRESENT = "color channel copied ID is not present"
COPIED_OPACITY = "opacity is copied"


def check_color_channel_copied_id_present(id: Optional[int]) -> int:
    if id is None:
        raise ValueError(COLOR_CHANNEL_COPIED_ID_NOT_PRESENT)

    return id


@define()
class CopiedColorChannel(BaseColorChannel):
    """Represents copied color channels."""

    copied_id: int = field()

    hsv: HSV = field(factory=HSV)

    opacity: Optional[float] = field(default=None)

    blending: bool = field(default=DEFAULT_BLENDING)

    def is_blending(self) -> bool:
        return self.blending

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        id = check_color_channel_id_present(view.get_option(ID).map(int).extract())

        copied_id = check_color_channel_copied_id_present(
            view.get_option(COPIED_ID).map(int).extract()
        )

        hsv = view.get_option(COLOR_HSV).map(HSV.from_robtop).unwrap_or_else(HSV)

        copy_opacity = view.get_option(COPY_OPACITY).map(int_bool).unwrap_or(DEFAULT_COPY_OPACITY)

        if copy_opacity:
            opacity = None

        else:
            opacity = view.get_option(OPACITY).map(float).unwrap_or(DEFAULT_OPACITY)

        blending = view.get_option(BLENDING).map(int_bool).unwrap_or(DEFAULT_BLENDING)

        return cls(id=id, copied_id=copied_id, hsv=hsv, opacity=opacity, blending=blending)

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        copy_opacity = self.is_copy_opacity()

        here = {
            COPIED_ID: str(self.copied_id),
            COLOR_HSV: self.hsv.to_robtop(),
            COPY_OPACITY: bool_str(copy_opacity),
            OPACITY_TOGGLED: bool_str(DEFAULT_OPACITY_TOGGLED),
        }

        data.update(here)

        if not copy_opacity:
            data[OPACITY] = float_str(self.opacity_checked)

        blending = self.is_blending()

        if blending:
            data[BLENDING] = bool_str(blending)

        return data

    def is_copied(self) -> bool:
        return True

    @property
    def opacity_checked(self) -> float:
        opacity = self.opacity

        if opacity is None:
            raise ValueError(COPIED_OPACITY)

        return opacity

    def is_copy_opacity(self) -> bool:
        return self.opacity is None

    def copy_opacity(self) -> Self:
        self.opacity = None

        return self


ColorChannel = Union[PlayerColorChannel, NormalColorChannel, CopiedColorChannel]
"""Represents color channels."""


def is_player_color_channel(color_channel: ColorChannel) -> TypeGuard[PlayerColorChannel]:
    return color_channel.is_player()


def is_normal_color_channel(color_channel: ColorChannel) -> TypeGuard[NormalColorChannel]:
    return color_channel.is_normal()


def is_copied_color_channel(color_channel: ColorChannel) -> TypeGuard[CopiedColorChannel]:
    return color_channel.is_copied()


def color_channel_from_robtop(string: str) -> ColorChannel:
    view = RobTopView(split_color_channel(string))

    player_color = (
        view.get_option(PLAYER_COLOR).map(int).map(PlayerColor).unwrap_or(PlayerColor.DEFAULT)
    )

    if player_color.is_used():
        return PlayerColorChannel.from_robtop_view(view)

    copied_id = view.get_option(COPIED_ID).map(int).extract()

    if copied_id is None:
        return NormalColorChannel.from_robtop_view(view)

    return CopiedColorChannel.from_robtop_view(view)


def color_channel_to_robtop(color_channel: ColorChannel) -> str:
    return color_channel.to_robtop()


class ColorChannels(Dict[int, ColorChannel]):
    """Represents collections of color channels."""

    def copy(self) -> Self:
        return type(self)(self)

    @classmethod
    def from_color_channel_iterable(cls, color_channels: Iterable[ColorChannel]) -> Self:
        return cls({color_channel.id: color_channel for color_channel in color_channels})

    @classmethod
    def from_color_channels(cls, *color_channels: ColorChannel) -> Self:
        return cls.from_color_channel_iterable(color_channels)

    @property
    def length(self) -> int:
        return len(self)

    def add(self, color_channel: ColorChannel) -> None:
        self[color_channel.id] = color_channel

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        return cls.from_color_channel_iterable(
            iter(split_color_channels(string)).filter(None).map(color_channel_from_robtop).unwrap()
        )

    def to_robtop(self) -> str:
        return concat_color_channels(map(color_channel_to_robtop, self.values()))


@define()
class PlayerCompatibilityColorChannel(FromRobTop):
    player_color: PlayerColor

    blending: bool = DEFAULT_BLENDING

    def is_blending(self) -> bool:
        return self.blending

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        data = split_color_channel(string)

        view = RobTopView(data)

        return cls.from_robtop_view(view)

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        player_color = (
            view.get_option(PLAYER_COLOR).map(int).map(PlayerColor).unwrap_or(PlayerColor.DEFAULT)
        )

        blending = view.get_option(BLENDING).map(int_bool).unwrap_or(DEFAULT_BLENDING)

        return cls(player_color=player_color, blending=blending)

    def migrate(self, id: int) -> PlayerColorChannel:
        return PlayerColorChannel(
            id=id, player_color=self.player_color, blending=self.is_blending()
        )


@define()
class NormalCompatibilityColorChannel(FromRobTop):
    color: Color

    blending: bool = DEFAULT_BLENDING

    def is_blending(self) -> bool:
        return self.blending

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        data = split_color_channel(string)

        view = RobTopView(data)

        return cls.from_robtop_view(view)

    @classmethod
    def from_robtop_view(cls, view: RobTopView[int, str]) -> Self:
        red = view.get_option(RED).map(int).unwrap_or(DEFAULT_RED)
        green = view.get_option(GREEN).map(int).unwrap_or(DEFAULT_GREEN)
        blue = view.get_option(BLUE).map(int).unwrap_or(DEFAULT_BLUE)

        color = Color.from_rgb(red, green, blue)

        blending = view.get_option(BLENDING).map(int_bool).unwrap_or(DEFAULT_BLENDING)

        return cls(color=color, blending=blending)

    def migrate(self, id: int) -> NormalColorChannel:
        return NormalColorChannel(id=id, color=self.color, blending=self.is_blending())


CompatibilityColorChannel = Union[PlayerCompatibilityColorChannel, NormalCompatibilityColorChannel]


def compatibility_color_channel_from_robtop(string: str) -> CompatibilityColorChannel:
    view = RobTopView(split_color_channel(string))

    player_color = (
        view.get_option(PLAYER_COLOR).map(int).map(PlayerColor).unwrap_or(PlayerColor.DEFAULT)
    )

    if player_color.is_used():
        return PlayerCompatibilityColorChannel.from_robtop_view(view)

    return NormalCompatibilityColorChannel.from_robtop_view(view)
