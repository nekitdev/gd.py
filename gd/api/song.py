from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from attrs import define
from yarl import URL

from gd.api.artist import ArtistAPI
from gd.constants import DEFAULT_ID, DEFAULT_PRIORITY, DEFAULT_SIZE, EMPTY
from gd.converter import dump_url
from gd.enums import InternalType
from gd.robtop_view import StringRobTopView

if TYPE_CHECKING:
    from typing_aliases import StringDict
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
SONG_URL = "10"


@define()
class SongAPI:
    id: int
    name: str
    artist: ArtistAPI
    size: float = DEFAULT_SIZE
    priority: int = DEFAULT_PRIORITY
    url: Optional[URL] = None

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

    @classmethod
    def default(cls, id: int = DEFAULT_ID, artist_id: int = DEFAULT_ID) -> Self:
        return cls(id=id, name=EMPTY, artist=ArtistAPI.default(artist_id))

    @classmethod
    def from_robtop_view(cls, view: StringRobTopView[Any]) -> Self:
        id = view.get_option(ID).unwrap_or(DEFAULT_ID)

        name = view.get_option(NAME).unwrap_or(EMPTY)

        artist_id = view.get_option(ARTIST_ID).unwrap_or(DEFAULT_ID)
        artist_name = view.get_option(ARTIST_NAME).unwrap_or(EMPTY)

        artist = ArtistAPI(id=artist_id, name=artist_name)

        size = view.get_option(SIZE).unwrap_or(DEFAULT_SIZE)

        priority = view.get_option(PRIORITY).unwrap_or(DEFAULT_PRIORITY)

        url = view.get_option(SONG_URL).filter(bool).map(URL).extract()

        return cls(
            id=id,
            name=name,
            artist=artist,
            size=size,
            priority=priority,
            url=url,
        )

    def to_robtop_data(self) -> StringDict[Any]:
        artist = self.artist

        url = self.url

        data = {
            INTERNAL_TYPE: InternalType.SONG.value,
            ID: self.id,
            NAME: self.name,
            ARTIST_ID: artist.id,
            ARTIST_NAME: artist.name,
            SIZE: self.size,
            PRIORITY: self.priority,
            SONG_URL: EMPTY if url is None else dump_url(url),
        }

        return data
