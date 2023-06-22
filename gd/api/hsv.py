from typing import Type, TypeVar

from attrs import define, field

from gd.binary import VERSION, Binary, BinaryReader, BinaryWriter
from gd.binary_constants import BITS, BYTE
from gd.binary_utils import Reader, Writer
from gd.enums import ByteOrder
from gd.models_constants import HSV_SEPARATOR
from gd.models_utils import bool_str, concat_hsv, float_str, int_bool, round_float, split_hsv
from gd.robtop import RobTop

__all__ = ("HSV",)

H_INITIAL = 0
S_INITIAL = 1.0
V_INITIAL = 1.0

S_MIN = 0.0
V_MIN = 0.0

S_MAX = 2.0
V_MAX = 2.0

S_MIN_CHECKED = -1.0
V_MIN_CHECKED = -1.0

S_MAX_CHECKED = 1.0
V_MAX_CHECKED = 1.0


def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(value, max_value))


def clamp_s(value: float) -> float:
    return clamp(value, S_MIN, S_MAX)


def clamp_v(value: float) -> float:
    return clamp(value, V_MIN, V_MAX)


def clamp_s_checked(value: float) -> float:
    return clamp(value, S_MIN_CHECKED, S_MAX_CHECKED)


def clamp_v_checked(value: float) -> float:
    return clamp(value, V_MIN_CHECKED, V_MAX_CHECKED)


S_CHECKED = False
V_CHECKED = False

V_BIT = 0b00000100_00000000
S_BIT = 0b00000010_00000000
H_MASK = 0b00000001_11111111

H_ADD = 180
S_MULTIPLY = 100
V_MULTIPLY = 100

T = TypeVar("T", bound="HSV")


@define()
class HSV(Binary, RobTop):
    h: int = field(default=H_INITIAL)
    s: float = field(default=S_INITIAL)
    v: float = field(default=V_INITIAL)
    s_checked: bool = field(default=S_CHECKED)
    v_checked: bool = field(default=V_CHECKED)

    def is_default(self) -> bool:
        return (
            self.h == H_INITIAL
            and self.s == S_INITIAL
            and self.v == V_INITIAL
            and self.s_checked == S_CHECKED
            and self.v_checked == V_CHECKED
        )

    @classmethod
    def from_robtop(cls: Type[T], string: str) -> T:
        h_string, s_string, v_string, s_checked_string, v_checked_string = split_hsv(string)

        h = round_float(h_string)
        s = float(s_string)
        v = float(v_string)

        h_add = H_ADD

        if abs(h) > h_add:
            h %= h_add

        s_checked = int_bool(s_checked_string)
        v_checked = int_bool(v_checked_string)

        if s < 0:
            s_checked = True

        if v < 0:
            v_checked = True

        s = clamp_s_checked(s) if s_checked else clamp_s(s)
        v = clamp_v_checked(v) if v_checked else clamp_v(v)

        return cls(h, s, v, s_checked, v_checked)

    def to_robtop(self) -> str:
        values = (
            str(self.h),
            float_str(self.s),
            float_str(self.v),
            bool_str(self.s_checked),
            bool_str(self.v_checked),
        )

        return concat_hsv(values)

    @staticmethod
    def can_be_in(string: str) -> bool:
        return HSV_SEPARATOR in string

    # 00000VSH HHHHHHHH SSSSSSSS VVVVVVVV

    @classmethod
    def from_value(cls: Type[T], value: int) -> T:
        bits = BITS
        byte = BYTE

        v = (value & byte) / V_MULTIPLY

        value >>= bits

        s = (value & byte) / S_MULTIPLY

        value >>= bits

        h = (value & H_MASK) - H_ADD

        s_bit = S_BIT
        v_bit = V_BIT

        s_checked = value & s_bit == s_bit
        v_checked = value & v_bit == v_bit

        if s_checked:
            s -= S_INITIAL

        if v_checked:
            v -= V_INITIAL

        return cls(h, s, v, s_checked, v_checked)

    def to_value(self) -> int:
        value = self.h + H_ADD

        s = int(self.s * S_MULTIPLY)
        v = int(self.v * V_MULTIPLY)

        if self.s_checked:
            value |= S_BIT
            s += S_MULTIPLY

        if self.v_checked:
            value |= V_BIT
            v += V_MULTIPLY

        bits = BITS

        value = (value << bits) | s
        value = (value << bits) | v

        return value

    @classmethod
    def from_binary(
        cls: Type[T],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> T:
        reader = Reader(binary, order)

        return cls.from_value(reader.read_u32())

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        writer = Writer(binary, order)

        writer.write_u32(self.to_value())
