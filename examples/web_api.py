"""Simple web server with aiohttp, which can retrieve info about users and return JSON responses.
See "https://docs.aiohttp.org/en/stable/web_quickstart.html" for more information.
Author: NeKitDS
"""

from aiohttp import web
import gd

# create our client instance
client = gd.Client()


def make_user_dict(user):
    """Create JSON-resizable dictionary containing user info."""
    icon = user.icon_set
    return {
        'name': user.name, 'id': user.id, 'account_id': user.account_id,
        'stars': user.stars, 'demons': user.demons, 'coins': user.coins,
        'user_coins': user.user_coins, 'cp': user.cp, 'diamonds': user.diamonds,
        'is_mod': user.is_mod(), 'status': user.role.value, 'rank': user.rank,
        'messages': user.msg_policy.value,
        'friend_requests': user.friend_req_policy.value,
        'comments': user.comments_policy.value,
        'youtube': user.youtube_link, 'twitter': user.twitter_link, 'twitch': user.twitch_link,
        'color_1': icon.color_1.value, 'color_2': icon.color_2.value,
        'main_icon_type': icon.main_type.value, 'has_glow_outline': icon.has_glow_outline(),
        'cube': icon.cube, 'ship': icon.ship, 'ball': icon.ball, 'ufo': icon.ufo,
        'wave': icon.wave, 'robot': icon.robot, 'spider': icon.spider
    }

# create a sequence of route table definitions
routes = web.RouteTableDef()

# let our app listen to GET requests
@routes.get('/api/user/{query}')
async def get_user(request):
    try:
        req = request.match_info.get('query')
        # try to convert query to an integer
        query = gd.utils.convert_to_type(req, int, str)

        # if we have an integer query, consider AccountID search
        if isinstance(query, int):
            user = await client.get_user(query)
        # if we have a string, do regular search
        else:
            user = await client.search_user(query)

        # return JSON response
        return web.json_response(make_user_dict(user))

    # return 404 if we have not found any users
    except Exception:
        raise web.HTTPNotFound(text='Failed to find a user by the query: {!r}'.format(query))

# initialize an application
app = web.Application()

# add routes
app.add_routes(routes)

# run the app
web.run_app(app)
