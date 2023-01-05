from typing import Iterable, List

from fastapi import Depends

from gd.artist import Artist, ArtistData
from gd.server.core import client, v1
from gd.server.dependencies import pages_dependency

__all__ = ("get_artists",)


def artist_to_json(artist: Artist) -> ArtistData:
    return artist.to_json()


@v1.get("/artists", summary="Fetches featured artists.")
async def get_artists(pages: Iterable[int] = Depends(pages_dependency)) -> List[ArtistData]:
    return await client.get_artists(pages=pages).map(artist_to_json).list()
