import json

from yarl import URL

from ..typing import Any, Dict, List, Optional, Union

__all__ = ("make_repr", "object_split", "dump")


def make_repr(obj: Any, info: Optional[Dict[Any, Any]] = None) -> str:
    """Create a nice __repr__ for the object."""
    if info is None:
        info = {}

    module = obj.__module__.split(".").pop(0)
    name = obj.__class__.__name__

    if not info:
        return "<{}.{}>".format(module, name)

    final = " ".join("{0}={1}".format(*t) for t in info.items())

    return "<{}.{} {}>".format(module, name, final)


def default(x: Any) -> Any:
    if isinstance(x, (list, tuple, set)):
        return list(x)

    elif isinstance(x, dict):
        return dict(x)

    elif hasattr(x, "_json"):
        return x._json()

    elif isinstance(x, URL):
        return str(x)

    else:
        raise TypeError(
            "Object of type {!r} is not JSON-serializable.".format(type(x).__name__)
        ) from None


def dump(x: Any, **kwargs) -> str:
    kwargs.update(default=default)
    return json.dumps(x, **kwargs)


def object_split(string: Union[bytes, str]) -> Union[List[bytes], List[str]]:
    sc = ";" if isinstance(string, str) else b";"  # type: ignore

    final = string.split(sc)  # type: ignore
    final.pop(0)  # pop header

    if string.endswith(sc):  # type: ignore
        final.pop()

    return final
