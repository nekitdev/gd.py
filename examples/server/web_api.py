"""Simple web server with aiohttp, which can retrieve info about users and return JSON responses.
See "https://docs.aiohttp.org/en/stable/web_quickstart.html" for more information.
Author: nekitdev
"""

from aiohttp import web
import gd

# create our client instance
client = gd.Client()

# create a sequence of route table definitions
routes = web.RouteTableDef()


def json_resp(item: object, **kwargs) -> str:
    # enforce <application/json> content type
    kwargs.update(content_type="application/json")
    # gd.py introduces gd.utils.dump method, used
    # for conveniently converting its objects to
    # JSON-resizable dictionaries
    return web.Response(text=gd.utils.dumps(item, indent=4), **kwargs)


# let our app listen to GET requests
@routes.get("/api/user/{query}")
async def get_user(request):
    try:
        query = request.match_info.get("query")

        if query.isdigit():  # if we have an integer query, consider AccountID search
            try:
                user = await client.get_user(int(query))

            except gd.MissingAccess:  # not found, attempt UserID search
                user = await client.search_user(int(query))

        # if we have a string, do regular search
        else:
            user = await client.search_user(query)

        return json_resp(user)

    # return 404 if we have not found any users
    except Exception:
        raise json_resp({"error": f"Failed to find a user by the query: {query!r}"}, status=404)


# initialize an application
app = web.Application()

# add routes
app.add_routes(routes)

print("Go to http://127.0.0.1:8080/api/user/RobTop to see info about RobTop.")

# run the app
web.run_app(app)
