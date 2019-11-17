import logging

from typing import Union

from .abstractentity import AbstractEntity
from .abstractuser import AbstractUser
from .song import Song

from .session import _session

from .errors import MissingAccess

from .utils.enums import (
    DemonDifficulty, LevelDifficulty, CommentStrategy,
    LevelLength, TimelyType, LevelLeaderboardStrategy,
    value_to_enum
)
from .utils.wrap_tools import make_repr, check

log = logging.getLogger(__name__)

class Level(AbstractEntity):
    """Class that represents a Geometry Dash Level.
    This class is derived from :class:`.AbstractEntity`.
    """
    def __init__(self, **options):
        super().__init__(**options)
        self.options = options

    def __repr__(self):
        info = {
            'id': self.id,
            'name': repr(self.name),
            'creator': self.creator,
            'version': self.version,
            'difficulty': self.difficulty
        }
        return make_repr(self, info)

    @property
    def name(self):
        """:class:`str`: The name of the level."""
        return self.options.get('name', 'Unnamed')

    @property
    def description(self):
        """:class:`str`: Description of the level."""
        return self.options.get('description', '')

    @property
    def version(self):
        """:class:`int`: Version of the level."""
        return self.options.get('version', 0)

    @property
    def downloads(self):
        """:class:`int`: Amount of the level's downloads."""
        return self.options.get('downloads', 0)

    @property
    def rating(self):
        """:class:`int`: Amount of the level's likes or dislikes."""
        return self.options.get('rating', 0)

    @property
    def score(self):
        """:class:`int`: Level's featured score."""
        return self.options.get('score', 0)

    @property
    def creator(self):
        """:class:`.AbstractUser`: Creator of the level."""
        return self.options.get('creator', AbstractUser())

    @property
    def song(self):
        """:class:`.Song`: Song used in the level."""
        return self.options.get('song', Song())

    @property
    def difficulty(self):
        """:class:`.LevelDifficulty`: Difficulty of the level."""
        return self.options.get('difficulty', LevelDifficulty(-1))

    @property
    def password(self):
        """:class:`str`: The password to copy the level.
        Empty string if the level is free to copy,
        ``None`` if not copyable,
        and a string containing password otherwise.
        """
        return self.options.get('password')

    @property
    def stars(self):
        """:class:`int`: Amount of stars the level has."""
        return self.options.get('stars', 0)

    @property
    def coins(self):
        """:class:`int`: Amount of coins in the level."""
        return self.options.get('coins', 0)

    @property
    def original_id(self):
        """:class:`int`: ID of the original level. (``0`` if is not a copy)"""
        return self.options.get('original', 0)

    @property
    def uploaded_timestamp(self):
        """:class:`str`: A human-readable string representing how much time ago level was uploaded."""
        return self.options.get('uploaded_timestamp', 'unknown')

    @property
    def last_updated_timestamp(self):
        """:class:`str`: A human-readable string showing how much time ago the last update was."""
        return self.options.get('last_updated_timestamp', 'unknown')

    @property
    def length(self):
        """:class:`.LevelLength`: A type that represents length of the level."""
        return self.options.get('length', LevelLength(-1))

    @property
    def game_version(self):
        """:class:`int`: A version of the game required to play the level."""
        return self.options.get('game_version', 0)

    @property
    def requested_stars(self):
        """:class:`int`: Amount of stars creator of the level has requested."""
        return self.options.get('stars_requested', 0)

    @property
    def objects(self):
        """List[:class:`str`]: A list of objects, represented as strings."""
        data = self.data.split(';')
        data.pop(0)
        return data

    @property
    def object_count(self):
        """:class:`int`: Amount of objects the level has."""
        return self.options.get('object_count', 0)

    @property
    def type(self):
        """:class:`.TimelyType`: A type that shows whether a level is Daily/Weekly."""
        return self.options.get('type', TimelyType(0))

    @property
    def timely_index(self):
        """:class:`int`: A number that represents current index of the timely.
        Increments on new dailies/weeklies. If not timely, equals ``-1``.
        """
        return self.options.get('time_n', -1)

    @property
    def cooldown(self):
        """:class:`int`: Represents a cooldown until next timely. If not timely, equals ``-1``."""
        return self.options.get('cooldown', -1)

    @property
    def data(self):
        """:class:`str`: Level data, represented as a string."""
        return self.options.get('data', '')

    def is_timely(self, daily_or_weekly: str = None):
        """:class:`bool`: Indicates whether a level is timely/daily/weekly.
        For instance, let's suppose a *level* is daily. Then, the behavior of this method is:
        ``level.is_timely() -> True`` and ``level.is_timely('daily') -> True`` but
        ``level.is_timely('weekly') -> False``."""
        if self.type is None:
            return False

        if daily_or_weekly is None:
            return self.type.value > 0

        assert daily_or_weekly in ('daily', 'weekly')

        return self.type.name.lower() == daily_or_weekly

    def is_rated(self):
        """:class:`bool`: Indicates if a level is rated (has stars)."""
        return self.stars > 0

    def is_featured(self):
        """:class:`bool`: Indicates whether a level is featured."""
        return self.score > 0  # not sure if this is the right way though

    def is_epic(self):
        """:class:`bool`: Indicates whether a level is epic."""
        return self.options.get('is_epic', False)

    def is_demon(self):
        """:class:`bool`: Indicates whether a level is demon."""
        return self.options.get('is_demon', False)

    def is_auto(self):
        """:class:`bool`: Indicates whether a level is auto."""
        return self.options.get('is_auto', False)

    def is_original(self):
        """:class:`bool`: Indicates whether a level is original."""
        return not self.original_id

    def has_coins_verified(self):
        """:class:`bool`: Indicates whether level's coins are verified."""
        return self.options.get('verified_coins', False)

    def download(self):
        """:class:`str`: Returns level data, represented as string."""
        return self.data

    async def report(self):
        """|coro|

        Reports a level.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to report a level.
        """
        await _session.report_level(self)

    async def upload(self, **kwargs):
        """|coro|

        Upload ``self``.

        Parameters
        ----------
        \*\*kwargs
            Arguments that :meth:`.Client.upload_level` accepts.
            Defaults are properties of the level.
        """
        track, song_id = (self.song.id, 0)

        if self.song.is_custom():
            track, song_id = song_id, track

        client = kwargs.pop('from_client', self._client)

        if client is None:
            raise MissingAccess(
                message=('Could not find the client to upload level from. '
                'Either attach a client to this level or provide "from_client" parameter.')
            )

        password = kwargs.pop('password', self.password)

        args = dict(
            name=self.name, id=self.id, version=self.version, length=abs(self.length.value),
            track=track, song_id=song_id, two_player=False, is_auto=self.is_auto(),
            original=self.original_id, objects=len(self.objects), coins=self.coins,
            star_amount=self.stars, unlist=False, ldm=False, password=password,
            copyable=(password is not None), description=self.description, data=self.data
        )

        args.update(kwargs)

        uploaded = await client.upload_level(**args)

        self.options = uploaded.options

    async def delete(self, *, from_client=None):
        """|coro|

        Deletes a level.

        Parameters
        ----------
        from_client: :class:`.Client`
            A logged in client to delete a level with. If ``None`` or omitted,
            defaults to the one attached to this level.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to delete a level.
        """
        client = from_client if from_client is not None else self._client
        check.is_logged_obj(client, 'delete')
        await _session.delete_level(self, client=client)

    async def update_description(self, content: str = None, *, from_client=None):
        """|coro|

        Updates level description.

        Parameters
        ----------
        content: :class:`str`
            Content of the new description. If ``None`` or omitted,
            sets content to :attr:`.Level.description`.

        from_client: :class:`.Client`
            A logged in client to update level description with. If ``None`` or omitted,
            defaults to the one attached to this level.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to update level's description.
        """
        if content is None:
            content = self.description

        client = from_client if from_client is not None else self._client
        check.is_logged_obj(client, 'update_description')
        await _session.update_level_desc(self, content, client=client)

    async def rate(self, stars: int = 1, *, from_client=None):
        """|coro|

        Sends level rating.

        Parameters
        ----------
        stars: :class:`int`
            Amount of stars to rate with.

        from_client: :class:`.Client`
            A logged in client to rate level with. If ``None`` or omitted,
            defaults to the one attached to this level.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to rate a level.
        """
        client = from_client if from_client is not None else self._client
        check.is_logged_obj(client, 'rate')
        await _session.rate_level(self, stars, client=client)

    async def rate_demon(
        self, demon_difficulty: Union[int, str, DemonDifficulty] = 1,
        as_mod: bool = False, *, from_client=None
    ):
        """|coro|

        Sends level demon rating.

        Parameters
        ----------
        demon_difficulty: Union[:class:`int`, :class:`str`, :class:`.DemonDifficulty`]
            Demon difficulty to rate a level with.

        as_mod: :class:`bool`
            Whether to send a demon rating as moderator.

        from_client: :class:`.Client`
            A logged in client to rate demon difficulty with. If ``None`` or omitted,
            defaults to the one attached to this level.

        Raises
        ------
        :exc:`.MissingAccess`
            If attempted to rate a level as moderator without required permissions.
        """
        client = from_client if from_client is not None else self._client
        check.is_logged_obj(client, 'rate_demon')
        demon_difficulty = value_to_enum(DemonDifficulty, demon_difficulty)

        success = await _session.rate_demon(self, demon_difficulty, mod=as_mod, client=client)

        if success:
            log.info('Successfully demon-rated level: %s.', self)
        else:
            log.warning('Failed to rate demon difficulty for level: %s.', self)

    async def send(self, stars: int = 1, featured: bool = True, *, from_client=None):
        """|coro|

        Sends a level to Geometry Dash Developer and Administrator, *RobTop*.

        Parameters
        ----------
        stars: :class:`int`
            Amount of stars to send with.

        featured: :class:`bool`
            Whether to send to feature, or to simply rate.

        from_client: :class:`.Client`
            A logged in client to send a level from. If ``None`` or omitted,
            defaults to the one attached to this level.

        Raises
        ------
        :exc:`.MissingAccess`
            Missing required moderator permissions.
        """
        client = from_client if from_client is not None else self._client
        check.is_logged_obj(client, 'send')
        await _session.send_level(self, stars, featured=featured, client=client)

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

        .. note::

            This function actually refreshes a level and its stats.
            No need to do funky stuff with its return.

        Returns
        -------
        :class:`.Level`
            A newly fetched version. ``None`` if failed to fetch.
        """
        try:
            if self.is_timely():
                new_ver = await _session.get_timely(self.type.name.lower(), client=self._client)

                if new_ver.id != self.id:
                    log.warning('There is a new {0.type.desc} Level: {1!r}. Updating to it...'.format(self, new_ver))

            else:
                new_ver = await _session.get_level(self.id, client=self._client)

        except MissingAccess:
            return log.warning('Failed to refresh level: %r. Most likely it was deleted.', self)

        self.options = new_ver.options

        return self

    async def comment(self, content: str, percentage: int = 0, *, from_client=None):
        """|coro|

        Posts a comment on a level.

        Parameters
        ----------
        content: :class:`str`
            Body of the comment to post.

        percentage: :class:`int`
            Percentage to display. Default is ``0``.

            .. note::

                gd.py developers are not responsible for effects that changing this may cause.
                Set this parameter higher than 0 on your own risk.

        from_client: :class:`.Client`
            A logged in client to post a comment from. If ``None`` or omitted,
            defaults to the one attached to this level.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to post a level comment.
        """
        client = from_client if from_client is not None else self._client
        check.is_logged_obj(client, 'comment')
        await _session.comment_level(self, content, percentage, client=client)

    async def like(self, from_client=None):
        """|coro|

        Likes a level.

        Parameters
        ----------
        from_client: :class:`.Client`
            A logged in client to like a level with. If ``None`` or omitted,
            defaults to the one attached to this level.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to like a level.
        """
        client = from_client if from_client is not None else self._client
        check.is_logged_obj(client, 'like')
        await _session.like(self, dislike=False, client=client)

    async def dislike(self, from_client=None):
        """|coro|

        Dislikes a level.

        Parameters
        ----------
        from_client: :class:`.Client`
            A logged in client to dislike a level with. If ``None`` or omitted,
            defaults to the one attached to this level.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to dislike a level.
        """
        client = from_client if from_client is not None else self._client
        check.is_logged_obj(client, 'dislike')
        await _session.like(self, dislike=True, client=client)

    async def get_leaderboard(
        self, strategy: Union[int, str, LevelLeaderboardStrategy] = 0, *, from_client=None
    ):
        """|coro|

        Retrieves the leaderboard of a level.

        Parameters
        ----------
        strategy: Union[:class:`int`, :class:`str`, :class:`.LevelLeaderboardStrategy`]
            A strategy to apply. This is converted to :class:`.LevelLeaderboardStrategy`
            using :func:`.utils.value_to_enum`.

        Returns
        -------
        List[:class:`.LevelRecord`]
            A list of user-like objects.
        """
        client = from_client if from_client is not None else self._client
        check.is_logged_obj(client, 'get_leaderboard')

        strategy = value_to_enum(LevelLeaderboardStrategy, strategy)

        return await _session.get_leaderboard(self, strategy=strategy, client=client)

    async def get_comments(self, strategy: Union[int, str, CommentStrategy] = 0, amount: int = 20):
        """|coro|

        Retrieves level comments.

        Parameters
        ----------
        strategy: Union[:class:`int`, :class:`str`, :class:`.CommentStrategy`]
            A strategy to apply when searching. This is converted to :class:`.CommentStrategy`
            using :func:`.utils.value_to_enum`.

        amount: :class:`int`
            Amount of comments to retrieve. Default is ``20``. (no limits)

        Returns
        -------
        List[:class:`.Comment`]
            List of comments retrieved.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to fetch comments.

        :exc:`.NothingFound`
            No comments were found.

        :exc:`.FailedConversion`
            Raised if ``strategy`` can not be converted to :class:`.CommentStrategy`.
        """
        strategy = value_to_enum(CommentStrategy, strategy)

        return await _session.get_level_comments(level=self, strategy=strategy, amount=amount)
