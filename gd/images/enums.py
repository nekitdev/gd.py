from enum import Enum

__all__ = ("Orientation",)


class Orientation(Enum):
    HORIZONTAL = 0
    VERTICAL = 1

    DEFAULT = HORIZONTAL

    def is_horizontal(self) -> bool:
        return self is type(self).HORIZONTAL

    def is_vertical(self) -> bool:
        return self is type(self).VERTICAL

    def is_default(self) -> bool:
        return self is type(self).DEFAULT
