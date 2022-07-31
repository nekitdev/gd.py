from attrs import field, frozen

from gd.constants import EMPTY
from gd.string_utils import password_repr

__all__ = ("Credentials",)


@frozen()
class Credentials:
    account_id: int = field(default=0)
    id: int = field(default=0)
    name: str = field(default=EMPTY)
    password: str = field(default=EMPTY, repr=password_repr)

    def is_loaded(self) -> bool:
        return bool(self.account_id and self.id and self.name and self.password)
