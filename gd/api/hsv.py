from gd.typing import Dict, HSV, Tuple, Union
from gd.utils.text_tools import make_repr

__all__ = ("HSV",)


class HSV:
    """A class that represents HSV - Hue, Saturation, Value (Brightness) options.

    Below is a table that shows how S and V depend on whether they are checked:

        +-------------+--------+---------+
        | value range |  false |    true |
        +=============+========+=========+
        | s range     | [0, 2] | [-1, 1] |
        +-------------+--------+---------+
        | v range     | [0, 2] | [-1, 1] |
        +-------------+--------+---------+

    Parameters
    ----------
    h: :class:`int`
        Hue integer value in range [-180, 180].
    s: :class:`float`
        Saturation float value in range [0, 2] or [-1, 1]
        depending on ``s_checked``.
    v: :class:`float`
        Value (Brightness) float value in range [0, 2] or [-1, 1]
        depending on ``v_checked``.
    s_checked: :class:`bool`
        Whether ``s`` is checked.
    v_checked: :class:`bool`
        Whether ``v`` is checked.
    """

    def __init__(
        self,
        h: int = 0,
        s: float = 1,
        v: float = 1,
        s_checked: bool = False,
        v_checked: bool = False,
    ) -> None:
        self.h = h
        self.s = s
        self.v = v
        self.s_checked = s_checked
        self.v_checked = v_checked

    def __repr__(self) -> str:
        info = {
            "h": self.h,
            "s": self.s,
            "v": self.v,
            "s_checked": self.s_checked,
            "v_checked": self.v_checked,
        }
        return make_repr(self, info)

    def __json__(self) -> Dict[str, Union[bool, float, int]]:
        return dict(
            h=self.h, s=self.s, v=self.v, s_checked=self.s_checked, v_checked=self.v_checked
        )

    def as_tuple(self) -> Tuple[int, float, float]:
        """Return an ``(h, s, v)`` tuple."""
        return self.h, self.s, self.v

    @classmethod
    def from_string(cls, string: str) -> HSV:
        h, s, v, s_checked, v_checked = string.split("a")

        value_tuple = (
            int(h),
            _maybefloat(s),
            _maybefloat(v),
            _bool(s_checked),
            _bool(v_checked),
        )

        return cls(*value_tuple)

    def dump(self) -> str:
        value_tuple = (self.h, self.s, self.v, int(self.s_checked), int(self.v_checked))
        return "a".join(map(str, value_tuple))


def _maybefloat(string: str) -> Union[float, int]:
    return (float if "." in string else int)(string)


def _bool(string: str) -> bool:
    return string == "1"
