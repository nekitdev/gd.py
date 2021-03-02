from gd.memory.traits import Layout
from gd.memory.types import Types
from gd.platform import Platform, system_bits, system_platform
from gd.text_utils import make_repr
from gd.typing import TYPE_CHECKING, Type, TypeVar, Union

if TYPE_CHECKING:
    from gd.memory.state import BaseState  # noqa

__all__ = ("Context",)

C = TypeVar("C", bound="Context")


class Context:
    def __init__(
        self, bits: int = system_bits, platform: Union[int, str, Platform] = system_platform
    ) -> None:
        self._bits = bits
        self._platform = Platform.from_value(platform)

    def __repr__(self) -> str:
        info = {"bits": self.bits, "platform": self.platform.name.casefold()}

        return make_repr(self, info)

    @classmethod
    def bound(cls: Type[C], state: "BaseState") -> C:
        return cls(state.bits, state.platform)

    @property
    def bits(self) -> int:
        return self._bits

    @property
    def platform(self) -> Platform:
        return self._platform

    @property
    def types(self) -> Types:
        return Types(self.bits, self.platform)

    def get_type(self, name: str) -> Type[Layout]:
        return self.types.get(name)
