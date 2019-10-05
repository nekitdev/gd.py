"""Simple web server with aiohttp, which can retrieve info about users and return JSON responses.
Author: NeKitDS
"""

from aiohttp import web
import gd

client = gd.Client()


def make_user_dict(user):
    return {
        'name': user.name,
        'id': user.id,
        'account_id': user.account_id,
        'stars': user.stars,
        'demons': user.demons,
        'coins': user.coins,
        'user_coins': user.user_coins,
        'cp': user.cp,
        'diamonds': user.cp,
        'is_mod': user.is_mod(),
        'status': user.role.value,
        'rank': user.rank,
        'messages': user.msg_policy.value,
        'friend_requests': user.friend_req_policy.value,
        'comments': user.comments_policy.value,
        'color_1': user.icon_set.color_1.value,
        'color_2': user.icon_set.color_2.value
    }


routes = web.RouteTableDef()

@routes.get('/api/user/{query}')
async def get_user(request):
    try:
        req = request.match_info.get('query')
        query = gd.utils.convert_to_type(req, int, str)

        if isinstance(query, int):
            user = await client.get_user(query)
        else:
            user = await client.search_user(query)

        return web.json_response(make_user_dict(user))

    except Exception:
        raise web.HTTPNotFound(text='Failed to find a user by the query: {!r}'.format(query))


app = web.Application()

app.add_routes(routes)

web.run_app(app)
