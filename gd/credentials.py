from attrs import field, frozen
from iters.iters import iter

from gd.constants import DEFAULT_ID, EMPTY
from gd.string_utils import password_repr

__all__ = ("Credentials",)


@frozen()
class Credentials:
    account_id: int = field(default=DEFAULT_ID)
    id: int = field(default=DEFAULT_ID)
    name: str = field(default=EMPTY)
    password: str = field(default=EMPTY, repr=password_repr)

    def is_loaded(self) -> bool:
        return iter.of(self.account_id, self.id, self.name, self.password).all()
