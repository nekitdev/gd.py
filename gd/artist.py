from __future__ import annotations

from enum import Flag
from typing import TYPE_CHECKING, AsyncIterator, Iterable, Type, TypeVar

from attrs import define, field
from iters.async_iters import wrap_async_iter
from yarl import URL

from gd.binary import VERSION, BinaryReader, BinaryWriter
from gd.binary_utils import Reader, Writer
from gd.constants import (
    DEFAULT_ARTIST_VERIFIED,
    DEFAULT_ENCODING,
    DEFAULT_ERRORS,
    DEFAULT_ID,
    DEFAULT_PAGE,
    DEFAULT_PAGES,
    EMPTY,
    UNKNOWN,
)
from gd.converter import CONVERTER, register_unstructure_hook_omit_client
from gd.entity import Entity, EntityData
from gd.enums import ByteOrder
from gd.models import ArtistModel
from gd.string_utils import case_fold, clear_whitespace

if TYPE_CHECKING:
    from gd.song import Song

__all__ = ("Artist", "ArtistData")

A = TypeVar("A", bound="Artist")

ARTIST_URL = "https://{}.newgrounds.com/"
artist_url = ARTIST_URL.format


class ArtistFlag(Flag):
    SIMPLE = 0

    VERIFIED = 1 << 0
    ID = 1 << 1

    def is_verified(self) -> bool:
        return type(self).VERIFIED in self

    def has_id(self) -> bool:
        return type(self).ID in self


class ArtistData(EntityData):
    name: str
    verified: bool


@register_unstructure_hook_omit_client
@define()
class Artist(Entity):
    """Represents artists on *Newgrounds*.

    Binary:
        ```rust
        const VERIFIED_BIT: u8 = 1 << 0;
        const HAS_ID_BIT: u8 = 1 << 1;

        struct Artist {
            value: u8,  // contains `verified` and `has_id`
            id: Option<u32>,  // if `has_id`
            name_length: u8,
            name: [u8; name_length],  // utf-8 string
        }
        ```
    """

    name: str = field(eq=False)
    verified: bool = field(default=DEFAULT_ARTIST_VERIFIED, eq=False)

    @property
    def url(self) -> URL:
        return URL(artist_url(self.id_name))

    @property
    def id_name(self) -> str:
        return clear_whitespace(case_fold(self.name))

    @classmethod
    def default(cls: Type[A], id: int = DEFAULT_ID) -> A:
        return cls(id=id, name=EMPTY)

    @classmethod
    def name_only(cls: Type[A], name: str) -> A:
        return cls(id=DEFAULT_ID, name=name)

    def __hash__(self) -> int:
        return hash(type(self)) ^ hash(self.id_name)

    def __str__(self) -> str:
        return self.name or UNKNOWN

    @classmethod
    def from_model(cls: Type[A], model: ArtistModel, id: int = DEFAULT_ID) -> A:
        return cls(id=id, name=model.name)

    @classmethod
    def from_data(cls: Type[A], data: ArtistData) -> A:  # type: ignore
        return CONVERTER.structure(data, cls)

    def into_data(self) -> ArtistData:
        return CONVERTER.unstructure(self)  # type: ignore

    @classmethod
    def from_binary(
        cls: Type[A],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
    ) -> A:
        reader = Reader(binary, order)

        artist_flag_value = reader.read_u8()

        artist_flag = ArtistFlag(artist_flag_value)

        if artist_flag.has_id():
            id = reader.read_u32()

        else:
            id = DEFAULT_ID

        name_length = reader.read_u8()

        data = reader.read(name_length)

        name = data.decode(encoding, errors)

        verified = artist_flag.is_verified()

        return cls(id=id, name=name, verified=verified)

    def to_binary(
        self,
        binary: BinaryWriter,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
    ) -> None:
        writer = Writer(binary, order)

        artist_flag = ArtistFlag.SIMPLE

        if self.is_verified():
            artist_flag |= ArtistFlag.VERIFIED

        id = self.id

        if id:
            artist_flag |= ArtistFlag.ID

        writer.write_u8(artist_flag.value)

        if id:
            writer.write_u32(id)

        data = self.name.encode(encoding, errors)

        writer.write_u8(len(data))

        writer.write(data)

    def is_verified(self) -> bool:
        return self.verified

    @wrap_async_iter
    def get_songs_on_page(self, page: int = DEFAULT_PAGE) -> AsyncIterator[Song]:
        return self.client.get_newgrounds_artist_songs_on_page(self, page=page).unwrap()

    @wrap_async_iter
    def get_songs(self, pages: Iterable[int] = DEFAULT_PAGES) -> AsyncIterator[Song]:
        return self.client.get_newgrounds_artist_songs(self, pages=pages).unwrap()
