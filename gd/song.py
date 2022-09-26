from __future__ import annotations

from typing import BinaryIO, Optional, Type, TypeVar

from attrs import define
from iters import iter
from yarl import URL

from gd.artist import Artist
from gd.binary import VERSION
from gd.binary_utils import Reader, Writer
from gd.constants import (
    DEFAULT_ENCODING,
    DEFAULT_ERRORS,
    DEFAULT_FROM_NEWGROUNDS,
    DEFAULT_ID,
    DEFAULT_RETURN_DEFAULT,
    DEFAULT_SERVER_STYLE,
    DEFAULT_SIZE,
    DEFAULT_WITH_BAR,
    EMPTY,
    UNKNOWN,
)
from gd.entity import Entity
from gd.enums import ByteOrder
from gd.errors import MissingAccess
from gd.http import NEWGROUNDS_SONG
from gd.models import SongModel
from gd.official_songs import (
    OFFICIAL_CLIENT_SONGS,
    OFFICIAL_SERVER_SONGS,
    OfficialSong,
    default_official_song,
)
from gd.typing import IntoPath, Predicate

__all__ = ("Song",)


def by_id(id: int) -> Predicate[OfficialSong]:
    def predicate(offical_song: OfficialSong) -> bool:
        return offical_song.id == id

    return predicate


def by_name(name: str) -> Predicate[OfficialSong]:
    def predicate(offical_song: OfficialSong) -> bool:
        return offical_song.name == name

    return predicate


S = TypeVar("S", bound="Song")

EXPECTED_QUERY = "expected either `id` or `name` query"
CAN_NOT_FIND_SONG = "can not find an official song by given query"
CAN_NOT_DOWNLOAD = "can not download an official song"
CAN_NOT_FIND_URL = "can not find download URL"

WRITE_BINARY = "wb"

DEFAULT_CUSTOM = True

CUSTOM_BIT = 0b00000001


@define()
class Song(Entity):
    """Represents *Geometry Dash* and *Newgrounds* songs."""

    name: str
    artist: Artist
    size: float = DEFAULT_SIZE

    custom: bool = DEFAULT_CUSTOM

    download_url: Optional[URL] = None

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

    @property
    def url(self) -> URL:
        return URL(NEWGROUNDS_SONG.format(self.id))

    @classmethod
    def from_binary(
        cls: Type[S],
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
    ) -> S:
        custom_bit = CUSTOM_BIT

        reader = Reader(binary)

        id = reader.read_u32(order)

        name_length = reader.read_u8(order)

        name = reader.read(name_length).decode(encoding, errors)

        artist = Artist.from_binary(binary, order, version, encoding, errors)

        size = reader.read_f32(order)

        value = reader.read_u8(order)

        custom = value & custom_bit == custom_bit

        download_url_length = reader.read_u16(order)

        string = reader.read(download_url_length).decode(encoding, errors)

        if not string:
            download_url = None

        else:
            download_url = URL(string)

        return cls(
            id=id, name=name, artist=artist, size=size, custom=custom, download_url=download_url
        )

    def to_binary(
        self,
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
    ) -> None:
        writer = Writer(binary)

        writer.write_u32(self.id, order)

        data = self.name.encode(encoding, errors)

        writer.write_u8(len(data), order)

        writer.write(data)

        self.artist.to_binary(binary, order, version, encoding, errors)

        writer.write_f32(self.size, order)

        value = 0

        if self.is_custom():
            value |= CUSTOM_BIT

        writer.write_u8(value, order)

        download_url = self.download_url

        if download_url is None:
            string = EMPTY

        else:
            string = str(download_url)

        data = string.encode(encoding, errors)

        writer.write_u16(len(data), order)

        writer.write(data)

    @classmethod
    def default(cls: Type[S]) -> S:
        return cls(id=DEFAULT_ID, name=UNKNOWN, artist=Artist.default())

    @classmethod
    def from_model(cls: Type[S], model: SongModel) -> S:
        return cls(
            id=model.id,
            name=model.name,
            artist=Artist(model.artist_name),
            size=model.size,
            download_url=model.download_url,
        )

    def __str__(self) -> str:
        return self.name

    def is_custom(self) -> bool:
        return self.custom

    @classmethod
    def official(
        cls: Type[S],
        id: Optional[int] = None,
        name: Optional[str] = None,
        server_style: bool = DEFAULT_SERVER_STYLE,
        return_default: bool = DEFAULT_RETURN_DEFAULT,
    ) -> S:
        official_songs = OFFICIAL_SERVER_SONGS if server_style else OFFICIAL_CLIENT_SONGS

        if id is None:
            if name is None:
                raise LookupError(EXPECTED_QUERY)

            official_song = iter(official_songs).find_or_none(by_name(name))

        else:
            official_song = iter(official_songs).find_or_none(by_id(id))

        if official_song is None:
            if return_default:
                official_song = default_official_song() if id is None else default_official_song(id)

            else:
                raise LookupError(CAN_NOT_FIND_SONG)

        return cls(
            id=official_song.id,
            name=official_song.name,
            size=DEFAULT_SIZE,
            artist=official_song.artist,
            custom=False,
        )

    async def update(self: S, from_newgrounds: bool = DEFAULT_FROM_NEWGROUNDS) -> S:
        if from_newgrounds:
            new = await self.client.get_newgrounds_song(self.id)

        else:
            new = await self.client.get_song(self.id)

        return self.update_from(new)

    async def ensure_download_url(self) -> None:
        download_url = self.download_url

        if download_url is None:
            await self.update(from_newgrounds=True)

        download_url = self.download_url

        if download_url is None:
            raise MissingAccess(CAN_NOT_FIND_URL)

    async def download(self, file: BinaryIO, with_bar: bool = DEFAULT_WITH_BAR) -> None:
        if self.is_custom():
            await self.ensure_download_url()

            await self.client.http.download(
                file, self.download_url, with_bar=with_bar  # type: ignore
            )

        else:
            raise MissingAccess(CAN_NOT_DOWNLOAD)

    async def download_bytes(self, with_bar: bool = DEFAULT_WITH_BAR) -> bytes:
        if self.is_custom():
            await self.ensure_download_url()

            return await self.client.http.download_bytes(
                self.download_url, with_bar=with_bar  # type: ignore
            )

        raise MissingAccess(CAN_NOT_DOWNLOAD)

    async def download_to(self, path: IntoPath, with_bar: bool = DEFAULT_WITH_BAR) -> None:
        if self.is_custom():
            await self.ensure_download_url()

            await self.client.http.download_to(
                path, self.download_url, with_bar=with_bar  # type: ignore
            )

        else:
            raise MissingAccess(CAN_NOT_DOWNLOAD)
