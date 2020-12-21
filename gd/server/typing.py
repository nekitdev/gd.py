from aiohttp import web

from gd.typing import Awaitable, Callable

__all__ = ("Handler", "Middleware")

Handler = Callable[[web.Request], Awaitable[web.StreamResponse]]
Middleware = Callable[[web.Request, Handler], Awaitable[web.StreamResponse]]
