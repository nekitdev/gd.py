from typing import Generic, Mapping, TypeVar, final

from attrs import frozen
from wraps import Null, Option, Some

__all__ = ("RobTopView",)

K = TypeVar("K")
V = TypeVar("V")


@final
@frozen()
class RobTopView(Generic[K, V]):
    mapping: Mapping[K, V]

    def get_option(self, key: K) -> Option[V]:
        mapping = self.mapping

        if key in mapping:
            return Some(mapping[key])

        return Null()


T = TypeVar("T")

StringRobTopView = RobTopView[str, T]
