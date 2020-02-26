from datetime import datetime
import pytest

from conftest import client

# PREPARATIONS

pytestmark = pytest.mark.asyncio
user = None

message = ('[gd.py] ({}): Running tests...'.format(datetime.utcnow()))


async def test_preparations():
    global user  # i am so very sorry for this
    user = await client.search_user('NekitDS')


# MAIN TESTS

async def test_retrieve_comments():
    await user.retrieve_comments(pages=range(10))


async def test_retrieve_page_comments():
    await user.retrieve_page_comments()


async def test_properties():
    user.has_cp()
    user.is_registered()
    user.is_mod()
    user.is_mod('elder')


async def test_update():
    await user.update()


async def test_userstats_update():
    userstats = await client.fetch_user(5509312, stats=True)
    await userstats.update()


async def test_user_get_levels_on_page():
    await user.get_levels_on_page()


async def test_get_levels():
    await user.get_levels()


async def testr_get_page_comments():
    await user.get_page_comments()


async def test_get_page_comment_history():
    await user.get_page_comment_history()


async def test_get_comments():
    await user.get_comments()


async def test_get_comment_history():
    await user.get_comment_history()


async def test_as_user():
    user.as_user()


async def test_abstractuser_update():
    abstractuser = user.as_user()
    abstractuser.update()


skip_not_logged = pytest.mark.skipif(
    not client.is_logged(), reason='Test for only logged in client.'
)


@skip_not_logged
async def test_block():
    await user.block()
    await user.unblock()


@skip_not_logged
async def test_send_message_and_request():
    await user.send_friend_request('<gd.py>')
    await user.send('<gd.py>', message)
