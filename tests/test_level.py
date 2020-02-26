from datetime import datetime
import pytest

from conftest import client, gd

# PREPARATIONS

pytestmark = pytest.mark.asyncio

level = gd.Level(id=30029017)
message = ('[gd.py] ({}): Running tests...'.format(datetime.utcnow()))

# MAIN TESTS


async def test_attach_client():
    level.attach_client(client)


async def test_properties():
    level.is_copyable()
    level.is_timely()
    level.is_rated()
    level.is_featured()
    level.is_epic()
    level.is_demon()
    level.is_auto()
    level.is_original()
    level.has_coins_verified()


async def test_download():
    level.download()


async def test_get_comments():
    await level.get_comments()


async def test_refresh():
    await level.refresh()


async def test_is_alive():
    await level.is_alive()


skip_not_logged = pytest.mark.skipif(
    not client.is_logged(), reason='Test for only logged in client.'
)


@skip_not_logged
async def test_like():
    await level.like()


@skip_not_logged
async def test_dislike():
    await level.dislike()


@skip_not_logged
async def test_rate_level():
    await level.rate(5)


@skip_not_logged
async def test_rate_demon():
    temp_level = await client.get_level(10565740)
    await temp_level.rate_demon(5)


@skip_not_logged
async def test_get_leaderboard():
    await level.get_leaderboard()


@skip_not_logged
async def test_send():
    try:
        await level.send()
    except gd.errors.MissingAccess:
        pass


@skip_not_logged
async def test_comment():
    await level.comment(message)
