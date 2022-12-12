from __future__ import annotations

from typing import TYPE_CHECKING, AsyncIterator, Iterable, Type, TypeVar

from attrs import define, field
from cattrs.gen import make_dict_unstructure_fn, override
from iters.async_iters import wrap_async_iter
from typing_extensions import TypedDict
from yarl import URL

from gd.binary import VERSION, BinaryReader, BinaryWriter
from gd.binary_utils import Reader, Writer
from gd.constants import DEFAULT_ENCODING, DEFAULT_ERRORS, DEFAULT_PAGE, DEFAULT_PAGES, UNKNOWN
from gd.entity import CONVERTER, Entity
from gd.enums import ByteOrder
from gd.string_utils import case_fold, clear_whitespace

if TYPE_CHECKING:
    from gd.song import Song

__all__ = ("Artist", "ArtistData")

A = TypeVar("A", bound="Artist")

ARTIST = "https://{}.newgrounds.com/"


class ArtistData(TypedDict):
    name: str


@define()
class Artist(Entity):
    """Represents artists on *Newgrounds*."""

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
    def from_json(cls: Type[A], data: ArtistData) -> A:  # type: ignore
        return CONVERTER.structure(data, cls)

    def to_json(self) -> ArtistData:  # type: ignore
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
        reader = Reader(binary)

        length = reader.read_u8(order)

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
        writer = Writer(binary)

        data = self.name.encode(encoding, errors)

        writer.write_u8(len(data), order)

        writer.write(data)

    @wrap_async_iter
    def get_songs_on_page(self, page: int = DEFAULT_PAGE) -> AsyncIterator[Song]:
        return self.client.get_newgrounds_artist_songs_on_page(self, page=page).unwrap()

    @wrap_async_iter
    def get_songs(self, pages: Iterable[int] = DEFAULT_PAGES) -> AsyncIterator[Song]:
        return self.client.get_newgrounds_artist_songs(self, pages=pages).unwrap()


CONVERTER.register_unstructure_hook(
    Artist,
    make_dict_unstructure_fn(
        Artist, CONVERTER, id=override(omit=True), maybe_client=override(omit=True)
    ),
)
