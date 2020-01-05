from ._typing import Client, Optional
from .abstractentity import AbstractEntity
from .abstractuser import AbstractUser
from .utils.text_tools import make_repr


class UnregisteredUser(AbstractEntity):
    """Class that represents Unregistered Users in Geometry Dash.
    This class is derived from :class:`.AbstractEntity`.
    """
    def __init__(
        self, id: int = 0, name: str = 'UnregisteredUser',
        client: Optional[Client] = None, **ignore
    ) -> None:
        super().__init__(id=id, client=client)
        self._name = name

    def __repr__(self) -> str:
        info = {
            'id': self.id, 'name': self.name
        }
        return make_repr(self, info)

    def __json__(self) -> dict:
        final = {'name': self.name}
        final.update(super().__json__())
        return final

    def as_user(self) -> AbstractUser:
        """:class:`.AbstractUser`: Construct user object from ``self``."""
        return AbstractUser(
            name=self.name,
            id=self.id,
            account_id=(-1),  # unregistered users do not have this one
            client=self._client
        )

    @property
    def name(self) -> str:
        """:class:`str`: A name of the user. ``'UnregisteredUser'`` if not present."""
        return self._name
