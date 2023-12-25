from attrs import define
from typing_extensions import Self

from gd.constants import DEFAULT_ID, EMPTY

__all__ = ("ArtistAPI",)


@define()
class ArtistAPI:
    id: int
    name: str

    @classmethod
    def default(cls, id: int = DEFAULT_ID, name: str = EMPTY) -> Self:
        return cls(id=id, name=name)
