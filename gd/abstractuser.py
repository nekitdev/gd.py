from .abstractentity import AbstractEntity
from .session import GDSession
from .utils.wrap_tools import _make_repr

_session = GDSession()

class AbstractUser(AbstractEntity):
    """Class that represents an Abstract Geometry Dash User."""
    def __init__(self, **options):
        super().__init__(**options)
        self.options = options
    
    def __repr__(self):
        info = {
            'name': repr(self.name),
            'id': self.id,
            'account_id': self.account_id
        }
        return _make_repr(self, info)
        
    @property
    def name(self):
        """:class:`str`: String representing name of the user."""
        return self.options.get('name')
    
    @property
    def account_id(self):
        """:class:`int`: Account ID of the user."""
        return self.options.get('account_id')
    
    async def to_user(self):
        """|coro|

        Convert ``self`` to :class:`.User` object.

        Returns
        -------
        :class:`.User`
            A user object corresponding to the abstract one.
        """
        return await _session.get_user(self.account_id)
