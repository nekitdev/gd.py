from gd.typing import Any, Callable, Dict, Iterable, List, Optional, Parser, Sequence, Type, Union

__all__ = ("Parser",)

Null = object()


class StopExecution(Exception):
    """Indicates that a check failed."""

    pass


def empty(string: str) -> str:
    return string


def action_split(delim: str) -> Callable[[str], List[str]]:
    def split(string: str) -> List[str]:
        return string.split(delim)

    return split


def action_take(key: Any) -> Callable[[Sequence[Any]], Any]:
    def take(sequence: Any) -> Any:
        return sequence[key]

    return take


def action_not_empty() -> Callable[[Sequence[Any]], Optional[Sequence[Any]]]:
    def not_empty(sequence: Sequence[Any]) -> Optional[Sequence[Any]]:
        if sequence:
            return sequence
        raise StopExecution()

    return not_empty


class ExtDict(dict):
    def __repr__(self) -> str:
        return self.__class__.__name__ + super().__repr__()

    def copy(self) -> Any:
        return self.__class__(super().copy())

    def get_default(self, value: Any, default: Any) -> Any:
        if default is Null:
            return value
        return default

    def getcast(self, key: Any, default: Any = Null, type: Type[Any] = int) -> Any:
        if key in self:
            value = self[key]

            try:
                return type(value)

            except Exception:  # noqa
                pass

        else:
            value = None

        return self.get_default(value, default)


class Parser:
    def __init__(self) -> None:
        self.split_f = empty
        self.need_map = False
        self.actions = list()
        self.ext = {}

    @staticmethod
    def map(item: Iterable[Any]) -> Dict[Any, Any]:
        # this is quite a magical one.
        # iterators are exhaustive (or lazy), which
        # means that consumed items can no longer be retrieved.
        # therefore, this function works.
        return ExtDict(zip(*(iter(item),) * 2))

    def split(self, delim: str) -> Parser:
        self.actions.append(action_split(delim))
        return self

    def take(self, key: Any) -> Parser:
        self.actions.append(action_take(key))
        return self

    def check_empty(self) -> Parser:
        self.actions.append(action_not_empty())
        return self

    def add_ext(self, ext: Dict[Any, Any]) -> Parser:
        self.ext.update(ext)
        return self

    def parse(self, string: str) -> Any:
        try:
            res = self.split_f(string)

            for action in self.actions:
                res = action(res)

            if self.need_map:
                res = self.map(res)
                res.update(self.ext)

            return res

        except Exception:  # noqa
            return

    def should_map(self) -> Parser:
        self.need_map = True
        return self

    def with_split(self, split: Union[str, Callable[[str], Any]]) -> Parser:
        if isinstance(split, str):
            self.split_f = action_split(split)
        else:
            self.split_f = split

        return self
