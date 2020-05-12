import pytest

from conftest import client

pytestmark = pytest.mark.asyncio


async def test_get_ng_song():
    await client.get_ng_song(1)


async def test_search_songs():
    assert await client.search_page_songs("Panda Eyes")


async def test_search_users():
    assert await client.search_page_users("CreoMusic")


async def test_get_user_songs():
    assert await client.get_page_user_songs("Xtrullor")
