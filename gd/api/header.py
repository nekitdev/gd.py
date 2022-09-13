from typing import BinaryIO, Optional, Type, TypeVar

from attrs import define, field

from gd.api.color_channels import ColorChannels

from gd.api.guidelines import Guidelines
from gd.binary import VERSION, Binary
from gd.binary_utils import Reader, Writer
from gd.constants import DEFAULT_ID
from gd.enums import ByteOrder, GameMode, Speed
from gd.models_constants import HEADER_SEPARATOR
from gd.models_utils import concat_header, float_str, split_header

DEFAULT_MINI_MODE = False

DEFAULT_DUAL_MODE = False

DEFAULT_START_POSITION = False

DEFAULT_TWO_PLAYER = False

DEFAULT_FLIP_GRAVITY = False

DEFAULT_SONG_OFFSET = 0.0

DEFAULT_SONG_FADE_IN = False
DEFAULT_SONG_FADE_OUT = False

DEFAULT_PLATFORMER_MODE = False

HALF_BYTE = 0xF
HALF_BITS = HALF_BYTE.bit_length()

MINI_MODE_BIT = 0b10000000
DUAL_MODE_BIT = 0b01000000
START_POSITION_BIT = 0b00100000
TWO_PLAYER_BIT = 0b00010000
FLIP_GRAVITY_BIT = 0b00001000
SONG_FADE_IN_BIT = 0b00000100
SONG_FADE_OUT_BIT = 0b00000010
PLATFORMER_MODE_BIT = 0b00000001

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


@define()
class Header(Binary):
    game_mode: GameMode = field(default=GameMode.DEFAULT)
    mini_mode: bool = field(default=DEFAULT_MINI_MODE)
    speed: Speed = field(default=Speed.DEFAULT)
    background_id: int = field(default=DEFAULT_ID)
    ground_id: int = field(default=DEFAULT_ID)
    dual_mode: bool = field(default=DEFAULT_DUAL_MODE)
    start_position: bool = field(default=DEFAULT_START_POSITION)
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

    @classmethod
    def from_binary(
        cls: Type[H], binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> H:
        mini_mode_bit = MINI_MODE_BIT
        dual_mode_bit = DUAL_MODE_BIT
        start_position_bit = START_POSITION_BIT
        two_player_bit = TWO_PLAYER_BIT
        flip_gravity_bit = FLIP_GRAVITY_BIT
        song_fade_in_bit = SONG_FADE_IN_BIT
        song_fade_out_bit = SONG_FADE_OUT_BIT
        platformer_mode_bit = PLATFORMER_MODE_BIT

        reader = Reader(binary)

        background_id = reader.read_u8(order)
        ground_id = reader.read_u8(order)
        ground_line_id = reader.read_u8(order)
        font_id = reader.read_u8(order)

        value = reader.read_u8(order)

        speed = Speed(value & HALF_BYTE)

        value >>= HALF_BITS

        game_mode = GameMode(value)

        bits = reader.read_u8(order)

        mini_mode = bits & mini_mode_bit == mini_mode_bit
        dual_mode = bits & dual_mode_bit == dual_mode_bit
        start_position = bits & start_position_bit == start_position_bit
        two_player = bits & two_player_bit == two_player_bit
        flip_gravity = bits & flip_gravity_bit == flip_gravity_bit
        song_fade_in = bits & song_fade_in_bit == song_fade_in_bit
        song_fade_out = bits & song_fade_out_bit == song_fade_out_bit
        platformer_mode = bits & platformer_mode_bit == platformer_mode_bit

        song_offset = reader.read_f32(order)

        guidelines = Guidelines.from_binary(binary, order, version)

        color_channels = ColorChannels.from_binary(binary, order, version)

        return cls(
            game_mode=game_mode,
            mini_mode=mini_mode,
            speed=speed,
            background_id=background_id,
            ground_id=ground_id,
            dual_mode=dual_mode,
            start_position=start_position,
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
        )

    def to_binary(
        self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        writer = Writer(binary)

        writer.write_u8(self.background_id, order)
        writer.write_u8(self.ground_id, order)
        writer.write_u8(self.ground_line_id, order)
        writer.write_u8(self.font_id, order)

        value = self.game_mode.value

        value = (value << HALF_BITS) | self.speed.value

        writer.write_u8(value, order)

        bits = 0

        if self.is_mini_mode():
            bits |= MINI_MODE_BIT

        if self.is_dual_mode():
            bits |= DUAL_MODE_BIT

        if self.is_start_position():
            bits |= START_POSITION_BIT

        if self.is_two_player():
            bits |= TWO_PLAYER_BIT

        if self.is_flip_gravity():
            bits |= FLIP_GRAVITY_BIT

        if self.is_song_fade_in():
            bits |= SONG_FADE_IN_BIT

        if self.is_song_fade_out():
            bits |= SONG_FADE_OUT_BIT

        if self.is_platformer_mode():
            bits |= PLATFORMER_MODE_BIT

        writer.write_u8(bits, order)

        writer.write_f32(self.song_offset, order)

        self.guidelines.to_binary(binary, order, version)

        self.color_channels.to_binary(binary, order, version)

    @classmethod
    def from_robtop(
        cls: Type[H],
        string: str,
        # indexes
        game_mode_index: str = GAME_MODE,
        mini_mode_index: str = MINI_MODE,
        speed_index: str = SPEED,
        background_id_index: str = BACKGROUND_ID,
        ground_id_index: str = GROUND_ID,
        dual_mode_index: str = DUAL_MODE,
        start_position_index: str = START_POSITION,
        two_player_index: str = TWO_PLAYER,
        flip_gravity_index: str = FLIP_GRAVITY,
        song_offset_index: str = SONG_OFFSET,
        guidelines_index: str = GUIDELINES,
        song_fade_in_index: str = SONG_FADE_IN,
        song_fade_out_index: str = SONG_FADE_OUT,
        ground_line_id_index: str = GROUND_LINE_ID,
        font_id_index: str = FONT_ID,
        platformer_mode_index: str = PLATFORMER_MODE,
        color_channels_index: str = COLOR_CHANNELS,
        # defaults
        game_mode_default: GameMode = GameMode.DEFAULT,
        mini_mode_default: bool = DEFAULT_MINI_MODE,
        speed_default: Speed = Speed.DEFAULT,
        background_id_default: int = DEFAULT_ID,
        ground_id_default: int = DEFAULT_ID,
        dual_mode_default: bool = DEFAULT_DUAL_MODE,
        start_position_default: bool = DEFAULT_START_POSITION,
        two_player_default: bool = DEFAULT_TWO_PLAYER,
        flip_gravity_default: bool = DEFAULT_FLIP_GRAVITY,
        song_offset_default: float = DEFAULT_SONG_OFFSET,
        guidelines_default: Optional[Guidelines] = None,
        song_fade_in_default: bool = DEFAULT_SONG_FADE_IN,
        song_fade_out_default: bool = DEFAULT_SONG_FADE_OUT,
        ground_line_id_default: int = DEFAULT_ID,
        font_id_default: int = DEFAULT_ID,
        platformer_mode_default: bool = DEFAULT_PLATFORMER_MODE,
        color_channels_default: Optional[ColorChannels] = None,
    ) -> H:
        if guidelines_default is None:
            guidelines_default = Guidelines()

        if color_channels_default is None:
            color_channels_default = ColorChannels()

        mapping = split_header(string)

        return cls()

    def to_robtop(
        self,
        game_mode_index: str = GAME_MODE,
        mini_mode_index: str = MINI_MODE,
        speed_index: str = SPEED,
        background_id_index: str = BACKGROUND_ID,
        ground_id_index: str = GROUND_ID,
        dual_mode_index: str = DUAL_MODE,
        start_position_index: str = START_POSITION,
        two_player_index: str = TWO_PLAYER,
        flip_gravity_index: str = FLIP_GRAVITY,
        song_offset_index: str = SONG_OFFSET,
        guidelines_index: str = GUIDELINES,
        song_fade_in_index: str = SONG_FADE_IN,
        song_fade_out_index: str = SONG_FADE_OUT,
        ground_line_id_index: str = GROUND_LINE_ID,
        font_id_index: str = FONT_ID,
        platformer_mode_index: str = PLATFORMER_MODE,
        color_channels_index: str = COLOR_CHANNELS,
    ) -> str:
        mapping = {
            game_mode_index: str(self.game_mode.value),
            mini_mode_index: str(int(self.mini_mode)),
            speed_index: str(self.speed.value),
            background_id_index: str(self.background_id),
            ground_id_index: str(self.ground_id),
            dual_mode_index: str(int(self.dual_mode)),
            start_position_index: str(int(self.start_position)),
            two_player_index: str(int(self.two_player)),
            flip_gravity_index: str(int(self.flip_gravity)),
            song_offset_index: float_str(self.song_offset),
            guidelines_index: self.guidelines.to_robtop(),
            song_fade_in_index: str(int(self.song_fade_in)),
            song_fade_out_index: str(int(self.song_fade_out)),
            ground_line_id_index: str(self.ground_line_id),
            font_id_index: str(self.font_id),
            platformer_mode_index: str(int(self.platformer_mode)),
            color_channels_index: self.color_channels.to_robtop(),
        }

        return concat_header(mapping)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return HEADER_SEPARATOR in string

    def is_mini_mode(self) -> bool:
        return self.mini_mode

    def is_dual_mode(self) -> bool:
        return self.dual_mode

    def is_start_position(self) -> bool:
        return self.start_position

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
