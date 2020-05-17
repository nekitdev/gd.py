from itertools import chain

from .enums import GuidelinesColor

from ..typing import Any, Guidelines, List, Union


class Guidelines(dict):
    # TODO: maybe add more functionality here ~ nekit
    def __repr__(self) -> str:
        data = {time: enum.name.lower() for time, enum in self.items()}
        return f"{self.__class__.__name__}({data})"

    def __setitem__(self, time: Union[float, int], color: Union[float, GuidelinesColor]) -> None:
        self[time] = GuidelinesColor.from_value(color) if isinstance(color, (float, int)) else color

    @classmethod
    def new(cls, mapping: Any) -> Guidelines:
        return cls({key: GuidelinesColor.from_value(value) for key, value in mapping})

    def points(self) -> List[Union[float, int]]:
        return list(self.keys())

    def dump(self, delim: str = "~", pad: int = 1) -> str:
        return delim.join(map(str, chain.from_iterable(
            (maybefloat(key), maybefloat(enum.value)) for key, enum in self.items()
        ))) + delim * pad


def maybefloat(number: float) -> Union[float, int]:
    if number.is_integer():
        return int(number)
    return number
