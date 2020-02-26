import pytest

from conftest import client, gd

# PREPARATIONS

pytestmark = pytest.mark.asyncio

artist = client.run(client.get_artist_info(1))

# MAIN TESTS


async def test_get_artist_info():
    song1 = await client.get_song(1)
    await song1.get_artist_info()

    song2 = gd.Song.official(0)
    await song2.get_artist_info()


async def test_artist_properties():
    artist.artist
    artist.song
    artist.exists

    artist.is_scouted()
    artist.is_whitelisted()
    artist.api_allowed()


async def test_song_properties():
    song = await client.get_song(1)
    song.name
    song.size
    song.author
    song.link
    song.dl_link
