from typing import BinaryIO, Dict, Iterable, Optional, Type, TypeVar

from attrs import define, field

from gd.api.hsv import HSV
from gd.binary import VERSION, Binary
from gd.binary_utils import Reader, Writer
from gd.color import Color
from gd.constants import BITS, BYTE, DEFAULT_ID
from gd.enums import ByteOrder, PlayerColor
from gd.models_utils import (
    concat_color_channel,
    float_str,
    int_bool,
    parse_get_or,
    partial_parse_enum,
    split_color_channel,
)

__all__ = ("ColorChannel", "ColorChannels", "Channel", "Channels")

DEFAULT_RED = BYTE
DEFAULT_GREEN = BYTE
DEFAULT_BLUE = BYTE

DEFAULT_BLENDING = False

DEFAULT_OPACITY = 1.0

DEFAULT_UNKNOWN = True

DEFAULT_DELTA = 0.0

DEFAULT_TO_RED = BYTE
DEFAULT_TO_GREEN = BYTE
DEFAULT_TO_BLUE = BYTE

DEFAULT_TO_OPACITY = 1.0

DEFAULT_COPY_OPACITY = False

DEFAULT_UNKNOWN_ANOTHER = False

OPACITY_MULTIPLY = 100.0

BLENDING_BIT = 0b100000000
OPACITY_MASK = 0b011111111

COPY_OPACITY_BIT = BLENDING_BIT

PLAYER_COLOR_MASK = 0b00000011
UNKNOWN_BIT = 0b00000100
UNKNOWN_ANOTHER_BIT = 0b00001000

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
TO_OPACITY = 15
COPY_OPACITY = 17
UNKNOWN_ANOTHER = 18


CC = TypeVar("CC", bound="ColorChannel")


@define()
class ColorChannel(Binary):
    id: int = field()
    color: Color = field(factory=Color.default)
    player_color: PlayerColor = field(default=PlayerColor.DEFAULT)
    blending: bool = field(default=DEFAULT_BLENDING)
    opacity: float = field(default=DEFAULT_OPACITY)
    unknown: bool = field(default=DEFAULT_UNKNOWN)
    copied_id: int = field(default=DEFAULT_ID)
    hsv: HSV = field(factory=HSV)
    to_color: Color = field(factory=Color.default)
    delta: float = field(default=DEFAULT_DELTA)
    to_opacity: float = field(default=DEFAULT_TO_OPACITY)
    copy_opacity: bool = field(default=DEFAULT_COPY_OPACITY)
    unknown_another: bool = field(default=DEFAULT_UNKNOWN_ANOTHER)

    @classmethod
    def from_robtop(
        cls: Type[CC],
        string: str,
        # indexes
        red_index: int = RED,
        green_index: int = GREEN,
        blue_index: int = BLUE,
        player_color_index: int = PLAYER_COLOR,
        blending_index: int = BLENDING,
        id_index: int = ID,
        opacity_index: int = OPACITY,
        unknown_index: int = UNKNOWN,
        copied_id_index: int = COPIED_ID,
        hsv_index: int = COLOR_HSV,
        to_red_index: int = TO_RED,
        to_green_index: int = TO_GREEN,
        to_blue_index: int = TO_BLUE,
        to_opacity_index: int = TO_OPACITY,
        copy_opacity_index: int = COPY_OPACITY,
        unknown_another_index: int = UNKNOWN_ANOTHER,
        # defaults
        red_default: int = DEFAULT_RED,
        green_default: int = DEFAULT_GREEN,
        blue_default: int = DEFAULT_BLUE,
        player_color_default: PlayerColor = PlayerColor.DEFAULT,
        blending_default: bool = DEFAULT_BLENDING,
        id_default: int = DEFAULT_ID,
        opacity_default: float = DEFAULT_OPACITY,
        unknown_default: bool = DEFAULT_UNKNOWN,
        copied_id_default: int = DEFAULT_ID,
        hsv_default: Optional[HSV] = None,
        to_red_default: int = DEFAULT_TO_RED,
        to_green_default: int = DEFAULT_TO_GREEN,
        to_blue_default: int = DEFAULT_TO_BLUE,
        to_opacity_default: float = DEFAULT_TO_OPACITY,
        copy_opacity_default: bool = DEFAULT_COPY_OPACITY,
        unknown_another_default: bool = DEFAULT_UNKNOWN_ANOTHER,
    ) -> CC:
        if hsv_default is None:
            hsv_default = HSV()

        mapping = split_color_channel(string)

        red, green, blue = (
            parse_get_or(int, red_default, mapping.get(red_index)),
            parse_get_or(int, green_default, mapping.get(green_index)),
            parse_get_or(int, blue_default, mapping.get(blue_index)),
        )

        color = Color.from_rgb(red, green, blue)

        player_color = parse_get_or(
            partial_parse_enum(int, PlayerColor),
            player_color_default,
            mapping.get(player_color_index),
        )

        blending = parse_get_or(int_bool, blending_default, mapping.get(blending_index))

        id = parse_get_or(int, id_default, mapping.get(id_index))

        opacity = parse_get_or(float, opacity_default, mapping.get(opacity_index))

        unknown = parse_get_or(int_bool, unknown_default, mapping.get(unknown_index))

        copied_id = parse_get_or(int, copied_id_default, mapping.get(copied_id_index))

        hsv = parse_get_or(HSV.from_robtop, hsv_default, mapping.get(hsv_index))

        to_red, to_green, to_blue = (
            parse_get_or(int, to_red_default, mapping.get(to_red_index)),
            parse_get_or(int, to_green_default, mapping.get(to_green_index)),
            parse_get_or(int, to_blue_default, mapping.get(to_blue_index)),
        )

        to_color = Color.from_rgb(to_red, to_green, to_blue)

        to_opacity = parse_get_or(float, to_opacity_default, mapping.get(to_opacity_index))

        copy_opacity = parse_get_or(
            int_bool,
            copy_opacity_default,
            mapping.get(copy_opacity_index),
        )

        unknown_another = parse_get_or(
            int_bool,
            unknown_another_default,
            mapping.get(unknown_another_index),
        )

        return cls(
            color=color,
            player_color=player_color,
            blending=blending,
            id=id,
            opacity=opacity,
            unknown=unknown,
            copied_id=copied_id,
            hsv=hsv,
            to_color=to_color,
            to_opacity=to_opacity,
            copy_opacity=copy_opacity,
            unknown_another=unknown_another,
        )

    def to_robtop(
        self,
        red_index: int = RED,
        green_index: int = GREEN,
        blue_index: int = BLUE,
        player_color_index: int = PLAYER_COLOR,
        blending_index: int = BLENDING,
        id_index: int = ID,
        opacity_index: int = OPACITY,
        unknown_index: int = UNKNOWN,
        copied_id_index: int = COPIED_ID,
        hsv_index: int = COLOR_HSV,
        to_red_index: int = TO_RED,
        to_green_index: int = TO_GREEN,
        to_blue_index: int = TO_BLUE,
        to_opacity_index: int = TO_OPACITY,
        copy_opacity_index: int = COPY_OPACITY,
        unknown_another_index: int = UNKNOWN_ANOTHER,
    ) -> str:
        red, green, blue = self.color.to_rgb()

        to_red, to_green, to_blue = self.to_color.to_rgb()

        mapping = {
            red_index: str(red),
            green_index: str(green),
            blue_index: str(blue),
            player_color_index: str(self.player_color.value),
            blending_index: str(int(self.blending)),
            id_index: str(self.id),
            opacity_index: float_str(self.opacity),
            unknown_index: str(int(self.unknown)),
            copied_id_index: str(self.copied_id),
            hsv_index: self.hsv.to_robtop(),
            to_red_index: str(to_red),
            to_green_index: str(to_green),
            to_blue_index: str(to_blue),
            to_opacity_index: float_str(self.to_opacity),
            copy_opacity_index: str(int(self.copy_opacity)),
            unknown_another_index: str(int(self.unknown_another)),
        }

        return concat_color_channel(mapping)

    @classmethod
    def from_binary(
        cls: Type[CC],
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> CC:
        bits = BITS
        byte = BYTE

        player_color_mask = PLAYER_COLOR_MASK
        unknown_bit = UNKNOWN_BIT
        unknown_another_bit = UNKNOWN_ANOTHER_BIT

        opacity_multiply = OPACITY_MULTIPLY

        opacity_mask = OPACITY_MASK
        copy_opacity_bit = COPY_OPACITY_BIT
        blending_bit = BLENDING_BIT

        reader = Reader(binary)

        id = reader.read_u16(order)

        value = reader.read_u32(order)

        blending_and_opacity = value & byte

        blending = blending_and_opacity & blending_bit == blending_bit

        opacity = float(blending_and_opacity & opacity_mask) / opacity_multiply

        value >>= bits

        color = Color(value)

        unknowns_and_player_color = reader.read_u8(order)

        unknown = unknowns_and_player_color & unknown_bit == unknown_bit
        unknown_another = unknowns_and_player_color & unknown_another_bit == unknown_another_bit

        player_color_value = unknowns_and_player_color & player_color_mask

        if player_color_value == player_color_mask:
            player_color = PlayerColor.NOT_USED

        else:
            player_color = PlayerColor(player_color_value)

        hsv = HSV.from_binary(binary, order, version)

        to_value = reader.read_u32(order)

        copy_opacity_and_to_opacity = to_value & byte

        copy_opacity = copy_opacity_and_to_opacity & copy_opacity_bit == copy_opacity_bit

        to_opacity = float(copy_opacity_and_to_opacity & opacity_mask) / opacity_multiply

        to_value >>= bits

        to_color = Color(to_value)

        delta = reader.read_f32(order)

        copied_id = reader.read_u16(order)

        return cls(
            id=id,
            color=color,
            player_color=player_color,
            blending=blending,
            opacity=opacity,
            unknown=unknown,
            copied_id=copied_id,
            hsv=hsv,
            to_color=to_color,
            delta=delta,
            to_opacity=to_opacity,
            copy_opacity=copy_opacity,
            unknown_another=unknown_another,
        )

    def to_binary(
        self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        bits = BITS

        player_color_mask = PLAYER_COLOR_MASK
        unknown_bit = UNKNOWN_BIT
        unknown_another_bit = UNKNOWN_ANOTHER_BIT

        opacity_multiply = OPACITY_MULTIPLY

        copy_opacity_bit = COPY_OPACITY_BIT
        blending_bit = BLENDING_BIT

        writer = Writer(binary)

        writer.write_u16(self.id, order)

        value = self.color.value

        opacity = round(self.opacity * opacity_multiply)

        if self.is_blending():
            opacity |= blending_bit

        value = (value << bits) | opacity

        writer.write_u32(value, order)

        player_color = self.player_color

        if player_color.is_not_used():
            unknowns_and_player_color = player_color_mask

        else:
            unknowns_and_player_color = player_color.value

        if self.is_unknown():
            unknowns_and_player_color |= unknown_bit

        if self.is_unknown_another():
            unknowns_and_player_color |= unknown_another_bit

        writer.write_u8(unknowns_and_player_color, order)

        self.hsv.to_binary(binary, order, version)

        to_value = self.to_color.value

        to_opacity = round(self.to_opacity * opacity_multiply)

        if self.is_copy_opacity():
            to_opacity |= copy_opacity_bit

        to_value = (to_value << bits) | to_opacity

        writer.write_u32(to_value, order)

        writer.write_f32(self.delta, order)

        writer.write_u16(self.copied_id, order)

    def is_blending(self) -> bool:
        return self.blending

    def is_unknown(self) -> bool:
        return self.unknown

    def is_copy_opacity(self) -> bool:
        return self.copy_opacity

    def is_unknown_another(self) -> bool:
        return self.unknown_another


Channel = ColorChannel  # alias


CCS = TypeVar("CCS", bound="ColorChannels")


class ColorChannels(Binary, Dict[int, ColorChannel]):
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
        ...

    def to_robtop(self) -> str:
        ...

    @classmethod
    def from_binary(
        cls: Type[CCS],
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        color_channel_type: Type[ColorChannel] = ColorChannel,
    ) -> CCS:
        reader = Reader(binary)

        length = reader.read_u16(order)

        color_channels = (
            color_channel_type.from_binary(binary, order, version) for _ in range(length)
        )

        return cls.from_color_channel_iterable(color_channels)

    def to_binary(
        self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        writer = Writer(binary)

        writer.write_u16(self.length, order)

        for color_channel in self.values():
            color_channel.to_binary(binary, order, version)


Channels = ColorChannels
