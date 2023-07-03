from __future__ import annotations

from enum import Flag
from typing import BinaryIO, Optional, Type, TypeVar

from attrs import define, field
from typing_aliases import IntoPath
from yarl import URL

from gd.artist import Artist, ArtistData
from gd.binary import VERSION, BinaryReader, BinaryWriter
from gd.binary_utils import Reader, Writer
from gd.constants import (
    DEFAULT_CUSTOM,
    DEFAULT_ENCODING,
    DEFAULT_ERRORS,
    DEFAULT_FROM_NEWGROUNDS,
    DEFAULT_ID,
    DEFAULT_ROUNDING,
    DEFAULT_WITH_BAR,
    EMPTY,
    UNKNOWN,
)
from gd.converter import CONVERTER, dump_url, register_unstructure_hook_omit_client
from gd.entity import Entity, EntityData
from gd.enums import ByteOrder
from gd.errors import MissingAccess
from gd.http import NEWGROUNDS_SONG
from gd.models import SongModel
from gd.official_songs import ID_TO_OFFICIAL_SONG, NAME_TO_OFFICIAL_SONG, OfficialSong

__all__ = ("Song",)


class SongFlag(Flag):
    SIMPLE = 0

    CUSTOM = 1 << 0
    SIZE = 1 << 1
    DOWNLOAD_URL = 1 << 2

    def is_custom(self) -> bool:
        return type(self).CUSTOM in self

    def has_size(self) -> bool:
        return type(self).SIZE in self

    def has_download_url(self) -> bool:
        return type(self).DOWNLOAD_URL in self


class SongData(EntityData):
    name: str
    artist: ArtistData
    size: Optional[float]
    download_url: Optional[str]


S = TypeVar("S", bound="Song")

EXPECTED_QUERY = "expected either `id` or `name`"
CAN_NOT_DOWNLOAD = "can not download an official song"
CAN_NOT_GET = "can not get an official song"
CAN_NOT_FIND_URL = "can not find download URL"


@register_unstructure_hook_omit_client
@define()
class Song(Entity):
    """Represents *Geometry Dash* and *Newgrounds* songs.

    Binary:

        ```rust
        const CUSTOM_BIT: u8 = 1 << 0;
        const HAS_SIZE_BIT: u8 = 1 << 1;
        const HAS_DOWNLOAD_URL_BIT: u8 = 1 << 2;

        struct DownloadURL {
            length: u16,
            url: [u8; length],  // utf-8 string
        }

        struct Song {
            value: u8,  // contains `custom`, `has_size` and `has_download_url`
            id: u32,
            name_length: u8,
            name: [u8; name_length],  // utf-8 string
            artist: Artist,
            size: Option<f32>,  // if `has_size`
            download_url: Option<DownloadURL>,  // if `has_download_url`
        }
        ```
    """

    name: str = field(eq=False)

    artist: Artist = field(eq=False)

    custom: bool = field(eq=False)

    size: Optional[float] = field(default=None, eq=False)

    download_url: Optional[URL] = field(default=None, eq=False)

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

    @property
    def url(self) -> URL:
        return URL(NEWGROUNDS_SONG.format(self.id))

    @classmethod
    def from_data(cls: Type[S], data: SongData) -> S:  # type: ignore
        return CONVERTER.structure(data, cls)

    def into_data(self) -> SongData:
        return CONVERTER.unstructure(self)  # type: ignore

    @classmethod
    def from_binary(
        cls: Type[S],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
    ) -> S:
        rounding = DEFAULT_ROUNDING

        reader = Reader(binary, order)

        song_flag_value = reader.read_u8()

        song_flag = SongFlag(song_flag_value)

        id = reader.read_u32()

        custom = song_flag.is_custom()

        name_length = reader.read_u8()

        name = reader.read(name_length).decode(encoding, errors)

        artist = Artist.from_binary(binary, order, version, encoding, errors)

        if song_flag.has_size():
            size = round(reader.read_f32(), rounding)

        else:
            size = None

        if song_flag.has_download_url():
            download_url_length = reader.read_u16()

            download_url_string = reader.read(download_url_length).decode(encoding, errors)

            download_url = URL(download_url_string)

        else:
            download_url = None

        return cls(
            id=id, custom=custom, name=name, artist=artist, size=size, download_url=download_url
        )

    def to_binary(
        self,
        binary: BinaryWriter,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
    ) -> None:
        writer = Writer(binary, order)

        song_flag = SongFlag.SIMPLE

        if self.is_custom():
            song_flag |= SongFlag.CUSTOM

        size = self.size

        if size is not None:
            song_flag |= SongFlag.SIZE

        download_url = self.download_url

        if download_url is not None:
            song_flag |= SongFlag.DOWNLOAD_URL

        writer.write_u8(song_flag.value)

        writer.write_u32(self.id)

        data = self.name.encode(encoding, errors)

        writer.write_u8(len(data))

        writer.write(data)

        self.artist.to_binary(binary, order, version, encoding, errors)

        if size is not None:
            writer.write_f32(size)

        if download_url is not None:
            data = dump_url(download_url).encode(encoding, errors)

            writer.write_u16(len(data))

            writer.write(data)

    @classmethod
    def default(
        cls: Type[S],
        id: int = DEFAULT_ID,
        artist_id: int = DEFAULT_ID,
        custom: bool = DEFAULT_CUSTOM,
    ) -> S:
        return cls(id=id, name=EMPTY, artist=Artist.default(artist_id), custom=custom)

    @classmethod
    def official(cls: Type[S], id: Optional[int] = None, name: Optional[str] = None) -> S:
        if id is None:
            if name is None:
                raise ValueError(EXPECTED_QUERY)

            else:
                official_song = NAME_TO_OFFICIAL_SONG.get(name)

                if official_song is None:
                    official_song = OfficialSong.default(name=name)

        else:
            official_song = ID_TO_OFFICIAL_SONG.get(id)

            if official_song is None:
                official_song = OfficialSong.default(id=id)

        return cls(
            id=official_song.id,
            custom=False,
            name=official_song.name,
            artist=Artist.name_only(official_song.artist_name),
        )

    @classmethod
    def from_model(cls: Type[S], model: SongModel) -> S:
        return cls(
            id=model.id,
            custom=True,
            name=model.name,
            artist=Artist(
                model.artist_id,
                model.artist_name,
                model.is_artist_verified(),
            ),
            size=model.size or None,
            download_url=model.download_url,
        )

    def __str__(self) -> str:
        return self.name or UNKNOWN

    def is_custom(self) -> bool:
        return self.custom

    async def get(self, from_newgrounds: bool = DEFAULT_FROM_NEWGROUNDS) -> Song:
        if self.is_custom():
            if from_newgrounds:
                return await self.client.get_newgrounds_song(self.id)

            else:
                return await self.client.get_song(self.id)

        raise MissingAccess(CAN_NOT_GET)

    async def update(self: S, from_newgrounds: bool = DEFAULT_FROM_NEWGROUNDS) -> S:
        return self.update_from(await self.get(from_newgrounds=from_newgrounds))

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
