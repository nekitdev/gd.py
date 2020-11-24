from functools import wraps

from aiohttp import web
from multidict import istr

from gd.async_utils import maybe_coroutine
from gd.enums import Enum
from gd.typing import (
    Any, Awaitable, Callable, Mapping, Optional, Protocol, Type, TypeVar, Union
)
from gd.server.utils import json_response

__all__ = (
    "Error",
    "ErrorHandler",
    "ErrorResult",
    "ErrorType",
    "default_error_handler",
    "error_handler",
    "error_handling",
    "error_into_response",
)

T_co = TypeVar("T_co", covariant=True)


class FormatOrStr(Protocol[T_co]):
    def __str__(self: T_co) -> str:
        ...

    def __format__(self: T_co, format_spec: str) -> str:
        ...


Headers = Mapping[Union[istr, str], FormatOrStr]


class ErrorType(Enum):
    DEFAULT = 13000
    INVALID_ENTITY = 13001
    MISSING_PARAMETER = 13002
    FORBIDDEN = 13003
    NOT_FOUND = 13004
    FAILED = 13005
    LOGIN_FAILED = 13006
    RATE_LIMIT_EXCEEDED = 13007

    INVALID_AUTH = 13101
    MISSING_AUTH = 13102


class Error:
    def __init__(
        self,
        status_code: int = 500,
        error_type: Union[int, str, ErrorType] = ErrorType.DEFAULT,
        error: Optional[BaseException] = None,
        message: Optional[FormatOrStr] = None,
        headers: Optional[Headers] = None,
        include_error: bool = True,
    ) -> None:
        self.status_code = status_code
        self.error_type = ErrorType.from_value(error_type)
        self.error_unchecked = error
        self.message = message
        self.headers = headers
        self.include_error = include_error

    def get_error(self) -> BaseException:
        error_unchecked = self.error_unchecked

        if error_unchecked is None:
            raise ValueError("Exception is not set.")

        return error_unchecked

    def set_error(self, error: Optional[BaseException]) -> None:
        self.error_unchecked = error

    def delete_error(self) -> None:
        self.set_error(None)

    error = property(get_error, set_error, delete_error)

    def into_data(self) -> Mapping[str, Any]:
        error_unchecked = self.error_unchecked

        error: Optional[Mapping[str, Any]]

        if error_unchecked is None:
            error = None

        elif self.include_error:
            error = {
                "type": type(error_unchecked).__name__,
                "message": f"{error_unchecked}",
            }

        else:
            error = None

        data = {
            "error_name": self.error_type.title,
            "error_code": self.error_type.value,
            "message": self.message,
            "error": error,
        }

        return data

    def into_response(self, **kwargs) -> web.Response:
        kwargs.setdefault("status", self.status_code)
        kwargs.setdefault("headers", self.headers)

        return json_response(self.into_data(), **kwargs)


ErrorResult = Union[Error, web.StreamResponse]
ErrorResultTypes = (Error, web.StreamResponse)


def error_into_response(result: ErrorResult) -> web.StreamResponse:
    if isinstance(result, web.StreamResponse):
        return result

    return result.into_response()


# error handler function type
ErrorHandler = Callable[  # may be async, may be sync
    [web.Request, BaseException],  # (request: web.Request, error: BaseException)
    Union[ErrorResult, Awaitable[ErrorResult]],  # -> ErrorResult
]


def error_handler(handler: ErrorHandler) -> ErrorHandler:
    return handler


@error_handler
def default_error_handler(request: web.Request, error: BaseException) -> Error:
    return Error(error=error)


Handler = Callable[[web.Request], Union[web.StreamResponse, Awaitable[web.StreamResponse]]]
AsyncHandler = Callable[[web.Request], Awaitable[web.StreamResponse]]


async def call_default_handler(request: web.Request, error: BaseException) -> web.StreamResponse:
    return error_into_response(
        await maybe_coroutine(default_error_handler, request, error)
    )


def error_handling(
    handlers: Mapping[Type[BaseException], ErrorHandler], strict: bool = True
) -> Callable[[Handler], AsyncHandler]:
    def wrapper(handler: Handler) -> AsyncHandler:
        @wraps(handler)
        async def actual_handler(request: web.Request) -> web.StreamResponse:
            handler_coroutine = maybe_coroutine(handler, request)

            try:
                return await handler_coroutine

            except BaseException as error:  # noqa  # this is intentional
                for error_class, error_handler in handlers.items():
                    if isinstance(error, error_class):
                        try:
                            error_result = await maybe_coroutine(error_handler, request, error)

                        except Exception:
                            if strict:
                                raise error from None

                            return await call_default_handler(request, error)

                        if isinstance(error_result, ErrorResultTypes):
                            return error_into_response(error_result)

                        elif strict:
                            raise

                        else:
                            return await call_default_handler(request, error)

                if strict:
                    raise

                else:
                    return await call_default_handler(request, error)

        return actual_handler

    return wrapper
