from attrs import frozen

from gd.memory.traits import Layout
from gd.memory.types import Types
from gd.platform import SYSTEM_PLATFORM_CONFIG, Platform, PlatformConfig, system_bits, system_platform
from gd.text_utils import nice_repr
from gd.typing import TYPE_CHECKING, Type, TypeVar, Union

if TYPE_CHECKING:
    from gd.memory.state import BaseState  # noqa

__all__ = ("Context",)

C = TypeVar("C", bound="Context")


@frozen()
class Context:
    config: PlatformConfig = SYSTEM_PLATFORM_CONFIG

    @classmethod
    def bound(cls: Type[C], state: "BaseState") -> C:
        return cls(state.config)

    @property
    def types(self) -> Types:
        return Types(self.config)

    def get_type(self, name: str) -> Type[Layout]:
        return self.types.get(name)
