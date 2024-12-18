from __future__ import annotations

from io import BufferedReader, BufferedWriter
from typing import TYPE_CHECKING, BinaryIO, Optional

from attrs import define, field
from typing_aliases import IntoPath
from typing_extensions import Self
from yarl import URL

from gd.binary.protocols import Binary
from gd.converters import CONVERTER, register_unstructure_hook_omit_client, unstructure_url
from gd.entities.artists import Artist, ArtistData
from gd.entities.core import Entity, EntityData
from gd.defaults.entities.core import DEFAULT_ID
from gd.defaults.entities.songs import (
    DEFAULT_CUSTOM,
    DEFAULT_FROM_NEWGROUNDS,
    DEFAULT_SIZE,
    DEFAULT_WITH_BAR,
)
from gd.internals.entities.songs import InternalSong
from gd.errors import MissingAccess
from gd.schema.constants import NONE
from gd.schema.core import SongReferenceSchema, SongSchema

if TYPE_CHECKING:
    from gd.schema.core import SongBuilder, SongReader, SongReferenceBuilder, SongReferenceReader

__all__ = ("Song", "SongData", "SongReference", "SongReferenceData")


CUSTOM_SONG_REFERENCE = "song reference (custom, ID: `{}`)"
custom_song_reference = CUSTOM_SONG_REFERENCE.format

SONG_REFERENCE = "song reference (ID: `{}`)"
song_reference = SONG_REFERENCE.format


class SongReferenceData(EntityData):
    custom: bool


@register_unstructure_hook_omit_client
@define()
class SongReference(Entity, Binary):
    """Represents song references."""

    custom: bool = field(eq=False)
    """Whether the song is custom."""

    @classmethod
    def default(cls, id: int = DEFAULT_ID, custom: bool = DEFAULT_CUSTOM) -> Self:
        return cls(id=id, custom=custom)

    def is_custom(self) -> bool:
        """Checks whether the song is custom.

        Returns:
            Whether the song is custom.
        """
        return self.custom

    @classmethod
    def from_data(cls, data: SongReferenceData) -> Self:  # type: ignore
        return CONVERTER.structure(data, cls)

    def into_data(self) -> SongReferenceData:
        return CONVERTER.unstructure(self)  # type: ignore

    @classmethod
    def from_binary(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(SongReferenceSchema.read(binary))

    @classmethod
    def from_binary_packed(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(SongReferenceSchema.read_packed(binary))

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        with SongReferenceSchema.from_bytes(data) as reader:
            return cls.from_reader(reader)

    @classmethod
    def from_bytes_packed(cls, data: bytes) -> Self:
        return cls.from_reader(SongReferenceSchema.from_bytes_packed(data))

    def to_binary(self, binary: BufferedWriter) -> None:
        self.to_builder().write(binary)

    def to_binary_packed(self, binary: BufferedWriter) -> None:
        self.to_builder().write_packed(binary)

    def to_bytes(self) -> bytes:
        return self.to_builder().to_bytes()

    def to_bytes_packed(self) -> bytes:
        return self.to_builder().to_bytes_packed()

    @classmethod
    def from_reader(cls, reader: SongReferenceReader) -> Self:
        return cls(id=reader.id, custom=reader.custom)

    def to_builder(self) -> SongReferenceBuilder:
        builder = SongReferenceSchema.new_message()

        builder.id = self.id
        builder.custom = self.is_custom()

        return builder

    def __str__(self) -> str:
        song_id = self.id

        return custom_song_reference(song_id) if self.is_custom() else song_reference(song_id)


class SongData(EntityData):
    name: str
    artist: ArtistData
    size: float
    url: Optional[str]


UNNAMED = "unnamed"

SONG = "{} by {}"
song = SONG.format

EXPECTED_QUERY = "expected either `id` or `name`"
CAN_NOT_FIND_URL = "can not find download URL"


@register_unstructure_hook_omit_client
@define()
class Song(Entity, Binary):
    """Represents songs."""

    name: str = field(eq=False)
    """The name of the song."""

    artist: Artist = field(eq=False)
    """The artist of the song."""

    size: float = field(default=DEFAULT_SIZE, eq=False)
    """The size of the song."""

    url: Optional[URL] = field(default=None, eq=False)
    """The URL to the song."""

    @classmethod
    def from_data(cls, data: SongData) -> Self:  # type: ignore
        return CONVERTER.structure(data, cls)

    def into_data(self) -> SongData:
        return CONVERTER.unstructure(self)  # type: ignore

    @classmethod
    def from_binary(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(SongSchema.read(binary))

    @classmethod
    def from_binary_packed(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(SongSchema.read_packed(binary))

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        with SongSchema.from_bytes(data) as reader:
            return cls.from_reader(reader)

    @classmethod
    def from_bytes_packed(cls, data: bytes) -> Self:
        return cls.from_reader(SongSchema.from_bytes_packed(data))

    def to_binary(self, binary: BufferedWriter) -> None:
        self.to_builder().write(binary)

    def to_binary_packed(self, binary: BufferedWriter) -> None:
        self.to_builder().write_packed(binary)

    def to_bytes(self) -> bytes:
        return self.to_builder().to_bytes()

    def to_bytes_packed(self) -> bytes:
        return self.to_builder().to_bytes_packed()

    @classmethod
    def from_reader(cls, reader: SongReader) -> Self:
        url_option = reader.url

        if url_option.which() == NONE:
            url = None

        else:
            url = URL(url_option.some)

        return cls(
            id=reader.id,
            name=reader.name,
            artist=Artist.from_reader(reader.artist),
            size=reader.size,
            url=url,
        )

    def to_builder(self) -> SongBuilder:
        builder = SongSchema.new_message()

        builder.id = self.id
        builder.name = self.name
        builder.artist = self.artist.to_builder()
        builder.size = self.size

        url = self.url

        if url is None:
            builder.url.none = None

        else:
            builder.url.some = unstructure_url(url)

        return builder

    @classmethod
    def from_internal(cls, internal: InternalSong) -> Self:
        return cls(
            id=internal.id,
            name=internal.name,
            artist=Artist(
                id=internal.artist_id,
                name=internal.artist_name,
                verified=internal.is_artist_verified(),
            ),
            size=internal.size,
            url=internal.url,
        )

    def __str__(self) -> str:
        return song(self.name or UNNAMED, self.artist)

    async def get(self, from_newgrounds: bool = DEFAULT_FROM_NEWGROUNDS) -> Song:
        """Fetches the song either from Newgrounds or Geometry Dash servers.

        Arguments:
            from_newgrounds: Whether to fetch the song from Newgrounds.

        Returns:
            The fetched song.
        """
        if from_newgrounds:
            return await self.client_expected.get_newgrounds_song(self.id)

        else:
            return await self.client_expected.get_song(self.id)

    async def update(self, from_newgrounds: bool = DEFAULT_FROM_NEWGROUNDS) -> Self:
        """Updates the song.

        Arguments:
            from_newgrounds: Whether to fetch the song from Newgrounds.

        Returns:
            The updated song.
        """
        return self.update_from(await self.get(from_newgrounds=from_newgrounds))

    async def ensure_url(self) -> URL:
        url = self.url

        if url is None:
            await self.update(from_newgrounds=True)

        url = self.url

        if url is None:
            raise MissingAccess(CAN_NOT_FIND_URL)

        return url

    async def download(self, file: BinaryIO, with_bar: bool = DEFAULT_WITH_BAR) -> None:
        """Downloads the song to the `file`.

        Arguments:
            file: The file to download the song to.
            with_bar: Whether to display the progress bar.
        """
        await self.client_expected.http.download(file, await self.ensure_url(), with_bar=with_bar)

    async def download_bytes(self, with_bar: bool = DEFAULT_WITH_BAR) -> bytes:
        """Downloads the song as [`bytes`][bytes].

        Arguments:
            with_bar: Whether to display the progress bar.

        Returns:
            The song as bytes.
        """
        return await self.client_expected.http.download_bytes(
            await self.ensure_url(), with_bar=with_bar
        )

    async def download_to(self, path: IntoPath, with_bar: bool = DEFAULT_WITH_BAR) -> None:
        """Downloads the song to the `path`.

        Arguments:
            path: The path to download the song to.
            with_bar: Whether to display the progress bar.
        """
        await self.client_expected.http.download_to(
            path, await self.ensure_url(), with_bar=with_bar
        )
