from __future__ import annotations

import gc
import json
from pathlib import Path
from typing import Optional, Type, TypeVar

from attrs import define, field
from typing_aliases import IntoPath, NormalError, StringMapping

try:
    from PIL.Image import Image
    from PIL.Image import open as open_image

except ImportError:
    pass

from gd.decorators import cache_by
from gd.image.sprite import Sprite, SpriteData, Sprites

__all__ = ("Sheet", "SheetData")

SheetData = StringMapping[SpriteData]

S = TypeVar("S", bound="Sheet")

NO_IMAGE = "`image` not attached to the sheet"
NO_DATA = "`data` not attached to the sheet"

IMAGE_PATH = "image_path"
DATA_PATH = "data_path"


@define()
class Sheet:
    image_path: Path = field()
    data_path: Path = field()

    image_unchecked: Optional[Image] = field(default=None, init=False, repr=False)
    data_unchecked: Optional[SheetData] = field(default=None, init=False, repr=False)

    loaded: bool = field(default=False, init=False)

    @property
    @cache_by(IMAGE_PATH, DATA_PATH)
    def sprites(self) -> Sprites:
        self.ensure_loaded()

        return {name: Sprite.from_data(sprite_data) for name, sprite_data in self.data.items()}

    @property
    def image(self) -> Image:
        image = self.image_unchecked

        if image is None:
            raise ValueError(NO_IMAGE)

        return image

    @image.setter
    def image(self, image: Image) -> None:
        self.image_unchecked = image

    @image.deleter
    def image(self) -> None:
        self.image_unchecked = None

    @property
    def data(self) -> SheetData:
        data = self.data_unchecked

        if data is None:
            raise ValueError(NO_DATA)

        return data

    @data.setter
    def data(self, data: SheetData) -> None:
        self.data_unchecked = data

    @data.deleter
    def data(self) -> None:
        self.data_unchecked = None

    def load(self) -> None:
        self.loaded = True

        try:
            self.image = open_image(self.image_path)

            with self.data_path.open() as file:
                self.data = json.load(file)

            self.image.load()

        except NormalError:
            self.loaded = False

            raise

    reload = load

    def unload(self) -> None:
        self.loaded = False

        del self.image
        del self.data

        gc.collect()

    def is_loaded(self) -> bool:
        return self.loaded

    def ensure_loaded(self) -> None:
        if not self.is_loaded():
            self.load()

    @classmethod
    def from_paths(cls: Type[S], image_path: IntoPath, data_path: IntoPath) -> S:
        return cls(Path(image_path), Path(data_path))
