from aiohttp import web
from multidict import istr

from gd.typing import Awaitable, Callable, Mapping, Protocol, Union

__all__ = ("Handler", "Headers", "Middleware", "ToString")


class ToString(Protocol):
    def __str__(self) -> str:
        ...


Handler = Callable[[web.Request], Awaitable[web.StreamResponse]]
Headers = Mapping[Union[istr, str], ToString]
Middleware = Callable[[web.Request, Handler], Awaitable[web.StreamResponse]]
