from typing import Sequence, Tuple, Type, TypeVar
from typing_extensions import TypedDict

from attrs import define

from gd.image.geometry import Point, Size

__all__ = ("Layer", "Layers", "LayerData")

PART = "part"
POSITION = "position"
SCALE = "scale"
ROTATION = "rotation"
H_FLIPPED = "h_flipped"
V_FLIPPED = "v_flipped"

L = TypeVar("L", bound="Layer")


class LayerData(TypedDict):
    part: int
    position: Tuple[float, float]
    scale: Tuple[float, float]
    rotation: float
    h_flipped: bool
    v_flipped: bool


@define()
class Layer:
    part: int
    position: Point
    scale: Size
    rotation: float
    h_flipped: bool
    v_flipped: bool

    def is_h_flipped(self) -> bool:
        return self.h_flipped

    def is_v_flipped(self) -> bool:
        return self.v_flipped

    def into_dict(self) -> LayerData:
        return LayerData(
            part=self.part,
            position=self.position.into_tuple(),
            scale=self.scale.into_tuple(),
            rotation=self.rotation,
            h_flipped=self.is_h_flipped(),
            v_flipped=self.is_v_flipped(),
        )

    @classmethod
    def from_dict(cls: Type[L], layer_dict: LayerData) -> L:
        part = layer_dict[PART]
        x, y = layer_dict[POSITION]
        width, height = layer_dict[SCALE]
        rotation = layer_dict[ROTATION]
        h_flipped = layer_dict[H_FLIPPED]
        v_flipped = layer_dict[V_FLIPPED]

        return cls(
            part=part,
            position=Point(x, y),
            scale=Size(width, height),
            rotation=rotation,
            h_flipped=h_flipped,
            v_flipped=v_flipped,
        )


Layers = Sequence[Layer]
