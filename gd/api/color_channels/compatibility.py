from attrs import define
from typing_extensions import Self

from gd.api.color_channels.core import DEFAULT_BLENDING
from gd.api.enums.player_colors import PlayerColor
from gd.internals.robtop.protocols import FromRobTop
from gd.internals.robtop.views import RobTopView

# NOTE: compatibility types only implement `FromRobTop` and not `ToRobTop` to force migrations


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
