from aiohttp.web import Request, Response, json_response

from gd.errors import LoginFailed, MissingAccess
from gd.server.constants import (
    CLIENT,
    HTTP_BAD_REQUEST,
    HTTP_CREATED,
    HTTP_OK,
    HTTP_UNAUTHORIZED,
    QUERY,
    TOKEN,
    TOKENS,
)
from gd.server.core import docs
from gd.server.handler import Error, ErrorType, request_handler
from gd.server.routes import get, post
from gd.server.tokens import token
from gd.server.types import STRING
from gd.server.utils import parameter
from gd.typing import is_instance

__all__ = ("login", "logout")

LOGIN = "/login"

LOGIN_TAG = "login"
LOGIN_SUMMARY = "Login and fetch the token."
LOGIN_DESCRIPTION = "Perform login and acquire the token for further interactions."
LOGIN_NAME = "name"
LOGIN_NAME_EXAMPLE = "name"
LOGIN_NAME_DESCRIPTION = "The name of the user to login with."
LOGIN_PASSWORD = "password"
LOGIN_PASSWORD_EXAMPLE = "password"
LOGIN_PASSWORD_DESCRIPTION = "The password of the user to login with."

LOGIN_OK_DESCRIPTION = "The token to use for authorized requests."
LOGIN_CREATED_DESCRIPTION = "The token created to use for authorized requests."
LOGIN_BAD_REQUEST_DESCRIPTION = "Required parameters are missing."
LOGIN_UNAUTHORIZED = "Failed to login."

NAME = "name"
PASSWORD = "password"


@docs(
    tags=[LOGIN_TAG],
    summary=LOGIN_SUMMARY,
    description=LOGIN_DESCRIPTION,
    parameters=[
        parameter(
            QUERY,
            description=LOGIN_NAME_DESCRIPTION,
            name=LOGIN_NAME,
            schema=dict(type=STRING, example=LOGIN_NAME_EXAMPLE),
            required=True,
        ),
        parameter(
            QUERY,
            description=LOGIN_PASSWORD_DESCRIPTION,
            name=LOGIN_PASSWORD,
            schema=dict(type=STRING, example=LOGIN_PASSWORD_EXAMPLE),
            required=True,
        ),
    ],
    responses={
        HTTP_OK: dict(description=LOGIN_OK_DESCRIPTION),
        HTTP_BAD_REQUEST: dict(description=LOGIN_BAD_REQUEST_DESCRIPTION),
        HTTP_UNAUTHORIZED: dict(description=LOGIN_UNAUTHORIZED),
    },
)
@get(LOGIN, version=1)
@post(LOGIN, version=1)
@request_handler()
async def login(request: Request) -> Response:
    client = request.app[CLIENT]
    tokens = request.app[TOKENS]

    query = request.query

    name = query[NAME]
    password = query[PASSWORD]

    token = tokens.get_user(name, password)

    if token is None:
        token = tokens.register(name, password)
        status = HTTP_CREATED

    else:
        status = HTTP_OK

    await client.session.login(name, password)  # attempt login to check credentials

    return json_response(dict(token=token.string), status=status)


MISSING_PARAMETER = "missing {} parameter"


@login.error
async def login_error(request: Request, error: Exception) -> Error:
    if is_instance(error, LookupError):
        return Error(
            HTTP_BAD_REQUEST, ErrorType.MISSING_PARAMETER, MISSING_PARAMETER.format(tick(error))
        )

    if is_instance(error, LoginFailed):
        return Error(HTTP_UNAUTHORIZED, ErrorType.LOGIN_FAILED, str(error))

    return Error(message="Some unexpected error has occured.")


LOGOUT = "/logout"
LOGOUT_TAG = "logout"
LOGOUT_SUMMARY = "Log out and remove the token."
LOGOUT_DESCRIPTION = "Perform logout and remove the token from the database."
LOGOUT_OK_DESCRIPTION = "Succeffully logged out."


@docs(
    tags=[LOGOUT],
    summary=LOGOUT_SUMMARY,
    description=LOGOUT_DESCRIPTION,
    parameters=[],
    responses={HTTP_OK: dict(description=LOGOUT_OK_DESCRIPTION)},
)
@get(LOGOUT, version=1)
@post(LOGOUT, version=1)
@request_handler()
@token(required=True)
async def logout(request: Request) -> Response:
    tokens = request.app[TOKENS]

    token = request[TOKEN]

    tokens.remove(token)

    return json_response(dict())
