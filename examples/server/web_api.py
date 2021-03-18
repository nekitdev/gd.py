"""Simple web server with aiohttp, which can retrieve info about users and return JSON responses.
See "https://docs.aiohttp.org/en/stable/web_quickstart.html" for more information.
Author: nekitdev
"""

from functools import partial

from aiohttp import web

import gd

# create our client instance
client = gd.Client()

# create a sequence of route table definitions
routes = web.RouteTableDef()

json_response = partial(web.json_response, dumps=partial(gd.utils.dumps, indent=4))


# let our app listen to GET requests
@routes.get("/api/users/{query}")
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

        return json_response(user)

    # return 404 if we have not found any users
    except Exception:
        raise json_response(
            {"error": f"Failed to find a user by the query: {query!r}"}, status=404
        )


# initialize an application
app = web.Application()

# add routes
app.add_routes(routes)

print("Go to http://localhost:8080/api/users/RobTop to see info about RobTop.")

# run the app
web.run_app(app)
