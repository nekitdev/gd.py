# DOCUMENT

from gd.index_parser import IndexParser
from gd.model_backend import BoolField, FloatField, IntField, Model  # type: ignore

__all__ = ("HSV",)


class HSV(Model):
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

    PARSER = IndexParser("a", map_like=False)

    h: int = IntField(index=0, default=0)
    s: float = FloatField(index=1, default=1.0)
    v: float = FloatField(index=2, default=1.0)
    s_checked: bool = BoolField(index=3, default=False)
    v_checked: bool = BoolField(index=4, default=False)
