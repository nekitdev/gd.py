from typing import Type, TypeVar

from attrs import define, field
from typing_aliases import Unary

from gd.binary import VERSION, Binary, BinaryReader, BinaryWriter
from gd.binary_constants import BITS, BYTE
from gd.binary_utils import Reader, Writer
from gd.enums import ByteOrder
from gd.models_constants import HSV_SEPARATOR
from gd.models_utils import bool_str, concat_hsv, float_str, int_bool, round_float, split_hsv
from gd.robtop import RobTop

__all__ = ("HSV",)

S_MIN = 0.0
V_MIN = 0.0

S_MAX = 2.0
V_MAX = 2.0

S_MIN_CHECKED = -1.0
V_MIN_CHECKED = -1.0

S_MAX_CHECKED = 1.0
V_MAX_CHECKED = 1.0

H_BOUND = 180
H_NORMAL_BOUND = 360


def rotate_h(h: int, bound: int = H_BOUND, normal_bound: int = H_NORMAL_BOUND) -> int:
    if abs(h) > bound:
        return (h + bound) % normal_bound - bound

    return h


Clamp = Unary[float, float]


def create_clamp(min_value: float, max_value: float, out_of_bounds: str) -> Clamp:
    def clamp(value: float) -> float:
        if value < min_value:
            return min_value

        if value > max_value:
            return max_value

        return value

    return clamp


clamp_s = create_clamp(S_MIN, S_MAX, "s")
clamp_v = create_clamp(V_MIN, V_MAX, "v")

clamp_s_checked = create_clamp(S_MIN_CHECKED, S_MAX_CHECKED, "s_checked")
clamp_v_checked = create_clamp(V_MIN_CHECKED, V_MAX_CHECKED, "v_checked")


H_INITIAL = 0
S_INITIAL = 1.0
V_INITIAL = 1.0

S_CHECKED = False
V_CHECKED = False

V_BIT = 0b00000100_00000000
S_BIT = 0b00000010_00000000
H_MASK = 0b00000001_11111111

H_ADD_DOUBLE = 360
H_ADD = 180
S_MULTIPLY = 100
V_MULTIPLY = 100

ROUNDING = 2

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

        h = rotate_h(h)

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
        rounding = ROUNDING

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

        return cls(h, round(s, rounding), round(v, rounding), s_checked, v_checked)

    def to_value(self) -> int:
        value = self.h + H_ADD

        s = round(self.s * S_MULTIPLY)
        v = round(self.v * V_MULTIPLY)

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
