from typing import Protocol, Type, TypeVar, runtime_checkable

from typing_extensions import Self

__all__ = ("Default", "default")


@runtime_checkable
class Default(Protocol):
    @classmethod
    def default(cls) -> Self:
        ...


D = TypeVar("D", bound=Default)


def default(type: Type[D]) -> D:
    return type.default()
