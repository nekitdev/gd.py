from aiohttp import web

from gd.typing import Awaitable, Callable, TypeVar, Union

__all__ = ("AsyncHandler", "Handler", "Middleware")

T = TypeVar("T")

MaybeAwaitable = Union[T, Awaitable[T]]

AsyncHandler = Callable[[web.Request], Awaitable[web.StreamResponse]]
Handler = Callable[[web.Request], MaybeAwaitable[web.StreamResponse]]
Middleware = Callable[[web.Request, Handler], MaybeAwaitable[web.StreamResponse]]
