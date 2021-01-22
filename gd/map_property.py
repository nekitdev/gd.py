from gd.code_utils import get_frame
from gd.typing import Any, Dict, Optional, TypeVar

__all__ = ("map_property", "is_null")

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")

TEMPLATE = """
def get_{name}(self) -> Optional[TYPE]:
    return self.{attr}.get({key!r})


def set_{name}(self, {name}: TYPE) -> None:
    self.{attr}[{key!r}] = {name}


def delete_{name}(self) -> None:
    try:
        del self.{attr}[{key!r}]

    except KeyError:
        pass


{name} = property(get_{name}, set_{name}, delete_{name})
"""


def map_property(
    name: str,
    attr: str,
    key: T,  # such that eval(repr(key)) == key
    *,
    type: Any = Any,
    doc: Optional[str] = None,
    # namespace to use, tries to fetch from caller frame if not given
    namespace: Optional[Dict[str, V]] = None,
) -> property:
    env: Dict[str, Any] = {}

    if namespace is None:
        namespace = {}

        try:  # ayy frame hacks! ~ nekit
            frame = get_frame(1)

            namespace.update(frame.f_globals)
            namespace.update(frame.f_locals)

            del frame

        except (AttributeError, ValueError):
            pass

    env.update(namespace, TYPE=type, Optional=Optional)

    code = TEMPLATE.format(name=name, attr=attr, key=key)

    exec(code, env)

    some_property = env[name]
    some_property.__doc__ = doc

    return some_property


def is_null(some: Optional[T]) -> bool:
    return some is None
