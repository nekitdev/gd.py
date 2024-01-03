from __future__ import annotations

import gc
import json
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

from attrs import Attribute, define, field
from typing_aliases import IntoPath, NormalError, StringDict, StringMapping

try:
    from PIL.Image import Image
    from PIL.Image import open as open_image

except ImportError:
    pass

from gd.assets import DATA_SUFFIX, IMAGE_SUFFIX
from gd.decorators import cache_by
from gd.image.icon import IconReference
from gd.image.sprite import Sprite, SpriteData, Sprites

if TYPE_CHECKING:
    from typing_extensions import Self

__all__ = ("Sheet", "SheetData", "SheetContainer", "IconSheets")

SheetData = StringMapping[SpriteData]

RGBA = "RGBA"

NO_IMAGE = "`image` not attached to the sheet"
NO_DATA = "`data` not attached to the sheet"

PATH_DOES_NOT_EXIST = "path `{}` does not exist"
path_does_not_exist = PATH_DOES_NOT_EXIST.format

IMAGE_PATH = "image_path"
DATA_PATH = "data_path"


@define()
class Sheet:
    image_path: Path = field()
    data_path: Path = field()

    image_unchecked: Optional[Image] = field(default=None, init=False, repr=False)
    data_unchecked: Optional[SheetData] = field(default=None, init=False, repr=False)

    loaded: bool = field(default=False, init=False)

    @image_path.validator
    def check_image_path(self, attribute: Attribute[Path], value: Path) -> None:
        if not value.exists():
            raise FileNotFoundError(path_does_not_exist(value.as_posix()))

    @data_path.validator
    def check_data_path(self, attribute: Attribute[Path], value: Path) -> None:
        if not value.exists():
            raise FileNotFoundError(path_does_not_exist(value.as_posix()))

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
            self.image = open_image(self.image_path).convert(RGBA)

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
    def from_paths(cls, image_path: IntoPath, data_path: IntoPath) -> Self:
        return cls(Path(image_path), Path(data_path))


Sheets = List[Sheet]


class SheetContainer(StringDict[Sheet]):
    def add(self, name: str, image_path: IntoPath, data_path: IntoPath) -> Sheet:
        if name in self:
            return self[name]

        sheet = Sheet.from_paths(image_path, data_path)

        self[name] = sheet

        return sheet

    def copy(self) -> Self:
        return type(self)(self)


@define()
class IconSheets:
    path: Path = field()
    container: SheetContainer = field(factory=SheetContainer, init=False, repr=False)

    @path.validator
    def check_path(self, attribute: Attribute[Path], value: Path) -> None:
        if not value.exists():
            raise FileNotFoundError(path_does_not_exist(value.as_posix()))

    @property
    def sheets(self) -> Sheets:
        return list(self.container.values())

    def is_loaded(self) -> bool:
        return all(sheet.is_loaded() for sheet in self.sheets)

    def ensure_loaded(self) -> None:
        for sheet in self.sheets:
            sheet.ensure_loaded()

    def load(self) -> None:
        for sheet in self.sheets:
            sheet.load()

    reload = load

    def unload(self) -> None:
        for sheet in self.sheets:
            sheet.unload()

    @classmethod
    def from_path(cls, path: IntoPath) -> Self:
        return cls(Path(path))

    def add(
        self, name: str, image_suffix: str = IMAGE_SUFFIX, data_suffix: str = DATA_SUFFIX
    ) -> Sheet:
        simple_path = self.path / name

        image_path = simple_path.with_suffix(image_suffix)
        data_path = simple_path.with_suffix(data_suffix)

        return self.container.add(name, image_path, data_path)

    def add_reference(self, reference: IconReference) -> Sheet:
        return self.add(reference.name)
