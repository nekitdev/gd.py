from typing import BinaryIO, Type, TypeVar
from attrs import define, field

from gd.api.api import API
from gd.binary import Binary
from gd.binary_utils import Reader, Writer
from gd.constants import BITS, BYTE
from gd.enums import ByteOrder
from gd.models import Model
from gd.models_constants import HSV_SEPARATOR
from gd.models_utils import bool_str, concat_hsv, float_str, int_bool, split_hsv

__all__ = ("HSV",)


H_INITIAL = 0
S_INITIAL = 1.0
V_INITIAL = 1.0

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
class HSV(Binary, Model, API):
    h: int = field(default=H_INITIAL)
    s: float = field(default=S_INITIAL)
    v: float = field(default=V_INITIAL)
    s_checked: bool = field(default=S_CHECKED)
    v_checked: bool = field(default=V_CHECKED)

    @classmethod
    def from_robtop(cls: Type[T], string: str) -> T:
        h, s, v, s_checked, v_checked = split_hsv(string)

        return cls(
            int(h),
            float(s),
            float(v),
            int_bool(s_checked),
            int_bool(v_checked),
        )

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return HSV_SEPARATOR in string

    def to_robtop(self) -> str:
        values = [
            str(self.h),
            float_str(self.s),
            float_str(self.v),
            bool_str(self.s_checked),
            bool_str(self.v_checked),
        ]

        return concat_hsv(values)

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
    def from_binary(cls: Type[T], binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT) -> T:
        reader = Reader(binary)

        return cls.from_value(reader.read_u32(order))

    def to_binary(self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT) -> None:
        writer = Writer(binary)

        writer.write_u32(self.to_value(), order)
