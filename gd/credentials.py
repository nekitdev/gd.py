from attrs import field, frozen

from gd.strings.constants import EMPTY
from gd.strings.operations import password_repr

__all__ = ("Credentials",)

DEFAULT_ID = 0


@frozen()
class Credentials:
    account_id: int = field(default=DEFAULT_ID)
    id: int = field(default=DEFAULT_ID)
    name: str = field(default=EMPTY)
    hashed_password: str = field(default=EMPTY, repr=password_repr)
