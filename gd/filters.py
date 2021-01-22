from gd.enums import DemonDifficulty, Enum, LevelDifficulty, LevelLength, SearchStrategy
from gd.iter_utils import is_iterable
from gd.text_utils import make_repr
from gd.typing import TYPE_CHECKING, Dict, Iterable, Optional, TypeVar, Union

__all__ = ("Filters", "join_with_wrap")

if TYPE_CHECKING:
    from gd.client import Client  # noqa
    from gd.level import Level  # noqa
    from gd.user import User  # noqa

T = TypeVar("T")

SPECIAL = {SearchStrategy.BY_USER, SearchStrategy.FEATURED, SearchStrategy.HALL_OF_FAME}


class Filters:
    """Class that adds ability to create custom filters to apply when searching for levels."""

    def __init__(
        self,
        strategy: Union[int, str, SearchStrategy] = SearchStrategy.REGULAR,
        difficulty: Optional[
            Union[Iterable[Union[int, str, LevelDifficulty]], Union[int, str, LevelDifficulty]]
        ] = None,
        demon_difficulty: Optional[Union[int, str, DemonDifficulty]] = None,
        length: Optional[Union[int, str, LevelLength]] = None,
        not_completed: bool = False,
        only_completed: bool = False,
        completed_levels: Iterable[Union[int, "Level"]] = (),
        require_coins: bool = False,
        featured: bool = False,
        epic: bool = False,
        rated: Optional[bool] = None,
        require_two_player: bool = False,
        song_id: Optional[int] = None,
        use_custom_song: bool = False,
        require_original: bool = False,
        followed: Iterable[Union[int, "User"]] = (),
    ) -> None:
        self.strategy = SearchStrategy.from_value(strategy)

        if difficulty and not is_iterable(difficulty):  # type: ignore
            difficulty = (difficulty,)  # type: ignore

        if length and not is_iterable(length):  # type: ignore
            length = (length,)  # type: ignore

        is_special = self.strategy in SPECIAL

        self.difficulty = (
            None
            if not difficulty or is_special
            else tuple(map(LevelDifficulty.from_value, difficulty))  # type: ignore
        )
        self.length = (
            None
            if not length or is_special
            else tuple(map(LevelLength.from_value, length))  # type: ignore
        )

        self.demon_difficulty = (
            None
            if not demon_difficulty or is_special
            else DemonDifficulty.from_value(demon_difficulty)
        )

        if self.demon_difficulty:
            self.difficulty = (LevelDifficulty.DEMON,)

        self.completed_levels = tuple(getattr(level, "id", level) for level in completed_levels)

        self.not_completed = not_completed if completed_levels else False
        self.only_completed = only_completed if completed_levels else False

        if self.not_completed and self.only_completed:
            raise ValueError("Both not_completed and only_completed are true.")

        self.require_coins = require_coins

        self.require_two_player = require_two_player

        self.rated = rated
        self.featured = featured
        self.epic = epic

        self.song_id = song_id
        self.use_custom_song = use_custom_song

        self.followed = tuple(getattr(user, "account_id", user) for user in followed)

        self.require_original = require_original

    def __repr__(self) -> str:
        info = {
            "strategy": self.strategy,
            "difficulty": self.difficulty,
            "length": self.length,
            "demon_difficulty": self.demon_difficulty,
            "not_completed": self.not_completed,
            "only_completed": self.only_completed,
            "require_coins": self.require_coins,
            "require_two_player": self.require_two_player,
            "rated": self.rated,
            "featured": self.featured,
            "epic": self.epic,
            "song_id": self.song_id,
            "use_custom_song": self.use_custom_song,
            "followed": self.followed,
            "require_original": self.require_original,
        }
        return make_repr(self, info)

    @classmethod
    def by_user(cls, *args, **kwargs) -> "Filters":
        return cls(SearchStrategy.BY_USER, *args, **kwargs)  # type: ignore

    @classmethod
    def with_song(cls, song_id: int, *args, is_custom: bool = True, **kwargs) -> "Filters":
        return cls(  # type: ignore
            *args, song_id=song_id, use_custom_song=is_custom, **kwargs,
        )

    @classmethod
    def search_many(cls, *args, **kwargs) -> "Filters":
        return cls(SearchStrategy.SEARCH_MANY, *args, **kwargs)  # type: ignore

    @classmethod
    def with_followed(cls, followed: Iterable[Union[int, "User"]], *args, **kwargs) -> "Filters":
        return cls(SearchStrategy.FOLLOWED, *args, followed=followed, **kwargs)  # type: ignore

    @classmethod
    def with_completed(
        cls, completed_levels: Iterable[Union[int, "Level"]], *args, **kwargs
    ) -> "Filters":
        return cls(*args, completed_levels=completed_levels, **kwargs)  # type: ignore

    @classmethod
    def by_friends(cls, *args, **kwargs) -> "Filters":
        return cls(SearchStrategy.FRIENDS, *args, **kwargs)  # type: ignore

    @classmethod
    def client_followed(cls, client: "Client", *args, **kwargs) -> "Filters":
        return cls.with_followed(client.database.followed, *args, **kwargs)  # type: ignore

    @classmethod
    def client_completed(cls, client: "Client", *args, **kwargs) -> "Filters":
        return cls.with_completed(  # type: ignore
            client.database.values.normal.completed, *args, **kwargs
        )

    def to_parameters(self) -> Dict[str, T]:
        parameters = {
            "type": self.strategy.value,
            "diff": "-" if not self.difficulty else join_with_wrap(self.difficulty),
            "len": "-" if not self.length else join_with_wrap(self.length),
            "uncompleted": int(self.not_completed),
            "only_completed": int(self.only_completed),
            "featured": int(self.featured),
            "original": int(self.require_original),
            "two_player": int(self.require_two_player),
            "coins": int(self.require_coins),
            "epic": int(self.epic),
        }

        if self.demon_difficulty:
            parameters["demon_filter"] = self.demon_difficulty.value

        if self.completed_levels:
            parameters["completed_levels"] = join_with_wrap(self.completed_levels, "({})")

        if self.rated is not None:
            parameters["star" if self.rated else "no_star"] = 1

        if self.followed:
            parameters["followed"] = join_with_wrap(self.followed)

        if self.song_id is not None:
            parameters["song"] = self.song_id
            parameters["custom_song"] = int(self.use_custom_song)

        return parameters


def value_if_enum_else_str(element: T) -> str:
    if isinstance(element, Enum):
        element = element.value

    return str(element)


def join_with_wrap(elements: Iterable[T], wrap: str = "{}", delim: str = ",") -> str:
    return wrap.format(delim.join(map(value_if_enum_else_str, elements)))
