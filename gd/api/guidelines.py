from itertools import chain

from gd.api.enums import GuidelinesColor

from gd.typing import Any, Guidelines, List, Union

__all__ = ("Guidelines",)


class Guidelines(dict):
    # TODO: maybe add more functionality here ~ nekit
    def __repr__(self) -> str:
        data = {time: enum.name.lower() for time, enum in self.items()}
        return f"{self.__class__.__name__}({data})"

    def __setitem__(self, time: Union[float, int], color: Union[float, GuidelinesColor]) -> None:
        if isinstance(color, GuidelinesColor):
            pass
        elif isinstance(color, (float, int)):
            color = GuidelinesColor.from_value(color)
        else:
            raise ValueError(
                f"Expected GuidelinesColor, float or int, got {color.__class__.__name__}."
            )
        super().__setitem__(time, color)

    def copy(self) -> Any:
        return self.__class__(super().copy())

    @classmethod
    def new(cls, mapping: Any) -> Guidelines:
        """Create a new Guidelines mapping."""
        return cls({key: GuidelinesColor.from_value(value) for key, value in mapping})

    def points(self) -> List[Union[float, int]]:
        """Get all points with lines on them."""
        return list(self.keys())

    def dump(self, delim: str = "~", pad: int = 1) -> str:
        """Dump Guidelines object to a string."""
        return (
            delim.join(
                map(
                    str,
                    chain.from_iterable(
                        (maybefloat(key), maybefloat(enum.value)) for key, enum in self.items()
                    ),
                )
            )
            + delim * pad
        )


def maybefloat(number: float) -> Union[float, int]:
    if number.is_integer():
        return int(number)
    return number
