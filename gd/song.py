from pathlib import Path
from urllib.parse import unquote

import aiohttp

from gd.typing import Any, Client, Dict, IO, Iterable, List, Optional, Song, Union

from gd.abstractentity import AbstractEntity
from gd.errors import ClientException

from gd.utils.converter import Converter
from gd.utils.http_request import HTTPClient, URL
from gd.utils.indexer import Index
from gd.utils.parser import ExtDict
from gd.utils.routes import Route
from gd.utils.text_tools import make_repr

UserAgent = HTTPClient.get_default_agent()


class ArtistInfo(AbstractEntity):
    """Class that represents info about the creator of a particular song."""

    def __str__(self) -> str:
        return str(self.artist)

    def __repr__(self) -> str:
        info = {
            "id": self.id,
            "artist": repr(self.artist),
            "song": repr(self.song),
            "is_scouted": self.is_scouted(),
            "is_whitelisted": self.is_whitelisted(),
            "exists": self.exists,
        }
        return make_repr(self, info)

    def __json__(self) -> Dict[str, Any]:
        return dict(super().__json__(), exists=self.exists)

    @property
    def artist(self) -> str:
        """:class:`str`: Author of the song."""
        return self.options.get("artist", "")

    @property
    def song(self) -> str:
        """:class:`str`: A name of the song."""
        return self.options.get("song", "")

    @property
    def exists(self) -> bool:
        """:class:`bool`: Whether the song exists."""
        return bool(self.artist and self.song)

    def is_scouted(self) -> bool:
        """:class:`bool`: Whether the artist is scouted."""
        return bool(self.options.get("scouted", ""))

    def is_whitelisted(self) -> bool:
        """:class:`bool`: Whether the artist is whitelisted."""
        return bool(self.options.get("whitelisted", ""))

    def api_allowed(self) -> bool:
        """:class:`bool`: Whether the external API is allowed."""
        return bool(self.options.get("api", ""))

    async def update(self) -> None:
        new = await self.client.get_artist_info(self.id)
        self.options = new.options


class Author(AbstractEntity):
    """Class that represents an author on Newgrounds.
    This class is derived from :class:`.AbstractEntity`.
    """

    def __repr__(self) -> str:
        info = {"name": repr(self.name), "link": repr(self.link)}
        return make_repr(self, info)

    def __str__(self) -> str:
        return str(self.name)

    @property
    def id(self) -> int:
        """:class:`int`: ID of the Author."""
        return hash(str(self))

    @property
    def link(self) -> URL:
        """:class:`yarl.URL`: URL to author's page."""
        return URL(self.options.get("link", "https://%s.newgrounds.com/" % self.name))

    @property
    def name(self) -> str:
        """:class:`str`: Name of the author."""
        return self.options.get("name", "")

    async def get_page_songs(self, page: int = 0) -> List[Song]:
        """|coro|

        Get songs on the page.

        Parameters
        ----------
        page: :class:`int`
            Page of songs to look at.

        Returns
        -------
        List[:class:`.Song`]
            Songs found. Can be empty.
        """
        return await self.client.get_page_user_songs(self, page=page)

    async def get_songs(self, pages: Iterable[int] = range(10)) -> List[Song]:
        """|coro|

        Get songs on the pages.

        Parameters
        ----------
        pages: Iterable[:class:`int`]
            Pages of songs to look at.

        Returns
        -------
        List[:class:`.Song`]
            Songs found. Can be empty.
        """
        return await self.client.get_user_songs(self, pages=pages)


class Song(AbstractEntity):
    """Class that represents Geometry Dash/Newgrounds songs.
    This class is derived from :class:`.AbstractEntity`.
    """

    def __init__(self, **options) -> None:
        super().__init__(**options)

    def __repr__(self) -> str:
        info = {"id": self.id, "name": repr(self.name), "author": repr(self.author)}
        return make_repr(self, info)

    def __str__(self) -> str:
        return str(self.name)

    @classmethod
    def from_data(cls, data: ExtDict, *, custom: bool = True, client: Client) -> Song:
        return cls(
            # name and author - cp1252 encoding seems to fix weird characters - Alex1304
            name=fix_song_encoding(data.get(Index.SONG_TITLE, "unknown")),
            author=fix_song_encoding(data.get(Index.SONG_AUTHOR, "unknown")),
            id=data.getcast(Index.SONG_ID, 0, int),
            size=data.getcast(Index.SONG_SIZE, 0.0, float),
            links=dict(
                normal=Route.NEWGROUNDS_SONG_LISTEN + data.get(Index.SONG_ID, ""),
                download=unquote(data.get(Index.SONG_URL, "")),
            ),
            custom=custom,
            client=client,
        )

    @property
    def name(self) -> int:
        """:class:`str`: A name of the song."""
        return self.options.get("name", "")

    @property
    def size(self) -> float:
        """:class:`float`: A float representing size of the song, in megabytes."""
        return self.options.get("size", 0.0)

    @property
    def author(self) -> str:
        """:class:`str`: An author of the song."""
        return self.options.get("author", "")

    @property
    def link(self) -> str:
        """:class:`str`: A link to the song on Newgrounds, e.g. ``.../audio/listen/<id>``."""
        return self.options.get("links", {}).get("normal", "")

    @property
    def dl_link(self) -> str:
        """:class:`str`: A link to download the song, used in :meth:`.Song.download`."""
        return self.options.get("links", {}).get("download", "")

    def is_custom(self) -> bool:
        """:class:`bool`: Indicates whether the song is custom or not."""
        return bool(self.options.get("custom"))

    @classmethod
    def official(
        cls, id: int, server_style: bool = True, *, client: Optional[Client] = None
    ) -> Song:
        data = Converter.to_normal_song(id, server_style)
        return cls(**data, client=client)

    def get_author(self) -> Author:
        """:class:`.Author`: Author of the song."""
        if not self.is_custom():
            raise ClientException("Can not get author of an official song.")

        return Author(name=self.author, client=self.client)

    async def update(self, from_ng: bool = False) -> None:
        """|coro|

        Update the song.

        Parameters
        ----------
        from_ng: :class:`bool`
            Whether to fetch song from Newgrounds.
        """
        if from_ng:
            new = await self.client.get_ng_song(self.id)
        else:
            new = await self.client.get_song(self.id)

        self.options = new.options

    async def get_artist_info(self) -> ArtistInfo:
        """|coro|

        Fetch artist info of ``self``.

        Acts like the following:

        .. code-block:: python3

            await client.get_artist_info(song.id)

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to find artist info.

        Returns
        -------
        :class:`.ArtistInfo`
            Fetched info about an artist.
        """
        if not self.is_custom():  # pragma: no cover
            return ArtistInfo(
                id=self.id,
                artist=self.author,
                song=self.name,
                whitelisted=True,
                scouted=True,
                api=True,
                client=self.options.get("client"),
            )

        return await self.client.get_artist_info(self.id)

    async def download(
        self, file: Optional[Union[str, Path, IO]] = None, with_bar: bool = False,
    ) -> Optional[bytes]:
        """|coro|

        Download a song from Newgrounds.

        Parameters
        ----------
        file: Optional[Union[:class:`str`, :class:`pathlib.Path`, IO]]
            File-like or Path-like object to write song to, instead of returning bytes.

        with_bar: :class:`bool`
            Whether to show a progress bar while downloading.
            Requires ``tqdm`` to be installed.

        Returns
        -------
        Optional[:class:`bytes`]
            A song as bytes, if ``file`` was not specified.
        """
        if not self.dl_link:
            # load song from NG if there is no link
            await self.update(from_ng=True)

        return await download(self.dl_link, file=file, with_bar=with_bar)


async def download(
    url: str,
    method: str = "GET",
    chunk_size: int = 64 * 1024,
    with_bar: bool = False,
    close: bool = False,
    file: Optional[Union[str, Path, IO]] = None,
    **kwargs,
) -> Optional[bytes]:
    if with_bar:
        import tqdm

    if isinstance(file, (str, Path)):
        file = open(file, "wb")

    async with aiohttp.ClientSession(headers={"User-Agent": UserAgent}) as client:
        async with client.request(url=url, method=method, **kwargs) as response:
            if file is None:
                result = bytes()

            if with_bar:
                bar = tqdm.tqdm(total=response.content_length, unit="b", unit_scale=True)

            while True:
                chunk = await response.content.read(chunk_size)
                if not chunk:
                    break

                if file is None:
                    result += chunk
                else:
                    file.write(chunk)

                if with_bar:
                    bar.update(len(chunk))

            if with_bar:
                bar.close()

    if close and file:
        file.close()

    if file is None:
        return result


def fix_song_encoding(string: str) -> str:
    try:
        return string.encode("cp1252").decode("utf-8")

    except (UnicodeEncodeError, UnicodeDecodeError):
        return string
