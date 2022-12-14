from __future__ import annotations

from math import atan2, cos, sin, sqrt
from typing import Tuple, Type, TypeVar

from attrs import Attribute, define, field

__all__ = ("Point", "Size", "Rectangle")

P = TypeVar("P", bound="Point")

S = TypeVar("S", bound="Size")

R = TypeVar("R", bound="Rectangle")


@define()
class Point:
    x: float = 0.0
    y: float = 0.0

    @classmethod
    def from_scalar(cls: Type[P], scalar: float) -> P:
        return cls(scalar, scalar)

    @classmethod
    def from_length_and_angle(cls: Type[P], length: float, angle: float) -> P:
        return cls(length * cos(angle), length * sin(angle))

    @classmethod
    def create(cls: Type[P], x: float = 0.0, y: float = 0.0) -> P:
        return cls(x, y)

    @property
    def length_squared(self) -> float:
        x = self.x
        y = self.y

        return x * x + y * y

    @property
    def length(self) -> float:
        return sqrt(self.length_squared)

    @property
    def angle(self) -> float:
        return atan2(self.y, self.x)

    def normalize(self: P) -> P:
        length = self.length

        if length:
            return self.create(self.x / length, self.y / length)

        return self

    def add(self: P, point: Point) -> P:
        return self.create(self.x + point.x, self.y + point.y)

    def add_in_place(self: P, point: Point) -> P:
        self.x += point.x
        self.y += point.y

        return self

    def sub(self: P, point: Point) -> P:
        return self.create(self.x - point.x, self.y - point.y)

    def sub_in_place(self: P, point: Point) -> P:
        self.x -= point.x
        self.y -= point.y

        return self

    def mul(self: P, scalar: float) -> P:
        return self.create(self.x * scalar, self.y * scalar)

    def mul_in_place(self: P, scalar: float) -> P:
        self.x *= scalar
        self.y *= scalar

        return self

    def div(self: P, scalar: float) -> P:
        return self.create(self.x / scalar, self.y / scalar)

    def div_in_place(self: P, scalar: float) -> P:
        self.x /= scalar
        self.y /= scalar

        return self

    def flipped(self: P) -> P:
        return self.create(-self.x, -self.y)

    def flip(self: P) -> P:
        self.x = -self.x
        self.y = -self.y

        return self

    def x_flipped(self: P) -> P:
        return self.create(-self.x, self.y)

    def x_flip(self: P) -> P:
        self.x = -self.x

        return self

    def y_flipped(self: P) -> P:
        return self.create(self.x, -self.y)

    def y_flip(self: P) -> P:
        self.y = -self.y

        return self

    def swapped(self: P) -> P:
        return self.create(self.y, self.x)

    def swap(self: P) -> P:
        self.x, self.y = self.y, self.x

        return self

    def clone(self: P) -> P:
        return self.create(self.x, self.y)

    def into_tuple(self) -> Tuple[float, float]:
        return (self.x, self.y)

    def round_tuple(self) -> Tuple[int, int]:
        return (round(self.x), round(self.y))

    __neg__ = flipped

    __add__ = add
    __sub__ = sub
    __mul__ = mul

    __iadd__ = add_in_place
    __isub__ = sub_in_place
    __imul__ = mul_in_place

    __truediv__ = div

    __itruediv__ = div_in_place


@define()
class Size:
    width: float = field(default=0.0)
    height: float = field(default=0.0)

    @width.validator
    def check_width(self, attribute: Attribute[float], width: float) -> None:
        if width < 0.0:
            raise ValueError  # TODO: message?

    @height.validator
    def check_height(self, attribute: Attribute[float], height: float) -> None:
        if height < 0.0:
            raise ValueError  # TODO: message?

    @classmethod
    def from_scalar(cls: Type[S], scalar: float) -> S:
        return cls(scalar, scalar)

    @classmethod
    def create(cls: Type[S], width: float = 0.0, height: float = 0.0) -> S:
        return cls(width, height)

    def mul(self: S, scalar: float) -> S:
        return self.create(self.width * scalar, self.height * scalar)

    def mul_in_place(self: S, scalar: float) -> S:
        self.width *= scalar
        self.height *= scalar

        return self

    def mul_components(self: S, size: Size) -> S:
        return self.create(self.width * size.width, self.height * size.height)

    def mul_components_in_place(self: S, size: Size) -> S:
        self.width *= size.width
        self.height *= size.height

        return self

    def div(self: S, scalar: float) -> S:
        return self.create(self.width / scalar, self.height / scalar)

    def div_in_place(self: S, scalar: float) -> S:
        self.width /= scalar
        self.height /= scalar

        return self

    def div_components(self: S, size: Size) -> S:
        return self.create(self.width / size.width, self.height / size.height)

    def div_components_in_place(self: S, size: Size) -> S:
        self.width /= size.width
        self.height /= size.height

        return self

    def swapped(self: S) -> S:
        return self.create(self.height, self.width)

    def swap(self: S) -> S:
        self.width, self.height = self.height, self.width

        return self

    def clone(self: S) -> S:
        return self.create(self.width, self.height)

    __mul__ = mul
    __imul__ = mul_in_place

    __truediv__ = div
    __itruediv__ = div_in_place

    def into_tuple(self) -> Tuple[float, float]:
        return (self.width, self.height)

    def round_tuple(self) -> Tuple[int, int]:
        return (round(self.width), round(self.height))


@define()
class Rectangle:
    origin: Point = field(factory=Point)
    size: Size = field(factory=Size)

    @classmethod
    def create(cls: Type[R], origin: Point, size: Size) -> R:
        return cls(origin, size)

    def clone(self: R) -> R:
        return self.create(self.origin.clone(), self.size.clone())

    @property
    def x(self) -> float:
        return self.origin.x

    @x.setter
    def x(self, x: float) -> None:
        self.origin.x = x

    @property
    def y(self) -> float:
        return self.origin.y

    @y.setter
    def y(self, y: float) -> None:
        self.origin.y = y

    @property
    def width(self) -> float:
        return self.size.width

    @width.setter
    def width(self, width: float) -> None:
        self.size.width = width

    @property
    def height(self) -> float:
        return self.size.height

    @height.setter
    def height(self, height: float) -> None:
        self.size.height = height

    @property
    def min_x(self) -> float:
        return self.x

    @property
    def mid_x(self) -> float:
        return self.x + self.width / 2

    @property
    def max_x(self) -> float:
        return self.x + self.width

    @property
    def min_y(self) -> float:
        return self.y

    @property
    def mid_y(self) -> float:
        return self.y + self.height / 2

    @property
    def max_y(self) -> float:
        return self.y + self.height

    @property
    def upper_left(self) -> Point:
        return self.origin.create(self.min_x, self.min_y)

    @property
    def upper_right(self) -> Point:
        return self.origin.create(self.max_x, self.min_y)

    @property
    def center(self) -> Point:
        return self.origin.create(self.mid_x, self.mid_y)

    @property
    def lower_left(self) -> Point:
        return self.origin.create(self.min_x, self.max_y)

    @property
    def lower_right(self) -> Point:
        return self.origin.create(self.max_x, self.max_y)

    def into_tuple(self) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        return (self.origin.into_tuple(), self.size.into_tuple())

    def round_tuple(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        return (self.origin.round_tuple(), self.size.round_tuple())

    def into_box(self) -> Tuple[float, float, float, float]:
        return (self.min_x, self.min_y, self.max_x, self.max_y)

    def round_box(self) -> Tuple[int, int, int, int]:
        return (round(self.min_x), round(self.min_y), round(self.max_x), round(self.max_y))
