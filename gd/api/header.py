from typing import Type, TypeVar

from attrs import define, field

from gd.api.color_channels import ColorChannels
from gd.api.guidelines import Guidelines
from gd.binary import VERSION, Binary, BinaryReader, BinaryWriter
from gd.binary_constants import HALF_BITS, HALF_BYTE
from gd.binary_utils import Reader, Writer
from gd.constants import DEFAULT_ID
from gd.enums import ByteOrder, GameMode, Speed
from gd.models_constants import HEADER_SEPARATOR
from gd.models_utils import (
    concat_header,
    float_str,
    int_bool,
    parse_get_or,
    parse_get_or_else,
    partial_parse_enum,
    split_header,
)
from gd.robtop import RobTop

DEFAULT_MINI_MODE = False

DEFAULT_DUAL_MODE = False

DEFAULT_TWO_PLAYER = False

DEFAULT_FLIP_GRAVITY = False

DEFAULT_SONG_OFFSET = 0.0

DEFAULT_SONG_FADE_IN = False
DEFAULT_SONG_FADE_OUT = False

DEFAULT_PLATFORMER_MODE = False

DEFAULT_COLOR_CHANNELS_PAGE = 0


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


@define()
class Header(Binary, RobTop):  # TODO: compatibility?
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

        song_offset = reader.read_f32()

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

        value = self.game_mode.value

        value = (value << HALF_BITS) | self.speed.value

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
        mapping = split_header(string)

        return cls(
            game_mode=parse_get_or(
                partial_parse_enum(int, GameMode), GameMode.DEFAULT, mapping.get(GAME_MODE)
            ),
            mini_mode=parse_get_or(int_bool, DEFAULT_MINI_MODE, mapping.get(MINI_MODE)),
            speed=parse_get_or(partial_parse_enum(int, Speed), Speed.DEFAULT, mapping.get(SPEED)),
            background_id=parse_get_or(int, DEFAULT_ID, mapping.get(BACKGROUND_ID)),
            ground_id=parse_get_or(int, DEFAULT_ID, mapping.get(GROUND_ID)),
            dual_mode=parse_get_or(int_bool, DEFAULT_DUAL_MODE, mapping.get(DUAL_MODE)),
            two_player=parse_get_or(int_bool, DEFAULT_TWO_PLAYER, mapping.get(TWO_PLAYER)),
            flip_gravity=parse_get_or(int_bool, DEFAULT_FLIP_GRAVITY, mapping.get(FLIP_GRAVITY)),
            song_offset=parse_get_or(float, DEFAULT_SONG_OFFSET, mapping.get(SONG_OFFSET)),
            guidelines=parse_get_or(Guidelines.from_robtop, Guidelines(), mapping.get(GUIDELINES)),
            song_fade_in=parse_get_or(int_bool, DEFAULT_SONG_FADE_IN, mapping.get(SONG_FADE_IN)),
            song_fade_out=parse_get_or(int_bool, DEFAULT_SONG_FADE_OUT, mapping.get(SONG_FADE_OUT)),
            ground_line_id=parse_get_or(int, DEFAULT_ID, mapping.get(GROUND_LINE_ID)),
            font_id=parse_get_or(int, DEFAULT_ID, mapping.get(FONT_ID)),
            platformer_mode=parse_get_or(
                int_bool, DEFAULT_PLATFORMER_MODE, mapping.get(PLATFORMER_MODE)
            ),
            color_channels=parse_get_or_else(
                ColorChannels.from_robtop, ColorChannels, mapping.get(COLOR_CHANNELS)
            ),
            color_channels_page=parse_get_or(
                int, DEFAULT_COLOR_CHANNELS_PAGE, mapping.get(COLOR_CHANNELS_PAGE)
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
            START_POSITION: str(int(False)),
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
