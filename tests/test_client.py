from datetime import datetime
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

# async def test_get_timely():
#     await client.get_daily()
#     await client.get_weekly()
# TODO: add check if daily/weekly is being refreshed

async def test_level_packs():
    await client.get_gauntlets()
    await client.get_page_map_packs()
    await client.get_map_packs()

async def test_captcha():
    await client.test_captcha()

async def test_ping():
    await client.ping_server()

async def test_get_leaderboard():
    await client.get_leaderboard()

async def test_search_levels():
    await client.search_levels(query='VorteX')

async def test_close():
    client.close()

# LOGGED IN CLIENT TESTS

@pytest.mark.skipif(user is None or password is None, reason='Environment variables not set.')
async def test_login():
    await client.login(user, password)

skip_not_logged = pytest.mark.skipif(not client.is_logged(), reason='Test for only logged in client.')

@skip_not_logged
async def test_levels():
    await client.get_levels()

@skip_not_logged
async def test_load():
    await client.load()

@skip_not_logged
async def test_backup():
    await client.backup()

@skip_not_logged
async def test_get_levels():
    await client.get_levels()

@skip_not_logged
async def test_get_blocked():
    await client.get_blocked_users()

@skip_not_logged
async def test_get_friends():
    await client.get_friends()

@skip_not_logged
async def test_get_messages():
    await client.get_messages()

@skip_not_logged
async def test_get_friend_requests():
    await client.get_friend_requests()

@skip_not_logged
async def test_to_user():
    await client.to_user()

@skip_not_logged
async def test_edit():
    await client.edit(password=client.password)

@skip_not_logged
async def test_post_comment():
    await client.post_comment('[gd.py] ({}): Running tests...'.format(datetime.utcnow()))

@skip_not_logged
async def test_update_profile():
    await client.update_profile()

@skip_not_logged
async def test_update_settings():
    await client.update_settings()

@skip_not_logged
def test_as_user():
    print(client.as_user())

# TODO: add more tests (yep, I use todo stuff ._.)
