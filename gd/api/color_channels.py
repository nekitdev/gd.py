from enum import Flag
from typing import Dict, Iterable, Mapping, Optional, Type, TypeVar, Union

from attrs import define, field
from funcs.application import partial
from iters.iters import iter
from typing_aliases import IntoMapping
from typing_extensions import TypeGuard

from gd.api.hsv import HSV
from gd.binary import VERSION, Binary, BinaryReader, BinaryWriter
from gd.binary_constants import BITS, BYTE
from gd.binary_utils import Reader, Writer
from gd.color import Color
from gd.enums import ByteOrder, PlayerColor
from gd.models_utils import (
    bool_str,
    concat_color_channel,
    concat_color_channels,
    float_str,
    int_bool,
    parse_get_or,
    parse_get_or_else,
    split_color_channel,
    split_color_channels,
)
from gd.robtop import RobTop

__all__ = (
    # cases (variants)
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

DEFAULT_PLAYER_COLOR_VALUE = PlayerColor.DEFAULT.value


class ColorChannelFlag(Flag):
    NORMAL = 0

    COPIED = 1 << 0

    def is_copied(self) -> bool:
        return type(self).COPIED in self


COLOR_CHANNEL_ID_NOT_PRESENT = "color channel ID is not present"

BCC = TypeVar("BCC", bound="BaseColorChannel")


@define()
class BaseColorChannel(Binary, RobTop):
    """Represents base color channels."""

    id: int
    blending: bool = DEFAULT_BLENDING

    @classmethod
    def from_robtop(cls: Type[BCC], string: str) -> BCC:
        return cls.from_robtop_data(split_color_channel(string))

    @classmethod
    def from_robtop_data(cls: Type[BCC], data: Mapping[int, str]) -> BCC:
        id_option = data.get(ID)

        if id_option is None:
            raise ValueError(COLOR_CHANNEL_ID_NOT_PRESENT)

        id = int(id_option)

        blending = parse_get_or(int_bool, DEFAULT_BLENDING, data.get(BLENDING))

        return cls(id=id, blending=blending)

    def to_robtop(self) -> str:
        return concat_color_channel(self.to_robtop_data())

    def to_robtop_data(self) -> Dict[int, str]:
        data = {ID: str(self.id), BLENDING: bool_str(self.is_blending())}

        return data

    @classmethod
    def from_binary(
        cls: Type[BCC],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> BCC:
        blending_bit = BLENDING_BIT

        reader = Reader(binary, order)

        id = reader.read_u16()

        value = reader.read_u8()

        blending = value & blending_bit == blending_bit

        return cls(id=id, blending=blending)

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        writer = Writer(binary, order)

        writer.write_u16(self.id)

        value = 0

        if self.is_blending():
            value |= BLENDING_BIT

        writer.write_u8(value)

    def is_blending(self) -> bool:
        return self.blending

    def is_normal(self) -> bool:
        return False

    def is_copied(self) -> bool:
        return False


NCC = TypeVar("NCC", bound="NormalColorChannel")


@define()
class NormalColorChannel(BaseColorChannel):
    """Represents normal color channels."""

    color: Color = field(factory=Color.default)
    player_color: PlayerColor = field(default=PlayerColor.DEFAULT)
    opacity: float = field(default=DEFAULT_OPACITY)

    @classmethod
    def from_robtop_data(cls: Type[NCC], data: Mapping[int, str]) -> NCC:
        color_channel = super().from_robtop_data(data)

        red = parse_get_or(int, DEFAULT_RED, data.get(RED))
        green = parse_get_or(int, DEFAULT_GREEN, data.get(GREEN))
        blue = parse_get_or(int, DEFAULT_BLUE, data.get(BLUE))

        color = Color.from_rgb(red, green, blue)

        player_color_value = parse_get_or(int, DEFAULT_PLAYER_COLOR_VALUE, data.get(PLAYER_COLOR))

        player_color_value = max(player_color_value, 0)

        player_color = PlayerColor(player_color_value)

        opacity = parse_get_or(float, DEFAULT_OPACITY, data.get(OPACITY))

        color_channel.color = color
        color_channel.player_color = player_color
        color_channel.opacity = opacity

        return color_channel

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        color = self.color

        data[RED] = str(color.red)
        data[GREEN] = str(color.green)
        data[BLUE] = str(color.blue)

        data[PLAYER_COLOR] = str(self.player_color.value)

        data[OPACITY] = float_str(self.opacity)

        return data

    @classmethod
    def from_binary(
        cls: Type[NCC],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> NCC:
        blending_bit = BLENDING_BIT

        reader = Reader(binary, order)

        id = reader.read_u16()

        value = reader.read_u32()

        blending = value & blending_bit == blending_bit

        player_color_value = (value & PLAYER_COLOR_MASK) >> PLAYER_COLOR_SHIFT

        player_color = PlayerColor(player_color_value)

        value >>= BITS

        color = Color(value)

        opacity = reader.read_f32()

        return cls(
            id=id, blending=blending, color=color, player_color=player_color, opacity=opacity
        )

    def to_binary(
        self,
        binary: BinaryWriter,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> None:
        writer = Writer(binary, order)

        writer.write_u16(self.id)

        value = 0

        if self.is_blending():
            value |= BLENDING_BIT

        value |= self.player_color.value << PLAYER_COLOR_SHIFT

        value |= self.color.value << BITS

        writer.write_u32(value)

        writer.write_f32(self.opacity)

    def is_normal(self) -> bool:
        return True


COLOR_CHANNEL_COPIED_ID_NOT_PRESENT = "color channel copied ID is not present"

CCC = TypeVar("CCC", bound="CopiedColorChannel")


@define()
class CopiedColorChannel(BaseColorChannel):
    """Represents copied color channels."""

    copied_id: int = field()
    blending: bool = field(default=DEFAULT_BLENDING)
    hsv: HSV = field(factory=HSV)
    opacity: Optional[float] = field(default=None)

    @classmethod
    def from_robtop_data(cls: Type[CCC], data: Mapping[int, str]) -> CCC:
        id_option = data.get(ID)

        if id_option is None:
            raise ValueError(COLOR_CHANNEL_ID_NOT_PRESENT)

        id = int(id_option)

        copied_id_option = data.get(COPIED_ID)

        if copied_id_option is None:
            raise ValueError(COLOR_CHANNEL_COPIED_ID_NOT_PRESENT)

        copied_id = int(copied_id_option)

        blending = parse_get_or(int_bool, DEFAULT_BLENDING, data.get(BLENDING))

        hsv = parse_get_or_else(HSV.from_robtop, HSV, data.get(COLOR_HSV))

        copy_opacity = parse_get_or(int_bool, DEFAULT_COPY_OPACITY, data.get(COPY_OPACITY))

        if copy_opacity:
            opacity = None

        else:
            opacity = parse_get_or(float, DEFAULT_OPACITY, data.get(OPACITY))

        return cls(id=id, copied_id=copied_id, blending=blending, hsv=hsv, opacity=opacity)

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        data[COPIED_ID] = str(self.copied_id)

        data[COLOR_HSV] = self.hsv.to_robtop()

        copy_opacity = self.is_copy_opacity()

        data[COPY_OPACITY] = bool_str(copy_opacity)

        opacity = self.opacity

        if opacity is not None:
            data[OPACITY] = float_str(opacity)

        return data

    @classmethod
    def from_binary(
        cls: Type[CCC],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> CCC:
        blending_bit = BLENDING_BIT
        copy_opacity_bit = COPY_OPACITY_BIT

        reader = Reader(binary, order)

        id = reader.read_u16()

        copied_id = reader.read_u16()

        value = reader.read_u8()

        blending = value & blending_bit == blending_bit
        copy_opacity = value & copy_opacity_bit == copy_opacity_bit

        hsv = HSV.from_binary(binary, order, version)

        if copy_opacity:
            opacity = None

        else:
            opacity = reader.read_f32()

        return cls(id=id, copied_id=copied_id, blending=blending, hsv=hsv, opacity=opacity)

    def to_binary(
        self,
        binary: BinaryWriter,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> None:
        writer = Writer(binary, order)

        writer.write_u16(self.id)

        writer.write_u16(self.copied_id)

        value = 0

        if self.is_blending():
            value |= BLENDING_BIT

        if self.is_copy_opacity():
            value |= COPY_OPACITY_BIT

        writer.write_u8(value)

        self.hsv.to_binary(binary, order, version)

        opacity = self.opacity

        if opacity is not None:
            writer.write_f32(opacity)

    def is_copied(self) -> bool:
        return True

    def is_copy_opacity(self) -> bool:
        return self.opacity is None

    def copy_opacity(self: CCC) -> CCC:
        self.opacity = None

        return self


ColorChannel = Union[NormalColorChannel, CopiedColorChannel]


def is_normal_color_channel(color_channel: ColorChannel) -> TypeGuard[NormalColorChannel]:
    return color_channel.is_normal()


def is_copied_color_channel(color_channel: ColorChannel) -> TypeGuard[CopiedColorChannel]:
    return color_channel.is_copied()


def color_channel_from_robtop(string: str) -> ColorChannel:
    data = split_color_channel(string)

    copied_id_option = data.get(COPIED_ID)

    if copied_id_option is None:
        return NormalColorChannel.from_robtop_data(data)

    copied_id = int(copied_id_option)

    if not copied_id:
        return NormalColorChannel.from_robtop_data(data)

    return CopiedColorChannel.from_robtop_data(data)


def color_channel_to_robtop(color_channel: ColorChannel) -> str:
    return color_channel.to_robtop()


def color_channel_from_binary(
    binary: BinaryReader, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
) -> ColorChannel:
    reader = Reader(binary, order)

    color_channel_flag_value = reader.read_u8()

    color_channel_flag = ColorChannelFlag(color_channel_flag_value)

    if color_channel_flag.is_copied():
        return CopiedColorChannel.from_binary(binary, order, version)

    return NormalColorChannel.from_binary(binary, order, version)


def color_channel_to_binary(
    color_channel: ColorChannel,
    binary: BinaryWriter,
    order: ByteOrder = ByteOrder.DEFAULT,
    version: int = VERSION,
) -> None:
    writer = Writer(binary, order)

    color_channel_flag = ColorChannelFlag.NORMAL

    if is_copied_color_channel(color_channel):
        color_channel_flag |= ColorChannelFlag.COPIED

    writer.write_u8(color_channel_flag.value)

    color_channel.to_binary(binary, order, version)


CCS = TypeVar("CCS", bound="ColorChannels")


class ColorChannels(Dict[int, ColorChannel], Binary):
    """Represents collections of color channels.

    Binary:
        ```rust
        enum ColorChannel {
            Normal(NormalColorChannel),
            Copied(CopiedColorChannel),
        }

        struct ColorChannels {
            color_channels_length: u16,
            color_channels: [ColorChannel; color_channels_length],
        }
        ```
    """

    def copy(self: CCS) -> CCS:
        return type(self)(self)

    @classmethod
    def from_color_channel_iterable(cls: Type[CCS], color_channels: Iterable[ColorChannel]) -> CCS:
        return cls({color_channel.id: color_channel for color_channel in color_channels})

    @classmethod
    def from_color_channels(cls: Type[CCS], *color_channels: ColorChannel) -> CCS:
        return cls.from_color_channel_iterable(color_channels)

    @property
    def length(self) -> int:
        return len(self)

    def add(self, color_channel: ColorChannel) -> None:
        self[color_channel.id] = color_channel

    @classmethod
    def from_robtop(cls: Type[CCS], string: str) -> CCS:
        return cls.from_color_channel_iterable(
            iter(split_color_channels(string)).filter(None).map(color_channel_from_robtop).unwrap()
        )

    def to_robtop(self) -> str:
        return concat_color_channels(map(color_channel_to_robtop, self.values()))

    @classmethod
    def from_binary(
        cls: Type[CCS],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> CCS:
        reader = Reader(binary, order)

        length = reader.read_u16()

        color_channel_from_binary_function = partial(
            color_channel_from_binary, binary, order, version
        )

        color_channels = iter.repeat_exactly_with(
            color_channel_from_binary_function, length
        ).unwrap()

        return cls.from_color_channel_iterable(color_channels)

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        writer = Writer(binary, order)

        writer.write_u16(self.length)

        for color_channel in self.values():
            color_channel_to_binary(color_channel, binary, order, version)
