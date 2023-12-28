from typing import TYPE_CHECKING

from attrs import define, field
from iters.iters import iter
from typing_aliases import Unary

from gd.models_constants import HSV_SEPARATOR
from gd.models_utils import bool_str, concat_hsv, float_str, int_bool, round_float, split_hsv
from gd.robtop import RobTop

if TYPE_CHECKING:
    from typing_extensions import Self

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


def create_clamp(min_value: float, max_value: float) -> Clamp:
    def clamp(value: float) -> float:
        if value < min_value:
            return min_value

        if value > max_value:
            return max_value

        return value

    return clamp


clamp_s = create_clamp(S_MIN, S_MAX)
clamp_v = create_clamp(V_MIN, V_MAX)

clamp_s_checked = create_clamp(S_MIN_CHECKED, S_MAX_CHECKED)
clamp_v_checked = create_clamp(V_MIN_CHECKED, V_MAX_CHECKED)


H_INITIAL = 0
S_INITIAL = 1.0
V_INITIAL = 1.0

S_CHECKED = False
V_CHECKED = False


@define()
class HSV(RobTop):
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
    def from_robtop(cls, string: str) -> Self:
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
        return iter.of(
            str(self.h),
            float_str(self.s),
            float_str(self.v),
            bool_str(self.s_checked),
            bool_str(self.v_checked),
        ).collect(concat_hsv)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return HSV_SEPARATOR in string
