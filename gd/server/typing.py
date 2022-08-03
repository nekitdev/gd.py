from abc import abstractmethod
from typing import Any, Awaitable, TypeVar
from typing_extensions import Protocol

from aiohttp.web import Application, Request, Response, StreamResponse

from gd.typing import Binary, StringMapping, Unary

__all__ = (
    "GenericHandler",
    "GenericMiddleware",
    "StreamHandler",
    "StreamMiddleware",
    "Handler",
    "Middleware",
    "Headers",
    "Tool",
)

In = TypeVar("In", bound=Request)
Out = TypeVar("Out", bound=StreamResponse)

GenericHandler = Unary[In, Awaitable[Out]]
GenericMiddleware = Binary[In, GenericHandler[In, Out], Awaitable[Out]]

StreamHandler = GenericHandler[Request, StreamResponse]
StreamMiddleware = GenericMiddleware[Request, StreamResponse]

Handler = GenericHandler[Request, Response]
Middleware = GenericMiddleware[Request, Response]

Headers = StringMapping[Any]


class Tool(Protocol):
    @abstractmethod
    async def setup(self, app: Application) -> None:
        ...
