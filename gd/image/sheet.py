from __future__ import annotations

import gc
import json
from pathlib import Path
from typing import Optional, Type, TypeVar

from attrs import define, field

try:
    from PIL.Image import Image  # type: ignore
    from PIL.Image import open as open_image  # type: ignore

except ImportError:
    pass

from gd.decorators import cache_by
from gd.image.sprite import Sprite, SpriteData, Sprites
from gd.typing import IntoPath, StringMapping

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

    def get_image(self) -> Image:
        result = self.image_unchecked

        if result is None:
            raise ValueError(NO_IMAGE)

        return result

    def set_image(self, image: Image) -> None:
        self.image_unchecked = image

    def delete_image(self) -> None:
        self.image_unchecked = None

    def free_image(self) -> None:
        del self.image

        gc.collect()  # force garbage collection

    image = property(get_image, set_image, delete_image)

    def get_data(self) -> SheetData:
        result = self.data_unchecked

        if result is None:
            raise ValueError(NO_DATA)

        return result

    def set_data(self, data: SheetData) -> None:
        self.data_unchecked = data

    def delete_data(self) -> None:
        self.data_unchecked = None

    data = property(get_data, set_data, delete_data)

    def load(self) -> None:
        self.loaded = True

        try:
            self.image = open_image(self.image_path)

            with self.data_path.open() as file:
                self.data = json.load(file)

            self.image.load()

        except Exception:
            self.loaded = False

            raise

    reload = load

    def unload(self) -> None:
        self.loaded = False

        self.free_image()
        self.delete_data()

    def is_loaded(self) -> bool:
        return self.loaded

    def ensure_loaded(self) -> None:
        if not self.loaded:
            self.load()

    @classmethod
    def from_paths(cls: Type[S], image_path: IntoPath, data_path: IntoPath) -> S:
        return cls(Path(image_path), Path(data_path))
