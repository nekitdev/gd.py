from enum import Enum as StandardEnum
from enum import Flag as StandardFlag
from typing import Any, Dict, Type, TypeVar

from gd.text_utils import case_fold, create_title
from gd.types import Nullable, is_null, null
from gd.typing import is_same_type, is_string

__all__ = ("Enum", "Flag")

T = TypeVar("T", bound="Trait")


class Trait(StandardEnum):
    pass


class Format(Trait):
    def __format__(self, specification: str) -> str:
        return str(self).__format__(specification)


class Order(Trait):
    def __lt__(self, other: Any) -> Any:
        if is_same_type(other, self):
            return self.value < other.value

        return NotImplemented

    def __le__(self, other: Any) -> Any:
        if is_same_type(other, self):
            return self.value <= other.value

        return NotImplemented

    def __gt__(self, other: Any) -> Any:
        if is_same_type(other, self):
            return self.value > other.value

        return NotImplemented

    def __ge__(self, other: Any) -> Any:
        if is_same_type(other, self):
            return self.value >= other.value

        return NotImplemented


ABBREVIATIONS = {"NA", "UFO", "XL"}


class Title(Trait):
    @property
    def title_name(self) -> str:
        name = self.name

        if name in ABBREVIATIONS:
            return name

        return create_title(name)


E = TypeVar("E", bound="EnumExtension")


class EnumExtension(Trait):
    @classmethod
    def fetch_case_fold_names(cls: Type[E]) -> Dict[str, E]:
        return {case_fold(name): member for name, member in cls.__members__.items()}

    @classmethod
    def from_name(cls: Type[E], name: str) -> E:
        return cls.fetch_case_fold_names()[case_fold(name)]

    @classmethod
    def from_value(cls: Type[E], value: Any, default: Nullable[Any] = null) -> E:  # type: ignore
        try:
            return cls(value)

        except ValueError:
            if is_null(default):
                raise

            return cls(default)

    @classmethod
    def from_data(cls: Type[E], data: Any, default: Nullable[Any] = null) -> E:  # type: ignore
        if is_string(data):
            try:
                return cls.from_name(data)

            except KeyError:
                pass

        try:
            return cls.from_value(data)

        except ValueError:
            if is_null(default):
                raise

            return cls.from_data(default)


DEFAULT_BOUND = True


F = TypeVar("F", bound="FlagExtension")


class FlagExtension(EnumExtension, StandardFlag):
    @classmethod
    def from_values(cls: Type[F], *values: int, bound: bool = DEFAULT_BOUND) -> F:
        result = cls(0)

        if bound:
            for value in values:
                result |= cls.from_value(value)

        else:
            for value in values:
                result |= cls.from_value(value, 0)

        return result

    @classmethod
    def from_names(cls: Type[F], *names: str) -> F:
        result = cls(0)

        for name in names:
            result |= cls.from_name(name)

        return result

    @classmethod
    def from_multiple_data(cls: Type[F], *multiple_data: int, bound: bool = DEFAULT_BOUND) -> F:
        result = cls(0)

        if bound:
            for data in multiple_data:
                result |= cls.from_data(data)

        else:
            for data in multiple_data:
                result |= cls.from_data(data, 0)

        return result


class Enum(EnumExtension, Format, Order, Title, StandardEnum):
    pass


class Flag(FlagExtension, Enum, StandardFlag):
    pass
