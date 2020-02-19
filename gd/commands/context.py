from ..client import Client
from ..comment import Comment
from ..friend_request import FriendRequest
from ..message import Message
from ..typing import Optional, Union
from ..utils.text_tools import make_repr

from .view import StringView

__all__ = ('Context',)


class Context:
    def __init__(
        self, prefix: Optional[str], client: Client, view: StringView,
        entity: Union[Comment, FriendRequest, Message]
    ) -> None:
        self.prefix = prefix
        self.client = client
        self.view = view
        self.entity = entity

    def __repr__(self) -> str:
        info = {
            'prefix': repr(self.prefix),
            'client': self.client,
            'view': self.view,
            'entity': repr(self.entity)
        }
        return make_repr(self, info)

    def is_comment(self) -> bool:
        return isinstance(self.entity, Comment)

    def is_friend_request(self) -> bool:
        return isinstance(self.entity, FriendRequest)

    def is_message(self) -> bool:
        return isinstance(self.entity, Message)
