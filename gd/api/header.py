from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field

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
    ColorChannels,
    CompatibilityColorChannel,
    NormalCompatibilityColorChannel,
    PlayerCompatibilityColorChannel,
    compatibility_color_channel_from_robtop,
)
from gd.api.guidelines import Guidelines
from gd.color import Color
from gd.constants import BYTE, DEFAULT_ID
from gd.enums import GameMode, PlayerColor, Speed
from gd.models_constants import HEADER_SEPARATOR
from gd.models_utils import bool_str, concat_header, float_str, int_bool, split_header
from gd.robtop import RobTop
from gd.robtop_view import RobTopView, StringRobTopView

if TYPE_CHECKING:
    from typing_extensions import Self


__all__ = ("Header",)

DEFAULT_MINI_MODE = False

DEFAULT_DUAL_MODE = False

DEFAULT_TWO_PLAYER = False

DEFAULT_FLIP_GRAVITY = False

DEFAULT_SONG_OFFSET = 0.0

DEFAULT_SONG_FADE_IN = False
DEFAULT_SONG_FADE_OUT = False

DEFAULT_PLATFORMER_MODE = False

DEFAULT_COLOR_CHANNELS_PAGE = 0

NOT_START_POSITION = False


DEFAULT_RED = BYTE
DEFAULT_GREEN = BYTE
DEFAULT_BLUE = BYTE


GAME_MODE = "kA2"
MINI_MODE = "kA3"
SPEED = "kA4"
BACKGROUND_ID = "kA6"
GROUND_ID = "kA7"
DUAL_MODE = "kA8"
START_POSITION = "kA9"
TWO_PLAYER = "kA10"
FLIP_GRAVITY = "kA11"
SONG_OFFSET = "kA13"
GUIDELINES = "kA14"
SONG_FADE_IN = "kA15"
SONG_FADE_OUT = "kA16"
GROUND_LINE_ID = "kA17"
FONT_ID = "kA18"
PLATFORMER_MODE = "kA22"
COLOR_CHANNELS = "kS38"
COLOR_CHANNELS_PAGE = "kS39"

# compatiblity

BACKGROUND_COLOR_CHANNEL = "kS29"
GROUND_COLOR_CHANNEL = "kS30"
LINE_COLOR_CHANNEL = "kS31"
OBJECT_COLOR_CHANNEL = "kS32"
COLOR_1_CHANNEL = "kS33"
COLOR_2_CHANNEL = "kS34"
COLOR_3_CHANNEL = "kS35"
COLOR_4_CHANNEL = "kS36"
LINE_3D_COLOR_CHANNEL = "kS37"

# even more compatibility

BACKGROUND_COLOR_CHANNEL_RED = "kS1"
BACKGROUND_COLOR_CHANNEL_GREEN = "kS2"
BACKGROUND_COLOR_CHANNEL_BLUE = "kS3"
GROUND_COLOR_CHANNEL_RED = "kS4"
GROUND_COLOR_CHANNEL_GREEN = "kS5"
GROUND_COLOR_CHANNEL_BLUE = "kS6"
LINE_COLOR_CHANNEL_RED = "kS7"
LINE_COLOR_CHANNEL_GREEN = "kS8"
LINE_COLOR_CHANNEL_BLUE = "kS9"
OBJECT_COLOR_CHANNEL_RED = "kS10"
OBJECT_COLOR_CHANNEL_GREEN = "kS11"
OBJECT_COLOR_CHANNEL_BLUE = "kS12"
COLOR_1_CHANNEL_RED = "kS13"
COLOR_1_CHANNEL_GREEN = "kS14"
COLOR_1_CHANNEL_BLUE = "kS15"
BACKGROUND_COLOR_CHANNEL_PLAYER_COLOR = "kS16"
GROUND_COLOR_CHANNEL_PLAYER_COLOR = "kS17"
LINE_COLOR_CHANNEL_PLAYER_COLOR = "kS18"
OBJECT_COLOR_CHANNEL_PLAYER_COLOR = "kS19"
COLOR_1_CHANNEL_PLAYER_COLOR = "kS20"


@define()
class Header(RobTop):
    game_mode: GameMode = field(default=GameMode.DEFAULT)
    mini_mode: bool = field(default=DEFAULT_MINI_MODE)
    speed: Speed = field(default=Speed.DEFAULT)
    background_id: int = field(default=DEFAULT_ID)
    ground_id: int = field(default=DEFAULT_ID)
    dual_mode: bool = field(default=DEFAULT_DUAL_MODE)
    two_player: bool = field(default=DEFAULT_TWO_PLAYER)
    flip_gravity: bool = field(default=DEFAULT_FLIP_GRAVITY)
    song_offset: float = field(default=DEFAULT_SONG_OFFSET)
    guidelines: Guidelines = field(factory=Guidelines)
    song_fade_in: bool = field(default=DEFAULT_SONG_FADE_IN)
    song_fade_out: bool = field(default=DEFAULT_SONG_FADE_OUT)
    ground_line_id: int = field(default=DEFAULT_ID)
    font_id: int = field(default=DEFAULT_ID)
    platformer_mode: bool = field(default=DEFAULT_PLATFORMER_MODE)
    color_channels: ColorChannels = field(factory=ColorChannels)
    color_channels_page: int = field(default=DEFAULT_COLOR_CHANNELS_PAGE)

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        return cls.from_robtop_view(RobTopView(split_header(string)))

    @classmethod
    def from_robtop_view(cls, view: StringRobTopView[str]) -> Self:
        game_mode = view.get_option(GAME_MODE).map(int).map(GameMode).unwrap_or(GameMode.DEFAULT)

        mini_mode = view.get_option(MINI_MODE).map(int_bool).unwrap_or(DEFAULT_MINI_MODE)

        speed = view.get_option(SPEED).map(int).map(Speed).unwrap_or(Speed.DEFAULT)

        background_id = view.get_option(BACKGROUND_ID).map(int).unwrap_or(DEFAULT_ID)

        ground_id = view.get_option(GROUND_ID).map(int).unwrap_or(DEFAULT_ID)

        dual_mode = view.get_option(DUAL_MODE).map(int_bool).unwrap_or(DEFAULT_DUAL_MODE)

        two_player = view.get_option(TWO_PLAYER).map(int_bool).unwrap_or(DEFAULT_TWO_PLAYER)

        flip_gravity = view.get_option(FLIP_GRAVITY).map(int_bool).unwrap_or(DEFAULT_FLIP_GRAVITY)

        song_offset = view.get_option(SONG_OFFSET).map(float).unwrap_or(DEFAULT_SONG_OFFSET)

        guidelines = (
            view.get_option(GUIDELINES).map(Guidelines.from_robtop).unwrap_or_else(Guidelines)
        )

        song_fade_in = view.get_option(SONG_FADE_IN).map(int_bool).unwrap_or(DEFAULT_SONG_FADE_IN)
        song_fade_out = (
            view.get_option(SONG_FADE_OUT).map(int_bool).unwrap_or(DEFAULT_SONG_FADE_OUT)
        )

        ground_line_id = view.get_option(GROUND_LINE_ID).map(int).unwrap_or(DEFAULT_ID)

        font_id = view.get_option(FONT_ID).map(int).unwrap_or(DEFAULT_ID)

        platformer_mode = (
            view.get_option(PLATFORMER_MODE).map(int_bool).unwrap_or(DEFAULT_PLATFORMER_MODE)
        )

        color_channels = ColorChannels()

        # even more compatibility

        background_color_channel_player_color = (
            view.get_option(BACKGROUND_COLOR_CHANNEL_PLAYER_COLOR)
            .map(int)
            .map(PlayerColor)
            .unwrap_or(PlayerColor.DEFAULT)
        )

        ground_color_channel_player_color = (
            view.get_option(GROUND_COLOR_CHANNEL_PLAYER_COLOR)
            .map(int)
            .map(PlayerColor)
            .unwrap_or(PlayerColor.DEFAULT)
        )

        line_color_channel_player_color = (
            view.get_option(LINE_COLOR_CHANNEL_PLAYER_COLOR)
            .map(int)
            .map(PlayerColor)
            .unwrap_or(PlayerColor.DEFAULT)
        )

        object_color_channel_player_color = (
            view.get_option(OBJECT_COLOR_CHANNEL_PLAYER_COLOR)
            .map(int)
            .map(PlayerColor)
            .unwrap_or(PlayerColor.DEFAULT)
        )

        color_1_channel_player_color = (
            view.get_option(COLOR_1_CHANNEL_PLAYER_COLOR)
            .map(int)
            .map(PlayerColor)
            .unwrap_or(PlayerColor.DEFAULT)
        )

        background_color_channel: CompatibilityColorChannel

        if background_color_channel_player_color.is_used():
            background_color_channel = PlayerCompatibilityColorChannel(
                background_color_channel_player_color
            )

        else:
            background_color_channel_red = (
                view.get_option(BACKGROUND_COLOR_CHANNEL_RED).map(int).unwrap_or(DEFAULT_RED)
            )
            background_color_channel_green = (
                view.get_option(BACKGROUND_COLOR_CHANNEL_GREEN).map(int).unwrap_or(DEFAULT_GREEN)
            )
            background_color_channel_blue = (
                view.get_option(BACKGROUND_COLOR_CHANNEL_BLUE).map(int).unwrap_or(DEFAULT_BLUE)
            )

            background_color_channel_color = Color.from_rgb(
                background_color_channel_red,
                background_color_channel_green,
                background_color_channel_blue,
            )

            background_color_channel = NormalCompatibilityColorChannel(
                background_color_channel_color
            )

        ground_color_channel: CompatibilityColorChannel

        if ground_color_channel_player_color.is_used():
            ground_color_channel = PlayerCompatibilityColorChannel(
                ground_color_channel_player_color
            )

        else:
            ground_color_channel_red = (
                view.get_option(GROUND_COLOR_CHANNEL_RED).map(int).unwrap_or(DEFAULT_RED)
            )
            ground_color_channel_green = (
                view.get_option(GROUND_COLOR_CHANNEL_GREEN).map(int).unwrap_or(DEFAULT_GREEN)
            )
            ground_color_channel_blue = (
                view.get_option(GROUND_COLOR_CHANNEL_BLUE).map(int).unwrap_or(DEFAULT_BLUE)
            )

            ground_color_channel_color = Color.from_rgb(
                ground_color_channel_red,
                ground_color_channel_green,
                ground_color_channel_blue,
            )

            ground_color_channel = NormalCompatibilityColorChannel(ground_color_channel_color)

        line_color_channel: CompatibilityColorChannel

        if line_color_channel_player_color.is_used():
            line_color_channel = PlayerCompatibilityColorChannel(line_color_channel_player_color)

        else:
            line_color_channel_red = (
                view.get_option(LINE_COLOR_CHANNEL_RED).map(int).unwrap_or(DEFAULT_RED)
            )
            line_color_channel_green = (
                view.get_option(LINE_COLOR_CHANNEL_GREEN).map(int).unwrap_or(DEFAULT_GREEN)
            )
            line_color_channel_blue = (
                view.get_option(LINE_COLOR_CHANNEL_BLUE).map(int).unwrap_or(DEFAULT_BLUE)
            )

            line_color_channel_color = Color.from_rgb(
                line_color_channel_red,
                line_color_channel_green,
                line_color_channel_blue,
            )

            line_color_channel = NormalCompatibilityColorChannel(line_color_channel_color)

        object_color_channel: CompatibilityColorChannel

        if object_color_channel_player_color.is_used():
            object_color_channel = PlayerCompatibilityColorChannel(
                object_color_channel_player_color
            )

        else:
            object_color_channel_red = (
                view.get_option(OBJECT_COLOR_CHANNEL_RED).map(int).unwrap_or(DEFAULT_RED)
            )
            object_color_channel_green = (
                view.get_option(OBJECT_COLOR_CHANNEL_GREEN).map(int).unwrap_or(DEFAULT_GREEN)
            )
            object_color_channel_blue = (
                view.get_option(OBJECT_COLOR_CHANNEL_BLUE).map(int).unwrap_or(DEFAULT_BLUE)
            )

            object_color_channel_color = Color.from_rgb(
                object_color_channel_red,
                object_color_channel_green,
                object_color_channel_blue,
            )

            object_color_channel = NormalCompatibilityColorChannel(object_color_channel_color)

        color_1_channel: CompatibilityColorChannel

        if color_1_channel_player_color.is_used():
            color_1_channel = PlayerCompatibilityColorChannel(color_1_channel_player_color)

        else:
            color_1_channel_red = (
                view.get_option(COLOR_1_CHANNEL_RED).map(int).unwrap_or(DEFAULT_RED)
            )
            color_1_channel_green = (
                view.get_option(COLOR_1_CHANNEL_GREEN).map(int).unwrap_or(DEFAULT_GREEN)
            )
            color_1_channel_blue = (
                view.get_option(COLOR_1_CHANNEL_BLUE).map(int).unwrap_or(DEFAULT_BLUE)
            )

            color_1_channel_color = Color.from_rgb(
                color_1_channel_red, color_1_channel_green, color_1_channel_blue
            )

            color_1_channel = NormalCompatibilityColorChannel(color_1_channel_color)

        initial_color_channels = ColorChannels.from_color_channels(
            background_color_channel.migrate(BACKGROUND_COLOR_CHANNEL_ID),
            ground_color_channel.migrate(GROUND_COLOR_CHANNEL_ID),
            line_color_channel.migrate(LINE_COLOR_CHANNEL_ID),
            object_color_channel.migrate(OBJECT_COLOR_CHANNEL_ID),
            color_1_channel.migrate(COLOR_1_CHANNEL_ID),
        )

        color_channels.update(initial_color_channels)

        # compatibility

        background_color_channel_option = (
            view.get_option(BACKGROUND_COLOR_CHANNEL)
            .map(compatibility_color_channel_from_robtop)
            .extract()
        )

        if background_color_channel_option is not None:
            color_channels.add(background_color_channel_option.migrate(BACKGROUND_COLOR_CHANNEL_ID))

        ground_color_channel_option = (
            view.get_option(GROUND_COLOR_CHANNEL)
            .map(compatibility_color_channel_from_robtop)
            .extract()
        )

        if ground_color_channel_option is not None:
            color_channels.add(ground_color_channel_option.migrate(GROUND_COLOR_CHANNEL_ID))

        line_color_channel_option = (
            view.get_option(LINE_COLOR_CHANNEL)
            .map(compatibility_color_channel_from_robtop)
            .extract()
        )

        if line_color_channel_option is not None:
            color_channels.add(line_color_channel_option.migrate(LINE_COLOR_CHANNEL_ID))

        object_color_channel_option = (
            view.get_option(OBJECT_COLOR_CHANNEL)
            .map(compatibility_color_channel_from_robtop)
            .extract()
        )

        if object_color_channel_option is not None:
            color_channels.add(object_color_channel_option.migrate(OBJECT_COLOR_CHANNEL_ID))

        color_1_channel_option = (
            view.get_option(COLOR_1_CHANNEL).map(compatibility_color_channel_from_robtop).extract()
        )

        if color_1_channel_option is not None:
            color_channels.add(color_1_channel_option.migrate(COLOR_1_CHANNEL_ID))

        color_2_channel_option = (
            view.get_option(COLOR_2_CHANNEL).map(compatibility_color_channel_from_robtop).extract()
        )

        if color_2_channel_option is not None:
            color_channels.add(color_2_channel_option.migrate(COLOR_2_CHANNEL_ID))

        color_3_channel_option = (
            view.get_option(COLOR_3_CHANNEL).map(compatibility_color_channel_from_robtop).extract()
        )

        if color_3_channel_option is not None:
            color_channels.add(color_3_channel_option.migrate(COLOR_3_CHANNEL_ID))

        color_4_channel_option = (
            view.get_option(COLOR_4_CHANNEL).map(compatibility_color_channel_from_robtop).extract()
        )

        if color_4_channel_option is not None:
            color_channels.add(color_4_channel_option.migrate(COLOR_4_CHANNEL_ID))

        line_3d_color_channel_option = (
            view.get_option(LINE_3D_COLOR_CHANNEL)
            .map(compatibility_color_channel_from_robtop)
            .extract()
        )

        if line_3d_color_channel_option is not None:
            color_channels.add(line_3d_color_channel_option.migrate(LINE_3D_COLOR_CHANNEL_ID))

        final_color_channels = (
            view.get_option(COLOR_CHANNELS)
            .map(ColorChannels.from_robtop)
            .unwrap_or_else(ColorChannels)
        )

        color_channels.update(final_color_channels)

        color_channels_page = (
            view.get_option(COLOR_CHANNELS_PAGE).map(int).unwrap_or(DEFAULT_COLOR_CHANNELS_PAGE)
        )

        return cls(
            game_mode=game_mode,
            mini_mode=mini_mode,
            speed=speed,
            background_id=background_id,
            ground_id=ground_id,
            dual_mode=dual_mode,
            two_player=two_player,
            flip_gravity=flip_gravity,
            song_offset=song_offset,
            guidelines=guidelines,
            song_fade_in=song_fade_in,
            song_fade_out=song_fade_out,
            ground_line_id=ground_line_id,
            font_id=font_id,
            platformer_mode=platformer_mode,
            color_channels=color_channels,
            color_channels_page=color_channels_page,
        )

    def to_robtop(self) -> str:
        mapping = {
            GAME_MODE: str(self.game_mode.value),
            MINI_MODE: bool_str(self.is_mini_mode()),
            SPEED: str(self.speed.value),
            BACKGROUND_ID: str(self.background_id),
            GROUND_ID: str(self.ground_id),
            DUAL_MODE: bool_str(self.is_dual_mode()),
            START_POSITION: bool_str(NOT_START_POSITION),
            TWO_PLAYER: bool_str(self.is_two_player()),
            FLIP_GRAVITY: bool_str(self.is_flip_gravity()),
            SONG_OFFSET: float_str(self.song_offset),
            GUIDELINES: self.guidelines.to_robtop(),
            SONG_FADE_IN: bool_str(self.is_song_fade_in()),
            SONG_FADE_OUT: bool_str(self.is_song_fade_out()),
            GROUND_LINE_ID: str(self.ground_line_id),
            FONT_ID: str(self.font_id),
            PLATFORMER_MODE: bool_str(self.is_platformer_mode()),
            COLOR_CHANNELS: self.color_channels.to_robtop(),
            COLOR_CHANNELS_PAGE: str(self.color_channels_page),
        }

        return concat_header(mapping)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return HEADER_SEPARATOR in string

    def is_mini_mode(self) -> bool:
        return self.mini_mode

    def is_dual_mode(self) -> bool:
        return self.dual_mode

    def is_two_player(self) -> bool:
        return self.two_player

    def is_flip_gravity(self) -> bool:
        return self.flip_gravity

    def is_song_fade_in(self) -> bool:
        return self.song_fade_in

    def is_song_fade_out(self) -> bool:
        return self.song_fade_out

    def is_platformer_mode(self) -> bool:
        return self.platformer_mode
