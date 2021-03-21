from pathlib import Path

from attr import attrib, dataclass
from iters import iter

from gd.abstract_entity import AbstractEntity
from gd.async_iters import awaitable_iterator
from gd.errors import MissingAccess
from gd.http import NEWGROUNDS_SONG_LISTEN, URL
from gd.model import SongModel  # type: ignore
from gd.text_utils import make_repr
from gd.typing import IO, TYPE_CHECKING, Any, AsyncIterator, Dict, Iterable, Optional, Union

if TYPE_CHECKING:
    from gd.client import Client  # noqa

__all__ = (
    "ArtistInfo",
    "Author",
    "Song",
    "default_song",
    "official_client_songs",
    "official_server_songs",
)


class Song(AbstractEntity):
    """Class that represents Geometry Dash/Newgrounds songs.
    This class is derived from :class:`~gd.AbstractEntity`.
    """

    def __repr__(self) -> str:
        info = {"id": self.id, "name": repr(self.name), "author": repr(self.author)}
        return make_repr(self, info)

    def __str__(self) -> str:
        return str(self.name)

    @classmethod
    def from_model(  # type: ignore
        cls, model: SongModel, *, client: Optional["Client"] = None, custom: bool = True
    ) -> "Song":
        return cls(
            id=model.id,
            name=model.name,
            size=model.size,
            author=model.author,
            download_link=model.download_link,
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
        if self.is_custom():
            return NEWGROUNDS_SONG_LISTEN.format(song_id=self.id)

        return ""

    @property
    def download_link(self) -> str:
        """:class:`str`: A link to download the song, used in :meth:`.Song.download`."""
        return self.options.get("download_link", "")

    def is_custom(self) -> bool:
        """:class:`bool`: Indicates whether the song is custom or not."""
        return bool(self.options.get("custom", True))

    @classmethod
    def official(
        cls,
        id: Optional[int] = None,
        name: Optional[str] = None,
        index: Optional[int] = None,
        server_style: bool = True,
        return_default: bool = True,
        *,
        client: Optional["Client"] = None,
    ) -> "Song":
        official_songs = official_server_songs if server_style else official_client_songs

        if id is not None:
            official_song = iter(official_songs).get(id=id)

        elif name is not None:
            official_song = iter(official_songs).get(name=name)

        elif index is not None:
            try:
                official_song = official_songs[index]

            except (IndexError, ValueError, TypeError):
                official_song = None

        else:
            raise ValueError("Expected either of queries: id, name or index.")

        if official_song is None:
            if return_default:
                official_song = get_default_song(id)

            else:
                raise LookupError("Could not find official level by given query.")

        return cls(
            id=official_song.id,
            name=official_song.name,
            size=0.0,
            author=official_song.author,
            custom=False,
            client=client,
        )

    def get_author(self) -> "Author":
        """:class:`~gd.Author`: Author of the song."""
        if not self.is_custom():
            raise MissingAccess("Can not get author of an official song.")

        return Author(name=self.author, client=self.client)

    async def update(self, from_ng: bool = False) -> None:
        """Update the song.

        Parameters
        ----------
        from_ng: :class:`bool`
            Whether to fetch song from Newgrounds.

        Raises
        ------
        :exc:`~gd.MissingAccess`
            Failed to find the song.

        :exc:`~gd.HTTPStatusError`
            Server returned error status code.

        :exc:`~gd.HTTPError`
            Failed to process the request.
        """
        if from_ng:
            new = await self.client.get_ng_song(self.id)
        else:
            new = await self.client.get_song(self.id)

        self.options.update(new.options)

    async def get_artist_info(self) -> "ArtistInfo":
        """Fetch artist info of ``self``.

        Acts like the following:

        .. code-block:: python3

            await client.get_artist_info(song.id)

        Raises
        ------
        :exc:`~gd.MissingAccess`
            Failed to find artist info.

        :exc:`~gd.HTTPStatusError`
            Server returned error status code.

        :exc:`~gd.HTTPError`
            Failed to process the request.

        Returns
        -------
        :class:`~gd.ArtistInfo`
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
                custom=False,
                client=self.client_unchecked,
            )

        return await self.client.get_artist_info(self.id)

    async def download(
        self, file: Optional[Union[str, Path, IO]] = None, with_bar: bool = False,
    ) -> Optional[bytes]:
        """Download a song from Newgrounds.

        Parameters
        ----------
        file: Optional[Union[:class:`str`, :class:`~pathlib.Path`, IO]]
            File-like or Path-like object to write song to, instead of returning bytes.

        with_bar: :class:`bool`
            Whether to show a progress bar while downloading.
            Requires ``tqdm`` to be installed.

        Raises
        ------
        :exc:`~gd.MissingAccess`
            Can not download the song because it is official or not found.

        :exc:`~gd.HTTPStatusError`
            Server returned error status code.

        :exc:`~gd.HTTPError`
            Failed to process the request.

        Returns
        -------
        Optional[:class:`bytes`]
            A song as bytes, if ``file`` was not specified.
        """
        if not self.is_custom():
            raise MissingAccess("Song is official. Can not download.")

        if not self.download_link:
            # load song from newgrounds if there is no link
            await self.update(from_ng=True)

        return await self.client.http.download(self.download_link, file=file, with_bar=with_bar)


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

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()

        result.update(exists=self.exists)

        return result

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
        return bool(self.options.get("scouted"))

    def is_whitelisted(self) -> bool:
        """:class:`bool`: Whether the artist is whitelisted."""
        return bool(self.options.get("whitelisted"))

    def api_allowed(self) -> bool:
        """:class:`bool`: Whether the external API is allowed."""
        return bool(self.options.get("api"))

    def is_custom(self) -> bool:
        """:class:`bool`: Whether the song is custom."""
        return bool(self.options.get("custom", True))

    def get_author(self) -> "Author":
        """:class:`~gd.Author` of the song."""
        if not self.is_custom():
            raise MissingAccess("Can not get author of an official song.")

        return Author(name=self.artist, client=self.client)

    author = property(get_author)

    async def update(self) -> None:
        """Update artist info.

        Raises
        ------
        :exc:`~gd.MissingAccess`
            Failed to find artist info.

        :exc:`~gd.HTTPStatusError`
            Server returned error status code.

        :exc:`~gd.HTTPError`
            Failed to process the request.
        """
        new = await self.client.get_artist_info(self.id)
        self.options.update(new.options)


class Author(AbstractEntity):
    """Class that represents an author on Newgrounds.
    This class is derived from :class:`~gd.AbstractEntity`.
    """

    def __repr__(self) -> str:
        info = {"name": repr(self.name), "link": repr(self.link)}
        return make_repr(self, info)

    def __str__(self) -> str:
        return str(self.name)

    @property
    def id(self) -> int:
        """:class:`int`: ID of the Author."""
        return hash(self.name) | hash(self.link)

    @property
    def link(self) -> URL:
        """:class:`~yarl.URL`: URL to author's page."""
        return URL(self.options.get("link", f"https://{self.name}.newgrounds.com/"))

    @property
    def name(self) -> str:
        """:class:`str`: Name of the author."""
        return self.options.get("name", "")

    @awaitable_iterator
    def get_page_songs(self, page: int = 0) -> AsyncIterator[Song]:
        """Get songs on the page.

        Parameters
        ----------
        page: :class:`int`
            Page of songs to look at.

        Raises
        ------
        :exc:`~gd.MissingAccess`
            Failed to find songs.

        :exc:`~gd.HTTPStatusError`
            Server returned error status code.

        :exc:`~gd.HTTPError`
            Failed to process the request.

        Returns
        -------
        AsyncIterator[:class:`~gd.Song`]
            Songs found.
        """
        return self.client.get_ng_user_songs_on_page(self, page=page)

    @awaitable_iterator
    def get_songs(self, pages: Iterable[int] = range(10)) -> AsyncIterator[Song]:
        """Get songs on the pages.

        Parameters
        ----------
        pages: Iterable[:class:`int`]
            Pages of songs to look at.

        Raises
        ------
        :exc:`~gd.MissingAccess`
            Failed to find songs.

        :exc:`~gd.HTTPStatusError`
            Server returned error status code.

        :exc:`~gd.HTTPError`
            Failed to process the request.

        Returns
        -------
        AsyncIterator[:class:`~gd.Song`]
            Songs found.
        """
        return self.client.get_ng_user_songs(self, pages=pages)


@dataclass
class OfficialSong:
    id: int = attrib()
    author: str = attrib()
    name: str = attrib()


default_song = OfficialSong(id=0, author="DJVI", name="Unknown")


def get_default_song(id: Optional[int] = None) -> OfficialSong:
    if id is None:
        return default_song

    return OfficialSong(id=id, author=default_song.author, name=default_song.name)


official_client_songs = (
    OfficialSong(id=0, author="OcularNebula", name="Practice: Stay Inside Me"),
    OfficialSong(id=1, author="ForeverBound", name="Stereo Madness"),
    OfficialSong(id=2, author="DJVI", name="Back On Track"),
    OfficialSong(id=3, author="Step", name="Polargeist"),
    OfficialSong(id=4, author="DJVI", name="Dry Out"),
    OfficialSong(id=5, author="DJVI", name="Base After Base"),
    OfficialSong(id=6, author="DJVI", name="Cant Let Go"),
    OfficialSong(id=7, author="Waterflame", name="Jumper"),
    OfficialSong(id=8, author="Waterflame", name="Time Machine"),
    OfficialSong(id=9, author="DJVI", name="Cycles"),
    OfficialSong(id=10, author="DJVI", name="xStep"),
    OfficialSong(id=11, author="Waterflame", name="Clutterfunk"),
    OfficialSong(id=12, author="DJ-Nate", name="Theory of Everything"),
    OfficialSong(id=13, author="Waterflame", name="Electroman Adventures"),
    OfficialSong(id=14, author="DJ-Nate", name="Clubstep"),
    OfficialSong(id=15, author="DJ-Nate", name="Electrodynamix"),
    OfficialSong(id=16, author="Waterflame", name="Hexagon Force"),
    OfficialSong(id=17, author="Waterflame", name="Blast Processing"),
    OfficialSong(id=18, author="DJ-Nate", name="Theory of Everything 2"),
    OfficialSong(id=19, author="Waterflame", name="Geometrical Dominator"),
    OfficialSong(id=20, author="F-777", name="Deadlocked"),
    OfficialSong(id=21, author="MDK", name="Fingerdash"),
    OfficialSong(id=22, author="F-777", name="The Seven Seas"),
    OfficialSong(id=23, author="F-777", name="Viking Arena"),
    OfficialSong(id=24, author="F-777", name="Airborne Robots"),
    OfficialSong(id=25, author="RobTop", name="Secret"),  # aka DJRubRub, LOL
    OfficialSong(id=26, author="Dex Arson", name="Payload"),
    OfficialSong(id=27, author="Dex Arson", name="Beast Mode"),
    OfficialSong(id=28, author="Dex Arson", name="Machina"),
    OfficialSong(id=29, author="Dex Arson", name="Years"),
    OfficialSong(id=30, author="Dex Arson", name="Frontlines"),
    OfficialSong(id=31, author="Waterflame", name="Space Pirates"),
    OfficialSong(id=32, author="Waterflame", name="Striker"),
    OfficialSong(id=33, author="Dex Arson", name="Embers"),
    OfficialSong(id=34, author="Dex Arson", name="Round 1"),
    OfficialSong(id=35, author="F-777", name="Monster Dance Off"),
    OfficialSong(id=36, author="MDK", name="Press Start"),
    OfficialSong(id=37, author="Bossfight", name="Nock Em"),
    OfficialSong(id=38, author="Boom Kitty", name="Power Trip"),
)

official_server_songs = tuple(
    OfficialSong(id=official_song.id - 1, author=official_song.author, name=official_song.name)
    for official_song in official_client_songs
)
