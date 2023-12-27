from __future__ import annotations

from typing import TYPE_CHECKING, AsyncIterator, Iterable

from attrs import define, field
from iters.async_iters import wrap_async_iter
from yarl import URL

from gd.binary import Binary
from gd.constants import (
    DEFAULT_ARTIST_VERIFIED,
    DEFAULT_ID,
    DEFAULT_PAGE,
    DEFAULT_PAGES,
    EMPTY,
    UNKNOWN,
)
from gd.converter import CONVERTER, register_unstructure_hook_omit_client
from gd.entity import Entity, EntityData
from gd.schema import ArtistSchema
from gd.string_utils import case_fold, clear_whitespace

if TYPE_CHECKING:
    from io import BufferedReader, BufferedWriter

    from typing_extensions import Self

    from gd.models import ArtistModel
    from gd.schema import ArtistBuilder, ArtistReader
    from gd.songs import Song

__all__ = ("Artist", "ArtistData")

ARTIST_URL = "https://{}.newgrounds.com/"
artist_url = ARTIST_URL.format


class ArtistData(EntityData):
    name: str
    verified: bool


@register_unstructure_hook_omit_client
@define()
class Artist(Entity, Binary):
    name: str = field(eq=False)
    verified: bool = field(default=DEFAULT_ARTIST_VERIFIED, eq=False)

    @property
    def url(self) -> URL:
        return URL(artist_url(self.id_name))

    @property
    def id_name(self) -> str:
        return clear_whitespace(case_fold(self.name))

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

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

    def __str__(self) -> str:
        return self.name or UNKNOWN

    @classmethod
    def from_model(cls, model: ArtistModel, id: int = DEFAULT_ID) -> Self:
        return cls(id=id, name=model.name)

    @classmethod
    def from_data(cls, data: ArtistData) -> Self:  # type: ignore[override]
        return CONVERTER.structure(data, cls)

    def into_data(self) -> ArtistData:
        return CONVERTER.unstructure(self)  # type: ignore

    def is_verified(self) -> bool:
        return self.verified

    @wrap_async_iter
    def get_songs_on_page(self, page: int = DEFAULT_PAGE) -> AsyncIterator[Song]:
        return self.client.get_newgrounds_artist_songs_on_page(self, page=page).unwrap()

    @wrap_async_iter
    def get_songs(self, pages: Iterable[int] = DEFAULT_PAGES) -> AsyncIterator[Song]:
        return self.client.get_newgrounds_artist_songs(self, pages=pages).unwrap()
