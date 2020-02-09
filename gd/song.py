from ._typing import Song

from .abstractentity import AbstractEntity
from .utils.http_request import http
from .utils.text_tools import make_repr


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
        return self.name

    @property
    def id(self) -> int:
        """:class:`int`: An ID of the song."""
        return self.options.get('id', 0)

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
        """:class:`str`: An author of the song."""
        return self.options.get('author', '')

    @property
    def link(self) -> str:
        """:class:`str`: A link to the song on Newgrounds, e.g. ``.../audio/listen/id``."""
        return self.options.get('links', {}).get('normal', '')

    @property
    def dl_link(self) -> str:
        """:class:`str`: A link to download the song, used in :meth:`.Song.download`."""
        return self.options.get('links', {}).get('download', '')

    def is_custom(self) -> bool:
        """:class:`bool`: Indicates whether the song is custom or not."""
        return bool(self.options.get('custom'))

    @classmethod
    def official(cls, id: int, server_style: bool = True) -> Song:
        from .utils.converter import Converter  # I am too lazy ~ nekit
        return Converter.to_normal_song(id, server_style)

    async def download(self) -> bytes:
        """|coro|

        Download a song from Newgrounds.

        Returns
        -------
        :class:`bytes`
            A song as bytes.
        """
        resp = await http.normal_request(self.dl_link)
        return await resp.content.read()
