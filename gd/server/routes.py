from gd.server.common import URL, web
from gd.server.typing import Handler
from gd.typing import Callable, Optional

__all__ = ("get_route", "routes", "delete", "get", "head", "patch", "post", "put", "static")

routes = web.RouteTableDef()


def get_route(
    route: str, version: Optional[int] = None, prefix: str = "/api", version_format: str = "v{}"
) -> str:
    route = route.strip("/")

    if version is None:
        return (URL(prefix) / route).human_repr()

    return (URL(prefix) / version_format.format(version) / route).human_repr()


def get(
    route: str,
    version: Optional[int] = None,
    prefix: str = "/api",
    version_format: str = "v{}",
    routes: web.RouteTableDef = routes,
    **kwargs,
) -> Callable[[Handler], Handler]:
    return routes.get(get_route(route, version, prefix, version_format), **kwargs)


def post(
    route: str,
    version: Optional[int] = None,
    prefix: str = "/api",
    version_format: str = "v{}",
    routes: web.RouteTableDef = routes,
    **kwargs,
) -> Callable[[Handler], Handler]:
    return routes.post(get_route(route, version, prefix, version_format), **kwargs)


def head(
    route: str,
    version: Optional[int] = None,
    prefix: str = "/api",
    version_format: str = "v{}",
    routes: web.RouteTableDef = routes,
    **kwargs,
) -> Callable[[Handler], Handler]:
    return routes.head(get_route(route, version, prefix, version_format), **kwargs)


def put(
    route: str,
    version: Optional[int] = None,
    prefix: str = "/api",
    version_format: str = "v{}",
    routes: web.RouteTableDef = routes,
    **kwargs,
) -> Callable[[Handler], Handler]:
    return routes.put(get_route(route, version, prefix, version_format), **kwargs)


def patch(
    route: str,
    version: Optional[int] = None,
    prefix: str = "/api",
    version_format: str = "v{}",
    routes: web.RouteTableDef = routes,
    **kwargs,
) -> Callable[[Handler], Handler]:
    return routes.patch(get_route(route, version, prefix, version_format), **kwargs)


def delete(
    route: str,
    version: Optional[int] = None,
    prefix: str = "/api",
    version_format: str = "v{}",
    routes: web.RouteTableDef = routes,
    **kwargs,
) -> Callable[[Handler], Handler]:
    return routes.delete(get_route(route, version, prefix, version_format), **kwargs)


def static(*, routes: web.RouteTableDef = routes, **kwargs) -> None:
    return routes.static(**kwargs)
