import pytest

from conftest import client, gd

# PREPARATIONS

pytestmark = pytest.mark.asyncio

artist = client.run(client.get_artist_info(1))

# MAIN TESTS


async def test_get_artist_info():
    custom_song = await client.get_song(1)
    await custom_song.get_artist_info()

    official_song = gd.Song.official(0, client=client)
    await official_song.get_artist_info()


async def test_artist_properties():
    info = await client.get_artist_info(1)
    assert info.artist
    assert info.song
    assert info.exists

    assert info.is_scouted()
    assert info.is_whitelisted()
    assert info.api_allowed()


async def test_song_properties():
    song = await client.get_song(1)
    assert song.name
    assert song.size
    assert song.author
    assert song.link
    assert song.dl_link
