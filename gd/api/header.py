from typing import Type, TypeVar

from attrs import define, field

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
    ColorChannels,
    CompatibilityColorChannel,
    NormalCompatibilityColorChannel,
    PlayerCompatibilityColorChannel,
    compatibility_color_channel_from_robtop,
)
from gd.api.guidelines import Guidelines
from gd.binary import VERSION, Binary, BinaryReader, BinaryWriter
from gd.binary_constants import BYTE, HALF_BITS, HALF_BYTE
from gd.binary_utils import Reader, Writer
from gd.color import Color
from gd.constants import DEFAULT_ID, DEFAULT_ROUNDING
from gd.enums import ByteOrder, GameMode, PlayerColor, Speed
from gd.models_constants import HEADER_SEPARATOR
from gd.models_utils import (
    bool_str,
    concat_header,
    float_str,
    int_bool,
    parse_get_or,
    parse_get_or_else,
    partial_parse_enum,
    split_header,
)
from gd.robtop import RobTop

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

DEFAULT_PLAYER_COLOR_VALUE = PlayerColor.DEFAULT.value


MINI_MODE_BIT = 0b00000001
DUAL_MODE_BIT = 0b00000010
TWO_PLAYER_BIT = 0b00000100
FLIP_GRAVITY_BIT = 0b00001000
SONG_FADE_IN_BIT = 0b00010000
SONG_FADE_OUT_BIT = 0b00100000
PLATFORMER_MODE_BIT = 0b01000000

H = TypeVar("H", bound="Header")


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

BACKGROUND_RED = "kS1"
BACKGROUND_GREEN = "kS2"
BACKGROUND_BLUE = "kS3"
GROUND_RED = "kS4"
GROUND_GREEN = "kS5"
GROUND_BLUE = "kS6"
LINE_RED = "kS7"
LINE_GREEN = "kS8"
LINE_BLUE = "kS9"
OBJECT_RED = "kS10"
OBJECT_GREEN = "kS11"
OBJECT_BLUE = "kS12"
COLOR_1_RED = "kS13"
COLOR_1_GREEN = "kS14"
COLOR_1_BLUE = "kS15"
BACKGROUND_PLAYER_COLOR = "kS16"
GROUND_PLAYER_COLOR = "kS17"
LINE_PLAYER_COLOR = "kS18"
OBJECT_PLAYER_COLOR = "kS19"
COLOR_1_PLAYER_COLOR = "kS20"


@define()
class Header(Binary, RobTop):
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
    def from_binary(
        cls: Type[H],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> H:
        rounding = DEFAULT_ROUNDING

        mini_mode_bit = MINI_MODE_BIT
        dual_mode_bit = DUAL_MODE_BIT
        two_player_bit = TWO_PLAYER_BIT
        flip_gravity_bit = FLIP_GRAVITY_BIT
        song_fade_in_bit = SONG_FADE_IN_BIT
        song_fade_out_bit = SONG_FADE_OUT_BIT
        platformer_mode_bit = PLATFORMER_MODE_BIT

        reader = Reader(binary, order)

        background_id = reader.read_u8()
        ground_id = reader.read_u8()
        ground_line_id = reader.read_u8()
        font_id = reader.read_u8()

        value = reader.read_u8()

        speed = Speed(value & HALF_BYTE)

        value >>= HALF_BITS

        game_mode = GameMode(value)

        value = reader.read_u8()

        mini_mode = value & mini_mode_bit == mini_mode_bit
        dual_mode = value & dual_mode_bit == dual_mode_bit
        two_player = value & two_player_bit == two_player_bit
        flip_gravity = value & flip_gravity_bit == flip_gravity_bit
        song_fade_in = value & song_fade_in_bit == song_fade_in_bit
        song_fade_out = value & song_fade_out_bit == song_fade_out_bit
        platformer_mode = value & platformer_mode_bit == platformer_mode_bit

        song_offset = round(reader.read_f32(), rounding)

        guidelines = Guidelines.from_binary(binary, order, version)

        color_channels = ColorChannels.from_binary(binary, order, version)

        color_channels_page = reader.read_u16()

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

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        writer = Writer(binary, order)

        writer.write_u8(self.background_id)
        writer.write_u8(self.ground_id)
        writer.write_u8(self.ground_line_id)
        writer.write_u8(self.font_id)

        value = self.speed.value

        value |= self.game_mode.value << HALF_BITS

        writer.write_u8(value)

        value = 0

        if self.is_mini_mode():
            value |= MINI_MODE_BIT

        if self.is_dual_mode():
            value |= DUAL_MODE_BIT

        if self.is_two_player():
            value |= TWO_PLAYER_BIT

        if self.is_flip_gravity():
            value |= FLIP_GRAVITY_BIT

        if self.is_song_fade_in():
            value |= SONG_FADE_IN_BIT

        if self.is_song_fade_out():
            value |= SONG_FADE_OUT_BIT

        if self.is_platformer_mode():
            value |= PLATFORMER_MODE_BIT

        writer.write_u8(value)

        writer.write_f32(self.song_offset)

        self.guidelines.to_binary(binary, order, version)

        self.color_channels.to_binary(binary, order, version)

        writer.write_u16(self.color_channels_page)

    @classmethod
    def from_robtop(cls: Type[H], string: str) -> H:
        default_player_color_value = DEFAULT_PLAYER_COLOR_VALUE

        mapping = split_header(string)

        game_mode = parse_get_or(
            partial_parse_enum(int, GameMode), GameMode.DEFAULT, mapping.get(GAME_MODE)
        )

        mini_mode = parse_get_or(int_bool, DEFAULT_MINI_MODE, mapping.get(MINI_MODE))

        speed = parse_get_or(partial_parse_enum(int, Speed), Speed.DEFAULT, mapping.get(SPEED))

        background_id = parse_get_or(int, DEFAULT_ID, mapping.get(BACKGROUND_ID))

        ground_id = parse_get_or(int, DEFAULT_ID, mapping.get(GROUND_ID))

        dual_mode = parse_get_or(int_bool, DEFAULT_DUAL_MODE, mapping.get(DUAL_MODE))

        two_player = parse_get_or(int_bool, DEFAULT_TWO_PLAYER, mapping.get(TWO_PLAYER))

        flip_gravity = parse_get_or(int_bool, DEFAULT_FLIP_GRAVITY, mapping.get(FLIP_GRAVITY))

        song_offset = parse_get_or(float, DEFAULT_SONG_OFFSET, mapping.get(SONG_OFFSET))

        guidelines = parse_get_or_else(Guidelines.from_robtop, Guidelines, mapping.get(GUIDELINES))

        song_fade_in = parse_get_or(int_bool, DEFAULT_SONG_FADE_IN, mapping.get(SONG_FADE_IN))
        song_fade_out = parse_get_or(int_bool, DEFAULT_SONG_FADE_OUT, mapping.get(SONG_FADE_OUT))

        ground_line_id = parse_get_or(int, DEFAULT_ID, mapping.get(GROUND_LINE_ID))

        font_id = parse_get_or(int, DEFAULT_ID, mapping.get(FONT_ID))

        platformer_mode = parse_get_or(
            int_bool, DEFAULT_PLATFORMER_MODE, mapping.get(PLATFORMER_MODE)
        )

        color_channels = ColorChannels()

        # even more compatiblity

        background_player_color_value = max(
            parse_get_or(
                int_bool, default_player_color_value, mapping.get(BACKGROUND_PLAYER_COLOR)
            ),
            default_player_color_value,
        )

        background_player_color = PlayerColor(background_player_color_value)

        ground_player_color_value = max(
            parse_get_or(int_bool, default_player_color_value, mapping.get(GROUND_PLAYER_COLOR)),
            default_player_color_value,
        )

        ground_player_color = PlayerColor(ground_player_color_value)

        line_player_color_value = max(
            parse_get_or(int_bool, default_player_color_value, mapping.get(LINE_PLAYER_COLOR)),
            default_player_color_value,
        )

        line_player_color = PlayerColor(line_player_color_value)

        object_player_color_value = max(
            parse_get_or(int_bool, default_player_color_value, mapping.get(OBJECT_PLAYER_COLOR)),
            default_player_color_value,
        )

        object_player_color = PlayerColor(object_player_color_value)

        color_1_player_color_value = max(
            parse_get_or(int_bool, default_player_color_value, mapping.get(COLOR_1_PLAYER_COLOR)),
            default_player_color_value,
        )

        color_1_player_color = PlayerColor(color_1_player_color_value)

        background_color_channel: CompatibilityColorChannel

        if background_player_color.is_used():
            background_color_channel = PlayerCompatibilityColorChannel(background_player_color)

        else:
            background_red = parse_get_or(int, DEFAULT_RED, mapping.get(BACKGROUND_RED))
            background_green = parse_get_or(int, DEFAULT_GREEN, mapping.get(BACKGROUND_GREEN))
            background_blue = parse_get_or(int, DEFAULT_BLUE, mapping.get(BACKGROUND_BLUE))

            background_color = Color.from_rgb(background_red, background_green, background_blue)

            background_color_channel = NormalCompatibilityColorChannel(background_color)

        ground_color_channel: CompatibilityColorChannel

        if ground_player_color.is_used():
            ground_color_channel = PlayerCompatibilityColorChannel(ground_player_color)

        else:
            ground_red = parse_get_or(int, DEFAULT_RED, mapping.get(GROUND_RED))
            ground_green = parse_get_or(int, DEFAULT_GREEN, mapping.get(GROUND_GREEN))
            ground_blue = parse_get_or(int, DEFAULT_BLUE, mapping.get(GROUND_BLUE))

            ground_color = Color.from_rgb(ground_red, ground_green, ground_blue)

            ground_color_channel = NormalCompatibilityColorChannel(ground_color)

        line_color_channel: CompatibilityColorChannel

        if line_player_color.is_used():
            line_color_channel = PlayerCompatibilityColorChannel(line_player_color)

        else:
            line_red = parse_get_or(int, DEFAULT_RED, mapping.get(LINE_RED))
            line_green = parse_get_or(int, DEFAULT_GREEN, mapping.get(LINE_GREEN))
            line_blue = parse_get_or(int, DEFAULT_BLUE, mapping.get(LINE_BLUE))

            line_color = Color.from_rgb(line_red, line_green, line_blue)

            line_color_channel = NormalCompatibilityColorChannel(line_color)

        object_color_channel: CompatibilityColorChannel

        if object_player_color.is_used():
            object_color_channel = PlayerCompatibilityColorChannel(object_player_color)

        else:
            object_red = parse_get_or(int, DEFAULT_RED, mapping.get(OBJECT_RED))
            object_green = parse_get_or(int, DEFAULT_GREEN, mapping.get(OBJECT_GREEN))
            object_blue = parse_get_or(int, DEFAULT_BLUE, mapping.get(OBJECT_BLUE))

            object_color = Color.from_rgb(object_red, object_green, object_blue)

            object_color_channel = NormalCompatibilityColorChannel(object_color)

        color_1_channel: CompatibilityColorChannel

        if color_1_player_color.is_used():
            color_1_channel = PlayerCompatibilityColorChannel(color_1_player_color)

        else:
            color_1_red = parse_get_or(int, DEFAULT_RED, mapping.get(COLOR_1_RED))
            color_1_green = parse_get_or(int, DEFAULT_GREEN, mapping.get(COLOR_1_GREEN))
            color_1_blue = parse_get_or(int, DEFAULT_BLUE, mapping.get(COLOR_1_BLUE))

            color_1 = Color.from_rgb(color_1_red, color_1_green, color_1_blue)

            color_1_channel = NormalCompatibilityColorChannel(color_1)

        initial_color_channels = ColorChannels.from_color_channels(
            background_color_channel.migrate(BACKGROUND_COLOR_ID),
            ground_color_channel.migrate(GROUND_COLOR_ID),
            line_color_channel.migrate(LINE_COLOR_ID),
            object_color_channel.migrate(OBJECT_COLOR_ID),
            color_1_channel.migrate(COLOR_1_ID),
        )

        color_channels.update(initial_color_channels)

        # compatibility

        background_color_channel_string = mapping.get(BACKGROUND_COLOR_CHANNEL)

        if background_color_channel_string is not None:
            background_color_channel = compatibility_color_channel_from_robtop(
                background_color_channel_string
            )

            color_channels.add(background_color_channel.migrate(BACKGROUND_COLOR_ID))

        ground_color_channel_string = mapping.get(GROUND_COLOR_CHANNEL)

        if ground_color_channel_string is not None:
            ground_color_channel = compatibility_color_channel_from_robtop(
                ground_color_channel_string
            )

            color_channels.add(ground_color_channel.migrate(GROUND_COLOR_ID))

        line_color_channel_string = mapping.get(LINE_COLOR_CHANNEL)

        if line_color_channel_string is not None:
            line_color_channel = compatibility_color_channel_from_robtop(line_color_channel_string)

            color_channels.add(line_color_channel.migrate(LINE_COLOR_ID))

        object_color_channel_string = mapping.get(OBJECT_COLOR_CHANNEL)

        if object_color_channel_string is not None:
            object_color_channel = compatibility_color_channel_from_robtop(
                object_color_channel_string
            )

            color_channels.add(object_color_channel.migrate(OBJECT_COLOR_ID))

        color_1_channel_string = mapping.get(COLOR_1_CHANNEL)

        if color_1_channel_string is not None:
            color_1_channel = compatibility_color_channel_from_robtop(color_1_channel_string)

            color_channels.add(color_1_channel.migrate(COLOR_1_ID))

        color_2_channel_string = mapping.get(COLOR_2_CHANNEL)

        if color_2_channel_string is not None:
            color_2_channel = compatibility_color_channel_from_robtop(color_2_channel_string)

            color_channels.add(color_2_channel.migrate(COLOR_2_ID))

        color_3_channel_string = mapping.get(COLOR_3_CHANNEL)

        if color_3_channel_string is not None:
            color_3_channel = compatibility_color_channel_from_robtop(color_3_channel_string)

            color_channels.add(color_3_channel.migrate(COLOR_3_ID))

        color_4_channel_string = mapping.get(COLOR_4_CHANNEL)

        if color_4_channel_string is not None:
            color_4_channel = compatibility_color_channel_from_robtop(color_4_channel_string)

            color_channels.add(color_4_channel.migrate(COLOR_4_ID))

        line_3d_color_channel_string = mapping.get(LINE_3D_COLOR_CHANNEL)

        if line_3d_color_channel_string is not None:
            line_3d_color_channel = compatibility_color_channel_from_robtop(
                line_3d_color_channel_string
            )

            color_channels.add(line_3d_color_channel.migrate(LINE_3D_COLOR_ID))

        final_color_channels = parse_get_or_else(
            ColorChannels.from_robtop, ColorChannels, mapping.get(COLOR_CHANNELS)
        )

        color_channels.update(final_color_channels)

        color_channels_page = parse_get_or(
            int, DEFAULT_COLOR_CHANNELS_PAGE, mapping.get(COLOR_CHANNELS_PAGE)
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

    @staticmethod
    def can_be_in(string: str) -> bool:
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
