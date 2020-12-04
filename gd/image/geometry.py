from typing import Any, Tuple, TypeVar

from attr import attrib, dataclass

__all__ = ("Point", "Size", "Rectangle")

P = TypeVar("P", bound="Point")
S = TypeVar("S", bound="Size")
R = TypeVar("R", bound="Rectangle")


@dataclass
class Point:
    x: float = attrib(default=0.0, converter=float)
    y: float = attrib(default=0.0, converter=float)

    def __add__(self: P, other: Any) -> P:
        if isinstance(other, self.__class__):
            return self.__class__(self.x + other.x, self.y + other.y)

        return self.__class__(self.x + other, self.y + other)

    def __sub__(self: P, other: Any) -> P:
        if isinstance(other, self.__class__):
            return self.__class__(self.x - other.x, self.y - other.y)

        return self.__class__(self.x - other, self.y - other)

    def __mul__(self: P, other: Any) -> P:
        return self.__class__(self.x * other, self.y * other)

    def __truediv__(self: P, other: Any) -> P:
        return self.__class__(self.x / other, self.y / other)

    def __floordiv__(self: P, other: Any) -> P:
        return self.__class__(self.x // other, self.y // other)

    __radd__ = __add__
    __rsub__ = __sub__
    __rmul__ = __mul__
    __rtruediv__ = __truediv__
    __rfloordiv__ = __floordiv__

    def __iadd__(self: P, other: Any) -> P:
        if isinstance(other, self.__class__):
            self.x += other.x
            self.y += other.y

            return self

        self.x += other
        self.y += other

        return self

    def __isub__(self: P, other: Any) -> P:
        if isinstance(other, self.__class__):
            self.x -= other.x
            self.y -= other.y

            return self

        self.x -= other
        self.y -= other

        return self

    def __imul__(self: P, other: Any) -> P:
        self.x *= other
        self.y *= other

        return self

    def __itruediv__(self: P, other: Any) -> P:
        self.x /= other
        self.y /= other

        return self

    def __ifloordiv__(self: P, other: Any) -> P:
        self.x //= other
        self.y //= other

        return self

    def x_flip(self: P) -> P:
        self.x = -self.x

        return self

    def y_flip(self: P) -> P:
        self.y = -self.y

        return self

    def as_tuple(self) -> Tuple[float, float]:
        return (self.x, self.y)


@dataclass
class Size:
    width: float = attrib(default=0.0, converter=float)
    height: float = attrib(default=0.0, converter=float)

    def __mul__(self: S, other: Any) -> S:
        return self.__class__(self.width * other, self.height * other)

    def __truediv__(self: S, other: Any) -> S:
        return self.__class__(self.width / other, self.height / other)

    def __floordiv__(self: S, other: Any) -> S:
        return self.__class__(self.width // other, self.height // other)

    def __imul__(self: S, other: Any) -> S:
        self.width *= other
        self.height *= other

        return self

    def __itruediv__(self: S, other: Any) -> S:
        self.width /= other
        self.height /= other

        return self

    def __ifloordiv__(self: S, other: Any) -> S:
        self.width //= other
        self.height //= other

        return self

    def as_tuple(self) -> Tuple[float, float]:
        return (self.width, self.height)


@dataclass
class Rectangle:
    origin: Point = attrib(factory=Point)
    size: Size = attrib(factory=Size)

    @property
    def x(self) -> float:
        return self.origin.x

    @property
    def y(self) -> float:
        return self.origin.y

    @property
    def width(self) -> float:
        return self.size.width

    @property
    def height(self) -> float:
        return self.size.height

    @property
    def min_x(self) -> float:
        return self.origin.x

    @property
    def mid_x(self) -> float:
        return self.origin.x + self.size.width / 2

    @property
    def max_x(self) -> float:
        return self.origin.x + self.size.width

    @property
    def min_y(self) -> float:
        return self.origin.y

    @property
    def mid_y(self) -> float:
        return self.origin.y + self.size.height / 2

    @property
    def max_y(self) -> float:
        return self.origin.y + self.size.height

    @property
    def upper_left(self) -> Point:
        return self.origin.__class__(self.min_x, self.min_y)

    @property
    def upper_right(self) -> Point:
        return self.origin.__class__(self.max_x, self.min_y)

    @property
    def center(self) -> Point:
        return self.origin.__class__(self.mid_x, self.mid_y)

    @property
    def lower_left(self) -> Point:
        return self.origin.__class__(self.min_x, self.max_y)

    @property
    def lower_right(self) -> Point:
        return self.origin.__class__(self.max_x, self.max_y)

    def as_tuple(self) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        return ((self.x, self.y), (self.width, self.height))

    def as_box(self) -> Tuple[float, float, float, float]:
        return (self.x, self.y, self.width, self.height)
