from typing import Optional

from attrs import define

__all__ = ("Folder",)


@define()
class Folder:
    id: int
    name: Optional[str] = None

    def __hash__(self) -> int:
        return self.id
