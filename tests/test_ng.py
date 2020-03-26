import pytest

from conftest import client, gd

pytestmark = pytest.mark.asyncio


async def test_get_ng_song():
    await client.get_ng_song(1)


async def test_search_songs():
    await client.search_page_songs('Panda Eyes')


async def test_search_users():
    await client.search_page_users('CreoMusic')


async def test_get_user_songs():
    await client.get_page_user_songs(gd.Author(name='Xtrullor'))
