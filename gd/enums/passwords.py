from enum import Enum


class PasswordType(Enum):
    NOT_COPYABLE = 0
    COPYABLE_NO_PASSWORD = 1
    COPYABLE_WITH_PASSWORD = 2

    def is_not_copyable(self) -> bool:
        return self is type(self).NOT_COPYABLE

    def is_copyable_no_password(self) -> bool:
        return self is type(self).COPYABLE_NO_PASSWORD

    def is_copyable_with_password(self) -> bool:
        return self is type(self).COPYABLE_WITH_PASSWORD

    def is_copyable(self) -> bool:
        return not self.is_not_copyable()
