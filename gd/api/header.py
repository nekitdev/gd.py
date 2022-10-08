from typing import BinaryIO, Optional, Type, TypeVar

from attrs import define, field

from gd.api.color_channels import ColorChannels
from gd.api.guidelines import Guidelines
from gd.binary import VERSION, Binary
from gd.binary_constants import HALF_BITS, HALF_BYTE
from gd.binary_utils import Reader, Writer
from gd.constants import DEFAULT_ID
from gd.enums import ByteOrder, GameMode, Speed
from gd.models import Model
from gd.models_constants import HEADER_SEPARATOR
from gd.models_utils import (
    concat_header,
    float_str,
    int_bool,
    parse_get_or,
    partial_parse_enum,
    split_header,
)

DEFAULT_MINI_MODE = False

DEFAULT_DUAL_MODE = False

DEFAULT_START_POSITION = False

DEFAULT_TWO_PLAYER = False

DEFAULT_FLIP_GRAVITY = False

DEFAULT_SONG_OFFSET = 0.0

DEFAULT_SONG_FADE_IN = False
DEFAULT_SONG_FADE_OUT = False

DEFAULT_PLATFORMER_MODE = False

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
class Header(Model, Binary):
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
    def from_robtop(cls: Type[H], string: str) -> H:
        mapping = split_header(string)

        return cls(
            game_mode=parse_get_or(
                partial_parse_enum(int, GameMode), GameMode.DEFAULT, mapping.get(GAME_MODE)
            ),
            mini_mode=parse_get_or(int_bool, DEFAULT_MINI_MODE, mapping.get(MINI_MODE)),
            speed=parse_get_or(
                partial_parse_enum(int, Speed), Speed.DEFAULT, mapping.get(SPEED)
            ),
            background_id=parse_get_or(
                int, DEFAULT_ID, mapping.get(BACKGROUND_ID)
            ),
            ground_id=parse_get_or(int, DEFAULT_ID, mapping.get(GROUND_ID)),
            dual_mode=parse_get_or(int_bool, DEFAULT_DUAL_MODE, mapping.get(DUAL_MODE)),
            start_position=parse_get_or(
                int_bool, DEFAULT_START_POSITION, mapping.get(START_POSITION)
            ),
            two_player=parse_get_or(int_bool, DEFAULT_TWO_PLAYER, mapping.get(TWO_PLAYER)),
            flip_gravity=parse_get_or(
                int_bool, DEFAULT_FLIP_GRAVITY, mapping.get(FLIP_GRAVITY)
            ),
            song_offset=parse_get_or(float, DEFAULT_SONG_OFFSET, mapping.get(SONG_OFFSET)),
            guidelines=parse_get_or(Guidelines.from_robtop, Guidelines(), mapping.get(GUIDELINES)),
            song_fade_in=parse_get_or(
                int_bool, DEFAULT_SONG_FADE_IN, mapping.get(SONG_FADE_IN)
            ),
            song_fade_out=parse_get_or(
                int_bool, DEFAULT_SONG_FADE_OUT, mapping.get(SONG_FADE_OUT)
            ),
            ground_line_id=parse_get_or(
                int, DEFAULT_ID, mapping.get(GROUND_LINE_ID)
            ),
            font_id=parse_get_or(int, DEFAULT_ID, mapping.get(FONT_ID)),
            platformer_mode=parse_get_or(
                int_bool, DEFAULT_PLATFORMER_MODE, mapping.get(PLATFORMER_MODE)
            ),
            color_channels=parse_get_or(
                ColorChannels.from_robtop, ColorChannels(), mapping.get(COLOR_CHANNELS)
            ),
        )

    def to_robtop(self) -> str:
        mapping = {
            GAME_MODE: str(self.game_mode.value),
            MINI_MODE: str(int(self.mini_mode)),
            SPEED: str(self.speed.value),
            BACKGROUND_ID: str(self.background_id),
            GROUND_ID: str(self.ground_id),
            DUAL_MODE: str(int(self.dual_mode)),
            START_POSITION: str(int(self.start_position)),
            TWO_PLAYER: str(int(self.two_player)),
            FLIP_GRAVITY: str(int(self.flip_gravity)),
            SONG_OFFSET: float_str(self.song_offset),
            GUIDELINES: self.guidelines.to_robtop(),
            SONG_FADE_IN: str(int(self.song_fade_in)),
            SONG_FADE_OUT: str(int(self.song_fade_out)),
            GROUND_LINE_ID: str(self.ground_line_id),
            FONT_ID: str(self.font_id),
            PLATFORMER_MODE: str(int(self.platformer_mode)),
            COLOR_CHANNELS: self.color_channels.to_robtop(),
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
