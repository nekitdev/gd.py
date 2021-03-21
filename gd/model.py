# type: ignore  # static type checkers do not understand this

from gd.color import Color
from gd.converters import GameVersion, Password, get_actual_difficulty, value_to_level_difficulty
from gd.crypto import (
    Key,
    decode_robtop_str,
    encode_robtop_str,
    fix_song_encoding,
    generate_rs,
    unzip_level_str,
    zip_level_str,
)
from gd.datetime import datetime
from gd.decorators import cache_by
from gd.enums import (
    CommentState,
    DemonDifficulty,
    FriendRequestState,
    FriendState,
    IconType,
    LevelDifficulty,
    LevelLength,
    MessageState,
    QuestType,
    RewardType,
    Role,
    TimelyType,
)
from gd.model_backend import (
    Base64Field,
    BoolField,
    ColorField,
    EnumField,
    Field,
    FloatField,
    IndexParser,
    IntField,
    IterableField,
    Model,
    ModelField,
    ModelIterField,
    RobTopStrField,
    RobTopTimeField,
    StrField,
    URLField,
)
from gd.text_utils import is_level_probably_decoded
from gd.typing import Dict, List, Optional, Tuple, TypeVar, Union

__all__ = (
    "ChestModel",
    "CommentBannedModel",
    "CommentInnerModel",
    "CommentModel",
    "CommentUserModel",
    "CreatorModel",
    "FriendRequestModel",
    "GauntletModel",
    "LevelLeaderboardUserModel",
    "LeaderboardUserModel",
    "LevelModel",
    "ListUserModel",
    "LoginIDModel",
    "MapPackModel",
    "MessageModel",
    "PageModel",
    "ProfileUserModel",
    "QuestModel",
    "SaveModel",
    "SearchUserModel",
    "SongModel",
    "TimelyInfoModel",
    "Model",
)

CHEST_SLICE = 5
QUEST_SLICE = 5

T = TypeVar("T")


class SongModel(Model):
    PARSER = IndexParser("~|~", map_like=True)

    id: int = IntField(index=1, default=0)
    name: str = Field(index=2, de=fix_song_encoding, ser=str, default="Unknown")
    author_id: int = IntField(index=3, default=0)
    author: str = Field(index=4, de=fix_song_encoding, ser=str, default="Unknown")
    size: float = FloatField(index=5, default=0.0)
    youtube_video_id: str = StrField(index=6, default="")
    youtube_channel_id: str = StrField(index=7, default="")
    index_8: str = StrField(index=8, default="")
    download_link: str = URLField(index=10, default="")


class LoginIDModel(Model):
    PARSER = IndexParser(",", map_like=False)

    account_id: int = IntField(index=0, default=0)
    id: int = IntField(index=1, default=0)


class LevelLeaderboardUserModel(Model):
    PARSER = IndexParser(":", map_like=True)

    name: str = StrField(index=1, default="Unknown")
    id: int = IntField(index=2, default=0)
    percent: int = IntField(index=3, default=0)
    place: int = IntField(index=6, default=0)
    icon_id: int = IntField(index=9, default=0)
    color_1_id: int = IntField(index=10, default=0)
    color_2_id: int = IntField(index=11, default=3)
    coins: int = IntField(index=13, default=0)
    icon_type: IconType = EnumField(index=14, enum_type=IconType, from_field=IntField)
    has_glow: bool = BoolField(index=15, false="0", true="2", default=False)
    recorded_at: datetime = RobTopTimeField(index=42)


class SearchUserModel(Model):
    PARSER = IndexParser(":", map_like=True)

    name: str = StrField(index=1, default="Unknown")
    id: int = IntField(index=2, default=0)
    stars: int = IntField(index=3, default=0)
    demons: int = IntField(index=4, default=0)
    place: int = IntField(index=6, default=0, use_default_on_fail=True)
    cp: int = IntField(index=8, default=0)
    icon_id: int = IntField(index=9, default=0)
    color_1_id: int = IntField(index=10, default=0)
    color_2_id: int = IntField(index=11, default=3)
    coins: int = IntField(index=13, default=0)
    icon_type: IconType = EnumField(index=14, enum_type=IconType, from_field=IntField)
    has_glow: bool = BoolField(index=15, false="0", true="2", default=False)
    account_id: int = IntField(index=16, default=0)
    user_coins: int = IntField(index=17, default=0)


class ListUserModel(Model):
    PARSER = IndexParser(":", map_like=True)

    name: str = StrField(index=1, default="Unknown")
    id: int = IntField(index=2, default=0)
    icon_id: int = IntField(index=9, default=0)
    color_1_id: int = IntField(index=10, default=0)
    color_2_id: int = IntField(index=11, default=3)
    icon_type: IconType = EnumField(index=14, enum_type=IconType, from_field=IntField)
    has_glow: bool = BoolField(index=15, false="0", true="2", default=False)
    account_id: int = IntField(index=16, default=0)
    message_state: MessageState = EnumField(index=18, enum_type=MessageState, from_field=IntField)


class LeaderboardUserModel(Model):
    PARSER = IndexParser(":", map_like=True)

    name: str = StrField(index=1, default="Unknown")
    id: int = IntField(index=2, default=0)
    stars: int = IntField(index=3, default=0)
    demons: int = IntField(index=4, default=0)
    place: int = IntField(index=6, default=0)
    cp: int = IntField(index=8, default=0)
    icon_id: int = IntField(index=9, default=0)
    color_1_id: int = IntField(index=10, default=0)
    color_2_id: int = IntField(index=11, default=3)
    coins: int = IntField(index=13, default=0)
    icon_type: IconType = EnumField(index=14, enum_type=IconType, from_field=IntField)
    has_glow: bool = BoolField(index=15, false="0", true="2", default=False)
    account_id: int = IntField(index=16, default=0)
    user_coins: int = IntField(index=17, default=0)
    diamonds: int = IntField(index=46, default=0)


class ProfileUserModel(Model):
    PARSER = IndexParser(":", map_like=True)

    name: str = StrField(index=1, default="Unknown")
    id: int = IntField(index=2, default=0)
    stars: int = IntField(index=3, default=0)
    demons: int = IntField(index=4, default=0)
    cp: int = IntField(index=8, default=0)
    color_1_id: int = IntField(index=10, default=0)
    color_2_id: int = IntField(index=11, default=3)
    coins: int = IntField(index=13, default=0)
    account_id: int = IntField(index=16, default=0)
    user_coins: int = IntField(index=17, default=0)
    message_state: MessageState = EnumField(index=18, enum_type=MessageState, from_field=IntField)
    friend_request_state: FriendRequestState = EnumField(
        index=19, enum_type=FriendRequestState, from_field=IntField
    )
    youtube: str = StrField(index=20, default="")
    cube_id: int = IntField(index=21, default=0)
    ship_id: int = IntField(index=22, default=0)
    ball_id: int = IntField(index=23, default=0)
    ufo_id: int = IntField(index=24, default=0)
    wave_id: int = IntField(index=25, default=0)
    robot_id: int = IntField(index=26, default=0)
    has_glow: bool = BoolField(index=28, default=False)
    not_banned: bool = BoolField(index=29, default=True)
    global_rank: int = IntField(index=30, default=0)
    friend_state: FriendState = EnumField(index=31, enum_type=FriendState, from_field=IntField)
    new_messages: int = IntField(index=38, default=0)
    new_friend_requests: int = IntField(index=39, default=0)
    new_friends: int = IntField(index=40, default=0)
    spider_id: int = IntField(index=43, default=0)
    twitter: str = StrField(index=44, default="")
    twitch: str = StrField(index=45, default="")
    diamonds: int = IntField(index=46, default=0)
    death_effect_id: int = IntField(index=48, default=0)
    role: Role = EnumField(index=49, enum_type=Role, from_field=IntField)
    comments_state: CommentState = EnumField(index=50, enum_type=CommentState, from_field=IntField)

    def to_dict(self) -> Dict[str, T]:
        result = super().to_dict()
        result.update(banned=self.banned)
        return result

    @property
    def banned(self) -> bool:
        return not self.not_banned

    @banned.setter
    def banned(self, value: bool) -> None:
        self.not_banned = not value

    @banned.deleter
    def banned(self) -> None:
        del self.not_banned

    def is_banned(self) -> bool:
        return self.banned

    def is_not_banned(self) -> bool:
        return self.not_banned


class CreatorModel(Model):
    PARSER = IndexParser(":", map_like=False)

    id: int = IntField(index=0, default=0)
    name: str = StrField(index=1, default="unknown")
    account_id: int = IntField(index=2, default=0)


class SaveModel(Model):
    PARSER = IndexParser(";", map_like=False)

    main: str = StrField(index=0, default="")
    levels: str = StrField(index=1, default="")


class PageModel(Model):
    PARSER = IndexParser(":", map_like=False)

    total: int = IntField(index=0, default=0, use_default_on_fail=True)
    page_start: int = IntField(index=1, default=0, use_default_on_fail=True)
    page_end: int = IntField(index=2, default=0, use_default_on_fail=True)


class LevelModel(Model):
    PARSER = IndexParser(":", map_like=True)
    REPR_IGNORE = {"unprocessed_data"}

    id: int = IntField(index=1, default=0)
    name: str = StrField(index=2, default="Unnamed")
    description: str = Base64Field(index=3, default="")
    unprocessed_data: str = StrField(index=4, default="")
    version: int = IntField(index=5, default=0)
    creator_id: int = IntField(index=6, default=0)
    difficulty_denominator: int = IntField(index=8, default=0)
    difficulty_numerator: int = IntField(index=9, default=0)
    downloads: int = IntField(index=10, default=0)
    official_song_id: int = IntField(index=12, default=0)
    game_version: GameVersion = Field(
        index=13, de=GameVersion.from_robtop, ser=GameVersion.to_robtop
    )
    rating: int = IntField(index=14, default=0)
    length: LevelLength = EnumField(index=15, enum_type=LevelLength, from_field=IntField)
    demon: bool = BoolField(index=17, false="", true="1", default=False)
    stars: int = IntField(index=18, default=0)
    score: int = IntField(index=19, default=0)
    auto: bool = BoolField(index=25, false="", true="1", default=False)
    password_field: Password = Field(index=27, de=Password.from_robtop, ser=Password.to_robtop)
    uploaded_at: datetime = RobTopTimeField(index=28)
    updated_at: datetime = RobTopTimeField(index=29)
    original_id: int = IntField(index=30, default=0)
    two_player: bool = BoolField(index=31, default=False)
    custom_song_id: int = IntField(index=35, default=0)
    extra_string: str = StrField(index=36, default="")
    coins: int = IntField(index=37, default=0)
    verified_coins: bool = BoolField(index=38, default=False)
    requested_stars: int = IntField(index=39, default=0)
    low_detail_mode: bool = BoolField(index=40, false="", true="1", default=False)
    real_timely_id: int = IntField(index=41, default=0)
    epic: bool = BoolField(index=42, default=False)
    demon_difficulty: int = IntField(index=43, default=0)
    object_count: int = IntField(index=45, default=0)
    editor_seconds: int = IntField(index=46, default=0, use_default_on_fail=True)
    copies_seconds: int = IntField(index=47, default=0, use_default_on_fail=True)

    def is_auto(self) -> bool:
        return self.auto

    def is_demon(self) -> bool:
        return self.demon

    def is_epic(self) -> bool:
        return self.epic

    def is_rated(self) -> bool:
        return self.stars > 0

    def is_featured(self) -> bool:
        return self.score > 0

    def was_unfeatured(self) -> bool:
        return self.score < 0

    def get_password(self) -> Optional[int]:
        if self.password_field is None:
            return None

        return self.password_field.password

    def set_password(self, password: Optional[int]) -> None:
        if self.password_field is None:
            self.password_field = Password(password)

        else:
            self.password_field.password = password

    password = property(get_password, set_password)

    def get_copyable(self) -> bool:
        if self.password_field is None:
            return False

        return self.password_field.copyable

    def set_copyable(self, copyable: bool) -> None:
        if self.password_field is None:
            self.password_field = Password(None, copyable)

        else:
            self.password_field.copyable = copyable

    copyable = property(get_copyable, set_copyable)

    @property
    def timely_id(self) -> int:
        if self.real_timely_id is None:
            return 0

        return self.real_timely_id % 100_000

    @property
    def type(self) -> TimelyType:
        real_timely_id = self.real_timely_id

        if not real_timely_id:
            return TimelyType.NOT_TIMELY

        elif real_timely_id // 100_000:
            return TimelyType.WEEKLY

        else:
            return TimelyType.DAILY

    @property
    def level_difficulty(self) -> int:
        if self.difficulty_denominator:
            return self.difficulty_numerator // self.difficulty_denominator

        return 0

    def get_difficulty(self) -> Union[LevelDifficulty, DemonDifficulty]:
        return get_actual_difficulty(
            level_difficulty=self.level_difficulty,
            demon_difficulty=self.demon_difficulty,
            is_auto=self.is_auto(),
            is_demon=self.is_demon(),
        )

    def set_difficulty(self, difficulty: Union[LevelDifficulty, DemonDifficulty]) -> None:
        ...

    difficulty = property(get_difficulty, set_difficulty)

    def to_dict(self) -> Dict[str, T]:
        result = super().to_dict()
        result.update(
            password=self.password,
            copyable=self.copyable,
            timely_id=self.timely_id,
            type=self.type,
            level_difficulty=self.level_difficulty,
            difficulty=self.difficulty,
        )
        return result

    @cache_by("unprocessed_data")
    def get_data(self) -> str:
        unprocessed_data = self.unprocessed_data

        if is_level_probably_decoded(unprocessed_data):
            return unprocessed_data

        else:
            return unzip_level_str(unprocessed_data)

    def set_data(self, data: str) -> None:
        if is_level_probably_decoded(data):
            self.unprocessed_data = zip_level_str(data)

        else:
            self.unprocessed_data = data

    data = property(get_data, set_data)


class CommentInnerModel(Model):
    PARSER = IndexParser("~", map_like=True)

    level_id: int = IntField(index=1, default=0)
    content: str = Base64Field(index=2, default="")
    author_id: int = IntField(index=3, default=0)
    rating: int = IntField(index=4, default=0)
    id: int = IntField(index=6, default=0)
    spam: bool = BoolField(index=7, default=False)
    created_at: datetime = RobTopTimeField(index=9)
    level_percent: int = IntField(index=10, default=0)
    mod_level: int = IntField(index=11, default=0)
    color: Color = ColorField(index=12, factory=lambda: Color(0xFFFFFF))

    def is_spam(self) -> bool:
        return self.spam


class CommentUserModel(Model):
    PARSER = IndexParser("~", map_like=True)

    name: str = StrField(index=1, default="Unknown")
    icon_id: int = IntField(index=9, default=0)
    color_1_id: int = IntField(index=10, default=0)
    color_2_id: int = IntField(index=11, default=3)
    icon_type: IconType = EnumField(index=14, enum_type=IconType, from_field=IntField)
    has_glow: bool = BoolField(index=15, false="0", true="2", default=False)
    account_id: int = IntField(index=16, default=0)


class CommentModel(Model):
    PARSER = IndexParser(":", map_like=False)

    inner: CommentInnerModel = ModelField(index=0, use_default=True, model=CommentInnerModel)
    user: CommentUserModel = ModelField(index=1, use_default=True, model=CommentUserModel)


class FriendRequestModel(Model):
    PARSER = IndexParser(":", map_like=True)

    name: str = StrField(index=1, default="Unknown")
    user_id: int = IntField(index=2, default=0)
    icon_id: int = IntField(index=9, default=0)
    color_1_id: int = IntField(index=10, default=0)
    color_2_id: int = IntField(index=11, default=3)
    icon_type: IconType = EnumField(index=14, enum_type=IconType, from_field=IntField)
    has_glow: bool = BoolField(index=15, false="0", true="2", default=False)
    account_id: int = IntField(index=16, default=0)
    id: int = IntField(index=32, default=0)
    content: str = Base64Field(index=35, default="")
    created_at: datetime = RobTopTimeField(index=37)
    unread: bool = BoolField(index=41, false="", true="1", default=True)

    def to_dict(self) -> Dict[str, T]:
        result = super().to_dict()
        result.update(read=self.read)
        return result

    @property
    def read(self) -> bool:
        return not self.unread

    @read.setter
    def read(self, value: bool) -> None:
        self.unread = not value

    @read.deleter
    def read(self) -> None:
        del self.unread

    def is_read(self) -> bool:
        return self.read


class MessageModel(Model):
    PARSER = IndexParser(":", map_like=True)

    id: int = IntField(index=1, default=0)
    account_id: int = IntField(index=2, default=0)
    user_id: int = IntField(index=3, default=0)
    subject: str = Base64Field(index=4, default="")
    content: str = RobTopStrField(index=5, key=Key.MESSAGE)
    name: str = StrField(index=6, default="Unknown")
    created_at: datetime = RobTopTimeField(index=7)
    read: bool = BoolField(index=8, default=False)
    sent: bool = BoolField(index=9, default=False)

    def to_dict(self) -> Dict[str, T]:
        result = super().to_dict()
        result.update(unread=self.unread)
        return result

    @property
    def unread(self) -> bool:
        return not self.read

    @unread.setter
    def unread(self, value: bool) -> None:
        self.read = not value

    @unread.deleter
    def unread(self) -> None:
        del self.read

    def is_read(self) -> bool:
        return self.read

    def is_unread(self) -> bool:
        return self.unread

    def is_incoming(self) -> bool:
        return not self.is_sent()

    def is_sent(self) -> bool:
        return self.sent


class MapPackModel(Model):
    PARSER = IndexParser(":", map_like=True)

    id: int = IntField(index=1, default=0)
    name: str = StrField(index=2, default="Unknown")
    levels: Tuple[int, ...] = IterableField(
        index=3, delim=",", transform=tuple, from_field=IntField, default=()
    )
    stars: int = IntField(index=4, default=0)
    coins: int = IntField(index=5, default=0)
    level_difficulty: int = IntField(index=6, default=-1)
    color: Color = ColorField(index=7, factory=lambda: Color(0xFFFFFF))
    other_color: Color = ColorField(index=8, factory=lambda: Color(0xFFFFFF))

    def to_dict(self) -> Dict[str, T]:
        result = super().to_dict()
        result.update(difficulty=self.difficulty)
        return result

    @property
    def difficulty(self) -> LevelDifficulty:
        return value_to_level_difficulty(self.level_difficulty)


class GauntletModel(Model):
    PARSER = IndexParser(":", map_like=True)

    id: int = IntField(index=1, default=0)
    levels: Tuple[int, ...] = IterableField(
        index=3, delim=",", transform=tuple, from_field=IntField, default=()
    )


class QuestModel(Model):
    PARSER = IndexParser(",", map_like=False)

    id: int = IntField(index=0, default=0)
    type: QuestType = EnumField(index=1, enum_type=QuestType, from_field=IntField)
    amount: int = IntField(index=2, default=0)
    reward: int = IntField(index=3, default=0)
    name: str = StrField(index=4, default="Unknown")


class ChestModel(Model):
    PARSER = IndexParser(",", map_like=False)

    orbs: int = IntField(index=0, default=0)
    diamonds: int = IntField(index=1, default=0)
    shard_id: int = IntField(index=2, default=0)
    keys: int = IntField(index=3, default=0)


class TimelyInfoModel(Model):
    PARSER = IndexParser("|", map_like=False)

    real_timely_id: int = IntField(index=0, default=0)
    cooldown: int = IntField(index=1, default=0)

    def to_dict(self) -> Dict[str, T]:
        result = super().to_dict()
        result.update(timely_id=self.timely_id, type=self.type)
        return result

    @property
    def timely_id(self) -> int:
        return self.real_timely_id % 100_000

    @property
    def type(self) -> TimelyType:
        real_timely_id = self.real_timely_id

        if not real_timely_id:
            return TimelyType.NOT_TIMELY

        elif real_timely_id // 100_000:
            return TimelyType.WEEKLY

        else:
            return TimelyType.DAILY


class SearchUserResponseModel(Model):
    PARSER = IndexParser("#", map_like=False)

    users: List[SearchUserModel] = ModelIterField(
        index=0, model=SearchUserModel, delim="|", use_default=True, transform=list, factory=list,
    )
    page: PageModel = ModelField(index=1, model=PageModel, factory=PageModel)


class LevelDownloadResponseModel(Model):
    PARSER = IndexParser("#", map_like=False)

    level: LevelModel = ModelField(index=0, model=LevelModel)
    hash: str = StrField(index=1, default="")


class LevelSearchResponseModel(Model):
    PARSER = IndexParser("#", map_like=False)

    levels: List[LevelModel] = ModelIterField(
        index=0, model=LevelModel, delim="|", use_default=True, transform=list, factory=list,
    )
    creators: List[CreatorModel] = ModelIterField(
        index=1, model=CreatorModel, delim="|", use_default=True, transform=list, factory=list,
    )
    songs: List[SongModel] = ModelIterField(
        index=2, model=SongModel, delim="~:~", use_default=True, transform=list, factory=list,
    )
    page: PageModel = ModelField(index=3, use_default=True, model=PageModel, factory=PageModel)
    hash: str = StrField(index=4, default="")


class FeaturedArtistsResponseModel(Model):
    PARSER = IndexParser("#", map_like=False)

    featured_artists: List[SongModel] = ModelIterField(
        index=0, model=SongModel, delim="|", use_default=True, transform=list, factory=list,
    )
    page: PageModel = ModelField(index=1, use_default=True, model=PageModel, factory=PageModel)


class UserListResponseModel(Model):
    PARSER = IndexParser("#", map_like=False)

    users: List[ListUserModel] = ModelIterField(
        index=0, model=ListUserModel, delim="|", use_default=True, transform=list, factory=list,
    )


class CommentsResponseModel(Model):
    PARSER = IndexParser("#", map_like=False)

    comments: List[CommentModel] = ModelIterField(
        index=0, model=CommentModel, delim="|", use_default=True, transform=list, factory=list,
    )
    page: PageModel = ModelField(index=1, use_default=True, model=PageModel, factory=PageModel)


class CommentBannedModel(Model):
    PARSER = IndexParser("_", map_like=False)

    TEMPORARY = "temp"

    string: str = StrField(index=0, default=TEMPORARY)
    timeout: Optional[int] = IntField(index=1, default=None)
    reason: Optional[str] = StrField(index=2, default=None)


class LeaderboardResponseModel(Model):
    PARSER = IndexParser("#", map_like=False)

    users: List[LeaderboardUserModel] = ModelIterField(
        index=0,
        model=LeaderboardUserModel,
        delim="|",
        use_default=True,
        transform=list,
        factory=list,
    )


class LevelLeaderboardResponseModel(Model):
    PARSER = IndexParser("#", map_like=False)

    users: List[LevelLeaderboardUserModel] = ModelIterField(
        index=0,
        model=LevelLeaderboardUserModel,
        delim="|",
        use_default=True,
        transform=list,
        factory=list,
    )


class FriendRequestsResponseModel(Model):
    PARSER = IndexParser("#", map_like=False)

    friend_requests: List[FriendRequestModel] = ModelIterField(
        index=0,
        model=FriendRequestModel,
        delim="|",
        use_default=True,
        transform=list,
        factory=list,
    )
    page: PageModel = ModelField(index=1, use_default=True, model=PageModel, factory=PageModel)


class MessagesResponseModel(Model):
    PARSER = IndexParser("#", map_like=False)

    messages: List[MessageModel] = ModelIterField(
        index=0, model=MessageModel, delim="|", use_default=True, transform=list, factory=list,
    )
    page: PageModel = ModelField(index=1, use_default=True, model=PageModel, factory=PageModel)


class MapPacksResponseModel(Model):
    PARSER = IndexParser("#", map_like=False)

    map_packs: List[MapPackModel] = ModelIterField(
        index=0, model=MapPackModel, delim="|", use_default=True, transform=list, factory=list,
    )
    page: PageModel = ModelField(index=1, use_default=True, model=PageModel, factory=PageModel)
    hash: str = StrField(index=2, default="")


class GauntletsResponseModel(Model):
    PARSER = IndexParser("#", map_like=False)

    gauntlets: List[GauntletModel] = ModelIterField(
        index=0, model=GauntletModel, delim="|", transform=list, factory=list
    )
    hash: str = StrField(index=1, default="")


class ChestsInnerModel(Model):
    PARSER = IndexParser(":", map_like=False)

    rs: str = StrField(index=0, default="")
    user_id: int = IntField(index=1, default=0)
    chk: str = StrField(index=2, default="")
    udid: str = StrField(index=3, default="")
    account_id: int = IntField(index=4, default=0)
    chest_1_left: int = IntField(index=5, default=0)
    chest_1: ChestModel = ModelField(
        index=6, model=ChestModel, use_default=True, factory=ChestModel
    )
    chest_1_count: int = IntField(index=7, default=0)
    chest_2_left: int = IntField(index=8, default=0)
    chest_2: ChestModel = ModelField(
        index=9, model=ChestModel, use_default=True, factory=ChestModel
    )
    chest_2_count: int = IntField(index=10, default=0)
    reward_type: RewardType = EnumField(index=11, enum_type=RewardType, from_field=IntField)


class QuestsInnerModel(Model):
    PARSER = IndexParser(":", map_like=False)

    rs: str = StrField(index=0, default="")
    user_id: int = IntField(index=1, default=0)
    chk: str = StrField(index=2, default="")
    udid: str = StrField(index=3, default="")
    account_id: int = IntField(index=4, default=0)
    time_left: int = IntField(index=5, default=0)
    quest_1: QuestModel = ModelField(
        index=6, model=QuestModel, use_default=True, factory=QuestModel
    )
    quest_2: QuestModel = ModelField(
        index=7, model=QuestModel, use_default=True, factory=QuestModel
    )
    quest_3: QuestModel = ModelField(
        index=8, model=QuestModel, use_default=True, factory=QuestModel
    )


def de_chests(string: str) -> ChestsInnerModel:
    return ChestsInnerModel.from_string(decode_robtop_str(string[CHEST_SLICE:], Key.CHESTS))


def de_quests(string: str) -> QuestsInnerModel:
    return QuestsInnerModel.from_string(decode_robtop_str(string[QUEST_SLICE:], Key.QUESTS))


def ser_chests(model: ChestsInnerModel) -> str:
    return generate_rs(CHEST_SLICE) + encode_robtop_str(model.to_string(), Key.CHESTS)


def ser_quests(model: QuestsInnerModel) -> str:
    return generate_rs(QUEST_SLICE) + encode_robtop_str(model.to_string(), Key.QUESTS)


class ChestsResponseModel(Model):
    PARSER = IndexParser("|", map_like=False)

    inner: ChestsInnerModel = Field(index=0, de=de_chests, ser=ser_chests)
    hash: str = StrField(index=1, default="")


class QuestsResponseModel(Model):
    PARSER = IndexParser("|", map_like=False)

    inner: QuestsInnerModel = Field(index=0, de=de_quests, ser=ser_quests)
    hash: str = StrField(index=1, default="")
