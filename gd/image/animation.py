import json
from pathlib import Path
from typing import Optional, Sequence, Type, TypeVar

from attrs import define, field
from typing_aliases import IntoPath, NormalError, StringMapping

from gd.decorators import cache_by
from gd.image.layer import Layer, LayerData, Layers

__all__ = ("Animation", "Animations", "AnimationSheet", "AnimationSheetData", "Frame", "Frames")

AS = TypeVar("AS", bound="AnimationSheet")


@define()
class Frame:
    layers: Layers


Frames = Sequence[Frame]


@define()
class Animation:
    frames: Frames

    @property
    def single(self) -> Optional[Frame]:
        frames = self.frames

        if frames:
            head, *tail = frames

            if not tail:
                return head

        return None  # explicit


Animations = StringMapping[Animation]

FrameData = Sequence[LayerData]
AnimationData = Sequence[FrameData]
AnimationSheetData = StringMapping[AnimationData]

NO_DATA = "`data` not attached to the animation container"

PATH = "path"


@define()
class AnimationSheet:
    path: Path = field()

    data_unchecked: Optional[AnimationSheetData] = field(default=None, init=False, repr=False)

    loaded: bool = field(default=False, init=False)

    @property
    @cache_by(PATH)
    def animations(self) -> Animations:
        self.ensure_loaded()

        return {
            name: Animation(
                [
                    Frame([Layer.from_data(layer_data) for layer_data in frame_data])
                    for frame_data in animation_data
                ]
            )
            for name, animation_data in self.data.items()
        }

    @property
    def data(self) -> AnimationSheetData:
        result = self.data_unchecked

        if result is None:
            raise ValueError(NO_DATA)

        return result

    @data.setter
    def data(self, data: AnimationSheetData) -> None:
        self.data_unchecked = data

    @data.deleter
    def data(self) -> None:
        self.data_unchecked = None

    def load(self) -> None:
        self.loaded = True

        try:
            with self.path.open() as file:
                self.data = json.load(file)

        except NormalError:
            self.loaded = False

            raise

    reload = load

    def unload(self) -> None:
        self.loaded = False

        del self.data

    def is_loaded(self) -> bool:
        return self.loaded

    def ensure_loaded(self) -> None:
        if not self.is_loaded():
            self.load()

    @classmethod
    def from_path(cls: Type[AS], into_path: IntoPath) -> AS:
        return cls(Path(into_path))
