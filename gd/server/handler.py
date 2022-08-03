from typing import Any, Awaitable, Optional, TypeVar, Union

from aiohttp.web import Request, Response, StreamResponse, json_response
from attrs import define, field, frozen
from typing_extensions import Never, TypedDict

from gd.enum_extensions import Enum
from gd.server.constants import (
    HTTP_FORBIDDEN,
    HTTP_INTERNAL_SERVER_ERROR,
    HTTP_NOT_FOUND,
    HTTP_TOO_MANY_REQUESTS,
    HTTP_UNAUTHORIZED,
    HTTP_UNPROCESSABLE_ENTITY,
)
from gd.server.typing import Headers, StreamHandler
from gd.typing import AnyException, AnyExceptionType, Binary, Decorator, DynamicTuple, Namespace, is_instance

__all__ = (
    "HTTP_STATUS_TO_ERROR_TYPE",
    # error handling
    "Error",
    "ErrorHandler",
    "ErrorResult",
    "default_error_handler",
    # request handling
    "RequestHandler",
    "request_handler",
    # utils for handling dynamic typing
    "error_result_into_response",
)


class ErrorType(Enum):
    DEFAULT = 13000

    INVALID_ENTITY = 13001
    MISSING_PARAMETER = 13002
    FORBIDDEN = 13003
    NOT_FOUND = 13004
    FAILED = 13005

    UNAUTHORIZED = 13101
    LOGIN_FAILED = 13102

    RATE_LIMITED = 13201

    AUTH_INVALID = 13301
    AUTH_MISSING = 13302
    AUTH_NOT_SET = 13303


HTTP_STATUS_TO_ERROR_TYPE = {
    HTTP_UNAUTHORIZED: ErrorType.UNAUTHORIZED,
    HTTP_FORBIDDEN: ErrorType.FORBIDDEN,
    HTTP_NOT_FOUND: ErrorType.NOT_FOUND,
    HTTP_UNPROCESSABLE_ENTITY: ErrorType.INVALID_ENTITY,
    HTTP_TOO_MANY_REQUESTS: ErrorType.RATE_LIMITED,
}


class ErrorData(TypedDict):
    code: int
    type: str
    message: Optional[str]


DEFAULT_STATUS_CODE = HTTP_INTERNAL_SERVER_ERROR
DEFAULT_ERROR_TYPE = ErrorType.DEFAULT


@frozen()
class Error:
    status: int = DEFAULT_STATUS_CODE
    type: ErrorType = DEFAULT_ERROR_TYPE
    message: Optional[str] = None
    headers: Optional[Headers] = None

    def into_data(self) -> ErrorData:
        return ErrorData(code=self.type.value, type=self.type.name, message=self.message)

    def into_response(self, **keywords: Any) -> Response:
        keywords.update(status=self.status, headers=self.headers)

        return json_response(self.into_data(), **keywords)


ErrorExcept = Union[AnyExceptionType, DynamicTuple[AnyExceptionType]]
ErrorResult = Union[Error, StreamResponse]
ErrorReturn = Union[Never, ErrorResult]

ErrorHandler = Binary[Request, AnyException, Awaitable[ErrorReturn]]


def error_result_into_response(error_result: ErrorResult) -> StreamResponse:
    if is_instance(error_result, Error):
        return error_result.into_response()

    if is_instance(error_result, StreamResponse):
        return error_result

    raise ValueError  # TODO: message?


UNEXPECTED_ERROR = "Some unexpected error has occured."


async def default_error_handler(request: Request, error: AnyException) -> Error:
    return Error(message=UNEXPECTED_ERROR)


EH = TypeVar("EH", bound="ErrorHandler")


@define(slots=False)
class RequestHandler:
    handler: StreamHandler
    error_except: ErrorExcept = Exception
    error_handler: ErrorHandler = default_error_handler

    async def __call__(self, request: Request) -> StreamResponse:
        try:
            return await self.handler(request)

        except self.error_except as error:
            error_result = await self.error_handler(request, error)

            return error_result_into_response(error_result)

    def error(self, error_handler: EH) -> EH:
        self.error_handler = error_handler

        return error_handler


def request_handler(
    error_except: ErrorExcept = Exception,
) -> Decorator[StreamHandler, RequestHandler]:
    def wrapper(handler: StreamHandler) -> RequestHandler:
        return RequestHandler(handler, error_except=error_except)

    return wrapper
