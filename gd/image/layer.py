from typing import Sequence, Tuple, Type, TypeVar

from attrs import define
from typing_extensions import Literal, TypedDict

from gd.image.geometry import Point, Size

__all__ = ("Layer", "Layers", "LayerData")

PART: Literal["part"] = "part"
POSITION: Literal["position"] = "position"
SCALE: Literal["scale"] = "scale"
ROTATION: Literal["rotation"] = "rotation"
H_FLIPPED: Literal["h_flipped"] = "h_flipped"
V_FLIPPED: Literal["v_flipped"] = "v_flipped"

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

    def into_data(self) -> LayerData:
        return LayerData(
            part=self.part,
            position=self.position.into_tuple(),
            scale=self.scale.into_tuple(),
            rotation=self.rotation,
            h_flipped=self.is_h_flipped(),
            v_flipped=self.is_v_flipped(),
        )

    @classmethod
    def from_data(cls: Type[L], layer_data: LayerData) -> L:
        part = layer_data[PART]
        x, y = layer_data[POSITION]
        width, height = layer_data[SCALE]
        rotation = layer_data[ROTATION]
        h_flipped = layer_data[H_FLIPPED]
        v_flipped = layer_data[V_FLIPPED]

        return cls(
            part=part,
            position=Point(x, y),
            scale=Size(width, height),
            rotation=rotation,
            h_flipped=h_flipped,
            v_flipped=v_flipped,
        )


Layers = Sequence[Layer]
