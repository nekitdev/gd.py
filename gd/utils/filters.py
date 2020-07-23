from enums import Enum

from gd.typing import AbstractUser, Any, Dict, Filters, Level, Optional, Sequence, Union

from gd.utils.enums import LevelDifficulty, DemonDifficulty, SearchStrategy, LevelLength
from gd.utils.text_tools import make_repr


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
    require_original: Optional[:class:`bool`]
        Whether levels must be original.
    followed: Optional[Sequence[Union[:class:`int`, :class:`.AbstractUser`, :class:`.User`]]]
        Followed users, basically this will work as ``BY_USER`` ``strategy``, but for many users.
    """

    def __init__(
        self,
        strategy: Union[int, str, SearchStrategy] = 0,
        difficulty: Optional[Sequence[Union[int, str, LevelDifficulty]]] = None,
        demon_difficulty: Optional[Union[int, str, DemonDifficulty]] = None,
        length: Optional[Union[int, str, LevelLength]] = None,
        uncompleted: bool = False,
        only_completed: bool = False,
        completed_levels: Optional[Sequence[Union[int, Level]]] = None,
        require_coins: bool = False,
        featured: bool = False,
        epic: bool = False,
        rated: Optional[bool] = None,
        require_two_player: bool = False,
        song_id: Optional[int] = None,
        use_custom_song: bool = False,
        require_original: bool = False,
        followed: Optional[Sequence[Union[int, AbstractUser]]] = None,
    ) -> None:
        if isinstance(difficulty, (int, str, Enum)):
            difficulty = [difficulty]

        if isinstance(length, (int, str, Enum)):
            length = [length]

        self.strategy = SearchStrategy.from_value(strategy)

        not_accepting = self.strategy.value in (5, 6, 16)

        self.difficulty = (
            None
            if ((difficulty is None) or not_accepting)
            else tuple(map(LevelDifficulty.from_value, difficulty))
        )

        self.length = (
            None
            if ((length is None) or not_accepting)
            else tuple(map(LevelLength.from_value, length))
        )

        self.demon_difficulty = (
            None
            if ((demon_difficulty is None) or not_accepting)
            else DemonDifficulty.from_value(demon_difficulty)
        )

        if self.demon_difficulty is not None:
            self.difficulty = (LevelDifficulty.DEMON,)

        self.uncompleted = uncompleted if completed_levels else False
        self.only_completed = only_completed if completed_levels else False
        self.completed_levels = list(completed_levels or [])
        self.require_coins = require_coins
        self.require_two_player = require_two_player
        self.rated = rated
        self.featured = featured
        self.epic = epic
        self.song_id = song_id
        self.use_custom_song = use_custom_song
        self.followed = list(followed or [])
        self.require_original = require_original
        self.set = (
            "strategy",
            "difficulty",
            "demon_difficulty",
            "length",
            "uncompleted",
            "only_completed",
            "completed_levels",
            "require_coins",
            "require_two_player",
            "rated",
            "featured",
            "epic",
            "song_id",
            "use_custom_song",
            "followed",
            "require_original",
        )

    def __repr__(self) -> str:
        info = {k: repr(getattr(self, k)) for k in self.set}
        return make_repr(self, info)

    @classmethod
    def setup_empty(cls, *args, **kwargs) -> Filters:
        return cls(*args, **kwargs)

    @classmethod
    def setup_simple(cls, *args, **kwargs) -> Filters:
        return cls(strategy=SearchStrategy.MOST_LIKED, *args, **kwargs)

    @classmethod
    def setup_by_user(cls, *args, **kwargs) -> Filters:
        return cls(strategy=SearchStrategy.BY_USER, *args, **kwargs)

    @classmethod
    def setup_with_song(cls, song_id: int, is_custom: bool = True, *args, **kwargs) -> Filters:
        return cls(
            strategy=SearchStrategy.MOST_LIKED,
            song_id=song_id,
            use_custom_song=is_custom,
            *args,
            **kwargs,
        )

    @classmethod
    def setup_search_many(cls) -> Filters:
        return cls(strategy=SearchStrategy.SEARCH_MANY)

    @classmethod
    def setup_with_followed(cls, followed: Sequence[int], *args, **kwargs) -> Filters:
        return cls(strategy=SearchStrategy.FOLLOWED, followed=followed, *args, **kwargs)

    @classmethod
    def setup_by_friends(cls, *args, **kwargs) -> Filters:
        return cls(strategy=SearchStrategy.FRIENDS, *args, **kwargs)

    @classmethod
    def setup_client_followed(cls, client, *args, **kwargs) -> Filters:
        return cls(strategy=SearchStrategy.FOLLOWED, followed=client.db.followed, *args, **kwargs)

    @classmethod
    def setup_client_completed(cls, client, *args, **kwargs) -> Filters:
        return cls(
            strategy=SearchStrategy.MOST_LIKED,
            completed_levels=client.db.values.normal.completed,
            *args,
            **kwargs,
        )

    def to_parameters(self) -> Dict[str, str]:
        main = {
            "type": self.strategy.value,
            "diff": "-" if self.difficulty is None else _join(self.difficulty),
            "len": "-" if self.length is None else _join(self.length),
            "uncompleted": int(self.uncompleted),
            "onlyCompleted": int(self.only_completed),
            "featured": int(self.featured),
            "original": int(self.require_original),
            "twoPlayer": int(self.require_two_player),
            "coins": int(self.require_coins),
            "epic": int(self.epic),
        }

        if self.demon_difficulty is not None:
            main.update(demonFilter=self.demon_difficulty.value)

        if self.uncompleted or self.only_completed:
            main.update(completedLevels=_join(self.completed_levels, wrap_with="({})"))

        if self.rated is not None:
            main.update({("star" if self.rated else "noStar"): 1})

        if self.strategy == SearchStrategy.FOLLOWED:
            main.update(followed=_join(self.followed))

        if self.song_id is not None:
            main.update(song=int(self.song_id), isCustom=int(self.use_custom_song))

        filters = {k: str(v) for k, v in main.items()}
        return filters


def _join(elements: Sequence[Any], *, string: str = ",", wrap_with: str = "{}") -> str:
    def func(element: Any) -> str:
        to_str = element

        if isinstance(element, Enum):  # Enum
            to_str = element.value
        elif hasattr(element, "account_id"):  # User
            to_str = element.account_id
        elif hasattr(element, "id"):  # Level
            to_str = element.id

        return str(to_str)

    return wrap_with.format(string.join(map(func, elements)))
