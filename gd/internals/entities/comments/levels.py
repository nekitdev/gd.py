from typing import Optional

from attrs import define, field
from pendulum import DateTime
from typing_extensions import Self

from gd.crypto.base64 import decode_base64_string_url_safe, encode_base64_string_url_safe
from gd.defaults.entities.comments import DEFAULT_RATING, DEFAULT_SPAM
from gd.defaults.entities.core import DEFAULT_ID
from gd.internals.robtop.core import (
    bool_str,
    concat_iterable_with,
    concat_mapping_with,
    int_bool,
    split_iterable_with,
    split_mapping_with,
)
from gd.internals.robtop.protocols import RobTop
from gd.internals.robtop.views import RobTopView
from gd.primitives.colors.core import Color
from gd.strings.constants import EMPTY
from gd.time.human import date_time_to_human, option_date_time_from_human
from gd.time.now import utc_now

LEVEL_COMMENT_INNER_SEPARATOR = "~"
"""The separator used in level comment inner strings."""

split_level_comment_inner = split_mapping_with(LEVEL_COMMENT_INNER_SEPARATOR)
concat_level_comment_inner = concat_mapping_with(LEVEL_COMMENT_INNER_SEPARATOR)

LEVEL_COMMENT_INNER_LEVEL_ID = 1
"""The ID of the level the comment is on."""

LEVEL_COMMENT_INNER_CONTENT = 2
"""The content of the level comment."""

LEVEL_COMMENT_INNER_USER_ID = 3
"""The ID of the user who commented on the level."""

LEVEL_COMMENT_INNER_RATING = 4
"""The rating of the level comment."""

LEVEL_COMMENT_INNER_ID = 6
"""The ID of the level comment."""

LEVEL_COMMENT_INNER_SPAM = 7
"""Whether the level comment is marked as spam."""

LEVEL_COMMENT_INNER_CREATED_AT = 9
"""When the level comment was created."""

LEVEL_COMMENT_INNER_RECORD = 10
"""The record of the level comment."""

LEVEL_COMMENT_INNER_ROLE_ID = 11
"""The role ID of the user who commented on the level."""

LEVEL_COMMENT_INNER_COLOR = 12
"""The color of the level comment."""


@define()
class InternalLevelCommentInner(RobTop):
    """Represents level comment inner parts internally."""

    level_id: int = field(default=DEFAULT_ID)
    """The ID of the level the comment is on."""

    content: str = field(default=EMPTY)
    """The content of the level comment."""

    user_id: int = field(default=DEFAULT_ID)
    """The ID of the user who commented on the level."""

    rating: int = field(default=DEFAULT_RATING)
    """The rating of the level comment."""

    id: int = field(default=DEFAULT_ID)
    """The ID of the level comment."""

    spam: bool = field(default=DEFAULT_SPAM)
    """Whether the level comment is marked as spam."""

    created_at: DateTime = field(factory=utc_now)
    """When the level comment was created."""

    record: Optional[int] = field(default=None)
    """The record of the level comment."""

    role_id: int = field(default=DEFAULT_ID)
    """The role ID of the user who commented on the level."""

    color: Color = field(factory=Color.default)
    """The color of the level comment."""

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        mapping = split_level_comment_inner(string)

        view = RobTopView(mapping)

        level_id = view.get_option(LEVEL_COMMENT_INNER_LEVEL_ID).map(int).unwrap_or(DEFAULT_ID)

        content = (
            view.get_option(LEVEL_COMMENT_INNER_CONTENT)
            .map(decode_base64_string_url_safe)
            .unwrap_or(EMPTY)
        )

        user_id = view.get_option(LEVEL_COMMENT_INNER_USER_ID).map(int).unwrap_or(DEFAULT_ID)

        rating = view.get_option(LEVEL_COMMENT_INNER_RATING).map(int).unwrap_or(DEFAULT_RATING)

        id = view.get_option(LEVEL_COMMENT_INNER_ID).map(int).unwrap_or(DEFAULT_ID)

        spam = view.get_option(LEVEL_COMMENT_INNER_SPAM).map(int_bool).unwrap_or(DEFAULT_SPAM)

        created_at = (
            view.get_option(LEVEL_COMMENT_INNER_CREATED_AT)
            .map(option_date_time_from_human)
            .flatten()
            .unwrap_or_else(utc_now)
        )

        record = view.get_option(LEVEL_COMMENT_INNER_RECORD).map(int).extract()

        role_id = view.get_option(LEVEL_COMMENT_INNER_ROLE_ID).map(int).unwrap_or(DEFAULT_ID)

        color = (
            view.get_option(LEVEL_COMMENT_INNER_COLOR)
            .map(Color.from_robtop)
            .unwrap_or_else(Color.default)
        )

        return cls(
            level_id=level_id,
            content=content,
            user_id=user_id,
            rating=rating,
            id=id,
            spam=spam,
            created_at=created_at,
            record=record,
            role_id=role_id,
            color=color,
        )

    def to_robtop(self) -> str:
        mapping = {
            LEVEL_COMMENT_INNER_LEVEL_ID: str(self.level_id),
            LEVEL_COMMENT_INNER_CONTENT: encode_base64_string_url_safe(self.content),
            LEVEL_COMMENT_INNER_USER_ID: str(self.user_id),
            LEVEL_COMMENT_INNER_RATING: str(self.rating),
            LEVEL_COMMENT_INNER_ID: str(self.id),
            LEVEL_COMMENT_INNER_SPAM: bool_str(self.spam),
            LEVEL_COMMENT_INNER_CREATED_AT: date_time_to_human(self.created_at),
            LEVEL_COMMENT_INNER_RECORD: str(self.record),
            LEVEL_COMMENT_INNER_ROLE_ID: str(self.role_id),
            LEVEL_COMMENT_INNER_COLOR: self.color.to_robtop(),
        }

        return concat_level_comment_inner(mapping)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return LEVEL_COMMENT_INNER_SEPARATOR in string

    def is_spam(self) -> bool:
        return self.spam


LEVEL_COMMENT_USER_SEPARATOR = "~"
"""The separator used in level comment user strings."""

LEVEL_COMMENT_USER_NAME = 1
LEVEL_COMMENT_USER_ICON_ID = 9
LEVEL_COMMENT_USER_COLOR_1_ID = 10
LEVEL_COMMENT_USER_COLOR_2_ID = 11
LEVEL_COMMENT_USER_ICON_TYPE = 14
LEVEL_COMMENT_USER_GLOW = 15
LEVEL_COMMENT_USER_ACCOUNT_ID = 16


@define()
class LevelCommentUserModel(RobTop):
    """Represents level comment user parts internally."""

    name: str = EMPTY
    icon_id: int = DEFAULT_ICON_ID
    color_1_id: int = DEFAULT_COLOR_1_ID
    color_2_id: int = DEFAULT_COLOR_2_ID
    icon_type: IconType = IconType.DEFAULT
    glow: bool = DEFAULT_GLOW
    account_id: int = DEFAULT_ID

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        mapping = split_level_comment_user(string)

        view = RobTopView(mapping)

        name = view.get_option(LEVEL_COMMENT_USER_NAME).unwrap_or(EMPTY)

        icon_id = view.get_option(LEVEL_COMMENT_USER_ICON_ID).map(int).unwrap_or(DEFAULT_ICON_ID)

        color_1_id = (
            view.get_option(LEVEL_COMMENT_USER_COLOR_1_ID).map(int).unwrap_or(DEFAULT_COLOR_1_ID)
        )
        color_2_id = (
            view.get_option(LEVEL_COMMENT_USER_COLOR_2_ID).map(int).unwrap_or(DEFAULT_COLOR_2_ID)
        )

        icon_type = (
            view.get_option(LEVEL_COMMENT_USER_ICON_TYPE)
            .map(int)
            .map(IconType)
            .unwrap_or(IconType.DEFAULT)
        )

        glow = view.get_option(LEVEL_COMMENT_USER_GLOW).map(int_bool).unwrap_or(DEFAULT_GLOW)

        account_id = view.get_option(LEVEL_COMMENT_USER_ACCOUNT_ID).map(int).unwrap_or(DEFAULT_ID)

        return cls(
            name=name,
            icon_id=icon_id,
            color_1_id=color_1_id,
            color_2_id=color_2_id,
            icon_type=icon_type,
            glow=glow,
            account_id=account_id,
        )

    def to_robtop(self) -> str:
        glow = self.has_glow()

        glow += glow  # type: ignore

        mapping = {
            LEVEL_COMMENT_USER_NAME: self.name,
            LEVEL_COMMENT_USER_ICON_ID: str(self.icon_id),
            LEVEL_COMMENT_USER_COLOR_1_ID: str(self.color_1_id),
            LEVEL_COMMENT_USER_COLOR_2_ID: str(self.color_2_id),
            LEVEL_COMMENT_USER_ICON_TYPE: str(self.icon_type.value),
            LEVEL_COMMENT_USER_GLOW: str(glow),
            LEVEL_COMMENT_USER_ACCOUNT_ID: str(self.account_id),
        }

        return concat_level_comment_user(mapping)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return LEVEL_COMMENT_USER_SEPARATOR in string

    def has_glow(self) -> bool:
        return self.glow


LEVEL_COMMENT_SEPARATOR = ":"
"""The separator used in level comment strings."""

split_level_comment = split_iterable_with(LEVEL_COMMENT_SEPARATOR)
concat_level_comment = concat_iterable_with(LEVEL_COMMENT_SEPARATOR)


@define()
class LevelCommentModel(RobTop):
    """Represents level comments internally."""

    inner: LevelCommentInnerModel = field(factory=LevelCommentInnerModel)
    user: LevelCommentUserModel = field(factory=LevelCommentUserModel)

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        inner_string, user_string = split_level_comment(string)

        inner = LevelCommentInnerModel.from_robtop(inner_string)
        user = LevelCommentUserModel.from_robtop(user_string)

        return cls(inner=inner, user=user)

    def to_robtop(self) -> str:
        return iter.of(self.inner.to_robtop(), self.user.to_robtop()).collect(concat_level_comment)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return LEVEL_COMMENT_SEPARATOR in string
