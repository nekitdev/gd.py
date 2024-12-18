from attrs import define, field
from pendulum import DateTime
from typing_extensions import Self
from gd.crypto.base64 import decode_base64_string_url_safe

from gd.defaults.entities.comments import DEFAULT_RATING
from gd.defaults.entities.core import DEFAULT_ID
from gd.internals.robtop.core import concat_mapping_with, split_mapping_with
from gd.internals.robtop.protocols import RobTop
from gd.internals.robtop.views import RobTopView
from gd.strings.constants import EMPTY
from gd.time.human import date_time_to_human, option_date_time_from_human
from gd.time.now import utc_now

USER_COMMENT_SEPARATOR = "~"
"""The separator used in user comment strings."""

split_user_comment = split_mapping_with(USER_COMMENT_SEPARATOR)
concat_user_comment = concat_mapping_with(USER_COMMENT_SEPARATOR)

USER_COMMENT_CONTENT = 2
"""The content of the user comment."""

USER_COMMENT_RATING = 4
"""The rating of the user comment."""

USER_COMMENT_ID = 6
"""The ID of the user comment."""

USER_COMMENT_CREATED_AT = 9
"""When the user comment was created."""


@define()
class InternalUserComment(RobTop):
    """Represents user comments internally."""

    content: str = field(default=EMPTY)
    """The content of the user comment."""

    rating: int = field(default=DEFAULT_RATING)
    """The rating of the user comment."""

    id: int = field(default=DEFAULT_ID)
    """The ID of the user comment."""

    created_at: DateTime = field(factory=utc_now)
    """When the user comment was created."""

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        mapping = split_user_comment(string)

        view = RobTopView(mapping)

        content = (
            view.get_option(USER_COMMENT_CONTENT)
            .map(decode_base64_string_url_safe)
            .unwrap_or(EMPTY)
        )

        rating = view.get_option(USER_COMMENT_RATING).map(int).unwrap_or(DEFAULT_RATING)

        id = view.get_option(USER_COMMENT_ID).map(int).unwrap_or(DEFAULT_ID)

        created_at = (
            view.get_option(USER_COMMENT_CREATED_AT)
            .map(option_date_time_from_human)
            .flatten()
            .unwrap_or_else(utc_now)
        )

        return cls(content=content, rating=rating, id=id, created_at=created_at)

    def to_robtop(self) -> str:
        mapping = {
            USER_COMMENT_CONTENT: decode_base64_string_url_safe(self.content),
            USER_COMMENT_RATING: str(self.rating),
            USER_COMMENT_ID: str(self.id),
            USER_COMMENT_CREATED_AT: date_time_to_human(self.created_at),
        }

        return concat_user_comment(mapping)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return USER_COMMENT_SEPARATOR in string
