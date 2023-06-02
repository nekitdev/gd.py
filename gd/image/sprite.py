from __future__ import annotations

from typing import Tuple, Type, TypeVar

from attrs import field, frozen
from typing_aliases import StringMapping
from typing_extensions import Literal, NotRequired, TypedDict

from gd.image.geometry import Point, Rectangle, Size

__all__ = ("Sprite", "Sprites", "SpriteData")

SIZE: Literal["size"] = "size"
OFFSET: Literal["offset"] = "offset"
LOCATION: Literal["location"] = "location"
ROTATED: Literal["rotated"] = "rotated"

S = TypeVar("S", bound="Sprite")


class SpriteData(TypedDict):
    size: Tuple[float, float]
    offset: Tuple[float, float]
    location: Tuple[float, float]
    rotated: NotRequired[bool]


@frozen()
class Sprite:
    size: Size = field(factory=Size)
    offset: Point = field(factory=Point)
    location: Point = field(factory=Point)
    rotated: bool = field(default=False)

    def is_rotated(self) -> bool:
        return self.rotated

    @property
    def rectangle(self) -> Rectangle:
        location = self.location
        size = self.size

        if self.is_rotated():
            size = size.swapped()

        return Rectangle(location, size)

    @property
    def box(self) -> Tuple[int, int, int, int]:  # for image cropping
        return self.rectangle.round_box()

    def into_data(self) -> SpriteData:
        return SpriteData(
            size=self.size.into_tuple(),
            offset=self.offset.into_tuple(),
            location=self.location.into_tuple(),
            rotated=self.is_rotated(),
        )

    @classmethod
    def from_data(cls: Type[S], sprite_dict: SpriteData) -> S:
        width, height = sprite_dict[SIZE]
        offset_x, offset_y = sprite_dict[OFFSET]
        x, y = sprite_dict[LOCATION]

        rotated = bool(sprite_dict.get(ROTATED))

        return cls(
            size=Size(width, height),
            offset=Point(offset_x, offset_y),
            location=Point(x, y),
            rotated=rotated,
        )


Sprites = StringMapping[Sprite]  # name -> sprite
