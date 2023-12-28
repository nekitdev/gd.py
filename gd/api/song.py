from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from attrs import define
from yarl import URL

from gd.api.artist import ArtistAPI
from gd.constants import DEFAULT_ID, DEFAULT_PRIORITY, DEFAULT_SIZE, EMPTY
from gd.enums import InternalType

if TYPE_CHECKING:
    from typing_aliases import StringDict, StringMapping
    from typing_extensions import Self


__all__ = ("SongAPI",)

INTERNAL_TYPE = "kCEK"

ID = "1"
NAME = "2"
ARTIST_ID = "3"
ARTIST_NAME = "4"
SIZE = "5"
# not using YouTube-related things here intentionally ~ nekit
PRIORITY = "9"
DOWNLOAD_URL = "10"


@define()
class SongAPI:
    id: int
    name: str
    artist: ArtistAPI
    size: float = DEFAULT_SIZE
    priority: int = DEFAULT_PRIORITY
    download_url: Optional[URL] = None

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

    @classmethod
    def default(cls, id: int = DEFAULT_ID, artist_id: int = DEFAULT_ID) -> Self:
        return cls(id=id, name=EMPTY, artist=ArtistAPI.default(artist_id))

    @classmethod
    def from_robtop_data(cls, data: StringMapping[Any]) -> Self:  # type: ignore
        id = data.get(ID, DEFAULT_ID)
        name = data.get(NAME, EMPTY)
        artist_id = data.get(ARTIST_ID, DEFAULT_ID)
        artist_name = data.get(ARTIST_NAME, EMPTY)
        size = data.get(SIZE, DEFAULT_SIZE)
        priority = data.get(PRIORITY, DEFAULT_PRIORITY)

        download_url_string = data.get(DOWNLOAD_URL, EMPTY)

        download_url = URL(download_url_string) if download_url_string else None

        return cls(
            id=id,
            name=name,
            artist=ArtistAPI(id=artist_id, name=artist_name),
            size=size,
            priority=priority,
            download_url=download_url,
        )

    def to_robtop_data(self) -> StringDict[Any]:
        artist = self.artist

        download_url = self.download_url

        data = {
            INTERNAL_TYPE: InternalType.SONG.value,
            ID: self.id,
            NAME: self.name,
            ARTIST_ID: artist.id,
            ARTIST_NAME: artist.name,
            SIZE: self.size,
            PRIORITY: self.priority,
            DOWNLOAD_URL: EMPTY if download_url is None else str(download_url),
        }

        return data
