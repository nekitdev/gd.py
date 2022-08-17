from __future__ import annotations

from datetime import timedelta
from typing import Any, Optional

from attrs import frozen
from yarl import URL

from gd.api.database import Database
from gd.api.save_manager import save_manager
from gd.enums import (
    AccountURLType,
    CommentState,
    CommentStrategy,
    CommentType,
    DemonDifficulty,
    FriendRequestState,
    FriendRequestType,
    IconType,
    LeaderboardStrategy,
    LevelLeaderboardStrategy,
    LevelLength,
    LikeType,
    MessageState,
    MessageType,
    RewardType,
    SimpleRelationshipType,
)
from gd.filters import Filters
from gd.http import HTTPClient
from gd.models import (
    LeaderboardResponseModel,
    LoginModel,
    ProfileModel,
    RelationshipsResponseModel,
    SearchUserModel,
    SearchUsersResponseModel,
    SongModel,
)
from gd.typing import IntString, MaybeIterable, URLString

__all__ = ("Session",)

FIRST = 0


@frozen()
class Session:
    http: HTTPClient

    def __init__(self, **http_keywords: Any) -> None:
        self.__attrs_init__(HTTPClient(**http_keywords))

    async def ping(self, url: URLString) -> timedelta:
        return await self.http.ping(url)

    async def login(self, name: str, password: str) -> LoginModel:
        response = await self.http.login(name, password)

        return LoginModel.from_robtop(response)

    # HERE

    async def load(self, *, account_id: int, name: str, password: str) -> Database:
        response = await self.http.load(account_id=account_id, name=name, password=password)

        main_string, levels_string, *rest = split_save(response)

        return await save_manager.from_strings_async(
            main_string, levels_string, apply_xor=False, follow_os=False
        )

    async def save(self, database: Database, *, account_id: int, name: str, password: str) -> None:
        parts = await save_manager.to_strings_async(database, apply_xor=False, follow_os=False)

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
        special: int = 0,
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
            explosion_id=explosion_id,
            special=special,
            account_id=account_id,
            name=name,
            encoded_password=encoded_password,
        )

    async def search_user(self, query: IntString) -> SearchUserModel:
        response_model = await self.search_users_on_page(query)

        return response_model.users[FIRST]

    async def search_users_on_page(
        self, query: IntString, page: int = 0
    ) -> SearchUsersResponseModel:
        response = await self.http.search_users_on_page(query, page=page)

        return SearchUsersResponseModel.from_robtop(response)

    async def get_user_profile(
        self,
        account_id: int,
        *,
        client_account_id: Optional[int] = None,
        encoded_password: Optional[str] = None,
    ) -> ProfileModel:
        response = await self.http.get_user_profile(
            account_id,
            client_account_id=client_account_id,
            encoded_password=encoded_password,
        )

        return ProfileModel.from_robtop(response)

    async def get_relationships(
        self, type: SimpleRelationshipType, *, account_id: int, encoded_password: str
    ) -> RelationshipsResponseModel:
        response = await self.http.get_relationships(
            type, account_id=account_id, encoded_password=encoded_password
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
            strategy, count, account_id=account_id, encoded_password=encoded_password
        )
        return LeaderboardResponseModel.from_robtop(response)

    async def search_levels_on_page(
        self,
        query: Optional[MaybeIterable[IntString]] = None,
        page: int = 0,
        filters: Optional[Filters] = None,
        user_id: Optional[int] = None,
        gauntlet: Optional[int] = None,
        *,
        client_account_id: Optional[int] = None,
        client_user_id: Optional[int] = None,
        encoded_password: Optional[str] = None,
    ) -> LevelSearchResponseModel:
        response = await self.http.search_levels_on_page(
            query,
            page=page,
            filters=filters,
            user_id=user_id,
            gauntlet=gauntlet,
            client_account_id=client_account_id,
            client_user_id=client_user_id,
            encoded_password=encoded_password,
        )
        return LevelSearchResponseModel.from_string(response, use_default=True)

    async def get_timely_info(self, weekly: bool) -> TimelyInfoModel:
        response = await self.http.get_timely_info(weekly)
        return TimelyInfoModel.from_string(response, use_default=True)

    async def download_level(
        self,
        level_id: int,
        *,
        account_id: Optional[int] = None,
        encoded_password: Optional[str] = None,
    ) -> LevelDownloadResponseModel:
        response = await self.http.download_level(
            level_id, account_id=account_id, encoded_password=encoded_password
        )
        return LevelDownloadResponseModel.from_string(response, use_default=True)

    async def report_level(self, level_id: int) -> None:
        await self.http.report_level(level_id)

    async def delete_level(self, level_id: int, *, account_id: int, encoded_password: str) -> None:
        await self.http.delete_level(
            level_id, account_id=account_id, encoded_password=encoded_password
        )

    async def update_level_description(
        self, level_id: int, description: str, *, account_id: int, encoded_password: str
    ) -> None:
        await self.http.update_level_description(
            level_id,
            description,
            account_id=account_id,
            encoded_password=encoded_password,
        )

    async def upload_level(
        self,
        name: str = "Unnamed",
        id: int = 0,
        version: int = 1,
        length: LevelLength = LevelLength.TINY,  # type: ignore
        track_id: int = 0,
        description: str = "",
        song_id: int = 0,
        is_auto: bool = False,
        original: int = 0,
        two_player: bool = False,
        objects: int = 0,
        coins: int = 0,
        stars: int = 0,
        unlisted: bool = False,
        friends_only: bool = False,
        low_detail_mode: bool = False,
        password: Optional[IntString] = None,
        copyable: bool = False,
        recording: Iterable[RecordingEntry] = (),
        editor_seconds: int = 0,
        copies_seconds: int = 0,
        data: str = "",
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
            track_id=track_id,
            description=description,
            song_id=song_id,
            is_auto=is_auto,
            original=original,
            two_player=two_player,
            objects=objects,
            coins=coins,
            stars=stars,
            unlisted=unlisted,
            friends_only=friends_only,
            low_detail_mode=low_detail_mode,
            password=password,
            copyable=copyable,
            recording=recording,
            editor_seconds=editor_seconds,
            copies_seconds=copies_seconds,
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
        as_mod: bool = False,
        *,
        account_id: int,
        encoded_password: str,
    ) -> None:
        await self.http.rate_demon(
            level_id=level_id,
            rating=rating,
            as_mod=as_mod,
            account_id=account_id,
            encoded_password=encoded_password,
        )

    async def send_level(
        self, level_id: int, stars: int, feature: bool, *, account_id: int, encoded_password: str
    ) -> None:
        await self.http.send_level(
            level_id=level_id,
            stars=stars,
            feature=feature,
            account_id=account_id,
            encoded_password=encoded_password,
        )

    async def get_level_top(
        self,
        level_id: int,
        strategy: LevelLeaderboardStrategy,
        *,
        account_id: int,
        encoded_password: str,
    ) -> LevelLeaderboardResponseModel:
        response = await self.http.get_level_top(
            level_id,
            strategy=strategy,
            account_id=account_id,
            encoded_password=encoded_password,
        )
        return LevelLeaderboardResponseModel.from_string(response, use_default=True)

    async def block_or_unblock(
        self,
        account_id: int,
        unblock: bool,
        *,
        client_account_id: int,
        encoded_password: str,
    ) -> None:
        await self.http.block_or_unblock(
            account_id=account_id,
            unblock=unblock,
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

    async def download_message(
        self,
        message_id: int,
        type: MessageType,
        *,
        account_id: int,
        encoded_password: str,
    ) -> MessageModel:
        response = await self.http.download_message(
            message_id,
            type=type,
            account_id=account_id,
            encoded_password=encoded_password,
        )
        return MessageModel.from_string(response, use_default=True)

    async def delete_message(
        self,
        message_id: int,
        type: MessageType,
        *,
        account_id: int,
        encoded_password: str,
    ) -> None:
        await self.http.delete_message(
            message_id,
            type=type,
            account_id=account_id,
            encoded_password=encoded_password,
        )

    async def get_messages_on_page(
        self, type: MessageType, page: int, *, account_id: int, encoded_password: str
    ) -> MessagesResponseModel:
        response = await self.http.get_messages_on_page(
            type, page, account_id=account_id, encoded_password=encoded_password
        )
        return MessagesResponseModel.from_string(response, use_default=True)

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
            type, page, account_id=account_id, encoded_password=encoded_password
        )
        return FriendRequestsResponseModel.from_string(response, use_default=True)

    async def like_or_dislike(
        self,
        type: LikeType,
        item_id: int,
        special_id: int,
        dislike: bool = False,
        *,
        account_id: int,
        encoded_password: str,
    ) -> None:
        await self.http.like_or_dislike(
            type=type,
            item_id=item_id,
            special_id=special_id,
            dislike=dislike,
            account_id=account_id,
            encoded_password=encoded_password,
        )

    async def post_comment(
        self,
        type: CommentType,
        content: Optional[str] = None,
        level_id: int = 0,
        percent: int = 0,
        *,
        account_id: int,
        account_name: str,
        encoded_password: str,
    ) -> None:
        await self.http.post_comment(
            content=content,
            type=type,
            level_id=level_id,
            percent=percent,
            account_id=account_id,
            account_name=account_name,
            encoded_password=encoded_password,
        )

    async def delete_comment(
        self,
        comment_id: int,
        type: CommentType,
        level_id: int = 0,
        *,
        account_id: int,
        encoded_password: str,
    ) -> None:
        await self.http.delete_comment(
            comment_id=comment_id,
            type=type,
            level_id=level_id,
            account_id=account_id,
            encoded_password=encoded_password,
        )

    async def get_user_comments_on_page(
        self,
        account_id: int,
        user_id: int,
        type: CommentType,
        page: int = 0,
        *,
        strategy: CommentStrategy,
    ) -> CommentsResponseModel:
        response = await self.http.get_user_comments_on_page(
            account_id=account_id,
            user_id=user_id,
            type=type,
            page=page,
            strategy=strategy,
        )
        return CommentsResponseModel.from_string(response, use_default=True)

    async def get_level_comments_on_page(
        self,
        level_id: int,
        amount: int,
        page: int = 0,
        *,
        strategy: CommentStrategy,
    ) -> CommentsResponseModel:
        response = await self.http.get_level_comments_on_page(
            level_id=level_id, amount=amount, page=page, strategy=strategy
        )
        return CommentsResponseModel.from_string(response, use_default=True)

    async def get_gauntlets(self) -> GauntletsResponseModel:
        response = await self.http.get_gauntlets()
        return GauntletsResponseModel.from_string(response, use_default=True)

    async def get_map_packs_on_page(self, page: int = 0) -> MapPacksResponseModel:
        response = await self.http.get_map_packs_on_page(page=page)
        return MapPacksResponseModel.from_string(response, use_default=True)

    async def get_quests(self, account_id: int, encoded_password: str) -> QuestsResponseModel:
        response = await self.http.get_quests(
            account_id=account_id, encoded_password=encoded_password
        )
        return QuestsResponseModel.from_string(response, use_default=True)

    async def get_chests(
        self,
        reward_type: RewardType,
        chest_1_count: int = 0,
        chest_2_count: int = 0,
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
        return ChestsResponseModel.from_string(response, use_default=True)

    async def get_featured_artists_on_page(self, page: int = 0) -> FeaturedArtistsResponseModel:
        response = await self.http.get_featured_artists_on_page(page=page)
        return FeaturedArtistsResponseModel.from_string(response, use_default=True)

    async def get_song(self, song_id: int) -> SongModel:
        response = await self.http.get_song(song_id)

        return SongModel.from_robtop(response)

    async def get_newgrounds_song(self, song_id: int) -> SongModel:
        response = await self.http.get_newgrounds_song(song_id)

        return SongModel.from_dict(find_song_data(response), id=song_id)

    async def get_artist_info(self, song_id: int) -> Dict[str, Any]:
        response = await self.http.get_artist_info(song_id)

        artist_info = find_info(response)
        artist_info.update(id=song_id, custom=True)  # type: ignore

        return artist_info

    async def search_newgrounds_songs_on_page(self, query: str, page: int = 0) -> List[SongModel]:
        response = await self.http.search_newgrounds_songs_on_page(query=query, page=page)
        return list(map(SongModel.from_dict, search_song_data(response)))

    async def search_newgrounds_users_on_page(
        self, query: str, page: int = 0
    ) -> List[Dict[str, Any]]:
        response = await self.http.search_newgrounds_users_on_page(query=query, page=page)
        return list(search_users(response))

    async def get_newgrounds_user_songs_on_page(self, name: str, page: int = 0) -> List[SongModel]:
        response = await self.http.get_newgrounds_user_songs_on_page(name=name, page=page)
        return [
            SongModel.from_dict(data, author=name)
            for data in search_user_songs(response)  # type: ignore
        ]
