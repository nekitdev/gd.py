from typing import Optional

from attrs import define

__all__ = ("Folder",)

UNNAMED_FOLDER = "unnamed folder (ID: `{}`)"
unnamed_folder = UNNAMED_FOLDER.format

FOLDER = "{} (ID: `{}`)"
folder = FOLDER.format


@define()
class Folder:
    id: int
    name: Optional[str] = None

    def __str__(self) -> str:
        id = self.id
        name = self.name

        return unnamed_folder(id) if name is None else folder(name, id)
