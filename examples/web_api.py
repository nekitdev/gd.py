"""Simple web server with aiohttp, which can retrieve info about users and return JSON responses.
See "https://docs.aiohttp.org/en/stable/web_quickstart.html" for more information.
Author: NeKitDS
"""

from aiohttp import web
import gd

# create our client instance
client = gd.Client()

# create a sequence of route table definitions
routes = web.RouteTableDef()


def json_resp(item: object, **kwargs) -> str:
    # enforce <application/json> content type
    kwargs.update(content_type='application/json')
    # gd.py introduces gd.utils.dump method, used
    # for conveniently converting its objects to
    # JSON-resizable dictionaries
    return web.Response(text=gd.utils.dump(item, indent=4), **kwargs)


# let our app listen to GET requests
@routes.get('/api/user/{query}')
async def get_user(request):
    try:
        req = request.match_info.get('query')
        # try to convert query to an integer
        try:
            query = int(req)
        except ValueError:
            query = str(req)

        # if we have an integer query, consider AccountID search
        if isinstance(query, int):
            user = await client.get_user(query)
        # if we have a string, do regular search
        else:
            user = await client.search_user(query)

        return json_resp(user)

    # return 404 if we have not found any users
    except Exception:
        raise web.HTTPNotFound(text='Failed to find a user by the query: {!r}'.format(query))

# initialize an application
app = web.Application()

# add routes
app.add_routes(routes)

# run the app
web.run_app(app)
