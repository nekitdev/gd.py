from datetime import datetime
import pytest

from conftest import client

# PREPARATIONS

pytestmark = pytest.mark.asyncio
user = client.run(client.search_user('NeKitDS'))

message = ('[gd.py] ({}): Running tests...'.format(datetime.utcnow()))


# MAIN TESTS

async def test_properties():
    user.stars
    user.demons
    user.cp
    user.diamonds
    user.coins
    user.user_coins
    user.lb_place
    user.role
    user.rank
    user.youtube
    user.youtube_link
    user.twitter
    user.twitter_link
    user.twitch
    user.twitch_link
    user.msg_policy
    user.friend_req_policy
    user.comments_policy
    user.icon_set

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


async def test_get_comments():
    await user.get_comments()


async def test_get_comment_history():
    await user.get_comment_history()


async def test_as_user():
    user.as_user()


async def test_abstractuser_update():
    abstract = user.as_user()
    await abstract.update()


skip_not_logged = pytest.mark.skipif(
    not client.is_logged(), reason='Test for only logged in client.'
)


@skip_not_logged
async def test_block():
    await user.block()
    await user.unblock()


# @skip_not_logged
# async def test_send_message_and_request():
#     await user.send_friend_request('gd.py test')
#     await user.send('gd.py test', message)


@skip_not_logged
async def test_unfriend():
    await user.unfriend()


# @skip_not_logged
# async def test_levelrecord():
#     temp_level = await client.get_level(30029017)
#     leaderboard = await temp_level.get_leaderboard(1)
#     entry = leaderboard[0]

#     entry.level_id
#     entry.percentage
#     entry.coins
#     entry.timestamp
#     entry.lb_place
#     entry.type

#     await entry.update()
