from __future__ import annotations

from typing import List, Optional, Sequence, TypeVar

from attrs import field, frozen
from pendulum import Duration
from yarl import URL

from gd.api.database.database import Database
from gd.api.recording import Recording
from gd.api.save_manager import save
from gd.capacity import Capacity
from gd.constants import (
    DEFAULT_CHEST_COUNT,
    DEFAULT_COINS,
    DEFAULT_ID,
    DEFAULT_LOW_DETAIL,
    DEFAULT_OBJECT_COUNT,
    DEFAULT_PAGE,
    DEFAULT_SPECIAL,
    DEFAULT_STARS,
    DEFAULT_TWO_PLAYER,
    DEFAULT_VERSION,
    EMPTY,
    UNNAMED,
)
from gd.enums import (
    AccountURLType,
    CommentState,
    CommentStrategy,
    DemonDifficulty,
    FriendRequestState,
    FriendRequestType,
    IconType,
    LeaderboardStrategy,
    LevelLeaderboardStrategy,
    LevelLength,
    LevelPrivacy,
    MessageState,
    MessageType,
    RelationshipType,
    RewardType,
    TimelyType,
)
from gd.filters import Filters
from gd.http import HTTPClient
from gd.models import (
    ArtistModel,
    ArtistsResponseModel,
    ChestsResponseModel,
    FriendRequestsResponseModel,
    GauntletsResponseModel,
    LeaderboardResponseModel,
    LevelCommentsResponseModel,
    LevelLeaderboardResponseModel,
    LevelResponseModel,
    LoginModel,
    MapPacksResponseModel,
    MessageModel,
    MessagesResponseModel,
    ProfileModel,
    QuestsResponseModel,
    RelationshipsResponseModel,
    SearchLevelsResponseModel,
    SearchUserModel,
    SearchUsersResponseModel,
    SongModel,
    TimelyInfoModel,
    UserCommentsResponseModel,
)
from gd.models_utils import concat_save, split_save
from gd.newgrounds import (
    find_song_model,
    search_artist_models,
    search_artist_song_models,
    search_song_models,
)
from gd.password import Password
from gd.typing import IntString, MaybeIterable, URLString

__all__ = ("Session",)

FIRST = 0

T = TypeVar("T")


def first(sequence: Sequence[T]) -> T:
    return sequence[FIRST]


@frozen()
class Session:
    http: HTTPClient = field(factory=HTTPClient)

    async def ping(self, url: URLString) -> Duration:
        return await self.http.ping(url)

    async def login(self, name: str, password: str) -> LoginModel:
        response = await self.http.login(name, password)

        return LoginModel.from_robtop(response)

    async def load(self, account_id: int, name: str, password: str) -> Database:
        response = await self.http.load(account_id=account_id, name=name, password=password)

        main_string, levels_string, *_ = split_save(response)

        return save.load_string_parts(
            main_string, levels_string, apply_xor=False, follow_system=False
        )

    async def save(self, database: Database, account_id: int, name: str, password: str) -> None:
        parts = save.dump_string_parts(database, apply_xor=False, follow_system=False)

        data = concat_save(parts)

        await self.http.save(data=data, account_id=account_id, name=name, password=password)

    async def get_account_url(self, account_id: int, type: AccountURLType) -> URL:
        return await self.http.get_account_url(account_id=account_id, type=type)

    async def get_role_id(self, account_id: int, encoded_password: str) -> int:
        return await self.http.get_role_id(account_id=account_id, encoded_password=encoded_password)

    async def update_settings(
        self,
        message_state: MessageState,
        friend_request_state: FriendRequestState,
        comment_state: CommentState,
        youtube: Optional[str],
        twitter: Optional[str],
        twitch: Optional[str],
        *,
        account_id: int,
        encoded_password: str,
    ) -> None:
        await self.http.update_settings(
            message_state=message_state,
            friend_request_state=friend_request_state,
            comment_state=comment_state,
            youtube=youtube,
            twitter=twitter,
            twitch=twitch,
            account_id=account_id,
            encoded_password=encoded_password,
        )

    async def update_profile(
        self,
        stars: int,
        diamonds: int,
        secret_coins: int,
        user_coins: int,
        demons: int,
        icon_type: IconType,
        icon_id: int,
        color_1_id: int,
        color_2_id: int,
        glow: bool,
        cube_id: int,
        ship_id: int,
        ball_id: int,
        ufo_id: int,
        wave_id: int,
        robot_id: int,
        spider_id: int,
        # swing_copter_id: int,
        explosion_id: int,
        special: int = DEFAULT_SPECIAL,
        *,
        account_id: int,
        name: str,
        encoded_password: str,
    ) -> None:
        await self.http.update_profile(
            stars=stars,
            diamonds=diamonds,
            secret_coins=secret_coins,
            user_coins=user_coins,
            demons=demons,
            icon_type=icon_type,
            icon_id=icon_id,
            color_1_id=color_1_id,
            color_2_id=color_2_id,
            glow=glow,
            cube_id=cube_id,
            ship_id=ship_id,
            ball_id=ball_id,
            ufo_id=ufo_id,
            wave_id=wave_id,
            robot_id=robot_id,
            spider_id=spider_id,
            # swing_copter_id=swing_copter_id,
            explosion_id=explosion_id,
            special=special,
            account_id=account_id,
            name=name,
            encoded_password=encoded_password,
        )

    async def search_user(self, query: IntString) -> SearchUserModel:
        response_model = await self.search_users_on_page(query)

        return first(response_model.users)

    async def search_users_on_page(
        self, query: IntString, page: int = DEFAULT_PAGE
    ) -> SearchUsersResponseModel:
        response = await self.http.search_users_on_page(query=query, page=page)

        return SearchUsersResponseModel.from_robtop(response)

    async def get_user_profile(
        self,
        account_id: int,
        *,
        client_account_id: Optional[int] = None,
        encoded_password: Optional[str] = None,
    ) -> ProfileModel:
        response = await self.http.get_user_profile(
            account_id=account_id,
            client_account_id=client_account_id,
            encoded_password=encoded_password,
        )

        return ProfileModel.from_robtop(response)

    async def get_relationships(
        self, type: RelationshipType, *, account_id: int, encoded_password: str
    ) -> RelationshipsResponseModel:
        response = await self.http.get_relationships(
            type=type, account_id=account_id, encoded_password=encoded_password
        )

        return RelationshipsResponseModel.from_robtop(response)

    async def get_leaderboard(
        self,
        strategy: LeaderboardStrategy,
        count: int,
        *,
        account_id: Optional[int] = None,
        encoded_password: Optional[str] = None,
    ) -> LeaderboardResponseModel:
        response = await self.http.get_leaderboard(
            strategy=strategy, count=count, account_id=account_id, encoded_password=encoded_password
        )

        return LeaderboardResponseModel.from_robtop(response)

    async def search_levels_on_page(
        self,
        query: Optional[MaybeIterable[IntString]] = None,
        page: int = DEFAULT_PAGE,
        filters: Optional[Filters] = None,
        user_id: Optional[int] = None,
        gauntlet: Optional[int] = None,
        *,
        client_account_id: Optional[int] = None,
        client_user_id: Optional[int] = None,
        encoded_password: Optional[str] = None,
    ) -> SearchLevelsResponseModel:
        response = await self.http.search_levels_on_page(
            query=query,
            page=page,
            filters=filters,
            user_id=user_id,
            gauntlet=gauntlet,
            client_account_id=client_account_id,
            client_user_id=client_user_id,
            encoded_password=encoded_password,
        )

        return SearchLevelsResponseModel.from_robtop(response)

    async def get_timely_info(self, type: TimelyType) -> TimelyInfoModel:
        response = await self.http.get_timely_info(type=type)

        return TimelyInfoModel.from_robtop(response, type=type)

    async def get_level(
        self,
        level_id: int,
        *,
        account_id: Optional[int] = None,
        encoded_password: Optional[str] = None,
    ) -> LevelResponseModel:
        response = await self.http.get_level(
            level_id=level_id, account_id=account_id, encoded_password=encoded_password
        )

        return LevelResponseModel.from_robtop(response)

    async def report_level(self, level_id: int) -> None:
        await self.http.report_level(level_id=level_id)

    async def delete_level(self, level_id: int, *, account_id: int, encoded_password: str) -> None:
        await self.http.delete_level(
            level_id=level_id, account_id=account_id, encoded_password=encoded_password
        )

    async def update_level_description(
        self, level_id: int, description: Optional[str], *, account_id: int, encoded_password: str
    ) -> None:
        await self.http.update_level_description(
            level_id=level_id,
            description=description,
            account_id=account_id,
            encoded_password=encoded_password,
        )

    async def upload_level(
        self,
        name: str = UNNAMED,
        id: int = DEFAULT_ID,
        version: int = DEFAULT_VERSION,
        length: LevelLength = LevelLength.DEFAULT,
        official_song_id: int = DEFAULT_ID,
        song_id: int = DEFAULT_ID,
        description: str = EMPTY,
        original_id: int = DEFAULT_ID,
        two_player: bool = DEFAULT_TWO_PLAYER,
        privacy: LevelPrivacy = LevelPrivacy.DEFAULT,
        object_count: int = DEFAULT_OBJECT_COUNT,
        coins: int = DEFAULT_COINS,
        stars: int = DEFAULT_STARS,
        low_detail: bool = DEFAULT_LOW_DETAIL,
        capacity: Optional[Capacity] = None,
        password: Optional[Password] = None,
        recording: Optional[Recording] = None,
        editor_time: Optional[Duration] = None,
        copies_time: Optional[Duration] = None,
        data: str = EMPTY,
        *,
        account_id: int,
        account_name: str,
        encoded_password: str,
    ) -> int:
        return await self.http.upload_level(
            name=name,
            id=id,
            version=version,
            length=length,
            official_song_id=official_song_id,
            song_id=song_id,
            description=description,
            original_id=original_id,
            two_player=two_player,
            object_count=object_count,
            coins=coins,
            stars=stars,
            privacy=privacy,
            low_detail=low_detail,
            capacity=capacity,
            password=password,
            recording=recording,
            editor_time=editor_time,
            copies_time=copies_time,
            data=data,
            account_id=account_id,
            account_name=account_name,
            encoded_password=encoded_password,
        )

    async def rate_level(
        self, level_id: int, stars: int, *, account_id: int, encoded_password: str
    ) -> None:
        await self.http.rate_level(
            level_id=level_id,
            stars=stars,
            account_id=account_id,
            encoded_password=encoded_password,
        )

    async def rate_demon(
        self,
        level_id: int,
        rating: DemonDifficulty,
        *,
        account_id: int,
        encoded_password: str,
    ) -> None:
        await self.http.rate_demon(
            level_id=level_id,
            rating=rating,
            account_id=account_id,
            encoded_password=encoded_password,
        )

    async def suggest_demon(
        self,
        level_id: int,
        rating: DemonDifficulty,
        *,
        account_id: int,
        encoded_password: str,
    ) -> None:
        await self.http.suggest_demon(
            level_id=level_id,
            rating=rating,
            account_id=account_id,
            encoded_password=encoded_password,
        )

    async def suggest_level(
        self, level_id: int, stars: int, feature: bool, *, account_id: int, encoded_password: str
    ) -> None:
        await self.http.suggest_level(
            level_id=level_id,
            stars=stars,
            feature=feature,
            account_id=account_id,
            encoded_password=encoded_password,
        )

    async def get_level_leaderboard(
        self,
        level_id: int,
        strategy: LevelLeaderboardStrategy,
        *,
        account_id: int,
        encoded_password: str,
    ) -> LevelLeaderboardResponseModel:
        response = await self.http.get_level_leaderboard(
            level_id=level_id,
            strategy=strategy,
            account_id=account_id,
            encoded_password=encoded_password,
        )

        return LevelLeaderboardResponseModel.from_robtop(response)

    async def block_user(
        self,
        account_id: int,
        *,
        client_account_id: int,
        encoded_password: str,
    ) -> None:
        await self.http.block_user(
            account_id=account_id,
            client_account_id=client_account_id,
            encoded_password=encoded_password,
        )

    async def unblock_user(
        self,
        account_id: int,
        *,
        client_account_id: int,
        encoded_password: str,
    ) -> None:
        await self.http.unblock_user(
            account_id=account_id,
            client_account_id=client_account_id,
            encoded_password=encoded_password,
        )

    async def unfriend_user(
        self, account_id: int, *, client_account_id: int, encoded_password: str
    ) -> None:
        await self.http.unfriend_user(
            account_id=account_id,
            client_account_id=client_account_id,
            encoded_password=encoded_password,
        )

    async def send_message(
        self,
        account_id: int,
        subject: Optional[str] = None,
        content: Optional[str] = None,
        *,
        client_account_id: int,
        encoded_password: str,
    ) -> None:
        await self.http.send_message(
            account_id=account_id,
            subject=subject,
            content=content,
            client_account_id=client_account_id,
            encoded_password=encoded_password,
        )

    async def get_message(
        self,
        message_id: int,
        type: MessageType,
        *,
        account_id: int,
        encoded_password: str,
    ) -> MessageModel:
        response = await self.http.get_message(
            message_id=message_id,
            type=type,
            account_id=account_id,
            encoded_password=encoded_password,
        )

        return MessageModel.from_robtop(response, content_present=True)

    async def delete_message(
        self,
        message_id: int,
        type: MessageType,
        *,
        account_id: int,
        encoded_password: str,
    ) -> None:
        await self.http.delete_message(
            message_id=message_id,
            type=type,
            account_id=account_id,
            encoded_password=encoded_password,
        )

    async def get_messages_on_page(
        self, type: MessageType, page: int, *, account_id: int, encoded_password: str
    ) -> MessagesResponseModel:
        response = await self.http.get_messages_on_page(
            type=type, page=page, account_id=account_id, encoded_password=encoded_password
        )

        return MessagesResponseModel.from_robtop(response)

    async def send_friend_request(
        self,
        account_id: int,
        message: Optional[str] = None,
        *,
        client_account_id: int,
        encoded_password: str,
    ) -> None:
        await self.http.send_friend_request(
            account_id=account_id,
            message=message,
            client_account_id=client_account_id,
            encoded_password=encoded_password,
        )

    async def delete_friend_request(
        self,
        account_id: int,
        type: FriendRequestType,
        *,
        client_account_id: int,
        encoded_password: str,
    ) -> None:
        await self.http.delete_friend_request(
            account_id=account_id,
            type=type,
            client_account_id=client_account_id,
            encoded_password=encoded_password,
        )

    async def accept_friend_request(
        self,
        account_id: int,
        request_id: int,
        type: FriendRequestType,
        *,
        client_account_id: int,
        encoded_password: str,
    ) -> None:
        await self.http.accept_friend_request(
            account_id=account_id,
            request_id=request_id,
            type=type,
            client_account_id=client_account_id,
            encoded_password=encoded_password,
        )

    async def read_friend_request(
        self, request_id: int, *, account_id: int, encoded_password: str
    ) -> None:
        await self.http.read_friend_request(
            request_id=request_id,
            account_id=account_id,
            encoded_password=encoded_password,
        )

    async def get_friend_requests_on_page(
        self,
        type: FriendRequestType,
        page: int,
        *,
        account_id: int,
        encoded_password: str,
    ) -> FriendRequestsResponseModel:
        response = await self.http.get_friend_requests_on_page(
            type=type, page=page, account_id=account_id, encoded_password=encoded_password
        )

        return FriendRequestsResponseModel.from_robtop(response)

    async def like_level(
        self,
        level_id: int,
        dislike: bool,
        *,
        account_id: int,
        encoded_password: str,
    ) -> None:
        await self.http.like_level(
            level_id=level_id,
            dislike=dislike,
            account_id=account_id,
            encoded_password=encoded_password,
        )

    async def like_user_comment(
        self,
        comment_id: int,
        dislike: bool,
        *,
        account_id: int,
        encoded_password: str,
    ) -> None:
        await self.http.like_user_comment(
            comment_id=comment_id,
            dislike=dislike,
            account_id=account_id,
            encoded_password=encoded_password,
        )

    async def like_level_comment(
        self,
        comment_id: int,
        level_id: int,
        dislike: bool,
        *,
        account_id: int,
        encoded_password: str,
    ) -> None:
        await self.http.like_level_comment(
            comment_id=comment_id,
            level_id=level_id,
            dislike=dislike,
            account_id=account_id,
            encoded_password=encoded_password,
        )

    async def post_user_comment(
        self,
        content: Optional[str],
        *,
        account_id: int,
        account_name: str,
        encoded_password: str,
    ) -> int:
        return await self.http.post_user_comment(
            content=content,
            account_id=account_id,
            account_name=account_name,
            encoded_password=encoded_password,
        )

    async def post_level_comment(
        self,
        level_id: int,
        content: Optional[str],
        record: int,
        *,
        account_id: int,
        account_name: str,
        encoded_password: str,
    ) -> int:
        return await self.http.post_level_comment(
            level_id=level_id,
            content=content,
            record=record,
            account_id=account_id,
            account_name=account_name,
            encoded_password=encoded_password,
        )

    async def delete_user_comment(
        self,
        comment_id: int,
        *,
        account_id: int,
        encoded_password: str,
    ) -> None:
        await self.http.delete_user_comment(
            comment_id=comment_id,
            account_id=account_id,
            encoded_password=encoded_password,
        )

    async def delete_level_comment(
        self,
        comment_id: int,
        level_id: int,
        *,
        account_id: int,
        encoded_password: str,
    ) -> None:
        await self.http.delete_level_comment(
            comment_id=comment_id,
            level_id=level_id,
            account_id=account_id,
            encoded_password=encoded_password,
        )

    async def get_user_comments_on_page(
        self,
        account_id: int,
        page: int = DEFAULT_PAGE,
    ) -> UserCommentsResponseModel:
        response = await self.http.get_user_comments_on_page(
            account_id=account_id,
            page=page,
        )

        return UserCommentsResponseModel.from_robtop(response)

    async def get_user_level_comments_on_page(
        self,
        user_id: int,
        count: int,
        page: int = DEFAULT_PAGE,
        strategy: CommentStrategy = CommentStrategy.DEFAULT,
    ) -> LevelCommentsResponseModel:
        response = await self.http.get_user_level_comments_on_page(
            user_id=user_id,
            count=count,
            page=page,
            strategy=strategy,
        )

        return LevelCommentsResponseModel.from_robtop(response)

    async def get_level_comments_on_page(
        self,
        level_id: int,
        count: int,
        page: int = DEFAULT_PAGE,
        strategy: CommentStrategy = CommentStrategy.DEFAULT,
    ) -> LevelCommentsResponseModel:
        response = await self.http.get_level_comments_on_page(
            level_id=level_id, count=count, page=page, strategy=strategy
        )

        return LevelCommentsResponseModel.from_robtop(response)

    async def get_gauntlets(self) -> GauntletsResponseModel:
        response = await self.http.get_gauntlets()

        return GauntletsResponseModel.from_robtop(response)

    async def get_map_packs_on_page(self, page: int = DEFAULT_PAGE) -> MapPacksResponseModel:
        response = await self.http.get_map_packs_on_page(page=page)

        return MapPacksResponseModel.from_robtop(response)

    async def get_quests(self, *, account_id: int, encoded_password: str) -> QuestsResponseModel:
        response = await self.http.get_quests(
            account_id=account_id, encoded_password=encoded_password
        )
        return QuestsResponseModel.from_robtop(response)

    async def get_chests(
        self,
        reward_type: RewardType,
        chest_1_count: int = DEFAULT_CHEST_COUNT,
        chest_2_count: int = DEFAULT_CHEST_COUNT,
        *,
        account_id: int,
        encoded_password: str,
    ) -> ChestsResponseModel:
        response = await self.http.get_chests(
            reward_type=reward_type,
            chest_1_count=chest_1_count,
            chest_2_count=chest_2_count,
            account_id=account_id,
            encoded_password=encoded_password,
        )
        return ChestsResponseModel.from_robtop(response)

    async def get_artists_on_page(self, page: int = DEFAULT_PAGE) -> ArtistsResponseModel:
        response = await self.http.get_artists_on_page(page=page)

        return ArtistsResponseModel.from_robtop(response)

    async def get_song(self, song_id: int) -> SongModel:
        response = await self.http.get_song(song_id)

        return SongModel.from_robtop(response)

    async def get_newgrounds_song(self, song_id: int) -> SongModel:
        response = await self.http.get_newgrounds_song(song_id)

        return find_song_model(response, song_id)

    async def search_newgrounds_songs_on_page(
        self, query: str, page: int = DEFAULT_PAGE
    ) -> List[SongModel]:
        response = await self.http.search_newgrounds_songs_on_page(query=query, page=page)

        return list(search_song_models(response))

    async def search_newgrounds_artists_on_page(
        self, query: str, page: int = DEFAULT_PAGE
    ) -> List[ArtistModel]:
        response = await self.http.search_newgrounds_artists_on_page(query=query, page=page)

        return list(search_artist_models(response))

    async def get_newgrounds_artist_songs_on_page(
        self, artist_name: str, page: int = DEFAULT_PAGE
    ) -> List[SongModel]:
        response = await self.http.get_newgrounds_artist_songs_on_page(
            artist_name=artist_name, page=page
        )

        return list(search_artist_song_models(response, artist_name))
