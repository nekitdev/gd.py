from pathlib import Path

from fastapi.responses import FileResponse

from gd.server.constants import CACHE, SONGS
from gd.server.core import client, v1
from gd.song import SongData

__all__ = ("download_song", "get_song")

PATH = Path(CACHE) / SONGS

PATH.mkdir(parents=True, exist_ok=True)

SONG = "{}.mp3"


@v1.get("/songs/{song_id}", summary="Fetches the song by the ID.")
async def get_song(song_id: int) -> SongData:
    song = await client.get_song(song_id)

    return song.into_data()


@v1.get("/songs/{song_id}/download", summary="Downloads the song by the ID.")
async def download_song(song_id: int) -> FileResponse:
    path = PATH / SONG.format(song_id)

    if path.exists():
        return FileResponse(path)

    song = await client.get_song(song_id)

    await song.download_to(path)

    return FileResponse(path)
