from gd.server.common import web
from gd.server.handler import (
    HTTP_STATUS_TO_ERROR_TYPE, Error, ErrorHandler, ErrorType, error_result_into_response
)
from gd.server.typing import Handler, Middleware
from gd.typing import Mapping, Optional, cast

__all__ = ("status_error_middleware",)


def status_error_middleware(config: Optional[Mapping[str, ErrorHandler]] = None) -> Middleware:
    if config is None:
        config = cast(Mapping[str, ErrorHandler], {})

    @web.middleware
    async def status_error_handler(request: web.Request, handler: Handler) -> web.StreamResponse:
        try:
            return await handler(request)

        except web.HTTPError as error:
            if config:
                request_path = request.rel_url.path

                for path, error_handler in config.items():
                    if request_path.startswith(path):
                        return error_result_into_response(await error_handler(request, error))

            status = error.status

            error_type = HTTP_STATUS_TO_ERROR_TYPE.get(status, ErrorType.DEFAULT)

            return Error(status, error_type, f"{status}: {error.reason}").into_response()

    return status_error_handler
