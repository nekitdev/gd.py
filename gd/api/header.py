from typing import BinaryIO, Type, TypeVar

from attrs import define, field

from gd.api.color_channels import ColorChannels

# from gd.api.guidelines import Guidelines
from gd.binary import VERSION, Binary
from gd.binary_utils import Reader, Writer
from gd.constants import DEFAULT_ID
from gd.enums import ByteOrder, GameMode, Speed

DEFAULT_MINI_MODE = False

DEFAULT_DUAL_MODE = False

DEFAULT_START_POS = False

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
START_POS_BIT = 0b00100000
TWO_PLAYER_BIT = 0b00010000
FLIP_GRAVITY_BIT = 0b00001000
SONG_FADE_IN_BIT = 0b00000100
SONG_FADE_OUT_BIT = 0b00000010
PLATFORMER_MODE_BIT = 0b00000001

H = TypeVar("H", bound="Header")


@define()
class Header(Binary):
    game_mode: GameMode = field(default=GameMode.DEFAULT)
    mini_mode: bool = field(default=DEFAULT_MINI_MODE)
    speed: Speed = field(default=Speed.DEFAULT)
    background_id: int = field(default=DEFAULT_ID)
    ground_id: int = field(default=DEFAULT_ID)
    dual_mode: bool = field(default=DEFAULT_DUAL_MODE)
    start_pos: bool = field(default=DEFAULT_START_POS)
    two_player: bool = field(default=DEFAULT_TWO_PLAYER)
    flip_gravity: bool = field(default=DEFAULT_FLIP_GRAVITY)
    song_offset: float = field(default=DEFAULT_SONG_OFFSET)
    # guidelines: Guidelines = field(factory=Guidelines)
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
        start_pos_bit = START_POS_BIT
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
        start_pos = bits & start_pos_bit == start_pos_bit
        two_player = bits & two_player_bit == two_player_bit
        flip_gravity = bits & flip_gravity_bit == flip_gravity_bit
        song_fade_in = bits & song_fade_in_bit == song_fade_in_bit
        song_fade_out = bits & song_fade_out_bit == song_fade_out_bit
        platformer_mode = bits & platformer_mode_bit == platformer_mode_bit

        song_offset = reader.read_f32(order)

        # guidelines = Guidelines.from_binary(binary, order, version)

        color_channels = ColorChannels.from_binary(binary, order, version)

        return cls(
            game_mode=game_mode,
            mini_mode=mini_mode,
            speed=speed,
            background_id=background_id,
            ground_id=ground_id,
            dual_mode=dual_mode,
            start_pos=start_pos,
            two_player=two_player,
            flip_gravity=flip_gravity,
            song_offset=song_offset,
            # guidelines=guidelines,
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

        if self.is_start_pos():
            bits |= START_POS_BIT

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

        # self.guidelines.to_binary(binary, order, version)

        self.color_channels.to_binary(binary, order, version)

    def is_mini_mode(self) -> bool:
        return self.mini_mode

    def is_dual_mode(self) -> bool:
        return self.dual_mode

    def is_start_pos(self) -> bool:
        return self.start_pos

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
