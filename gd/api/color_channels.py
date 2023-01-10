from functools import partial
from typing import Dict, Iterable, Type, TypeVar

from attrs import define, field
from iters import iter

from gd.api.hsv import HSV
from gd.binary import VERSION, Binary, BinaryReader, BinaryWriter
from gd.binary_constants import BITS, BYTE
from gd.binary_utils import Reader, Writer
from gd.color import Color
from gd.constants import DEFAULT_ID
from gd.enums import ByteOrder, PlayerColor
from gd.models_utils import (
    concat_color_channel,
    concat_color_channels,
    float_str,
    int_bool,
    parse_get_or,
    split_color_channel,
    split_color_channels,
)
from gd.robtop import RobTop

__all__ = ("ColorChannel", "ColorChannels", "Channel", "Channels")

RED = 1
GREEN = 2
BLUE = 3
PLAYER_COLOR = 4
BLENDING = 5
ID = 6
OPACITY = 7
UNKNOWN = 8
COPIED_ID = 9
COLOR_HSV = 10
TO_RED = 11
TO_GREEN = 12
TO_BLUE = 13
DURATION = 14
TO_OPACITY = 15
COPY_OPACITY = 17
UNKNOWN_ANOTHER = 18


PLAYER_COLOR_MASK = 0b00000110

BLENDING_BIT = 0b00000001

PLAYER_COLOR_SHIFT = BLENDING_BIT.bit_length()

COPY_OPACITY_BIT = 0b00000010


DEFAULT_UNKNOWN = True

DEFAULT_TO_RED = BYTE
DEFAULT_TO_GREEN = BYTE
DEFAULT_TO_BLUE = BYTE

DEFAULT_DURATION = 0.0

DEFAULT_TO_OPACITY = 1.0

DEFAULT_UNKNOWN_ANOTHER = True


DEFAULT_RED = BYTE
DEFAULT_GREEN = BYTE
DEFAULT_BLUE = BYTE

DEFAULT_BLENDING = False

DEFAULT_OPACITY = 1.0

DEFAULT_COPY_OPACITY = False


CC = TypeVar("CC", bound="ColorChannel")


@define()
class ColorChannel(Binary, RobTop):
    """Represents color channels.

    Binary:
        ```rust
        struct ColorChannel {
            id: u16,
            copied_id: u16,
            nested: NestedColorChannel,
        }

        enum NestedColorChannel {
            Normal(NormalColorChannel),  // if `copied_id == 0`
            Copied(CopiedColorChannel),  // if `copied_id != 0`
        }

        const BLENDING_BIT: u8 = 0b00000001;
        const COPY_OPACITY_BIT: u8 = 0b00000010;

        struct CopiedColorChannel {
            hsv: HSV,
            copy_opacity_and_blending: u8,
            opacity: Option<f32>,  // if `!copy_opacity`
        }

        const BYTE: u32 = 0b11111111;

        const PLAYER_COLOR_MASK: u8 = 0b00000110;
        const PLAYER_COLOR_SHIFT: u8 = PLAYER_COLOR_MASK.leading_zeros() as u8;

        struct NormalColorChannel {
            color_player_color_and_blending: u32,
            opacity: f32,
        }
        ```
    """

    id: int = field()
    color: Color = field(factory=Color.default)
    player_color: PlayerColor = field(default=PlayerColor.DEFAULT)
    blending: bool = field(default=DEFAULT_BLENDING)
    opacity: float = field(default=DEFAULT_OPACITY)
    copied_id: int = field(default=DEFAULT_ID)
    hsv: HSV = field(factory=HSV)
    copy_opacity: bool = field(default=DEFAULT_COPY_OPACITY)

    @classmethod
    def from_robtop(cls: Type[CC], string: str) -> CC:
        mapping = split_color_channel(string)

        id = parse_get_or(int, DEFAULT_ID, mapping.get(ID))

        copied_id = parse_get_or(int, DEFAULT_ID, mapping.get(COPIED_ID))

        blending = parse_get_or(int_bool, DEFAULT_BLENDING, mapping.get(BLENDING))

        if copied_id:
            hsv = parse_get_or(HSV.from_robtop, HSV(), mapping.get(COLOR_HSV))

            copy_opacity = parse_get_or(int_bool, DEFAULT_COPY_OPACITY, mapping.get(COPY_OPACITY))

            player_color = PlayerColor.DEFAULT

            if not copy_opacity:
                opacity = parse_get_or(float, DEFAULT_OPACITY, mapping.get(OPACITY))

            else:
                opacity = DEFAULT_OPACITY

            color = Color.default()

        else:
            hsv = HSV()

            copy_opacity = DEFAULT_COPY_OPACITY

            player_color_value = parse_get_or(
                int, PlayerColor.DEFAULT.value, mapping.get(PLAYER_COLOR)
            )

            if player_color_value < 0:
                player_color_value = 0

            player_color = PlayerColor(player_color_value)

            red, green, blue = (
                parse_get_or(int, DEFAULT_RED, mapping.get(RED)),
                parse_get_or(int, DEFAULT_GREEN, mapping.get(GREEN)),
                parse_get_or(int, DEFAULT_BLUE, mapping.get(BLUE)),
            )

            color = Color.from_rgb(red, green, blue)

            opacity = parse_get_or(float, DEFAULT_OPACITY, mapping.get(OPACITY))

        return cls(
            id=id,
            color=color,
            player_color=player_color,
            blending=blending,
            opacity=opacity,
            copied_id=copied_id,
            hsv=hsv,
            copy_opacity=copy_opacity,
        )

    def to_robtop(self) -> str:
        red, green, blue = self.color.to_rgb()

        mapping = {
            RED: str(red),
            GREEN: str(green),
            BLUE: str(blue),
            PLAYER_COLOR: str(self.player_color.value),
            BLENDING: str(int(self.is_blending())),
            ID: str(self.id),
            OPACITY: float_str(self.opacity),
            UNKNOWN: str(int(DEFAULT_UNKNOWN)),
            COPIED_ID: str(self.copied_id),
            COLOR_HSV: self.hsv.to_robtop(),
            TO_RED: str(DEFAULT_TO_RED),
            TO_GREEN: str(DEFAULT_TO_GREEN),
            TO_BLUE: str(DEFAULT_TO_BLUE),
            DURATION: float_str(DEFAULT_DURATION),
            TO_OPACITY: float_str(DEFAULT_TO_OPACITY),
            COPY_OPACITY: str(int(self.is_copy_opacity())),
            UNKNOWN_ANOTHER: str(int(DEFAULT_UNKNOWN_ANOTHER)),
        }

        return concat_color_channel(mapping)

    @classmethod
    def from_binary(
        cls: Type[CC],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> CC:
        bits = BITS
        byte = BYTE

        player_color_mask = PLAYER_COLOR_MASK
        blending_bit = BLENDING_BIT
        copy_opacity_bit = COPY_OPACITY_BIT

        reader = Reader(binary, order)

        id = reader.read_u16()

        copied_id = reader.read_u16()

        if copied_id:
            hsv = HSV.from_binary(binary, order, version)

            copy_opacity_and_blending = reader.read_u8()

            blending = copy_opacity_and_blending & blending_bit == blending_bit

            copy_opacity = copy_opacity_and_blending & copy_opacity_bit == copy_opacity_bit

            player_color = PlayerColor.DEFAULT

            if not copy_opacity:
                opacity = reader.read_f32()

            else:
                opacity = DEFAULT_OPACITY  # does not matter

            color = Color.default()

        else:
            hsv = HSV()

            copy_opacity = DEFAULT_COPY_OPACITY

            value = reader.read_u32()

            player_color_and_blending = value & byte

            player_color_value = (
                player_color_and_blending & player_color_mask
            ) >> PLAYER_COLOR_SHIFT

            player_color = PlayerColor(player_color_value)

            blending = player_color_and_blending & blending_bit == blending_bit

            value >>= bits

            color = Color(value)

            opacity = reader.read_f32()

        return cls(
            id=id,
            color=color,
            player_color=player_color,
            blending=blending,
            opacity=opacity,
            copied_id=copied_id,
            hsv=hsv,
            copy_opacity=copy_opacity,
        )

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        bits = BITS

        writer = Writer(binary, order)

        writer.write_u16(self.id)

        copied_id = self.copied_id

        writer.write_u16(copied_id)

        if copied_id:
            self.hsv.to_binary(binary, order, version)

            value = 0

            if self.is_blending():
                value |= BLENDING_BIT

            copy_opacity = self.is_copy_opacity()

            if copy_opacity:
                value |= COPY_OPACITY_BIT

            writer.write_u8(value)

            if not copy_opacity:
                writer.write_f32(self.opacity)

        else:
            value = 0

            if self.is_blending():
                value |= BLENDING_BIT

            value |= self.player_color.value << PLAYER_COLOR_SHIFT

            value |= self.color.value << bits

            writer.write_u32(value)

            writer.write_f32(self.opacity)

    def is_blending(self) -> bool:
        return self.blending

    def is_copied(self) -> bool:
        return bool(self.copied_id)

    def is_copy_opacity(self) -> bool:
        return self.copy_opacity


Channel = ColorChannel  # alias


CCS = TypeVar("CCS", bound="ColorChannels")


class ColorChannels(Binary, Dict[int, ColorChannel]):
    def copy(self: CCS) -> CCS:
        return type(self)(self)

    @classmethod
    def from_color_channel_iterable(cls: Type[CCS], color_channels: Iterable[ColorChannel]) -> CCS:
        return cls({color_channel.id: color_channel for color_channel in color_channels})

    from_channel_iterable = from_color_channel_iterable

    @classmethod
    def from_color_channels(cls: Type[CCS], *color_channels: ColorChannel) -> CCS:
        return cls.from_color_channel_iterable(color_channels)

    from_channels = from_color_channels

    @property
    def length(self) -> int:
        return len(self)

    def add(self, color_channel: ColorChannel) -> None:
        self[color_channel.id] = color_channel

    @classmethod
    def from_robtop(cls: Type[CCS], string: str) -> CCS:
        return cls.from_color_channel_iterable(
            iter(split_color_channels(string)).map(ColorChannel.from_robtop).unwrap()
        )

    def to_robtop(self) -> str:
        return concat_color_channels(color_channel.to_robtop() for color_channel in self.values())

    @classmethod
    def from_binary(
        cls: Type[CCS],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> CCS:
        reader = Reader(binary, order)

        length = reader.read_u16()

        color_channel_from_binary = partial(ColorChannel.from_binary, binary, order, version)

        color_channels = iter.repeat_exactly_with(color_channel_from_binary, length).unwrap()

        return cls.from_color_channel_iterable(color_channels)

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        writer = Writer(binary, order)

        writer.write_u16(self.length)

        for color_channel in self.values():
            color_channel.to_binary(binary, order, version)


Channels = ColorChannels
