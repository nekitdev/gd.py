from functools import partial

from aiohttp import web

from gd.typing import Any, Callable, Mapping, TypeVar
import gd

__all__ = (
    "parameter",
    "html_response",
    "json_response",
    "text_response",
    "unwrap_partial",
)

T_co = TypeVar("T_co", covariant=True)

json_prefix = "json_"
json_prefix_length = len(json_prefix)


def unwrap_partial(function: Callable[..., T_co], strict: bool = True) -> Callable[..., T_co]:
    if strict:
        while isinstance(function, partial):
            function = function.func  # type: ignore

        return function

    else:
        while True:
            try:
                function = function.func  # type: ignore

            except AttributeError:
                return function


def parameter(where: str, **kwargs) -> Mapping[str, Any]:
    kwargs.setdefault("in", where)
    return kwargs


def html_response(*args, **kwargs) -> web.Response:
    kwargs.setdefault("content_type", "text/html")

    return web.Response(*args, **kwargs)


def json_response(*args, **kwargs) -> web.Response:
    actual_kwargs = {}
    json_kwargs = {}

    if kwargs:
        _json_prefix = json_prefix
        _json_prefix_length = json_prefix_length

        for key, value in kwargs.items():
            if key.startswith(_json_prefix):
                json_kwargs[key[_json_prefix_length:]] = value

            else:
                actual_kwargs[key] = value

    dumps = partial(gd.json.dumps, **json_kwargs)

    actual_kwargs.setdefault("dumps", dumps)

    return web.json_response(*args, **actual_kwargs)


def text_response(*args, **kwargs) -> web.Response:
    kwargs.setdefault("content_type", "text/plain")

    return web.Response(*args, **kwargs)
