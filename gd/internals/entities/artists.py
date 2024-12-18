from attrs import define
from typing_extensions import Self

from gd.internals.robtop.core import concat_mapping_with, split_mapping_with
from gd.internals.robtop.protocols import RobTop
from gd.internals.robtop.views import RobTopView
from gd.strings.constants import EMPTY

ARTIST_SEPARATOR = ":"
"""The separator used in artist strings."""

split_artist = split_mapping_with(ARTIST_SEPARATOR)
concat_artist = concat_mapping_with(ARTIST_SEPARATOR)

ARTIST_NAME = 4
"""The name of the artist."""


@define()
class InternalArtist(RobTop):
    """Represents artists internally."""

    name: str = EMPTY
    """The name of the artist."""

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        mapping = split_artist(string)

        view = RobTopView(mapping)

        name = view.get_option(ARTIST_NAME).unwrap_or(EMPTY)

        return cls(name=name)

    def to_robtop(self) -> str:
        mapping = {ARTIST_NAME: self.name}

        return concat_artist(mapping)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return ARTIST_SEPARATOR in string
