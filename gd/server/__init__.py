from gd.server.artists import get_artists
from gd.server.core import app, v1
from gd.server.newgrounds import (
    get_newgrounds_artist_songs,
    get_newgrounds_song,
    search_newgrounds_artists,
    search_newgrounds_songs,
)
from gd.server.songs import download_song, get_song
from gd.server.users import get_user, get_user_icons, search_user, search_user_icons, search_users

__all__ = (
    # apps
    "app",
    "v1",
    # artists
    "get_artists",
    # newgrounds
    "get_newgrounds_artist_songs",
    "get_newgrounds_song",
    "search_newgrounds_artists",
    "search_newgrounds_songs",
    # songs
    "download_song",
    "get_song",
    # users
    "get_user",
    "get_user_icons",
    "search_user",
    "search_user_icons",
    "search_users",
)
