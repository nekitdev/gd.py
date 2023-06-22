from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import frozen

from gd.enums import ByteOrder
from gd.memory.constants import ZERO_SIZE
from gd.memory.data import Data
from gd.platform import PlatformConfig

if TYPE_CHECKING:
    from gd.memory.state import AbstractState

# TODO: add `this`?

__all__ = ("Void",)


@frozen()
class Void(Data[None]):
    def read(self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE) -> None:
        return None

    def write(
        self, state: AbstractState, address: int, value: None, order: ByteOrder = ByteOrder.NATIVE
    ) -> None:
        pass

    def compute_size(self, config: PlatformConfig) -> int:
        return ZERO_SIZE

    def compute_alignment(self, config: PlatformConfig) -> int:
        return ZERO_SIZE
