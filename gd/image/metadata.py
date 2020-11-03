from attr import attrib, dataclass

from gd.image.geometry import Size

__all__ = ("Metadata",)


@dataclass
class Metadata:
    format: int = attrib()
    pixel_format: str = attrib()
    premultiply_alpha: bool = attrib()
    file_name: str = attrib()
    size: Size = attrib()

    def __str__(self) -> str:
        return self.file_name
