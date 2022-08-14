from __future__ import annotations

from typing import TYPE_CHECKING, Type, TypeVar

from attrs import frozen

from gd.memory.data import AnyData
from gd.memory.types import Types
from gd.platform import SYSTEM_PLATFORM_CONFIG, Platform, PlatformConfig

if TYPE_CHECKING:
    from gd.memory.state import AbstractState

__all__ = ("Context",)

C = TypeVar("C", bound="Context")


@frozen()
class Context:
    config: PlatformConfig = SYSTEM_PLATFORM_CONFIG

    @property
    def platform(self) -> Platform:
        return self.config.platform

    @property
    def bits(self) -> int:
        return self.config.bits

    @classmethod
    def bound(cls: Type[C], state: AbstractState) -> C:
        return cls(state.config)

    @property
    def types(self) -> Types:
        return Types(self.config)

    def get(self, name: str) -> Type[AnyData]:
        return self.types.get(name)
