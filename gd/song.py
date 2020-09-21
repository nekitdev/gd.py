from pathlib import Path

from attr import attrib, dataclass
import tqdm  # type: ignore

from gd.typing import Any, Dict, IO, Iterable, List, Optional, Union, TYPE_CHECKING

from gd.abstract_entity import AbstractEntity
from gd.errors import MissingAccess
from gd.http import HTTPClient, NEWGROUNDS_SONG_LISTEN, URL
from gd.model import SongModel  # type: ignore
from gd.text_utils import make_repr

if TYPE_CHECKING:
    from gd.client import Client  # noqa

__all__ = ("ArtistInfo", "Author", "Song")


class Song(AbstractEntity):
    """Class that represents Geometry Dash/Newgrounds songs.
    This class is derived from :class:`.AbstractEntity`.
    """

    def __repr__(self) -> str:
        info = {"id": self.id, "name": repr(self.name), "author": repr(self.author)}
        return make_repr(self, info)

    def __str__(self) -> str:
        return str(self.name)

    @classmethod
    def from_model(
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
        cls, id: int, server_style: bool = True, *, client: Optional["Client"] = None
    ) -> "Song":
        songs = OFFICIAL_SERVER_SONGS if server_style else OFFICIAL_CLIENT_SONGS
        song = songs.get(id, OfficialSong(author="DJVI", name="Unknown"))

        return cls(
            id=id, name=song.name, size=0.0, author=song.author, custom=False, client=client,
        )

    def get_author(self) -> "Author":
        """:class:`.Author`: Author of the song."""
        if not self.is_custom():
            raise MissingAccess("Can not get author of an official song.")

        return Author(name=self.author, client=self.client)

    async def update(self, from_ng: bool = False) -> None:
        """Update the song.

        Parameters
        ----------
        from_ng: :class:`bool`
            Whether to fetch song from Newgrounds.
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
                official=True,
                client=self.client_unchecked,
            )

        return await self.client.get_artist_info(self.id)

    async def download(
        self, file: Optional[Union[str, Path, IO]] = None, with_bar: bool = False,
    ) -> Optional[bytes]:
        """Download a song from Newgrounds.

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
        if not self.is_custom():
            raise MissingAccess("Song is official. Can not download.")

        if not self.download_link:
            # load song from NG if there is no link
            await self.update(from_ng=True)

        return await download(
            self.client.http, "GET", self.download_link, file=file, with_bar=with_bar
        )


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
        return bool(self.options.get("scouted"))

    def is_whitelisted(self) -> bool:
        """:class:`bool`: Whether the artist is whitelisted."""
        return bool(self.options.get("whitelisted"))

    def api_allowed(self) -> bool:
        """:class:`bool`: Whether the external API is allowed."""
        return bool(self.options.get("api"))

    def is_official(self) -> bool:
        return bool(self.options.get("official"))

    def get_author(self) -> "Author":
        """:class:`.Author`: Author of the song."""
        if self.is_official():
            raise MissingAccess("Can not get author of an official song.")

        return Author(name=self.artist, client=self.client)

    async def update(self) -> None:
        new = await self.client.get_artist_info(self.id)
        self.options.update(new.options)


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
        return hash(self.name) | hash(self.link)

    @property
    def link(self) -> URL:
        """:class:`yarl.URL`: URL to author's page."""
        return URL(self.options.get("link", f"https://{self.name}.newgrounds.com/"))

    @property
    def name(self) -> str:
        """:class:`str`: Name of the author."""
        return self.options.get("name", "")

    async def get_page_songs(self, page: int = 0) -> List[Song]:
        """Get songs on the page.

        Parameters
        ----------
        page: :class:`int`
            Page of songs to look at.

        Returns
        -------
        List[:class:`.Song`]
            Songs found. Can be empty.
        """
        return await self.client.get_ng_user_songs_on_page(self, page=page)

    async def get_songs(self, pages: Iterable[int] = range(10)) -> List[Song]:
        """Get songs on the pages.

        Parameters
        ----------
        pages: Iterable[:class:`int`]
            Pages of songs to look at.

        Returns
        -------
        List[:class:`.Song`]
            Songs found. Can be empty.
        """
        return await self.client.get_ng_user_songs(self, pages=pages)


async def download(
    http_client: HTTPClient,
    method: str,
    url: str,
    chunk_size: int = 64 * 1024,
    with_bar: bool = False,
    close: bool = False,
    file: Optional[Union[str, Path, IO]] = None,
    **kwargs,
) -> Optional[bytes]:
    if isinstance(file, (str, Path)):
        file = open(file, "wb")
        close = True

    await http_client.ensure_session()

    async with http_client.session.request(  # type: ignore
        url=url, method=method, **kwargs
    ) as response:
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

    return None


@dataclass
class OfficialSong:
    author: str = attrib()
    name: str = attrib()


OFFICIAL_CLIENT_SONGS = {
    0: OfficialSong(author="OcularNebula", name="Practice: Stay Inside Me"),
    1: OfficialSong(author="ForeverBound", name="Stereo Madness"),
    2: OfficialSong(author="DJVI", name="Back On Track"),
    3: OfficialSong(author="Step", name="Polargeist"),
    4: OfficialSong(author="DJVI", name="Dry Out"),
    5: OfficialSong(author="DJVI", name="Base After Base"),
    6: OfficialSong(author="DJVI", name="Cant Let Go"),
    7: OfficialSong(author="Waterflame", name="Jumper"),
    8: OfficialSong(author="Waterflame", name="Time Machine"),
    9: OfficialSong(author="DJVI", name="Cycles"),
    10: OfficialSong(author="DJVI", name="xStep"),
    11: OfficialSong(author="Waterflame", name="Clutterfunk"),
    12: OfficialSong(author="DJ-Nate", name="Theory of Everything"),
    13: OfficialSong(author="Waterflame", name="Electroman Adventures"),
    14: OfficialSong(author="DJ-Nate", name="Clubstep"),
    15: OfficialSong(author="DJ-Nate", name="Electrodynamix"),
    16: OfficialSong(author="Waterflame", name="Hexagon Force"),
    17: OfficialSong(author="Waterflame", name="Blast Processing"),
    18: OfficialSong(author="DJ-Nate", name="Theory of Everything 2"),
    19: OfficialSong(author="Waterflame", name="Geometrical Dominator"),
    20: OfficialSong(author="F-777", name="Deadlocked"),
    21: OfficialSong(author="MDK", name="Fingerdash"),
    22: OfficialSong(author="F-777", name="The Seven Seas"),
    23: OfficialSong(author="F-777", name="Viking Arena"),
    24: OfficialSong(author="F-777", name="Airborne Robots"),
    25: OfficialSong(author="RobTop", name="Secret"),  # aka DJRubRub, LOL
    26: OfficialSong(author="Dex Arson", name="Payload"),
    27: OfficialSong(author="Dex Arson", name="Beast Mode"),
    28: OfficialSong(author="Dex Arson", name="Machina"),
    29: OfficialSong(author="Dex Arson", name="Years"),
    30: OfficialSong(author="Dex Arson", name="Frontlines"),
    31: OfficialSong(author="Waterflame", name="Space Pirates"),
    32: OfficialSong(author="Waterflame", name="Striker"),
    33: OfficialSong(author="Dex Arson", name="Embers"),
    34: OfficialSong(author="Dex Arson", name="Round 1"),
    35: OfficialSong(author="F-777", name="Monster Dance Off"),
    36: OfficialSong(author="MDK", name="Press Start"),
    37: OfficialSong(author="Bossfight", name="Nock Em"),
    38: OfficialSong(author="Boom Kitty", name="Power Trip"),
}

OFFICIAL_SERVER_SONGS = {
    song_id - 1: official_song for song_id, official_song in OFFICIAL_CLIENT_SONGS.items()
}
