from gd.errors import MissingAccess
from gd.typing import Optional, Union

from gd.server.core import client, docs, routes, web
from gd.server.error import Error, ErrorHandler, ErrorType, error_handler, error_handling
from gd.server.types import int_type, str_type
from gd.server.utils import get_pages, json_response, parameter

__all__ = ("get_user", "search_user")


@error_handler
def handle_value_error(request: web.Request, error: BaseException) -> Error:
    return Error(422, ErrorType.INVALID_ENTITY, error=error)


def handle_missing_access(
    status_code: int, error_type: Union[int, str, ErrorType], message: Optional[str] = None
) -> ErrorHandler:
    @error_handler
    def actual_handler(request: web.Request, error: BaseException) -> Error:
        return Error(status_code, error_type, error=error, message=message)

    return actual_handler


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
    responses={
        200: dict(description="User fetched from the server."),
        404: dict(description="User was not found."),
        422: dict(description="Invalid Account ID was passed."),
    }
)
@routes.get("/api/user/{account_id}")
@error_handling(
    {
        ValueError: handle_value_error,
        MissingAccess: handle_missing_access(404, ErrorType.NOT_FOUND),
    }
)
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
    responses={
        200: dict(description="User fetched from the server."),
        404: dict(description="User was not found."),
    }
)
@routes.get("/api/search/user/{query}")
@error_handling({MissingAccess: handle_missing_access(404, ErrorType.NOT_FOUND)})
async def search_user(request: web.Request) -> web.Response:
    query = request.match_info["query"]

    user = await client.search_user(query)

    return json_response(user)


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
    ],
    responses={
        200: dict(description="Users fetched from the server. Can be empty."),
        422: dict(description="Invalid pages parameter was passed."),
    }
)
@routes.get("/api/search/users/{query}")
@error_handling({ValueError: handle_value_error})
async def search_users(request: web.Request) -> web.Response:
    query = request.match_info["query"]

    pages_string = request.query.get("pages")

    if pages_string:
        pages = get_pages(pages_string)

        users = await client.search_users(query, pages=pages).list()

    else:
        users = await client.search_users(query).list()

    return json_response(users)
