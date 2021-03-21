import linecache
import secrets

from gd.code_utils import get_frame
from gd.typing import Any, Dict, Iterable, Optional, Type, TypeVar

__all__ = ("map_property",)

T = TypeVar("T")
U = TypeVar("U")

EMPTY = ""
EXECUTE = "exec"

OPTIONAL = "Optional"

INCLUDE = {OPTIONAL: Optional}

FILE_NAME = "<generated {function}_{token}>"
FUNCTION = "{method}_{name}"

DOC = "__doc__"

SIZE = 4

GET = "get"

GET_TEMPLATE = """
def {function}(self) -> Optional[TYPE]:
    return self.{attr}.get({key!r})
""".strip()


GET_OR_DEFAULT = "get_or_default"

GET_OR_DEFAULT_TEMPLATE = """
def {function}(self) -> TYPE:
    return self.{attr}.get({key!r}, {default!r})
""".strip()


SET = "set"

SET_TEMPLATE = """
def {function}(self, {name}: TYPE) -> None:
    self.{attr}[{key!r}] = {name}
""".strip()


DELETE = "delete"

DELETE_TEMPLATE = """
def {function}(self) -> None:
    mapping = self.{attr}
    key = {key!r}

    if key in mapping:
        del mapping[key]
""".strip()


METHOD_TO_TEMPLATE = {
    GET: GET_TEMPLATE,
    GET_OR_DEFAULT: GET_OR_DEFAULT_TEMPLATE,
    SET: SET_TEMPLATE,
    DELETE: DELETE_TEMPLATE,
}


def compile_method(
    method: str,  # either "get", "get_or_default", "set" or "delete"
    name: str,  # name to use
    attr: str,  # attribute to fetch the mapping from
    type: Type[T],  # type of the value
    key: U,  # such that eval(repr(key)) <==> key
    default: Optional[T],  # such that eval(repr(default)) <==> default
    namespace: Optional[Dict[str, Any]] = None,
) -> Any:
    function = FUNCTION.format(method=method, name=name)

    source = METHOD_TO_TEMPLATE[method].format(
        function=function, name=name, attr=attr, key=key, default=default
    )

    if namespace is None:
        namespace = {}

    environment = INCLUDE.copy()

    environment.update(namespace, TYPE=type)  # type: ignore

    if namespace is not None:
        environment.update(namespace)

    file_name = FILE_NAME.format(function=function, token=secrets.token_hex(SIZE))

    linecache.cache[file_name] = (  # type: ignore
        len(source),
        None,  # timestamp
        source.splitlines(True),  # include line endings
        file_name,
    )

    code = compile(source, file_name, EXECUTE)

    exec(code, environment)

    return environment[function]


def map_property(
    name: str,
    attr: str,
    key: U,
    type: Type[T],
    default: Optional[T] = None,
    *,
    doc: Optional[str] = None,
    namespace: Optional[Dict[str, Any]] = None,
    no_default: Iterable[str] = (GET, SET, DELETE),
    or_default: Iterable[str] = (GET_OR_DEFAULT, SET, DELETE),
) -> property:
    if namespace is None:
        namespace = {}

        try:  # ayy, frame hacks! ~ nekit
            frame = get_frame(1)

            namespace.update(frame.f_globals)
            namespace.update(frame.f_locals)

            del frame

        except (AttributeError, ValueError):
            pass

    generated = property(
        *(
            compile_method(method, name, attr, type, key, default, namespace)
            for method in (no_default if default is None else or_default)
        )
    )

    return generated
