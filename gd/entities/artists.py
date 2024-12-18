from __future__ import annotations

from io import BufferedReader, BufferedWriter
from typing import TYPE_CHECKING, AsyncIterator, Iterable

from attrs import define, field
from iters.async_iters import wrap_async_iter
from typing_extensions import Self
from yarl import URL

from gd.binary.protocols import Binary
from gd.defaults.entities.artists import DEFAULT_ARTIST_VERIFIED
from gd.internals.entities.artists import InternalArtist
from gd.defaults.entities.core import DEFAULT_ID
from gd.defaults.pages import DEFAULT_PAGE, DEFAULT_PAGES
from gd.converters import CONVERTER, register_unstructure_hook_omit_client
from gd.entities.core import Entity, EntityData
from gd.schema.core import ArtistSchema
from gd.strings.case_folding import case_fold
from gd.strings.constants import EMPTY
from gd.strings.removing import remove_whitespace

if TYPE_CHECKING:
    from gd.schema.core import ArtistBuilder, ArtistReader

__all__ = ("Artist", "ArtistData")

ARTIST_URL = "https://{}.newgrounds.com/"
artist_url = ARTIST_URL.format


class ArtistData(EntityData):
    name: str
    verified: bool


UNNAMED = "unnamed"


@register_unstructure_hook_omit_client
@define()
class Artist(Entity, Binary):
    """Represents artists."""

    name: str = field(eq=False)
    """The name of the artist."""

    verified: bool = field(default=DEFAULT_ARTIST_VERIFIED, eq=False)
    """Whether the artist is verified."""

    @property
    def url(self) -> URL:
        """The URL to the artist's Newgrounds profile."""
        return URL(artist_url(self.id_name))

    @property
    def id_name(self) -> str:
        """The normalized name of the artist."""
        return remove_whitespace(case_fold(self.name))

    @classmethod
    def default(cls, id: int = DEFAULT_ID) -> Self:
        return cls(id=id, name=EMPTY)

    @classmethod
    def name_only(cls, name: str) -> Self:
        return cls(id=DEFAULT_ID, name=name)

    @classmethod
    def from_binary(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(ArtistSchema.read(binary))

    @classmethod
    def from_binary_packed(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(ArtistSchema.read_packed(binary))

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        with ArtistSchema.from_bytes(data) as reader:
            return cls.from_reader(reader)

    @classmethod
    def from_bytes_packed(cls, data: bytes) -> Self:
        return cls.from_reader(ArtistSchema.from_bytes_packed(data))

    def to_binary(self, binary: BufferedWriter) -> None:
        self.to_builder().write(binary)

    def to_binary_packed(self, binary: BufferedWriter) -> None:
        self.to_builder().write_packed(binary)

    def to_bytes(self) -> bytes:
        return self.to_builder().to_bytes()

    def to_bytes_packed(self) -> bytes:
        return self.to_builder().to_bytes_packed()

    @classmethod
    def from_reader(cls, reader: ArtistReader) -> Self:
        return cls(id=reader.id, name=reader.name, verified=reader.verified)

    def to_builder(self) -> ArtistBuilder:
        builder = ArtistSchema.new_message()

        builder.id = self.id
        builder.name = self.name
        builder.verified = self.verified

        return builder

    def __str__(self) -> str:
        return self.name or UNNAMED

    @classmethod
    def from_internal(cls, internal: InternalArtist, id: int = DEFAULT_ID) -> Self:
        return cls(id=id, name=internal.name)

    @classmethod
    def from_data(cls, data: ArtistData) -> Self:  # type: ignore[override]
        return CONVERTER.structure(data, cls)

    def into_data(self) -> ArtistData:
        return CONVERTER.unstructure(self)  # type: ignore[no-any-return]

    def is_verified(self) -> bool:
        """Checks if the artist is verified.

        Returns:
            Whether the artist is verified.
        """
        return self.verified

    @wrap_async_iter
    def get_songs_on_page(self, page: int = DEFAULT_PAGE) -> AsyncIterator[Song]:
        """Fetches songs by the artist from Newgrounds on `page`.

        Arguments:
            page: The page to fetch.

        Returns:
            An async iterator over the fetched songs.
        """
        return self.client_expected.get_newgrounds_artist_songs_on_page(self, page=page).unwrap()

    @wrap_async_iter
    def get_songs(self, pages: Iterable[int] = DEFAULT_PAGES) -> AsyncIterator[Song]:
        """Fetches songs by the artist from Newgrounds on `pages`.

        Arguments:
            pages: The pages to fetch.

        Returns:
            An async iterator over the fetched songs.
        """
        return self.client_expected.get_newgrounds_artist_songs(self, pages=pages).unwrap()


from gd.entities.songs import Song
