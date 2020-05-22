import json

from yarl import URL

from gd.typing import Any, Dict, List, Optional, Union

__all__ = ("get_module", "make_repr", "object_split", "dump")


def get_module(module: str) -> str:
    return module.split(".", 1)[0]


def make_repr(obj: Any, info: Optional[Dict[Any, Any]] = None) -> str:
    """Create a nice __repr__ for the object."""
    if info is None:
        info = {}

    module = get_module(obj.__module__)
    name = obj.__class__.__name__

    if not info:
        return f"<{module}.{name}>"

    formatted_info = " ".join(f"{key}={value}" for key, value in info.items())

    return f"<{module}.{name} {formatted_info}>"


def default(x: Any) -> Any:
    if hasattr(x, "_json"):
        return x._json()

    elif isinstance(x, (list, tuple, set)):
        return list(x)

    elif isinstance(x, dict):
        return dict(x)

    elif isinstance(x, URL):
        return str(x)

    else:
        raise TypeError(f"Object of type {type(x).__name__!r} is not JSON-serializable.") from None


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
