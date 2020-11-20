from functools import partial
import re

from aiohttp import web

from gd.json import dumps
from gd.typing import Any, Iterable, Mapping, Optional, TypeVar

from gd.server.typing import Handler

__all__ = (
    "parameter",
    "get_original_handler",
    "get_pages",
    "html_response",
    "json_response",
    "text_response",
)

DELIM = ","
RANGE = re.compile(
    r"(?P<start>-*[0-9]+)\.\.(?P<inclusive>=)?(?P<stop>-*[0-9]+)(?:\.\.(?P<step>-*[0-9]+))?"
)

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)

json_prefix = "json_"
json_prefix_length = len(json_prefix)


def get_original_handler(handler: Handler, strict: bool = True) -> Handler:
    if strict:
        while isinstance(handler, partial):
            handler = handler.keywords.get("handler")  # type: ignore

            if handler is None:
                raise TypeError("Can not retrieve original handler.")

        return handler

    else:
        while True:
            try:
                handler = handler.keywords.get("handler")  # type: ignore

                if handler is None:
                    raise TypeError("Can not retrieve original handler.")

            except AttributeError:
                return handler


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

    actual_kwargs.setdefault("dumps", partial(dumps, **json_kwargs))

    return web.json_response(*args, **actual_kwargs)


def text_response(*args, **kwargs) -> web.Response:
    kwargs.setdefault("content_type", "text/plain")

    return web.Response(*args, **kwargs)


def int_or(string: Optional[str], default: int) -> int:
    return default if string is None else int(string)


def get_pages(string: str) -> Iterable[int]:
    match = RANGE.fullmatch(string)

    if match is None:
        return map(int, filter(bool, string.split(DELIM)))

    start = int_or(match.group("start"), 0)
    stop = int_or(match.group("stop"), 0)

    if match.group("inclusive"):
        stop += 1

    step = int_or(match.group("step"), 1)

    return range(start, stop, step)
