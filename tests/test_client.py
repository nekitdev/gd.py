import os

import gd
import pytest

# PREPARATIONS

gd.setup_logging()

pytestmark = pytest.mark.asyncio

user, password = (
    os.getenv('GD_USER'), os.getenv('GD_PASSWORD')
)

client = gd.Client()

# MAIN TESTS

async def test_get_song():
    await client.get_song(1)

async def test_ng_song():
    await client.get_ng_song(1)

async def test_get_user():
    await client.get_user(71)

async def test_fetch_user():
    await client.fetch_user(5509312, stats=True)

async def test_search_user():
    await client.search_user('NeKitDS')  # 1
    await client.find_user('RobTop')     # 2

async def test_get_level():
    await client.get_level(30029017)

async def test_many_levels():
    await client.get_many_levels(30029017, 44622744)

async def test_get_timely():
    # TODO: add check if daily/weekly is being refreshed
    await client.get_daily()
    await client.get_weekly()

async def test_level_packs():
    await client.get_gauntlets()
    await client.get_map_packs()

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
