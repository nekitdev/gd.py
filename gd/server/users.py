# Request handler decorators in the order they should be used:
#
# - decorators that modify or wrap functions they decorate;
# - decorators which leave functions they decorate untouched;
# - @request_handler() decorator (may be placed before transparent decorators);
# - @route(...) decorators that register routes and handlers;
# - @docs(...) decorator;
#
# If said order is followed, everything will work as intended.
#
# For example:
#
#     @docs(...)
#     @get("/path")
#     @request_handler()
#     async def handler(request: web.Request) -> web.Response:
#         ...
#
#     @handler.error
#     async def handler_error(request: web.Request, error: Exception) -> Error:
#         ...

from gd.enums import LeaderboardStrategy
from gd.errors import LoginRequired, MissingAccess
from gd.server.common import docs, web
from gd.server.handler import Error, ErrorType, request_handler
from gd.server.routes import get
from gd.server.token import token
from gd.server.types import bool_type, int_type, str_type
from gd.server.utils import json_response, parameter, parse_bool, parse_enum, parse_pages

__all__ = ("get_leaderboard", "get_self", "get_user", "search_user", "search_users")


@docs(
    tags=["get_self"],
    summary="Get user currently logged in.",
    parameters=[
        parameter(
            "query",
            description="Whether to return simple information, or load fully. Default is false.",
            name="simple",
            schema=dict(type=bool_type, example="false"),
            required=False,
        ),
    ],
    responses={
        200: dict(description="User fetched from the server."),
        401: dict(description="Unauthorized."),
        404: dict(description="User was not found."),
        422: dict(description="Invalid parameters were passed."),
    },
)
@get("/users/@me", version=1)
@request_handler()
@token(required=True)
async def get_self(request: web.Request) -> web.Response:
    client = request.app.client  # type: ignore
    token = request.token  # type: ignore

    simple = parse_bool(request.query.get("simple", "false"))

    async with token.into(client):
        user = client.user

        if not simple:
            await user.update()

        return json_response(user)


@get_self.error
async def get_self_error(request: web.Request, error: Exception) -> Error:
    if isinstance(error, ValueError):
        return Error(422, ErrorType.INVALID_ENTITY, "Can not parse <simple>.")

    if isinstance(error, MissingAccess):
        return Error(404, ErrorType.NOT_FOUND, "User was not found.")

    return Error(message="Some unexpected error has occurred.")


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
        parameter(
            "query",
            description="Whether to return simple information, or load fully. Default is false.",
            name="simple",
            schema=dict(type=bool_type, example="false"),
            required=False,
        )
    ],
    responses={
        200: dict(description="User fetched from the server."),
        404: dict(description="User was not found."),
        422: dict(description="Invalid parameters were passed."),
    },
)
@get("/users/{account_id}", version=1)
@request_handler()
async def get_user(request: web.Request) -> web.Response:
    client = request.app.client  # type: ignore

    account_id = int(request.match_info["account_id"])
    simple = parse_bool(request.query.get("simple", "false"))

    user = await client.get_user(account_id, simple=simple)

    return json_response(user)


@get_user.error
async def get_user_error(request: web.Request, error: Exception) -> Error:
    if isinstance(error, ValueError):
        return Error(422, ErrorType.INVALID_ENTITY, "Can not parse <account_id> or <simple>.")

    if isinstance(error, MissingAccess):
        return Error(404, ErrorType.NOT_FOUND, "User was not found.")

    return Error(message="Some unexpected error has occurred.")


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
        parameter(
            "query",
            description="Whether to return simple information, or load fully. Default is false.",
            name="simple",
            schema=dict(type=bool_type, example="false"),
            required=False,
        )
    ],
    responses={
        200: dict(description="User fetched from the server."),
        404: dict(description="User was not found."),
        422: dict(description="Invalid parameters were passed."),
    },
)
@get("/users/find/{query}", version=1)
@request_handler()
async def search_user(request: web.Request) -> web.Response:
    client = request.app.client  # type: ignore

    query = request.match_info["query"]
    simple = parse_bool(request.query.get("simple", "false"))

    user = await client.search_user(query, simple=simple)

    return json_response(user)


@search_user.error
async def search_user_error(request: web.Request, error: Exception) -> Error:
    if isinstance(error, ValueError):
        return Error(422, ErrorType.INVALID_ENTITY, "Can not parse <simple> to bool.")

    if isinstance(error, MissingAccess):
        return Error(404, ErrorType.NOT_FOUND, "User was not found.")

    return Error(message="Some unexpected error has occured.")


@docs(
    tags=["search_users"],
    summary="Search users given by query.",
    description="Search users given by query, either ID or name.",
    parameters=[
        parameter(
            "path",
            description="ID or name of users.",
            name="query",
            schema=dict(type=str_type, example="Player"),
            required=True,
        ),
        parameter(
            "query",
            description="Pages to look on. If not provided, default values are used.",
            name="pages",
            schema=dict(type=str_type),
            required=False,
        ),
    ],
    responses={200: dict(description="Users fetched from the server. Can be empty.")},
)
@get("/users/search/{query}", version=1)
@request_handler()
async def search_users(request: web.Request) -> web.Response:
    client = request.app.client  # type: ignore

    query = request.match_info["query"]

    pages_string = request.query.get("pages")

    if pages_string is None:
        users = await client.search_users(query).list()

    else:
        pages = parse_pages(pages_string)

        users = await client.search_users(query, pages=pages).list()

    return json_response(users)


@search_users.error
async def search_users_error(request: web.Request, error: Exception) -> Error:
    if isinstance(error, ValueError):
        return Error(422, ErrorType.INVALID_ENTITY, "Can not parse <pages> parameter.")

    return Error(message="Some unexpected error has occurred.")


@docs(
    tags=["get_leaderboard"],
    summary="Get user leaderboard.",
    description="Get user leaderboard with given strategy.",
    parameters=[
        parameter(
            "query",
            description="Amount of users to fetch. Default is 100.",
            name="amount",
            schema=dict(type=int_type, example=100),
            required=False,
        ),
        parameter(
            "query",
            description="Strategy of the leaderboard. Default is top.",
            name="strategy",
            schema=dict(type=str_type, example="top"),
            required=False,
        ),
    ],
    responses={
        200: dict(description="Users fetched from the server. Can be empty."),
        401: dict(description="Authorization is required but is missing."),
        422: dict(description="Given strategy or amount is invalid."),
    },
)
@get("/users/leaderboard", version=1)
@get("/users/top", version=1)
@request_handler()
async def get_leaderboard(request: web.Request) -> web.Response:
    client = request.app.client  # type: ignore

    amount = int(request.query.get("amount", 100))
    strategy = parse_enum(request.query.get("strategy", "top"), LeaderboardStrategy, int)

    leaderboard = await client.get_leaderboard(strategy, amount=amount).list()

    return json_response(leaderboard)


@get_leaderboard.error
async def get_leaderboard_error(request: web.Request, error: Exception) -> Error:
    if isinstance(error, ValueError):
        return Error(422, ErrorType.INVALID_ENTITY, "Can not parse <amount> or <strategy>.")

    if isinstance(error, LoginRequired):
        return Error(401, ErrorType.UNAUTHORIZED, "Authorization is required but is missing.")

    if isinstance(error, MissingAccess):
        return Error(404, ErrorType.NOT_FOUND, "Can not fetch the leaderboard.")

    return Error(message="Some unexpected error has occurred.")
