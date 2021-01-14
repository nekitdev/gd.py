from gd.enums import FriendRequestType, RelationshipType
from gd.errors import MissingAccess
from gd.server.common import docs, web
from gd.server.handler import Error, ErrorType, request_handler
from gd.server.routes import get
from gd.server.token import token
from gd.server.types import str_type
from gd.server.utils import json_response, parameter, parse_enum, parse_pages

__all__ = ("get_relationships",)


@docs(
    tags=["get_relationships"],
    summary="Get relationships.",
    description="Fetch all relationships of the user.",
    parameters=[
        parameter(
            "query",
            description="Type of the relationship, default is friend.",
            name="type",
            schema=dict(type=str_type, default="friend"),
            required=False,
        ),
        parameter(
            "query",
            description="Pages to look on. If not provided, default values are used.",
            name="pages",
            schema=dict(type=str_type),
            required=False,
        ),
    ],
    responses={
        200: dict(description="Relationships fetched from the server. Can be empty."),
        401: dict(description="Authorization is required but is missing."),
        404: dict(description="Failed to fetch relationships."),
        422: dict(description="Invalid relationship type was passed."),
    },
)
@get("/users/@me/relationships", version=1)
@request_handler()
@token(required=True)
async def get_relationships(request: web.Request) -> web.Response:
    client = request.app.client  # type: ignore
    token = request.token  # type: ignore

    type = parse_enum(request.query.get("type", "friend"), RelationshipType, int)
    pages_string = request.query.get("pages")

    async with token.into(client):
        if type is RelationshipType.FRIEND:
            relationships = await client.get_friends()

        if type is RelationshipType.BLOCKED:
            relationships = await client.get_blocked()

        if type is RelationshipType.INCOMING_REQUEST:
            if pages_string is None:
                relationships = await client.get_friend_requests(type=FriendRequestType.INCOMING)

            else:
                pages = parse_pages(pages_string)

                relationships = await client.get_friend_requests(
                    type=FriendRequestType.INCOMING, pages=pages
                )

        if type is RelationshipType.OUTGOING_REQUEST:
            if pages_string is None:
                relationships = await client.get_friend_requests(type=FriendRequestType.OUTGOING)

            else:
                pages = parse_pages(pages_string)

                relationships = await client.get_friend_requests(
                    type=FriendRequestType.OUTGOING, pages=pages
                )

    return json_response(relationships)


@get_relationships.error
async def get_relationships_error(request: web.Request, error: Exception) -> Error:
    if isinstance(error, ValueError):
        return Error(422, ErrorType.INVALID_ENTITY, "Can not parse <type> parameter.")

    if isinstance(error, MissingAccess):
        return Error(404, ErrorType.NOT_FOUND, "Can not fetch relationships.")

    return Error(message="Some unexpected error has occurred.")
