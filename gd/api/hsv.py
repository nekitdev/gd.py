from ..utils.wrap_tools import make_repr

__all__ = ('HSV',)

class HSV:
    def __init__(
        self, h: int = 0, s: float = 1, v: float = 1,
        s_checked: bool = False, v_checked: bool = False
    ):
        self.h = h
        self.s = s
        self.v = v
        self.s_checked = s_checked
        self.v_checked = v_checked

    def __repr__(self):
        info = {
            'h': self.h,
            's': self.s,
            'v': self.v,
            's_checked': self.s_checked,
            'v_checked': self.v_checked
        }
        return make_repr(self, info)

    @classmethod
    def from_string(cls, string: str):
        h, s, v, s_checked, v_checked = string.split('a')

        value_tuple = (
            int(h), _maybefloat(s), _maybefloat(v), bool(int(s_checked)), bool(int(v_checked))
        )

        return cls(*value_tuple)

    def dump(self):
        value_tuple = (
            self.h, self.s, self.v,
            int(self.s_checked), int(self.v_checked)
        )
        return 'a'.join(map(str, value_tuple))


def _maybefloat(string: str):
    return (float if '.' in string else int)(string)
