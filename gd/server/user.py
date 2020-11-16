from gd.server.core import client, docs, routes, web
from gd.server.types import int_type
from gd.server.utils import json_response, parameter

__all__ = ("get_user",)


@docs(
    tags=["get_user"],
    summary="Get user given by Account ID.",
    parameters=[
        parameter(
            "path",
            description="Account ID of the user.",
            name="account_id",
            schema=dict(type=int_type, example=13),
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
