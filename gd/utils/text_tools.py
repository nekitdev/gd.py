from functools import partial
import json

from yarl import URL

from gd.typing import Any, Dict, List, Optional, Union

__all__ = (
    "make_repr",
    "object_split",
    "dump",
    "dumps",
    "load",
    "loads",
)


def make_repr(obj: Any, info: Optional[Dict[Any, Any]] = None) -> str:
    """Create a nice __repr__ for the object."""
    if info is None:
        info = {}

    name = obj.__class__.__name__

    if not info:
        return f"<{name}>"

    formatted_info = " ".join(f"{key!s}={value!s}" for key, value in info.items())

    return f"<{name} {formatted_info}>"


class JSDict(dict):
    """Improved version of stdlib dictionary, which implements following:
    - Fields can be accessed as attributes;
    - Get Item supports snake case to camel case option.
    """

    def copy(self) -> Any:
        return self.__class__(super().copy())

    def __getitem__(self, item: Any) -> Any:
        try:
            return super().__getitem__(item)

        except KeyError:
            from gd.utils.converter import Converter

            try:
                return super().__getitem__(Converter.snake_to_camel(item))

            except KeyError:
                pass

            raise

    def __setattr__(self, attr: str, value: Any) -> None:
        if attr in self.attr_dict:
            self.attr_dict[attr] = value
        else:
            self[attr] = value

    def __getattr__(self, attr: str) -> Any:
        return self[attr]

    @property
    def attr_dict(self) -> Dict[str, Any]:
        return self.__dict__

    def get(self, item: Any, default: Any = None) -> Any:
        try:
            return self[item]
        except KeyError:
            return default


def default(some_object: Any) -> Any:
    if hasattr(some_object, "__json__"):
        return some_object.__json__()

    elif isinstance(some_object, (list, tuple, set)):
        return list(some_object)

    elif isinstance(some_object, dict):
        return dict(some_object)

    elif isinstance(some_object, URL):
        return str(some_object)

    else:
        raise TypeError(
            f"Object of type {type(some_object).__name__!r} is not JSON-serializable."
        ) from None


dump = partial(json.dump, default=default)
dumps = partial(json.dumps, default=default)
load = partial(json.load, object_hook=JSDict)
loads = partial(json.loads, object_hook=JSDict)


def object_split(string: Union[bytes, str]) -> Union[List[bytes], List[str]]:
    sc = ";" if isinstance(string, str) else b";"  # type: ignore

    final = string.split(sc)  # type: ignore
    final.pop(0)  # pop header

    if string.endswith(sc):  # type: ignore
        final.pop()

    return final
