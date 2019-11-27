import os

import gd
import pytest

pytestmark = pytest.mark.asyncio

user, password = (
    os.getenv('USER'), os.getenv('PASSWORD')
)

client = gd.Client()

# MAIN TESTS

async def test_get_song():
    song = await client.get_song(1)
    assert isinstance(song, gd.Song)

async def test_get_ng_song():
    song = await client.get_ng_song(1)
    assert isinstance(song, gd.Song)

async def test_get_user():
    user = await client.get_user(71)
    assert isinstance(user, gd.User)

async def test_fetch_user():
    stats = await client.fetch_user(5509312, stats=True)
    assert isinstance(stats, gd.UserStats)

async def test_search_user():
    user = await client.search_user('NeKitDS')  # 1
    a_user = await client.find_user('RobTop')   # 2
    assert isinstance(user, gd.User) and isinstance(a_user, gd.AbstractUser)

async def test_get_level():
    level = await client.get_level(30029017)
    assert isinstance(level, gd.Level)

async def test_get_timely():
    # TODO: add check if daily/weekly is being refreshed
    daily = await client.get_daily()
    weekly = await client.get_weekly()
    assert isinstance(daily, gd.Level) and isinstance(weekly, gd.Level)

# LOGGED IN CLIENT TESTS

@pytest.mark.skipif(user is None or password is None, reason='Environment variables not set.')
async def test_login():
    await client.login(user, password)

skip_not_logged = pytest.mark.skipif(not client.is_logged(), reason='Test for only logged in client.')

@skip_not_logged
async def test_levels():
    await client.get_levels()

@skip_not_logged
async def test_message():
    user = await client.find_user('NeKitDS')
    await user.send('[Test]', 'Testing gd.py now...')

@skip_not_logged
async def test_load():
    await client.load()

@skip_not_logged
async def test_backup():
    await client.backup()


# TODO: add more tests (yep, I use todo stuff ._.)
