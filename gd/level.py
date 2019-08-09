import logging

from typing import Sequence, Union

from .abstractentity import AbstractEntity
from .session import GDSession

from .errors import MissingAccess
from .utils.wrap_tools import _make_repr

from . import utils

log = logging.getLogger(__name__)

_session = GDSession()

class Level(AbstractEntity):
    """Class that represents a Geometry Dash Level."""
    def __init__(self, **options):
        super().__init__(**options)
        self._data = options.pop('data')
        self.options = options

    def __repr__(self):
        info = {
            'id': self.id,
            'name': self.name,
            'creator': self.creator,
            'version': self.version,
            'difficulty': self.difficulty
        }
        return _make_repr(self, info)

    @property
    def name(self):
        """:class:`str`: The name of the level."""
        return self.options.get('name')

    @property
    def description(self):
        """:class:`str`: Description of the level."""
        return self.options.get('description')
    
    @property
    def version(self):
        """:class:`int`: Version of the level."""
        return self.options.get('version')

    @property
    def downloads(self):
        """:class:`int`: Amount of the level's downloads."""
        return self.options.get('downloads')

    @property
    def likes(self):
        """:class:`int`: Amount of the level's likes."""
        return self.options.get('likes')

    @property
    def score(self):
        """:class:`int`: Level's featured score."""
        return self.options.get('score')

    @property
    def creator(self):
        """:class:`.AbstractUser`: Creator of the level."""
        return self.options.get('creator')

    @property
    def song(self):
        """:class:`.Song`: Song used in the level."""
        return self.options.get('song')

    @property
    def difficulty(self):
        """:class:`.LevelDifficulty`: Difficulty of the level."""
        return self.options.get('difficulty')

    @property
    def stars(self):
        """:class:`int`: Amount of stars the level has."""
        return self.options.get('stars')

    @property
    def coins(self):
        """:class:`int`: Amount of coins in the level."""
        return self.options.get('coins')

    @property
    def original_id(self):
        """:class:`int`: ID of the original level. (``0`` if is not a copy)"""
        return self.options.get('original')    

    @property
    def uploaded_timestamp(self):
        """:class:`str`: A human-readable string representing how much time ago level was uploaded."""
        return self.options.get('uploaded_timestamp')

    @property
    def last_uploaded_timestamp(self):
        """:class:`str`: A human-readable string showing how much time ago the last update was."""
        return self.options.get('last_updated_timestamp')

    @property
    def length(self):
        """:class:`.LevelLength`: A type that represents length of the level."""
        return self.options.get('length')

    @property
    def game_version(self):
        """:class:`int`: A version of the game required to play the level."""
        return self.options.get('game_version')

    @property
    def requested_stars(self):
        """:class:`int`: Amount of stars creator of the level has requested."""
        return self.options.get('stars_requested')

    @property
    def object_count(self):
        """:class:`int`: Amount of objects the level has."""
        return self.options.get('object_count')

    @property
    def type(self):
        """:class:`.TimelyType`: A type that shows whether a level is Daily/Weekly."""
        return self.options.get('typeof')

    @property
    def timely_index(self):
        """:class:`int`: A number that represents current index of the timely.
        Increments on new dailies/weeklies. If not timely, equals ``-1``.
        """
        return self.options.get('time_n')

    @property
    def cooldown(self):
        """:class:`int`: Represents a cooldown until next timely. If not timely, equals ``-1``."""
        return self.options.get('cooldown')

    def is_timely(self, daily_or_weekly: str = None):
        """:class:`bool`: Indicates whether a level is timely/daily/weekly.
        For instance, let's suppose a *level* is daily. Then, the behavior of this method is:
        ``level.is_timely() -> True`` and ``level.is_timely('daily') -> True`` but
        ``level.is_timely('weekly') -> False``."""
        if daily_or_weekly is None:
            return self.type > 0

        t = ('daily', 'weekly')
        assert daily_or_weekly in t, f'parameter not in {t}.'

        return self.type == t.index(daily_or_weekly)+1

    def is_featured(self):
        """:class:`bool`: Indicates whether a level is featured."""
        return self.score > 0  # not sure if this is the right way though

    def is_epic(self):
        """:class:`bool`: Indicates whether a level is epic."""
        return self.options.get('is_epic')

    def is_demon(self):
        """:class:`bool`: Indicates whether a level is demon."""
        return options.get('is_demon')

    def is_auto(self):
        """:class:`bool`: Indicates whether a level is auto."""
        return options.get('is_auto')

    def is_original(self):
        """:class:`bool`: Indicates whether a level is original."""
        return not self.original_id

    def has_coins_verified(self):
        """:class:`bool`: Indicates whether level's coins are verified."""
        return self.options.get('verified_coins')

    def download(self):
        """:class:`bytes`: Returns level data, represented as bytes."""
        return self._data

    def is_deleted(self):
        """:class:`bool`: A blocking version of :meth:`.Level.is_alive`."""
        return not utils.run(self.is_alive())

    async def is_alive(self):
        """|coro|

        Checks if a level is still on Geometry Dash servers.

        Returns
        -------
        :class:`bool`
            ``True`` if a level is still *alive*, and ``False`` otherwise.
        """
        new_version = await self.refresh()
        return not (new_version is None)

    async def refresh(self):
        """|coro|

        Refreshes a level. Returns ``None`` on fail.

        Returns
        -------
        :class:`.Level`
            A newly fetched version. ``None`` if failed to fetch.
        """
        try:
            new_ver = await _session.get_level(level_id)
        except MissingAccess:
            return log.warning('Failed to refresh level: %r. Most likely it was deleted.', self)

        self.options = new_ver.options
        return self

    async def get_page_comments(self, page: int = 0):  # [FUTURE]
        return await _session.get_level_page_comments(self, page)

    async def get_comments(  # [FUTURE]
        self, pages: Sequence[int] = [],
        *, sort_by_page: bool = True,
        timeout: Union[int, float] = 5.0
    ):
        return await _session.get_level_comments(
            level=self, pages=pages, sort_by_page=sort_by_page, timeout=timeout
        )
