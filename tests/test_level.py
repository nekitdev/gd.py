from datetime import datetime
import pytest

from conftest import client, gd

# PREPARATIONS

pytestmark = pytest.mark.asyncio

level = client.run(client.get_level(30029017))
message = ('[gd.py] ({}): Running tests...'.format(datetime.utcnow()))

# MAIN TESTS


async def test_attach_client():
    level.attach_client(client)


async def test_properties():
    level.name
    level.description
    level.version
    level.downloads
    level.rating
    level.score
    level.creator
    level.song
    level.difficulty
    level.password
    level.stars
    level.coins
    level.uploaded_timestamp
    level.last_updated_timestamp
    level.length
    level.game_version
    level.requested_stars
    level.objects
    level.object_count
    level.timely_index
    level.cooldown

    level.is_copyable()
    level.is_timely()
    level.is_rated()
    level.is_featured()
    level.is_epic()
    level.is_demon()
    level.is_auto()
    level.is_original()
    level.has_coins_verified()


async def test_demon_difficulty():
    temp_level = await client.get_level(10565740)
    temp_level.difficulty


async def test_download():
    level.download()


async def test_get_comments():
    await level.get_comments()


async def test_refresh():
    await level.refresh()


async def test_is_alive():
    await level.is_alive()

    temp_level = gd.Level(id=0)
    await temp_level.is_alive()


async def test_report():
    await level.report()


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


# @skip_not_logged
# async def test_rate_demon():  # got disabled
#     temp_level = await client.get_level(10565740)
#     await temp_level.rate_demon(5)


@skip_not_logged
async def test_get_leaderboard():
    await level.get_leaderboard()


@skip_not_logged
async def test_send():
    try:
        await level.send()
    except gd.MissingAccess:
        pass


@skip_not_logged
async def test_comment():
    await level.comment(message)


@skip_not_logged
async def test_upload_update_delete():
    try:
        await level.upload(id=0)
        await level.update_description()
        await level.delete()
    except gd.MissingAccess:
        pass
