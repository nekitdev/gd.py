from typing import Any

from aiohttp.web import RouteTableDef
from yarl import URL

from gd.constants import SLASH
from gd.server.constants import PREFIX, VERSION, VERSION_FORMAT
from gd.server.typing import StreamHandler
from gd.typing import DecoratorIdentity

__all__ = ("ROUTES", "get_route", "delete", "get", "head", "patch", "post", "put", "static")

ROUTES = RouteTableDef()


def get_route(
    route: str, version: int = VERSION, prefix: str = PREFIX, version_format: str = VERSION_FORMAT
) -> str:
    return (URL(prefix) / version_format.format(version) / route.strip(SLASH)).human_repr()


def get(
    route: str,
    version: int = VERSION,
    prefix: str = PREFIX,
    version_format: str = VERSION_FORMAT,
    routes: RouteTableDef = ROUTES,
    **kwargs: Any,
) -> DecoratorIdentity[StreamHandler]:
    return routes.get(get_route(route, version, prefix, version_format), **kwargs)


def post(
    route: str,
    version: int = VERSION,
    prefix: str = PREFIX,
    version_format: str = VERSION_FORMAT,
    routes: RouteTableDef = ROUTES,
    **kwargs: Any,
) -> DecoratorIdentity[StreamHandler]:
    return routes.post(get_route(route, version, prefix, version_format), **kwargs)


def head(
    route: str,
    version: int = VERSION,
    prefix: str = PREFIX,
    version_format: str = VERSION_FORMAT,
    routes: RouteTableDef = ROUTES,
    **kwargs: Any,
) -> DecoratorIdentity[StreamHandler]:
    return routes.head(get_route(route, version, prefix, version_format), **kwargs)


def put(
    route: str,
    version: int = VERSION,
    prefix: str = PREFIX,
    version_format: str = VERSION_FORMAT,
    routes: RouteTableDef = ROUTES,
    **kwargs: Any,
) -> DecoratorIdentity[StreamHandler]:
    return routes.put(get_route(route, version, prefix, version_format), **kwargs)


def patch(
    route: str,
    version: int = VERSION,
    prefix: str = PREFIX,
    version_format: str = VERSION_FORMAT,
    routes: RouteTableDef = ROUTES,
    **kwargs: Any,
) -> DecoratorIdentity[StreamHandler]:
    return routes.patch(get_route(route, version, prefix, version_format), **kwargs)


def delete(
    route: str,
    version: int = VERSION,
    prefix: str = PREFIX,
    version_format: str = VERSION_FORMAT,
    routes: RouteTableDef = ROUTES,
    **kwargs: Any,
) -> DecoratorIdentity[StreamHandler]:
    return routes.delete(get_route(route, version, prefix, version_format), **kwargs)


def static(*, routes: RouteTableDef = ROUTES, **kwargs: Any) -> None:
    return routes.static(**kwargs)
