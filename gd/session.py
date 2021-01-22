from gd.api.database import Database
from gd.api.loader import SAVE_DELIM, save
from gd.api.recording import RecordingEntry
from gd.decorators import synchronize
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
from gd.http import URL, HTTPClient
from gd.model import (  # type: ignore
    ChestsResponseModel,
    CommentsResponseModel,
    FeaturedArtistsResponseModel,
    FriendRequestsResponseModel,
    GauntletsResponseModel,
    LeaderboardResponseModel,
    LevelDownloadResponseModel,
    LevelLeaderboardResponseModel,
    LevelSearchResponseModel,
    LoginIDModel,
    MapPacksResponseModel,
    MessageModel,
    MessagesResponseModel,
    ProfileUserModel,
    QuestsResponseModel,
    SearchUserModel,
    SearchUserResponseModel,
    SongModel,
    TimelyInfoModel,
    UserListResponseModel,
)
from gd.newgrounds_parser import (
    extract_info_from_endpoint,
    extract_user_songs,
    extract_users,
    find_song_info,
    search_song_data,
)
from gd.text_utils import make_repr
from gd.typing import Any, Dict, Iterable, List, Optional, Union

__all__ = ("Session",)


@synchronize
class Session:
    def __init__(self, **http_args) -> None:
        self.http = HTTPClient(**http_args)

    def __repr__(self) -> str:
        info = {"http": self.http}
        return make_repr(self, info)

    async def ping(self, url: Union[str, URL]) -> float:
        return await self.http.ping(url)

    async def login(self, name: str, password: str) -> LoginIDModel:
        response = await self.http.login(name, password)
        return LoginIDModel.from_string(response, use_default=True)

    async def load(self, *, account_id: int, name: str, password: str) -> Database:
        response = await self.http.load(account_id=account_id, name=name, password=password)

        main_part, levels_part, *_ = response.split(SAVE_DELIM)

        return await save.from_string_async(
            main_part, levels_part, apply_xor=False, follow_os=False
        )

    async def save(self, database: Database, *, account_id: int, name: str, password: str) -> None:
        parts = await save.to_string_async(database, apply_xor=False, follow_os=False, decode=True)

        data = SAVE_DELIM.join(parts)  # type: ignore  # they are already strings

        await self.http.save(data=data, account_id=account_id, name=name, password=password)

    async def get_account_url(self, account_id: int, type: AccountURLType) -> URL:
        url = await self.http.get_account_url(account_id=account_id, type=type)
        return URL(url)

    async def get_role_id(self, account_id: int, encoded_password: str) -> int:
        return await self.http.get_role_id(account_id=account_id, encoded_password=encoded_password)

    async def update_settings(
        self,
        message_state: MessageState,
        friend_request_state: FriendRequestState,
        comment_state: CommentState,
        youtube: str,
        twitter: str,
        twitch: str,
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
        coins: int,
        user_coins: int,
        demons: int,
        icon_type: IconType,
        icon: int,
        color_1_id: int,
        color_2_id: int,
        has_glow: bool,
        cube: int,
        ship: int,
        ball: int,
        ufo: int,
        wave: int,
        robot: int,
        spider: int,
        death_effect: int,
        special: int = 0,
        *,
        account_id: int,
        name: str,
        encoded_password: str,
    ) -> None:
        await self.http.update_profile(
            stars=stars,
            diamonds=diamonds,
            coins=coins,
            user_coins=user_coins,
            demons=demons,
            icon_type=icon_type,
            icon=icon,
            color_1_id=color_1_id,
            color_2_id=color_2_id,
            has_glow=has_glow,
            cube=cube,
            ship=ship,
            ball=ball,
            ufo=ufo,
            wave=wave,
            robot=robot,
            spider=spider,
            death_effect=death_effect,
            special=special,
            account_id=account_id,
            name=name,
            encoded_password=encoded_password,
        )

    async def search_user(self, query: Union[int, str]) -> SearchUserModel:
        response_model = await self.search_users_on_page(query, page=0)
        return response_model.users[0]

    async def search_users_on_page(
        self, query: Union[int, str], page: int = 0
    ) -> SearchUserResponseModel:
        response = await self.http.search_users_on_page(query, page=page)
        return SearchUserResponseModel.from_string(response, use_default=True)

    async def get_user_profile(
        self,
        account_id: int,
        *,
        client_account_id: Optional[int] = None,
        encoded_password: Optional[str] = None,
    ) -> ProfileUserModel:
        response = await self.http.get_user_profile(
            account_id, client_account_id=client_account_id, encoded_password=encoded_password,
        )
        return ProfileUserModel.from_string(response, use_default=True)

    async def get_relationships(
        self, type: SimpleRelationshipType, *, account_id: int, encoded_password: str
    ) -> UserListResponseModel:
        response = await self.http.get_relationships(
            type, account_id=account_id, encoded_password=encoded_password
        )
        return UserListResponseModel.from_string(response, use_default=True)

    async def get_top(
        self,
        strategy: LeaderboardStrategy,
        amount: int,
        *,
        account_id: Optional[int] = None,
        encoded_password: Optional[str] = None,
    ) -> LeaderboardResponseModel:
        response = await self.http.get_top(
            strategy, amount, account_id=account_id, encoded_password=encoded_password
        )
        return LeaderboardResponseModel.from_string(response, use_default=True)

    async def search_levels_on_page(
        self,
        query: Optional[Union[int, str, Iterable[Any]]] = None,
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
            level_id, description, account_id=account_id, encoded_password=encoded_password,
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
        password: Optional[Union[int, str]] = None,
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
            level_id, strategy=strategy, account_id=account_id, encoded_password=encoded_password,
        )
        return LevelLeaderboardResponseModel.from_string(response, use_default=True)

    async def block_or_unblock(
        self, account_id: int, unblock: bool, *, client_account_id: int, encoded_password: str,
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
        self, message_id: int, type: MessageType, *, account_id: int, encoded_password: str,
    ) -> MessageModel:
        response = await self.http.download_message(
            message_id, type=type, account_id=account_id, encoded_password=encoded_password,
        )
        return MessageModel.from_string(response, use_default=True)

    async def delete_message(
        self, message_id: int, type: MessageType, *, account_id: int, encoded_password: str,
    ) -> None:
        await self.http.delete_message(
            message_id, type=type, account_id=account_id, encoded_password=encoded_password,
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
            request_id=request_id, account_id=account_id, encoded_password=encoded_password,
        )

    async def get_friend_requests_on_page(
        self, type: FriendRequestType, page: int, *, account_id: int, encoded_password: str,
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
            account_id=account_id, user_id=user_id, type=type, page=page, strategy=strategy,
        )
        return CommentsResponseModel.from_string(response, use_default=True)

    async def get_level_comments_on_page(
        self, level_id: int, amount: int, page: int = 0, *, strategy: CommentStrategy,
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
        return SongModel.from_string(response, use_default=True)

    async def get_ng_song(self, song_id: int) -> SongModel:
        response = await self.http.get_ng_song(song_id)
        return SongModel.from_dict(find_song_info(response), id=song_id)

    async def get_artist_info(self, song_id: int) -> Dict[str, Any]:
        response = await self.http.get_artist_info(song_id)

        artist_info = extract_info_from_endpoint(response)
        artist_info.update(id=song_id, custom=True)  # type: ignore

        return artist_info

    async def search_ng_songs_on_page(self, query: str, page: int = 0) -> List[SongModel]:
        response = await self.http.search_ng_songs_on_page(query=query, page=page)
        return list(map(SongModel.from_dict, search_song_data(response)))

    async def search_ng_users_on_page(self, query: str, page: int = 0) -> List[Dict[str, Any]]:
        response = await self.http.search_ng_users_on_page(query=query, page=page)
        return list(extract_users(response))

    async def get_ng_user_songs_on_page(self, name: str, page: int = 0) -> List[SongModel]:
        response = await self.http.get_ng_user_songs_on_page(name=name, page=page)
        return [
            SongModel.from_dict(data, author=name)
            for data in extract_user_songs(response)  # type: ignore
        ]
