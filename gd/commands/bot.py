from ..client import Client
from ..comment import Comment
from ..friend_request import FriendRequest
from ..message import Message

from ..typing import Callable, Optional, Sequence, Union

from .. import utils

from .context import Context
from .view import StringView

__all__ = ('Bot',)

Prefix = Union[str, Sequence[str], Callable[[Context], Sequence[str]]]
Authored = Union[Comment, FriendRequest, Message]


class Bot(Client):
    def __init__(self, *, command_prefix: Prefix, **client_args) -> None:
        self.prefix = command_prefix
        super().__init__(**client_args)

    async def process_commands(self, item: Authored) -> None:
        if isinstance(item, Message) and not item.body:
            await item.read()  # read message if body is empty

        ctx = await self.get_context(item)

        if ctx is None:
            return

    async def get_context(self, item: Authored) -> Optional[Context]:
        view = StringView(item.body)
        ctx = Context(client=self, entity=item, prefix=None, view=view)

        ctx.prefix = await _process_prefix(ctx, self.prefix)

        if ctx.prefix is None:
            return

        return ctx


async def _process_prefix(ctx: Context, prefix: Prefix) -> str:
    view = ctx.view

    if isinstance(prefix, str):
        if view.skip_string(prefix):
            return prefix
        return

    elif isinstance(prefix, Sequence):
        for var in prefix:
            if view.skip_string(var):
                return var
        return

    elif isinstance(prefix, Callable):
        prefix = await utils.maybe_coroutine(prefix, ctx)
        return await _process_prefix(ctx, prefix)

    else:
        raise ValueError('Invalid prefix: {!r}.'.format(prefix))
