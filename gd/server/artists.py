from typing import Iterable, List

from fastapi import Depends

from gd.artist import Artist, ArtistData
from gd.server.core import client, v1
from gd.server.dependencies import pages_dependency

__all__ = ("get_artists",)


def artist_into_data(artist: Artist) -> ArtistData:
    return artist.into_data()


@v1.get("/artists", summary="Fetches featured artists.")
async def get_artists(pages: Iterable[int] = Depends(pages_dependency)) -> List[ArtistData]:
    return await client.get_artists(pages=pages).map(artist_into_data).list()
