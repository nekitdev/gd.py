from __future__ import annotations

from enum import Enum
from typing import Dict, Iterable, Mapping, Optional, Type, TypeVar, Union

from attrs import define, field
from funcs.application import partial
from iters.iters import iter
from typing_extensions import TypeGuard

from gd.api.hsv import HSV
from gd.binary import VERSION, Binary, BinaryReader, BinaryWriter
from gd.binary_constants import BITS, BYTE
from gd.binary_utils import Reader, Writer
from gd.color import Color
from gd.constants import DEFAULT_ID, DEFAULT_ROUNDING
from gd.enums import ByteOrder, PlayerColor, SpecialColorID
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
from gd.robtop import FromRobTop, RobTop

__all__ = (
    # cases (variants)
    "PlayerColorChannel",
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
OPACITY_TOGGLED = 8
COPIED_ID = 9
COLOR_HSV = 10
TO_RED = 11
TO_GREEN = 12
TO_BLUE = 13
DURATION = 14
TO_OPACITY = 15
COPY_OPACITY = 17
UNKNOWN = 18

PLAYER_COLOR_MASK = 0b00000110

BLENDING_BIT = 0b00000001

PLAYER_COLOR_SHIFT = BLENDING_BIT.bit_length()

COPY_OPACITY_BIT = 0b00000010


DEFAULT_OPACITY_TOGGLED = True

DEFAULT_TO_RED = BYTE
DEFAULT_TO_GREEN = BYTE
DEFAULT_TO_BLUE = BYTE

DEFAULT_DURATION = 0.0

DEFAULT_TO_OPACITY = 1.0

DEFAULT_UNKNOWN = False


DEFAULT_RED = BYTE
DEFAULT_GREEN = BYTE
DEFAULT_BLUE = BYTE

DEFAULT_BLENDING = False

DEFAULT_OPACITY = 1.0

DEFAULT_COPY_OPACITY = False

DEFAULT_PLAYER_COLOR_VALUE = PlayerColor.DEFAULT.value


BACKGROUND_COLOR_ID = SpecialColorID.BACKGROUND.id
GROUND_COLOR_ID = SpecialColorID.GROUND.id
LINE_COLOR_ID = SpecialColorID.LINE.id
LINE_3D_COLOR_ID = SpecialColorID.LINE_3D.id
OBJECT_COLOR_ID = SpecialColorID.OBJECT.id
SECONDARY_GROUND_COLOR_ID = SpecialColorID.SECONDARY_GROUND.id

COLOR_1_ID = 1
COLOR_2_ID = 2
COLOR_3_ID = 3
COLOR_4_ID = 4


class ColorChannelType(Enum):
    PLAYER = 0
    NORMAL = 1
    COPIED = 2

    def is_player(self) -> bool:
        return self is type(self).PLAYER

    def is_normal(self) -> bool:
        return self is type(self).NORMAL

    def is_copied(self) -> bool:
        return self is type(self).COPIED


COLOR_CHANNEL_ID_NOT_PRESENT = "color channel ID is not present"

BCC = TypeVar("BCC", bound="BaseColorChannel")


@define()
class BaseColorChannel(Binary, RobTop):
    """Represents base color channels."""

    id: int

    @classmethod
    def from_robtop(cls: Type[BCC], string: str) -> BCC:
        return cls.from_robtop_data(split_color_channel(string))

    @classmethod
    def from_robtop_data(cls: Type[BCC], data: Mapping[int, str]) -> BCC:
        id = parse_get_or(int, DEFAULT_ID, data.get(ID))

        if not id:
            raise ValueError(COLOR_CHANNEL_ID_NOT_PRESENT)

        return cls(id=id)

    def to_robtop(self) -> str:
        return concat_color_channel(self.to_robtop_data())

    def to_robtop_data(self) -> Dict[int, str]:
        data = {ID: str(self.id)}

        return data

    @classmethod
    def from_binary(
        cls: Type[BCC],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> BCC:
        reader = Reader(binary, order)

        id = reader.read_u16()

        return cls(id=id)

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        writer = Writer(binary, order)

        writer.write_u16(self.id)

    def is_player(self) -> bool:
        return False

    def is_normal(self) -> bool:
        return False

    def is_copied(self) -> bool:
        return False


PCC = TypeVar("PCC", bound="PlayerColorChannel")


@define()
class PlayerColorChannel(BaseColorChannel):
    """Represents player color channels."""

    player_color: PlayerColor

    opacity: float = DEFAULT_OPACITY
    blending: bool = DEFAULT_BLENDING

    def is_blending(self) -> bool:
        return self.blending

    @classmethod
    def from_robtop_data(cls: Type[PCC], data: Mapping[int, str]) -> PCC:
        id = parse_get_or(int, DEFAULT_ID, data.get(ID))

        if not id:
            raise ValueError(COLOR_CHANNEL_ID_NOT_PRESENT)

        default_player_color_value = DEFAULT_PLAYER_COLOR_VALUE

        player_color_value = max(
            parse_get_or(int, default_player_color_value, data.get(PLAYER_COLOR)),
            default_player_color_value,
        )

        player_color = PlayerColor(player_color_value)

        opacity = parse_get_or(float, DEFAULT_OPACITY, data.get(OPACITY))

        blending = parse_get_or(int_bool, DEFAULT_BLENDING, data.get(BLENDING))

        return cls(id=id, player_color=player_color, opacity=opacity, blending=blending)

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        actual = {
            PLAYER_COLOR: str(self.player_color.value),
            OPACITY: float_str(self.opacity),
            OPACITY_TOGGLED: bool_str(DEFAULT_OPACITY_TOGGLED),
        }

        data.update(actual)

        blending = self.is_blending()

        if blending:
            data[BLENDING] = bool_str(blending)

        return data

    @classmethod
    def from_binary(
        cls: Type[PCC],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> PCC:
        rounding = DEFAULT_ROUNDING

        blending_bit = BLENDING_BIT

        reader = Reader(binary, order)

        id = reader.read_u16()

        value = reader.read_u8()

        blending = value & blending_bit == blending_bit

        player_color_value = (value & PLAYER_COLOR_MASK) >> PLAYER_COLOR_SHIFT

        player_color = PlayerColor(player_color_value)

        opacity = round(reader.read_f32(), rounding)

        return cls(id=id, blending=blending, player_color=player_color, opacity=opacity)

    def to_binary(
        self,
        binary: BinaryWriter,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary, order)

        value = 0

        if self.is_blending():
            value |= BLENDING_BIT

        value |= self.player_color.value << PLAYER_COLOR_SHIFT

        writer.write_u8(value)

        writer.write_f32(self.opacity)

    def is_player(self) -> bool:
        return True


NCC = TypeVar("NCC", bound="NormalColorChannel")


@define()
class NormalColorChannel(BaseColorChannel):
    """Represents normal color channels."""

    color: Color

    opacity: float = DEFAULT_OPACITY
    blending: bool = DEFAULT_BLENDING

    def is_blending(self) -> bool:
        return self.blending

    @classmethod
    def from_robtop_data(cls: Type[NCC], data: Mapping[int, str]) -> NCC:
        id = parse_get_or(int, DEFAULT_ID, data.get(ID))

        if not id:
            raise ValueError(COLOR_CHANNEL_ID_NOT_PRESENT)

        red = parse_get_or(int, DEFAULT_RED, data.get(RED))
        green = parse_get_or(int, DEFAULT_GREEN, data.get(GREEN))
        blue = parse_get_or(int, DEFAULT_BLUE, data.get(BLUE))

        color = Color.from_rgb(red, green, blue)

        opacity = parse_get_or(float, DEFAULT_OPACITY, data.get(OPACITY))

        blending = parse_get_or(int_bool, DEFAULT_BLENDING, data.get(BLENDING))

        return cls(id=id, color=color, opacity=opacity, blending=blending)

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        color = self.color

        actual = {
            RED: str(color.red),
            GREEN: str(color.green),
            BLUE: str(color.blue),
            OPACITY: float_str(self.opacity),
            OPACITY_TOGGLED: bool_str(DEFAULT_OPACITY_TOGGLED),
        }

        data.update(actual)

        blending = self.is_blending()

        if blending:
            data[BLENDING] = bool_str(blending)

        return data

    @classmethod
    def from_binary(
        cls: Type[NCC],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> NCC:
        rounding = DEFAULT_ROUNDING

        blending_bit = BLENDING_BIT

        reader = Reader(binary, order)

        id = reader.read_u16()

        value = reader.read_u32()

        blending = value & blending_bit == blending_bit

        value >>= BITS

        color = Color(value)

        opacity = round(reader.read_f32(), rounding)

        return cls(id=id, color=color, opacity=opacity, blending=blending)

    def to_binary(
        self,
        binary: BinaryWriter,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary, order)

        value = 0

        if self.is_blending():
            value |= BLENDING_BIT

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

    hsv: HSV = field(factory=HSV)

    opacity: Optional[float] = field(default=None)

    blending: bool = field(default=DEFAULT_BLENDING)

    def is_blending(self) -> bool:
        return self.blending

    @classmethod
    def from_robtop_data(cls: Type[CCC], data: Mapping[int, str]) -> CCC:
        id = parse_get_or(int, DEFAULT_ID, data.get(ID))

        if not id:
            raise ValueError(COLOR_CHANNEL_ID_NOT_PRESENT)

        copied_id = parse_get_or(int, DEFAULT_ID, data.get(COPIED_ID))

        if not copied_id:
            raise ValueError(COLOR_CHANNEL_COPIED_ID_NOT_PRESENT)

        hsv = parse_get_or_else(HSV.from_robtop, HSV, data.get(COLOR_HSV))

        copy_opacity = parse_get_or(int_bool, DEFAULT_COPY_OPACITY, data.get(COPY_OPACITY))

        if copy_opacity:
            opacity = None

        else:
            opacity = parse_get_or(float, DEFAULT_OPACITY, data.get(OPACITY))

        blending = parse_get_or(int_bool, DEFAULT_BLENDING, data.get(BLENDING))

        return cls(id=id, copied_id=copied_id, hsv=hsv, opacity=opacity, blending=blending)

    def to_robtop_data(self) -> Dict[int, str]:
        data = super().to_robtop_data()

        actual = {
            COPIED_ID: str(self.copied_id),
            COLOR_HSV: self.hsv.to_robtop(),
            COPY_OPACITY: bool_str(self.is_copy_opacity()),
            OPACITY_TOGGLED: bool_str(DEFAULT_OPACITY_TOGGLED),
        }

        data.update(actual)

        opacity = self.opacity

        if opacity is not None:
            data[OPACITY] = float_str(opacity)

        blending = self.is_blending()

        if blending:
            data[BLENDING] = bool_str(blending)

        return data

    @classmethod
    def from_binary(
        cls: Type[CCC],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> CCC:
        rounding = DEFAULT_ROUNDING

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
            opacity = round(reader.read_f32(), rounding)

        return cls(id=id, copied_id=copied_id, blending=blending, hsv=hsv, opacity=opacity)

    def to_binary(
        self,
        binary: BinaryWriter,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary, order)

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


ColorChannel = Union[PlayerColorChannel, NormalColorChannel, CopiedColorChannel]


def is_player_color_channel(color_channel: ColorChannel) -> TypeGuard[PlayerColorChannel]:
    return color_channel.is_player()


def is_normal_color_channel(color_channel: ColorChannel) -> TypeGuard[NormalColorChannel]:
    return color_channel.is_normal()


def is_copied_color_channel(color_channel: ColorChannel) -> TypeGuard[CopiedColorChannel]:
    return color_channel.is_copied()


def color_channel_from_robtop(string: str) -> ColorChannel:
    data = split_color_channel(string)

    default_player_color_value = DEFAULT_PLAYER_COLOR_VALUE

    player_color_value = max(
        parse_get_or(int, default_player_color_value, data.get(PLAYER_COLOR)),
        default_player_color_value,
    )

    player_color = PlayerColor(player_color_value)

    if player_color.is_used():
        return PlayerColorChannel.from_robtop_data(data)

    copied_id = parse_get_or(int, DEFAULT_ID, data.get(COPIED_ID))

    if copied_id:
        return CopiedColorChannel.from_robtop_data(data)

    return NormalColorChannel.from_robtop_data(data)


def color_channel_to_robtop(color_channel: ColorChannel) -> str:
    return color_channel.to_robtop()


def color_channel_from_binary(
    binary: BinaryReader, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
) -> ColorChannel:
    reader = Reader(binary, order)

    color_channel_type_value = reader.read_u8()

    color_channel_type = ColorChannelType(color_channel_type_value)

    if color_channel_type.is_player():
        return PlayerColorChannel.from_binary(binary, order, version)

    if color_channel_type.is_normal():
        return NormalColorChannel.from_binary(binary, order, version)

    return CopiedColorChannel.from_binary(binary, order, version)


def color_channel_to_binary(
    color_channel: ColorChannel,
    binary: BinaryWriter,
    order: ByteOrder = ByteOrder.DEFAULT,
    version: int = VERSION,
) -> None:
    writer = Writer(binary, order)

    if is_player_color_channel(color_channel):
        color_channel_type = ColorChannelType.PLAYER

    elif is_normal_color_channel(color_channel):
        color_channel_type = ColorChannelType.NORMAL

    else:
        color_channel_type = ColorChannelType.COPIED

    writer.write_u8(color_channel_type.value)

    color_channel.to_binary(binary, order, version)


CCS = TypeVar("CCS", bound="ColorChannels")


class ColorChannels(Dict[int, ColorChannel], Binary):
    """Represents collections of color channels.

    Binary:
        ```rust
        enum ColorChannel {
            Player(PlayerColorChannel),
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


PCCC = TypeVar("PCCC", bound="PlayerCompatibilityColorChannel")


@define()
class PlayerCompatibilityColorChannel(FromRobTop):
    player_color: PlayerColor
    blending: bool = DEFAULT_BLENDING

    def is_blending(self) -> bool:
        return self.blending

    @classmethod
    def from_robtop(cls: Type[PCCC], string: str) -> PCCC:
        return cls.from_robtop_data(split_color_channel(string))

    @classmethod
    def from_robtop_data(cls: Type[PCCC], data: Mapping[int, str]) -> PCCC:
        default_player_color_value = DEFAULT_PLAYER_COLOR_VALUE

        player_color_value = max(
            parse_get_or(int, default_player_color_value, data.get(PLAYER_COLOR)),
            default_player_color_value,
        )

        player_color = PlayerColor(player_color_value)

        blending = parse_get_or(int_bool, DEFAULT_BLENDING, data.get(BLENDING))

        return cls(player_color=player_color, blending=blending)

    def migrate(self, id: int) -> PlayerColorChannel:
        return PlayerColorChannel(
            id=id, player_color=self.player_color, blending=self.is_blending()
        )


NCCC = TypeVar("NCCC", bound="NormalCompatibilityColorChannel")


@define()
class NormalCompatibilityColorChannel(FromRobTop):
    color: Color

    blending: bool = DEFAULT_BLENDING

    def is_blending(self) -> bool:
        return self.blending

    @classmethod
    def from_robtop(cls: Type[NCCC], string: str) -> NCCC:
        return cls.from_robtop_data(split_color_channel(string))

    @classmethod
    def from_robtop_data(cls: Type[NCCC], data: Mapping[int, str]) -> NCCC:
        red = parse_get_or(int, DEFAULT_RED, data.get(RED))
        green = parse_get_or(int, DEFAULT_GREEN, data.get(GREEN))
        blue = parse_get_or(int, DEFAULT_BLUE, data.get(BLUE))

        color = Color.from_rgb(red, green, blue)

        blending = parse_get_or(int_bool, DEFAULT_BLENDING, data.get(BLENDING))

        return cls(color=color, blending=blending)

    def migrate(self, id: int) -> NormalColorChannel:
        return NormalColorChannel(id=id, color=self.color, blending=self.is_blending())


CompatibilityColorChannel = Union[PlayerCompatibilityColorChannel, NormalCompatibilityColorChannel]


def compatibility_color_channel_from_robtop(string: str) -> CompatibilityColorChannel:
    data = split_color_channel(string)

    default_player_color_value = DEFAULT_PLAYER_COLOR_VALUE

    player_color_value = max(
        parse_get_or(int, default_player_color_value, data.get(PLAYER_COLOR)),
        default_player_color_value,
    )

    player_color = PlayerColor(player_color_value)

    if player_color.is_used():
        return PlayerCompatibilityColorChannel.from_robtop_data(data)

    return NormalCompatibilityColorChannel.from_robtop_data(data)
