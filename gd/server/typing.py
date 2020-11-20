from aiohttp import web

from gd.typing import Awaitable, Callable, TypeVar, Union

__all__ = ("Handler", "Middleware")

T = TypeVar("T")

MaybeAwaitable = Union[T, Awaitable[T]]

Handler = Callable[[web.Request], MaybeAwaitable[web.StreamResponse]]
Middleware = Callable[[web.Request, Handler], MaybeAwaitable[web.StreamResponse]]
