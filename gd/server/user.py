from gd.server.core import client, docs, routes, web
from gd.server.types import int_type, str_type
from gd.server.utils import json_response, parameter

__all__ = ("get_user", "search_user")


@docs(
    tags=["get_user"],
    summary="Get user given by Account ID.",
    parameters=[
        parameter(
            "path",
            description="Account ID of the user.",
            name="account_id",
            schema=dict(type=int_type, example=1),
            required=True,
        ),
    ],
    responses={200: dict(description="User fetched from the server.")}
)
@routes.get("/api/user/{account_id}")
async def get_user(request: web.Request) -> web.Response:
    account_id = int(request.match_info["account_id"])

    user = await client.get_user(account_id)

    return json_response(user)


@docs(
    tags=["search_user"],
    summary="Search user given by query.",
    description="Search user given by query, either ID or name.",
    parameters=[
        parameter(
            "path",
            description="ID or name of the user.",
            name="query",
            schema=dict(type=str_type, example="Player"),
            required=True,
        ),
    ],
    responses={200: dict(description="User fetched from the server.")}
)
@routes.get("/api/search/user/{query}")
async def search_user(request: web.Request) -> web.Response:
    query = request.match_info["query"]

    user = await client.search_user(query)

    return json_response(user)
