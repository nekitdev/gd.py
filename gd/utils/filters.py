from typing import Any, Sequence

from .enums import (
    NEnum, LevelDifficulty, DemonDifficulty,
    SearchStrategy, LevelLength, value_to_enum
)
from .wrap_tools import make_repr

class Filters:
    """Class that adds ability to create custom filters to apply when searching for levels.

    Attributes
    ----------
    strategy: Optional[Union[:class:`int`, :class:`str`, :class:`SearchStrategy`]]
        A strategy to apply.
    difficulty: Optional[Sequence[Union[:class:`int`, :class:`str`, :class:`LevelDifficulty`]]]
        Level difficulties to apply. Either sequence of many or just one difficulty.
    demon_difficulty: Optional[Union[:class:`int`, :class:`str`, :class:`DemonDifficulty`]]
        **One** Demon difficulty to apply as a filter.
    length: Sequence[Union[:class:`int`, :class:`str`, :class:`LevelLength`]]
        Same as ``difficulty``, but for lengths.
    uncompleted: Optional[:class:`bool`]
        Whether to search for uncompleted levels only. If true, ``completed_levels`` is required.
    only_completed: Optional[:class:`bool`]
        Opposite of ``uncompleted``.
    completed_levels: Optional[Sequence[Union[:class:`int`, :class:`.Level`]]]
        A sequence of completed levels.
    require_coins: Optional[:class:`bool`]
        Whether levels must have coins in them.
    featured: Optional[:class:`bool`]
        Whether levels **must** be featured.
    epic: Optional[:class:`bool`]
        Whether levels ought to be epic.
    rated: Optional[:class:`bool`]
        This defaults to ``None``. If true, will search for only rated levels,
        if false, will search for only not rated levels. If ``None``, makes no changes.
    require_two_player: Optional[:class:`bool`]
        Whether a level must be for two players.
    song_id: Optional[:class:`int`]
        An ID of the song that should be used.
    use_custom_song: Optional[:class:`int`]
        Whether a custom song should be used. Requires ``song_id`` to be defined.
    followed: Optional[Sequence[Union[:class:`int`, :class:`.AbstractUser`, :class:`.User`]]]
        Followed users, basically this will work as ``BY_USER`` ``strategy``, but for many users.
    require_original: Optional[:class:`bool`]
        Whether levels must be original.
    """
    def __init__(
        self, strategy=0, difficulty=None, demon_difficulty=None, length=None,
        uncompleted=False, only_completed=False, completed_levels=[],
        require_coins=False, featured=False, epic=False, rated=None,
        require_two_player=False, song_id=None, use_custom_song=False,
        followed=[], require_original=False
    ):
        if isinstance(difficulty, (int, str, NEnum)):
            difficulty = [difficulty]

        if isinstance(length, (int, str, NEnum)):
            length = [length]

        self.strategy = value_to_enum(SearchStrategy, strategy)

        ss = (self.strategy.value in (5, 6, 16))

        self.difficulty = None if ((difficulty is None) or ss) else tuple(
            map(lambda diff: value_to_enum(LevelDifficulty, diff), difficulty)
        )

        self.length = None if ((length is None) or ss) else tuple(
            map(lambda l_length: value_to_enum(LevelLength, l_length), length)
        )

        self.demon_difficulty = (
            None if (
                (demon_difficulty is None) or ss
            ) else value_to_enum(DemonDifficulty, demon_difficulty)
        )

        if self.demon_difficulty is not None:
            self.diffculty = LevelDifficulty.DEMON

        self.uncompleted = uncompleted if completed_levels else False
        self.only_completed = only_completed if completed_levels else False
        self.completed_levels = list(completed_levels)
        self.require_coins = require_coins
        self.require_two_player = require_two_player
        self.rated = rated
        self.featured = featured
        self.epic = epic
        self.song_id = song_id
        self.use_custom_song = use_custom_song
        self.followed = list(followed)
        self.require_original = require_original
        self.set = (
            'strategy', 'difficulty', 'demon_difficulty', 'length',
            'uncompleted', 'only_completed', 'completed_levels',
            'require_coins', 'require_two_player', 'rated',
            'featured', 'epic', 'song_id', 'use_custom_song',
            'followed', 'require_original'
        )

    def __repr__(self):
        info = {k: repr(getattr(self, k)) for k in self.set}
        return make_repr(self, info)

    @classmethod
    def setup_empty(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    @classmethod
    def setup_simple(cls, *args, **kwargs):
        return cls(strategy=SearchStrategy.MOST_LIKED, *args, **kwargs)

    @classmethod
    def setup_by_user(cls, *args, **kwargs):
        return cls(strategy=SearchStrategy.BY_USER, *args, **kwargs)

    @classmethod
    def setup_with_song(cls, song_id: int, is_custom: bool = True, *args, **kwargs):
        return cls(strategy=SearchStrategy.MOST_LIKED, song_id=song_id, use_custom_song=is_custom, *args, **kwargs)

    @classmethod
    def setup_search_many(cls):
        return cls(strategy=SearchStrategy.SEARCH_MANY)

    @classmethod
    def setup_with_followed(cls, followed: Sequence[int], *args, **kwargs):
        return cls(strategy=SearchStrategy.FOLLOWED, followed=followed, *args, **kwargs)

    @classmethod
    def setup_by_friends(cls, *args, **kwargs):
        return cls(strategy=SearchStrategy.FRIENDS, *args, **kwargs)

    @classmethod
    def setup_client_followed(cls, client, *args, **kwargs):
        return cls(strategy=SearchStrategy.FOLLOWED, followed=client.save.followed, *args, **kwargs)

    @classmethod
    def setup_client_completed(cls, client, *args, **kwargs):
        return cls(strategy=SearchStrategy.MOST_LIKED, completed_levels=client.save.completed, *args, **kwargs)

    def to_parameters(self):
        main = {
            'type': self.strategy.value,
            'diff': '-' if self.difficulty is None else _join(',', self.difficulty),
            'len': '-' if self.length is None else _join(',', self.length),
            'uncompleted': int(self.uncompleted),
            'onlyCompleted': int(self.only_completed),
            'featured': int(self.featured),
            'original': int(self.require_original),
            'twoPlayer': int(self.require_two_player),
            'coins': int(self.require_coins),
            'epic': int(self.epic)
        }

        if self.demon_difficulty is not None:
            main.update(
                {'demonFilter': self.demon_difficulty.value}
            )

        if self.uncompleted or self.only_completed:  # adds only if completed_levels not empty
            main.update(
                {'completedLevels': _join(',', self.completed_levels, wrap_with='({})')}
            )

        if self.rated is not None:
            main.update(
                {('star' if self.rated else 'noStar'): 1}
            )

        if self.strategy == SearchStrategy.FOLLOWED:
            main.update(
                {'followed': _join(',', self.followed)}
            )

        if self.song_id is not None:
            main.update({
                'song': int(self.song_id),
                'isCustom': int(self.use_custom_song)
            })

        filters = {k: str(v) for k, v in main.items()}
        return filters

def _join(string: str, elements: Sequence[Any], *, wrap_with: str = '{}'):

    def func(element):
        to_str = element
        if isinstance(element, NEnum):  # Enum
            to_str = element.value
        elif hasattr(element, 'account_id'):  # AbstractUser
            to_str = element.account_id
        elif hasattr(element, 'id'):  # Level
            to_str = element.id
        return str(to_str)

    return wrap_with.format(string.join(map(func, elements)))
