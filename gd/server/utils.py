from functools import partial

from aiohttp import web

from gd.typing import Any, Dict
import gd

__all__ = (
    "parameter",
    "html_response",
    "json_response",
    "text_response",
)

json_prefix = "json_"
json_prefix_length = len(json_prefix)


def parameter(where: str, **kwargs) -> Dict[str, Any]:
    kwargs.setdefault("in", where)
    return kwargs


def html_response(*args, **kwargs) -> web.Response:
    kwargs.setdefault("content_type", "text/html")

    return web.Response(*args, **kwargs)


def json_response(*args, **kwargs) -> web.Response:
    actual_kwargs = {}
    json_kwargs = {}

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
