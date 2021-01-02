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
#     @docs()
#     @get("/path")
#     @request_handler()
#     async def handler(request: web.Request) -> web.Response:
#         ...
#
#     @handler.error
#     async def handler_error(request: web.Request, error: Exception) -> Error:
#         ...

from gd.errors import MissingAccess, SongRestricted
from gd.server.routes import get
from gd.server.common import docs, web
from gd.server.handler import Error, ErrorType, request_handler
from gd.server.types import int_type
from gd.server.utils import json_response, parameter

__all__ = ("get_artist_info", "get_song")


@docs(
    tags=["get_song"],
    summary="Get song given by ID.",
    parameters=[
        parameter(
            "path",
            description="ID of the song.",
            name="id",
            schema=dict(type=int_type, example=1),
            required=True,
        ),
    ],
    responses={
        200: dict(description="Song fetched from the server."),
        403: dict(description="Song is not allowed for use."),
        404: dict(description="Song was not found."),
        422: dict(description="Invalid ID was passed."),
    },
)
@get("/song/{id}", version=1)
@request_handler()
async def get_song(request: web.Request) -> web.Response:
    client = request.app.client  # type: ignore

    id = int(request.match_info["id"])

    song = await client.get_song(id)

    return json_response(song)


@get_song.error
async def get_song_error(request: web.Request, error: Exception) -> Error:
    if isinstance(error, ValueError):
        return Error(422, ErrorType.INVALID_ENTITY, "Can not parse <id> to int.")

    if isinstance(error, SongRestricted):
        return Error(403, ErrorType.FORBIDDEN, "Song is not allowed for use.")

    if isinstance(error, MissingAccess):
        return Error(404, ErrorType.NOT_FOUND, "Song was not found.")

    return Error(message="Some unexpected error has occurred.")


@docs(
    tags=["get_artist_info"],
    summary="Get artist information given by song ID.",
    parameters=[
        parameter(
            "path",
            description="ID of the song.",
            name="id",
            schema=dict(type=int_type, example=1),
            required=True,
        ),
    ],
    responses={
        200: dict(description="Artist information fetched from the server."),
        404: dict(description="Song was not found."),
        422: dict(description="Invalid ID was passed."),
    },
)
@get("/song/{id}/info", version=1)
@request_handler()
async def get_artist_info(request: web.Request) -> web.Response:
    client = request.app.client  # type: ignore

    id = int(request.match_info["id"])

    artist_info = await client.get_artist_info(id)

    return json_response(artist_info)


@get_artist_info.error
async def get_artist_info_error(request: web.Request, error: Exception) -> Error:
    if isinstance(error, ValueError):
        return Error(422, ErrorType.INVALID_ENTITY, "Can not parse <id> to int.")

    if isinstance(error, MissingAccess):
        return Error(404, ErrorType.NOT_FOUND, "Song was not found.")

    return Error(message="Some unexpected error has occurred.")
