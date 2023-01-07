from pathlib import Path
from typing import Iterable, List

from fastapi import Depends
from fastapi.responses import FileResponse

from gd.artist import Artist, ArtistData
from gd.server.constants import CACHE, SONGS
from gd.server.core import client, v1
from gd.server.dependencies import pages_dependency
from gd.song import Song, SongData

__all__ = (
    "get_newgrounds_artist_songs",
    "get_newgrounds_song",
    "search_newgrounds_artists",
    "search_newgrounds_songs",
)

PATH = Path(CACHE) / SONGS

PATH.mkdir(parents=True, exist_ok=True)

SONG = "{}.newgrounds.mp3"


@v1.get("/newgrounds/songs/{song_id}", summary="Fetches the Newgrounds song by the ID.")
async def get_newgrounds_song(song_id: int) -> SongData:
    song = await client.get_newgrounds_song(song_id)

    return song.to_json()


@v1.get("/newgrounds/songs/{song_id}/download", summary="Downloads the song by the ID.")
async def download_song(song_id: int) -> FileResponse:
    path = PATH / SONG.format(song_id)

    if path.exists():
        return FileResponse(path)

    song = await client.get_newgrounds_song(song_id)

    await song.download_to(path)

    return FileResponse(path)


def artist_to_json(artist: Artist) -> ArtistData:
    return artist.to_json()


@v1.get(
    "/search/newgrounds/artists/{query}", summary="Searches for Newgrounds artists by the query."
)
async def search_newgrounds_artists(
    query: str, pages: Iterable[int] = Depends(pages_dependency)
) -> List[ArtistData]:
    return await client.search_newgrounds_artists(query, pages=pages).map(artist_to_json).list()


def song_to_json(song: Song) -> SongData:
    return song.to_json()


@v1.get("/search/newgrounds/songs/{query}", summary="Searches for Newgrounds songs by the query.")
async def search_newgrounds_songs(
    query: str, pages: Iterable[int] = Depends(pages_dependency)
) -> List[SongData]:
    return await client.search_newgrounds_songs(query, pages=pages).map(song_to_json).list()


@v1.get("/newgrounds/artists/{name}/songs", summary="Fetches songs by the Newgrounds artist.")
async def get_newgrounds_artist_songs(
    name: str, pages: Iterable[int] = Depends(pages_dependency)
) -> List[SongData]:
    artist = Artist(name).attach_client(client)

    return await artist.get_songs(pages=pages).map(song_to_json).list()
