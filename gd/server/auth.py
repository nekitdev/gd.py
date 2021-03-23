from gd.errors import LoginFailure
from gd.server.common import docs, web
from gd.server.handler import Error, ErrorType, request_handler
from gd.server.routes import get, post
from gd.server.token import token
from gd.server.types import str_type
from gd.server.utils import json_response, parameter

__all__ = ("login", "logout")


@docs(
    tags=["login"],
    summary="Login and get token.",
    description="Perform login and acquire token for further interactions.",
    parameters=[
        parameter(
            "query",
            description="Name of the account to log into.",
            name="name",
            schema=dict(type=str_type, example="User"),
            required=True,
        ),
        parameter(
            "query",
            description="Password of the account to log into.",
            name="password",
            schema=dict(type=str_type, example="Password"),
            required=True,
        ),
    ],
    responses={
        200: dict(description="Token to use for authorized requests."),
        400: dict(description="Required parameters are missing."),
        401: dict(description="Failed to login and check credentials."),
    }
)
@get("/login", version=1)
@post("/login", version=1)
@request_handler()
async def login(request: web.Request) -> web.Response:
    client = request.app.client  # type: ignore
    token_database = request.app.token_database  # type: ignore

    name = request.query["name"]
    password = request.query["password"]

    token = token_database.get_user(name, password)

    if token is None:
        token = token_database.register(name, password)
        status = 201  # new token was inserted, so we return "created" status

    else:
        status = 200  # old token is used, so we return simple "ok" status

    await client.session.login(name, password)  # attempt login to check credentials

    await token.load(client, force=True)

    return json_response(dict(token=token.string), status=status)


@login.error
async def login_error(request: web.Request, error: Exception) -> Error:
    if isinstance(error, LookupError):
        return Error(400, ErrorType.MISSING_PARAMETER, f"Missing {error!s} parameter.")

    if isinstance(error, LoginFailure):
        return Error(401, ErrorType.LOGIN_FAILED, f"{error}")

    return Error(message="Some unexpected error has occured.")


@docs(
    tags=["logout"],
    summary="Logout and remove token.",
    description="Perform logout and remove token from the database.",
    parameters=[],
    responses={200: dict(description="Successfully logged out.")}
)
@get("/logout", version=1)
@post("/logout", version=1)
@request_handler()
@token(required=True)
async def logout(request: web.Request) -> web.Response:
    token_database = request.app.token_database  # type: ignore

    token = request.token  # type: ignore

    token_database.remove(token)

    return json_response({})
