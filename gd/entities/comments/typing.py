from typing import Union

from gd.entities.comments.levels import LevelComment, LevelCommentReference
from gd.entities.comments.users import UserComment, UserCommentReference

__all__ = ("Comment", "CommentReference")

Comment = Union[UserComment, LevelComment]
CommentReference = Union[UserCommentReference, LevelCommentReference]
