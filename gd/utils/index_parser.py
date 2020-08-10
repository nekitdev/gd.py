import itertools

from gd.typing import Dict, Generator, Iterable, Iterator, List, Tuple, TypeVar, Union

from gd.utils.text_tools import make_repr

T = TypeVar("T")

chain_from_iterable = itertools.chain.from_iterable


def group(iterable: Iterable[T], into_number: int = 2) -> Iterator[Tuple[T, ...]]:
    iterators = (iter(iterable),) * into_number
    return zip(*iterators)


def iter_split(string: str, delim: str) -> Generator[str, None, None]:
    length = len(delim)
    start = 0

    while True:
        index = string.find(delim, start)

        if index == -1:
            yield string[start:]
            return

        yield string[start:index]

        start = index + length


class IndexParser:
    def __init__(self, delim: str, *, map_like: bool = False) -> None:
        self._delim = delim
        self._map_like = map_like

    def __repr__(self) -> str:
        info = {"delim": repr(self.delim), "map_like": self.map_like}
        return make_repr(self, info)

    @property
    def delim(self) -> str:
        return self._delim

    @property
    def map_like(self) -> bool:
        return self._map_like

    def is_map_like(self) -> bool:
        return self.map_like

    @staticmethod
    def split(
        string: str, delim: str, *, return_iter: bool = False
    ) -> Union[Iterator[str], List[str]]:
        if return_iter:
            return iter_split(string, delim)

        else:
            return string.split(delim)

    def parse(
        self, string: str, *, return_iter: bool = False
    ) -> Dict[str, str]:
        if self.map_like:
            return {
                key: value for key, value in group(
                    self.split(string, self.delim, return_iter=return_iter)
                )
            }

        return {
            f"{index}": value for index, value in enumerate(
                self.split(string, self.delim, return_iter=return_iter)
            )
        }

    def unparse(self, mapping: Dict[str, str]) -> str:
        if self.map_like:
            return self.delim.join(chain_from_iterable(mapping.items()))

        return self.delim.join(mapping.values())
