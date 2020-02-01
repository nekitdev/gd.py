from .._typing import Any, Callable, Dict, List, Optional, Parser, Sequence, Union

__all__ = ('Parser',)

Function = Callable[[Any], Any]


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
    def take(x: Any) -> Any:
        return x[key]
    return take


def action_not_empty() -> Callable[[Sequence[Any]], Optional[Sequence[Any]]]:
    def not_empty(seq: Sequence[Any]) -> Optional[Sequence[Any]]:
        if seq:
            return seq
        raise StopExecution()
    return not_empty


def convert(x: Any) -> Any:
    try:
        return int(x)
    except Exception:
        return x


class Parser:
    def __init__(self) -> None:
        self.split_f = empty
        self.need_map = False
        self.attempt = True
        self.actions = list()
        self.ext = {}

    @staticmethod
    def map(item: Sequence, try_convert: bool = True) -> Dict[Any, Any]:
        mapping = zip(item[::2], item[1::2])

        if try_convert:
            res = {convert(key): convert(value) for key, value in mapping}
        else:
            res = {convert(key): value for key, value in mapping}

        return res

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
                res = self.map(res, self.attempt)
                res.update(self.ext)

            return res

        except Exception:
            return

    def no_convert(self) -> Parser:
        self.attempt = False
        return self

    def should_map(self) -> Parser:
        self.need_map = True
        return self

    def with_split(self, split: Union[str, Callable[[str], Any]]) -> Parser:
        if isinstance(split, str):
            self.split_f = action_split(split)
        else:
            self.split_f = split

        return self
