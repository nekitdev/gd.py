from .typing import Any, Callable, Client, Iterable, List, Optional, Song, Union

from .abstractentity import AbstractEntity
from .utils.http_request import HTTPClient, URL
from .utils.text_tools import make_repr

Function = Callable[[Any], Any]

http = HTTPClient(use_user_agent=True)  # used in song downloading


class ArtistInfo(AbstractEntity):
    """Class that represents info about the creator of a particular song."""
    def __str__(self) -> str:
        return str(self.artist)

    def __repr__(self) -> str:
        info = {
            'id': self.id,
            'artist': repr(self.artist),
            'song': repr(self.song),
            'is_scouted': self.is_scouted(),
            'is_whitelisted': self.is_whitelisted(),
            'exists': self.exists
        }
        return make_repr(self, info)

    @property
    def artist(self) -> str:
        """:class:`str`: Author of the song."""
        return self.options.get('artist', '')

    @property
    def song(self) -> str:
        """:class:`str`: A name of the song."""
        return self.options.get('song', '')

    @property
    def exists(self) -> bool:
        """:class:`bool`: Whether the song exists."""
        return bool(self.artist and self.song)

    def is_scouted(self) -> bool:
        """:class:`bool`: Whether the artist is scouted."""
        return bool(self.options.get('scouted', ''))

    def is_whitelisted(self) -> bool:
        """:class:`bool`: Whether the artist is whitelisted."""
        return bool(self.options.get('whitelisted', ''))

    def api_allowed(self) -> bool:
        """:class:`bool`: Whether the external API is allowed."""
        return bool(self.options.get('api', ''))


class Author(AbstractEntity):
    """Class that represents an author on Newgrounds.
    This class is derived from :class:`.AbstractEntity`.
    """
    def __repr__(self) -> str:
        info = {
            'name': repr(self.name),
            'link': repr(self.link)
        }
        return make_repr(self, info)

    def __str__(self) -> str:
        return str(self.name)

    @property
    def id(self) -> int:
        return product(map(ord, self.name)) ^ 1

    @property
    def link(self) -> URL:
        return URL(self.options.get('link', 'https://%s.newgrounds.com/' % self.name))

    @property
    def name(self) -> str:
        return self.options.get('name', '')

    async def get_page_songs(self, page: int = 0) -> List[Song]:
        return await self.client.get_page_user_songs(self, page=page)

    async def get_songs(self, pages: Iterable[int] = range(10)) -> List[Song]:
        return await self.client.get_user_songs(self, pages=pages)


class Song(AbstractEntity):
    """Class that represents Geometry Dash/Newgrounds songs.
    This class is derived from :class:`.AbstractEntity`.
    """
    def __repr__(self) -> str:
        info = {
            'id': self.id,
            'name': repr(self.name),
            'author': repr(self.author)
        }
        return make_repr(self, info)

    def __str__(self) -> str:
        return '{} - {}'.format(self.author, self.name)

    @property
    def name(self) -> int:
        """:class:`str`: A name of the song."""
        return self.options.get('name', '')

    @property
    def size(self) -> float:
        """:class:`float`: A float representing size of the song, in megabytes."""
        return self.options.get('size', 0.0)

    @property
    def author(self) -> str:
        """:class:`.Author`: An author of the song."""
        return Author(name=self.options.get('author', ''))

    @property
    def link(self) -> str:
        """:class:`str`: A link to the song on Newgrounds, e.g. ``.../audio/listen/<id>``."""
        return self.options.get('links', {}).get('normal', '')

    @property
    def dl_link(self) -> str:
        """:class:`str`: A link to download the song, used in :meth:`.Song.download`."""
        return self.options.get('links', {}).get('download', '')

    def is_custom(self) -> bool:
        """:class:`bool`: Indicates whether the song is custom or not."""
        return bool(self.options.get('custom'))

    @classmethod
    def official(cls, id: int, server_style: bool = True, client: Optional[Client] = None) -> Song:
        from .utils.converter import Converter  # ehh
        return Converter.to_normal_song(id, server_style, client=client)

    async def update(self, from_ng: bool = False) -> None:
        method = 'get_ng_song' if from_ng else 'get_song'
        new = await getattr(self.client, method)(self.id)
        self.options = new.options

    async def get_artist_info(self) -> ArtistInfo:
        """|coro|

        Fetch artist info of ``self``.

        If song is official, returns ``ArtistInfo()``.

        Otherwise, acts like the following:

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
                id=self.id, artist=self.author, song=self.name,
                whitelisted=True, scouted=True, api=True,
                client=self._client  # might be not attached
            )

        return await self.client.get_artist_info(self.id)

    async def download(self) -> bytes:
        """|coro|

        Download a song from Newgrounds.

        Returns
        -------
        :class:`bytes`
            A song as bytes.
        """
        return await http.normal_request(self.dl_link)


def product(iterable: Iterable[Union[float, int]]) -> Union[float, int]:
    result = 1

    for element in iterable:
        result *= element

    return result
