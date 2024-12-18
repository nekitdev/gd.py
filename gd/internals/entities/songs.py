from typing import Optional
from urllib.parse import quote, unquote

from attrs import define
from typing_extensions import Self
from yarl import URL

from gd.converters import unstructure_url
from gd.defaults.encoding import DEFAULT_ENCODING, DEFAULT_ERRORS
from gd.defaults.entities.core import DEFAULT_ID
from gd.defaults.entities.artists import DEFAULT_ARTIST_VERIFIED
from gd.defaults.entities.songs import DEFAULT_SIZE
from gd.internals.robtop.core import (
    bool_str,
    concat_mapping_with,
    float_str,
    int_bool,
    split_mapping_with,
)
from gd.internals.robtop.protocols import RobTop
from gd.internals.robtop.views import RobTopView
from gd.strings.constants import EMPTY

SONG_SEPARATOR = "~|~"
"""The separator used in song strings."""

split_song = split_mapping_with(SONG_SEPARATOR)
concat_song = concat_mapping_with(SONG_SEPARATOR)

SONG_ID = 1
"""The ID of the song."""

SONG_NAME = 2
"""The name of the song."""

SONG_ARTIST_ID = 3
"""The ID of the song's artist."""

SONG_ARTIST_NAME = 4
"""The name of the song's artist."""

SONG_SIZE = 5
"""The size of the song."""

SONG_YOUTUBE_VIDEO_ID = 6
"""The YouTube video ID of the song."""

SONG_YOUTUBE_CHANNEL_ID = 7
"""The YouTube channel ID of the song's artist."""

SONG_ARTIST_VERIFIED = 8
"""Whether the song's artist is verified."""

SONG_URL = 10
"""The URL of the song."""


@define()
class InternalSong(RobTop):
    """Represents songs internally."""

    id: int = DEFAULT_ID
    """The ID of the song."""

    name: str = EMPTY
    """The name of the song."""

    artist_id: int = DEFAULT_ID
    """The ID of the song's artist."""

    artist_name: str = EMPTY
    """The name of the song's artist."""

    size: float = DEFAULT_SIZE
    """The size of the song."""

    youtube_video_id: str = EMPTY
    """The YouTube video ID of the song."""

    youtube_channel_id: str = EMPTY
    """The YouTube channel ID of the song's artist."""

    artist_verified: bool = DEFAULT_ARTIST_VERIFIED
    """Whether the song's artist is verified."""

    url: Optional[URL] = None
    """The URL of the song."""

    @classmethod
    def from_robtop(
        cls, string: str, encoding: str = DEFAULT_ENCODING, errors: str = DEFAULT_ERRORS
    ) -> Self:
        mapping = split_song(string)

        view = RobTopView(mapping)

        id = view.get_option(SONG_ID).map(int).unwrap_or(DEFAULT_ID)

        name = view.get_option(SONG_NAME).unwrap_or(EMPTY)

        artist_name = view.get_option(SONG_ARTIST_NAME).unwrap_or(EMPTY)

        artist_id = view.get_option(SONG_ARTIST_ID).map(int).unwrap_or(DEFAULT_ID)

        size = view.get_option(SONG_SIZE).map(float).unwrap_or(DEFAULT_SIZE)

        youtube_video_id = view.get_option(SONG_YOUTUBE_VIDEO_ID).unwrap_or(EMPTY)
        youtube_channel_id = view.get_option(SONG_YOUTUBE_CHANNEL_ID).unwrap_or(EMPTY)

        artist_verified = (
            view.get_option(SONG_ARTIST_VERIFIED).map(int_bool).unwrap_or(DEFAULT_ARTIST_VERIFIED)
        )

        url = view.get_option(SONG_URL).filter(bool).map(unquote).map(URL).extract()

        return cls(
            id=id,
            name=name,
            artist_name=artist_name,
            artist_id=artist_id,
            size=size,
            youtube_video_id=youtube_video_id,
            youtube_channel_id=youtube_channel_id,
            artist_verified=artist_verified,
            url=url,
        )

    def to_robtop(self) -> str:
        url = self.url

        mapping = {
            SONG_ID: str(self.id),
            SONG_NAME: self.name,
            SONG_ARTIST_NAME: self.artist_name,
            SONG_ARTIST_ID: str(self.artist_id),
            SONG_SIZE: float_str(self.size),
            SONG_YOUTUBE_VIDEO_ID: self.youtube_video_id,
            SONG_YOUTUBE_CHANNEL_ID: self.youtube_channel_id,
            SONG_ARTIST_VERIFIED: bool_str(self.is_artist_verified()),
            SONG_URL: EMPTY if url is None else quote(unstructure_url(url)),
        }

        return concat_song(mapping)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return SONG_SEPARATOR in string

    def is_artist_verified(self) -> bool:
        """Checks if the song's artist is verified.

        Returns:
            Whether the song's artist is verified.
        """
        return self.artist_verified
