from gd.enums import GuidelinesColor
from gd.typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple, TypeVar, Union

__all__ = ("Guidelines",)

K = TypeVar("K")
V = TypeVar("V")

Pairs = Iterable[Tuple[K, V]]
MappingOrPairs = Union[Mapping[K, V], Pairs]
Number = Union[float, int]
ColorOrNumber = Union[GuidelinesColor, Number]


class Guidelines(Dict[Number, GuidelinesColor]):
    def __init__(self, guidelines: MappingOrPairs[Number, ColorOrNumber]) -> None:
        super().__init__()

        self.update(guidelines)

    def __repr__(self) -> str:
        time_to_str = {time: enum.name.lower() for time, enum in self.items()}
        return f"{self.__class__.__name__}({time_to_str})"

    def __setitem__(self, time: Number, color: ColorOrNumber) -> None:
        super().__setitem__(time, GuidelinesColor.from_value(color))

    def at(self, time: Number) -> Optional[GuidelinesColor]:
        return self.get(time, None)

    def copy(self) -> Any:
        return self.__class__(super().copy())

    def points(self) -> List[Number]:
        """Get all points with lines on them."""
        return list(self.keys())

    def update(  # type: ignore
        self, guidelines: MappingOrPairs[Number, ColorOrNumber], **ignore_kwargs
    ) -> None:
        pairs: Pairs[Number, ColorOrNumber]

        if isinstance(guidelines, Mapping):
            pairs = guidelines.items()

        else:
            pairs = guidelines

        super().update((time, GuidelinesColor.from_value(color)) for (time, color) in pairs)
