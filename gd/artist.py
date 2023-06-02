from __future__ import annotations

from typing import TYPE_CHECKING, AsyncIterator, Iterable, Type, TypeVar

from attrs import define, field
from iters.async_iters import wrap_async_iter
from typing_extensions import TypedDict as Data
from yarl import URL

from gd.binary import VERSION, BinaryReader, BinaryWriter
from gd.binary_utils import Reader, Writer
from gd.constants import DEFAULT_ENCODING, DEFAULT_ERRORS, DEFAULT_PAGE, DEFAULT_PAGES, UNKNOWN
from gd.converter import CONVERTER, register_unstructure_hook_omit_id_and_client
from gd.entity import Entity
from gd.enums import ByteOrder
from gd.models import ArtistModel
from gd.string_utils import case_fold, clear_whitespace

if TYPE_CHECKING:
    from gd.song import Song

__all__ = ("Artist", "ArtistData")

A = TypeVar("A", bound="Artist")

ARTIST = "https://{}.newgrounds.com/"


class ArtistData(Data):
    name: str


@register_unstructure_hook_omit_id_and_client
@define()
class Artist(Entity):
    """Represents artists on *Newgrounds*.

    Binary:
        ```rust
        struct Artist {
            name_length: u8,
            name: [u8; name_length],  // utf-8 string
        }
        ```
    """

    name: str = field(eq=False)

    id: int = field(repr=False, init=False)

    @id.default
    def default_id(self) -> int:
        return hash(self.id_name)

    @property
    def url(self) -> URL:
        return URL(ARTIST.format(self.id_name))

    @property
    def id_name(self) -> str:
        return clear_whitespace(case_fold(self.name))

    @classmethod
    def default(cls: Type[A]) -> A:
        return cls(name=UNKNOWN)

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

    def __str__(self) -> str:
        return self.name

    @classmethod
    def from_model(cls: Type[A], model: ArtistModel) -> A:
        return cls(name=model.name)

    @classmethod
    def from_data(cls: Type[A], data: ArtistData) -> A:  # type: ignore
        return CONVERTER.structure(data, cls)

    def into_data(self) -> ArtistData:  # type: ignore
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

        length = reader.read_u8()

        data = reader.read(length)

        name = data.decode(encoding, errors)

        return cls(name=name)

    def to_binary(
        self,
        binary: BinaryWriter,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
    ) -> None:
        writer = Writer(binary, order)

        data = self.name.encode(encoding, errors)

        writer.write_u8(len(data))

        writer.write(data)

    @wrap_async_iter
    def get_songs_on_page(self, page: int = DEFAULT_PAGE) -> AsyncIterator[Song]:
        return self.client.get_newgrounds_artist_songs_on_page(self, page=page).unwrap()

    @wrap_async_iter
    def get_songs(self, pages: Iterable[int] = DEFAULT_PAGES) -> AsyncIterator[Song]:
        return self.client.get_newgrounds_artist_songs(self, pages=pages).unwrap()
