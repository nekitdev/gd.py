from __future__ import annotations

from typing import TYPE_CHECKING, BinaryIO, Optional

from attrs import define, field
from typing_extensions import Self
from yarl import URL

from gd.artist import Artist, ArtistData
from gd.binary import Binary
from gd.constants import (
    DEFAULT_CUSTOM,
    DEFAULT_FROM_NEWGROUNDS,
    DEFAULT_ID,
    DEFAULT_SIZE,
    DEFAULT_WITH_BAR,
    UNKNOWN,
)
from gd.converter import CONVERTER, register_unstructure_hook_omit_client
from gd.entity import Entity, EntityData
from gd.errors import MissingAccess
from gd.schema import SongReferenceSchema, SongSchema
from gd.schema_constants import NONE

if TYPE_CHECKING:
    from io import BufferedReader, BufferedWriter

    from typing_aliases import IntoPath

    from gd.models import SongModel
    from gd.schema import SongBuilder, SongReader, SongReferenceBuilder, SongReferenceReader

__all__ = ("Song", "SongReference")


class SongReferenceData(EntityData):
    custom: bool


@register_unstructure_hook_omit_client
@define()
class SongReference(Entity, Binary):
    custom: bool = field(eq=False)

    @classmethod
    def default(cls, id: int = DEFAULT_ID, custom: bool = DEFAULT_CUSTOM) -> Self:
        return cls(id=id, custom=custom)

    def is_custom(self) -> bool:
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


class SongData(EntityData):
    name: str
    artist: ArtistData
    size: float
    url: Optional[str]


EXPECTED_QUERY = "expected either `id` or `name`"
CAN_NOT_DOWNLOAD = "can not download an official song"
CAN_NOT_GET = "can not get an official song"
CAN_NOT_FIND_URL = "can not find download URL"


@register_unstructure_hook_omit_client
@define()
class Song(Entity, Binary):
    name: str = field(eq=False)

    artist: Artist = field(eq=False)

    size: float = field(default=DEFAULT_SIZE, eq=False)

    url: Optional[URL] = field(default=None, eq=False)

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

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
            builder.url.some = str(url)

        return builder

    @classmethod
    def from_model(cls, model: SongModel) -> Self:
        return cls(
            id=model.id,
            name=model.name,
            artist=Artist(
                id=model.artist_id,
                name=model.artist_name,
                verified=model.is_artist_verified(),
            ),
            size=model.size,
            url=model.url,
        )

    def __str__(self) -> str:
        return self.name or UNKNOWN

    async def get(self, from_newgrounds: bool = DEFAULT_FROM_NEWGROUNDS) -> Song:
        if from_newgrounds:
            return await self.client.get_newgrounds_song(self.id)

        else:
            return await self.client.get_song(self.id)

    async def update(self, from_newgrounds: bool = DEFAULT_FROM_NEWGROUNDS) -> Self:
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
        await self.client.http.download(file, await self.ensure_url(), with_bar=with_bar)

    async def download_bytes(self, with_bar: bool = DEFAULT_WITH_BAR) -> bytes:
        return await self.client.http.download_bytes(await self.ensure_url(), with_bar=with_bar)

    async def download_to(self, path: IntoPath, with_bar: bool = DEFAULT_WITH_BAR) -> None:
        await self.client.http.download_to(path, await self.ensure_url(), with_bar=with_bar)
