
from attrs import frozen
from iters.iters import iter

from gd.constants import DEFAULT_ID
from gd.enums import LikeType
from gd.models_constants import LIKE_SEPARATOR
from gd.models_utils import concat_like, split_like
from gd.robtop import RobTop
from typing_extensions import Self


__all__ = ("Like",)

LIKE = "like"

DEFAULT_LIKED = True


@frozen()
class Like(RobTop):
    type: LikeType
    id: int
    other_id: int = DEFAULT_ID
    liked: bool = DEFAULT_LIKED

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        type_value, id, liked_value, other_id = iter(split_like(string)).skip(1).map(int).unwrap()

        return cls(type=LikeType(type_value), id=id, other_id=other_id, liked=bool(liked_value))

    def to_robtop(self) -> str:
        return iter.of(
            LIKE, str(self.type.value), str(self.id), str(int(self.liked)), str(self.other_id)
        ).collect(concat_like)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return LIKE_SEPARATOR in string

    def is_liked(self) -> bool:
        return self.liked
