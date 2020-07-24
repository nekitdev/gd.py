import asyncio
import json
import string
import time  # for perf_counter in ping

from itertools import chain
from yarl import URL

from gd.typing import (
    Any,
    Client,
    Dict,
    Iterable,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
)

from gd.errors import (
    MissingAccess,
    SongRestrictedForUsage,
    NothingFound,
    LoginFailure,
)

from gd.utils.converter import Converter
from gd.utils.decorators import check_logged_obj
from gd.utils.enums import (
    CommentPolicyType,
    CommentStrategy,
    CommentType,
    DemonDifficulty,
    FriendRequestPolicyType,
    LeaderboardStrategy,
    LevelLeaderboardStrategy,
    LevelLength,
    MessageOrRequestType,
    MessagePolicyType,
    RewardType,
    ShardType,
    QuestType,
    SearchStrategy,
)
from gd.utils.filters import Filters
from gd.utils.http_request import HTTPClient
from gd.utils.indexer import Index
from gd.utils.ng_parser import (
    find_song_info,
    search_song_data,
    extract_info_from_endpoint,
    extract_user_songs,
    extract_users,
)
from gd.utils.params import Parameters as Params
from gd.utils.parser import ExtDict, Parser
from gd.utils.routes import Route
from gd.utils.text_tools import make_repr
from gd.utils.crypto.coders import Coder

from gd import api

REWARD_CHALLENGE_CHK_LENGTH = 13
REWARD_CHALLENGE_SLICE_LENGTH = 5
QUEST_AMOUNT = 3
CHEST_AMOUNT = 2
CHEST_INNER_PARTS = 3


class Session:
    """Implements all requests-related functionality.
    No docstrings here yet...
    """

    def __init__(self, **http_args) -> None:
        self.http = HTTPClient(**http_args)

    def __repr__(self) -> str:
        info = {"http": self.http}
        return make_repr(self, info)

    async def ping_server(self, link: str) -> float:
        start = time.perf_counter()
        await self.http.normal_request(link)
        end = time.perf_counter()
        return round((end - start) * 1000, 2)

    async def get_song(self, song_id: int = 0) -> ExtDict:
        payload = Params().create_new().put_definer("song", song_id).finish()
        codes = {
            -1: MissingAccess(f"No songs were found with ID: {song_id}."),
            -2: SongRestrictedForUsage(song_id),
        }
        resp = await self.http.request(Route.GET_SONG_INFO, payload, error_codes=codes)
        return Parser().with_split("~|~").should_map().parse(resp)

    async def test_song(self, song_id: int = 0) -> ExtDict:
        codes = {-1: MissingAccess(f"Failed to fetch artist info for ID: {song_id}")}
        payload = Params().create_new("web").put_definer("song", song_id).close()
        resp = await self.http.request(
            Route.TEST_SONG, params=payload, method="get", error_codes=codes
        )

        data = ExtDict(id=song_id)

        try:
            data.update(extract_info_from_endpoint(resp))
        except ValueError:
            raise MissingAccess(f"Failed to load data. Response: {resp!r}.") from None

        return data

    async def get_ng_song(self, song_id: int = 0) -> ExtDict:
        # just like get_song(), but gets anything available on NG.
        link = Route.NEWGROUNDS_SONG_LISTEN + str(song_id)

        content = await self.http.normal_request(link)
        html = content.decode().replace("\\", "")

        try:
            info = find_song_info(html)
        except ValueError:
            raise MissingAccess(f"Song was not found by ID: {song_id}") from None

        return ExtDict(
            name=info.name,
            author=info.author,
            id=song_id,
            size=round(info.size / 1024 / 1024, 2),
            links=dict(normal=link, download=info.link),
            custom=True,
        )

    async def search_page_songs(self, query: str, page: int = 0) -> List[ExtDict]:
        payload = {"terms": query, "page": page + 1}

        data = await self.http.normal_request(
            Route.NEWGROUNDS_SEARCH.format(type="audio"), params=payload
        )

        return search_song_data(data.decode())

    async def search_songs(self, query: str, pages: Iterable[int]) -> List[ExtDict]:
        to_run = [self.search_page_songs(query=query, page=page) for page in pages]

        return await self.run_many(to_run)

    async def search_page_users(self, query: str, page: int = 0) -> List[ExtDict]:
        payload = {"terms": query, "page": page + 1}

        data = await self.http.normal_request(
            Route.NEWGROUNDS_SEARCH.format(type="users"), params=payload
        )

        return extract_users(data.decode())

    async def search_users(self, query: str, pages: Iterable[int]) -> List[ExtDict]:
        to_run = [self.search_page_users(query=query, page=page) for page in pages]

        return await self.run_many(to_run)

    async def get_page_user_songs(self, user_name: str, page: int = 0) -> List[ExtDict]:
        link = URL("https://%s.newgrounds.com/" % user_name) / f"audio/page/{page + 1}"

        data = await self.http.normal_request(link, headers={"X-Requested-With": "XMLHttpRequest"})

        info = extract_user_songs(json.loads(data.decode(errors="replace")))

        for part in info:
            part.update(author=user_name)

        return info

    async def get_user_songs(self, user_name: str, pages: Iterable[int]) -> List[ExtDict]:
        to_run = [self.get_page_user_songs(user_name=user_name, page=page) for page in pages]

        return await self.run_many(to_run)

    async def get_user(self, account_id: int = 0, return_only_stats: bool = False) -> ExtDict:
        payload = Params().create_new().put_definer("user", account_id).finish()
        codes = {-1: MissingAccess(f"No users were found with ID: {account_id}.")}

        resp = await self.http.request(Route.GET_USER_INFO, payload, error_codes=codes)
        mapped = Parser().with_split(":").should_map().parse(resp)

        if return_only_stats:
            return mapped

        another = (
            Params()
            .create_new()
            .put_definer("search", mapped.getcast(Index.USER_PLAYER_ID, 0, int))
            .put_total(0)
            .put_page(0)
            .finish()
        )
        some_resp = await self.http.request(Route.USER_SEARCH, another)

        new_resp = (
            Parser().split("#").take(0).check_empty().split(":").should_map().parse(some_resp)
        )

        if new_resp is None:
            raise codes.get(-1)

        mapped.update(
            {k: new_resp.get(k) for k in (Index.USER_NAME, Index.USER_ICON, Index.USER_ICON_TYPE)}
        )

        return mapped

    async def search_user(self, query: Union[int, str], return_abstract: bool = False) -> ExtDict:

        payload = (
            Params().create_new().put_definer("search", query).put_total(0).put_page(0).finish()
        )
        codes = {-1: MissingAccess(f"Searching for {query!r} failed.")}

        resp = await self.http.request(Route.USER_SEARCH, payload, error_codes=codes)
        mapped = Parser().split("#").take(0).check_empty().split(":").should_map().parse(resp)

        if mapped is None:
            raise codes.get(-1)

        account_id = mapped.getcast(Index.USER_ACCOUNT_ID, 0, int)

        if return_abstract or not account_id:
            return mapped

        # ok; if we should not return abstract, let's find all other parameters
        payload = Params().create_new().put_definer("user", account_id).finish()

        resp = await self.http.request(Route.GET_USER_INFO, payload, error_codes=codes)
        mapped.update(Parser().with_split(":").should_map().parse(resp))

        return mapped

    async def get_level_info(self, level_id: int = 0) -> Tuple[ExtDict, ExtDict, ExtDict]:
        # level data, creator, song
        assert level_id >= -2, "Invalid Level ID provided."

        if level_id < 0:
            type, number, cooldown = await self.get_timely_info(level_id)
        else:
            type, number, cooldown = 0, -1, -1

        ext = {"101": type, "102": number, "103": cooldown}

        codes = {-1: MissingAccess(f"Failed to get a level. Given ID: {level_id}")}

        payload = Params().create_new().put_definer("levelid", level_id).finish()
        resp = await self.http.request(Route.DOWNLOAD_LEVEL, payload, error_codes=codes)

        level_data = Parser().split("#").take(0).split(":").add_ext(ext).should_map().parse(resp)

        real_id = level_data.getcast(Index.LEVEL_ID, 0, int)

        payload = (
            Params()
            .create_new()
            .put_definer("search", real_id)
            .put_filters(Filters.setup_empty())
            .finish()
        )
        resp = await self.http.request(Route.LEVEL_SEARCH, payload, error_codes=codes)

        if not resp or resp.count("#") < 2:
            raise codes.get(-1)

        data = resp.split("#")

        # getting song
        song_data = data[2]

        if not song_data:
            song = Converter.to_normal_song(level_data.getcast(Index.LEVEL_AUDIO_TRACK, 0, int))
        else:
            song = Parser().with_split("~|~").should_map().parse(song_data)

        # getting creator
        creator_data = data[1]

        if not creator_data:
            id, name, account_id = (0, "unknown", 0)
        else:
            id, name, account_id = creator_data.split(":")

        creator = ExtDict(id=id, name=name, account_id=account_id)

        return level_data, creator, song

    async def get_timely_info(self, type_id: int = -1) -> Tuple[int, int, int]:
        # Daily: -1, Weekly: -2
        weekly = ~type_id
        payload = Params().create_new().put_weekly(weekly).finish()
        codes = {-1: MissingAccess(f"Failed to fetch a {type!r} level.")}
        resp = await self.http.request(Route.GET_TIMELY, payload, error_codes=codes)

        try:
            number, cooldown, *_ = map(int, resp.split("|"))
        except ValueError:  # unpacking failed or something else
            raise MissingAccess(
                "Failed to fetch a timely level. Most likely it is being refreshed."
            ) from None

        number %= 100000
        weekly += 1

        return (weekly, number, cooldown)

    async def upload_level(
        self,
        data: str,
        name: str,
        level_id: int,
        version: int,
        length: LevelLength,
        audio_track: int,
        desc: str,
        song_id: int,
        is_auto: bool,
        original: int,
        two_player: bool,
        objects: int,
        coins: int,
        stars: int,
        unlisted: bool,
        friends_only: bool,
        ldm: bool,
        password: Optional[Union[int, str]],
        copyable: bool,
        *,
        client: Client,
    ) -> int:
        data = Coder.zip(data)
        extra_string = "_".join(map(str, (0 for _ in range(55))))
        desc = Coder.do_base64(desc)

        upload_seed = Coder.gen_level_upload_seed(data)
        seed2 = Coder.gen_chk(type="level", values=[upload_seed])
        seed = Coder.gen_rs()

        pwd = 0

        if copyable and password is None:
            pwd = 1

        check, add = str(password), 1000000

        if check.isdigit() and int(check) < add:
            pwd = add + int(password)

        if friends_only:
            unlisted, unlisted2 = (1, 1)
        elif unlisted:
            unlisted, unlisted2 = (1, 0)
        else:
            unlisted, unlisted2 = (0, 0)

        payload = (
            Params()
            .create_new()
            .put_definer("accountid", client.account_id)
            .put_definer("levelid", level_id)
            .put_definer("song", song_id)
            .put_seed(seed)
            .put_seed(seed2, suffix=2)
            .put_seed(0, prefix="wt")
            .put_seed(0, prefix="wt", suffix=2)
            .put_password(client.encodedpass)
            .put_username(client.name)
            .finish()
        )

        options = {
            "level_name": name,
            "level_desc": desc,
            "level_version": version,
            "level_length": length.value,
            "audio_track": audio_track,
            "auto": int(is_auto),
            "original": int(original),
            "two_player": int(two_player),
            "objects": objects,
            "coins": coins,
            "requested_stars": stars,
            "unlisted": unlisted,
            "unlisted2": unlisted2,
            "ldm": int(ldm),
            "password": pwd,
            "level_string": data,
            "extra_string": extra_string,
            "level_info": "H4sIAAAAAAAAC_NIrVQoyUgtStVRCMpPSi0qUbDStwYAsgpl1RUAAAA=",
        }

        payload_cased = {
            Converter.snake_to_camel(key): str(value) for key, value in options.items()
        }

        payload.update(payload_cased)

        level_id = await self.http.request(Route.UPLOAD_LEVEL, payload)

        if level_id == -1:
            raise MissingAccess("Failed to upload a level.")

        return level_id

    async def get_user_list(
        self, type: int = 0, *, exclude: Tuple[Type[BaseException]] = (), client: Client
    ) -> List[ExtDict]:
        payload = (
            Params()
            .create_new()
            .put_definer("accountid", client.account_id)
            .put_password(client.encodedpass)
            .put_type(type)
            .finish()
        )
        codes = {
            -1: MissingAccess("Failed to fetch a user list."),
            -2: NothingFound("gd.AbstractUser"),
        }

        resp = await self.http.request(
            Route.GET_USER_LIST, payload, error_codes=codes, exclude=exclude
        )

        if resp is None:
            return []

        resp, parser = resp.split("|"), Parser().with_split(":").should_map()

        return list(map(parser.parse, resp))

    async def get_leaderboard(
        self, level_id: int, strategy: LevelLeaderboardStrategy, *, client: Client
    ) -> List[ExtDict]:
        # timely_type: TimelyType, played: bool = False, timely_index: int = 0, percentage: int = 0,
        # jumps: int = 0, attempts: int = 0, seconds: int = 0, coins: int = 0
        # rs = Coder.gen_rs()
        # seed = Coder.gen_level_lb_seed(jumps, percentage, seconds, played)

        # if str(timely_type) == 'weekly':
        #     timely_index += 100000

        # values = [
        #     client.account_id, level_id, percentage, seconds, jumps, attempts,
        #     percentage, 100 - percentage, 1, coins, timely_index, rs
        # ]

        # chk = Coder.gen_chk(type='levelscore', values=values)

        params = (
            Params()
            .create_new()
            .put_definer("accountid", client.account_id)
            .put_definer("levelid", level_id)
            .put_password(client.encodedpass)
            .put_type(strategy.value)
        )

        # params.put_percent(percentage).put_chk(chk)

        # for index, value in enumerate((
        #     attempts + 8354, jumps + 3991, seconds + 4085, seed, random.randint(100, 10000),
        #     "", rs, attempts, coins + 5819, timely_index
        # ), 1):
        #     params.put_seed(value, prefix='s', suffix=index)

        payload = params.finish()

        codes = {-1: MissingAccess(f"Failed to get leaderboard of the level by ID: {level_id!r}.")}

        resp = await self.http.request(Route.GET_LEVEL_SCORES, payload, error_codes=codes)

        if not resp:
            return []

        resp, parser = (
            resp.split("|"),
            Parser().with_split(":").add_ext({"101": level_id}).should_map(),
        )

        return list(map(parser.parse, filter(is_not_empty, resp)))

    async def get_top(
        self, strategy: LeaderboardStrategy, count: int, *, client: Client
    ) -> List[ExtDict]:
        needs_login = strategy.value in (1, 2)

        # special case: map 'players' -> 'top'
        strategy = strategy.name.lower() if strategy.value else "top"

        params = Params().create_new().put_type(strategy).put_count(count)
        codes = {-1: MissingAccess(f"Failed to fetch leaderboard for strategy: {strategy!r}.")}

        if needs_login:
            check_logged_obj(client, "get_top")
            params.put_definer("accountid", client.account_id).put_password(client.encodedpass)

        payload = params.finish()

        resp = await self.http.request(Route.GET_USER_TOP, payload, error_codes=codes)
        resp, parser = resp.split("|"), Parser().with_split(":").should_map()

        return list(map(parser.parse, filter(is_not_empty, resp)))

    async def login(self, user: str, password: str) -> Tuple[int, int]:
        # account_id, id
        payload = (
            Params().create_new().put_login_definer(username=user, password=password).finish_login()
        )
        codes = {
            -1: LoginFailure(login=user, password=password),
            -12: MissingAccess(f"Account {user!r} (password {password!r}) is disabled."),
        }

        resp = await self.http.request(Route.LOGIN, payload, error_codes=codes)

        account_id, id, *junk = resp.split(",")

        return int(account_id), int(id)

    async def load_save(self, client: Client) -> Optional[api.Database]:
        link = Route.GD_URL

        payload = (
            Params()
            .create_new()
            .put_username(client.name)
            .put_definer("password", client.password)
            .finish_login()
        )
        codes = {-11: MissingAccess(f"Failed to load data for client: {client!r}.")}

        resp = await self.http.request(
            Route.LOAD_DATA, payload, error_codes=codes, custom_base=link
        )

        try:
            main, levels, *_ = resp.split(";")
            db = await api.save.from_string_async(main, levels, xor=False, follow_os=False)

            return db

        except Exception:
            return

    async def do_save(self, data: str, client: Client) -> None:
        link = Route.GD_URL

        codes = {
            -4: MissingAccess("Data is too large."),
            -5: MissingAccess("Invalid login credentials."),
            -6: MissingAccess("Something wrong happened."),
        }

        payload = (
            Params()
            .create_new()
            .put_username(client.name)
            .put_definer("password", client.password)
            .put_save_data(data)
            .finish_login()
        )

        resp = await self.http.request(
            Route.SAVE_DATA, payload, custom_base=link, error_codes=codes
        )

        if resp != 1:
            raise MissingAccess(f"Failed to do backup for client: {client!r}")

    async def search_levels_on_page(
        self,
        page: int = 0,
        query: str = "",
        filters: Optional[Filters] = None,
        user_id: Optional[int] = None,
        gauntlet: Optional[int] = None,
        *,
        exclude: Tuple[Type[BaseException]] = (),
        client: Client,
    ) -> Tuple[List[ExtDict], List[ExtDict], List[ExtDict]]:
        # levels, creators, songs
        if filters is None:
            filters = Filters.setup_empty()

        codes = {-1: MissingAccess("No levels were found.")}

        params = Params().create_new()

        if gauntlet is not None:
            params.put_definer("gauntlet", gauntlet)

        else:
            params.put_definer("search", query).put_page(page).put_total(0).put_filters(filters)

            if filters.strategy == SearchStrategy.BY_USER:

                if user_id is None:
                    check_logged_obj(client, "search_levels_on_page(...)")

                    user_id = client.id

                    params.put_definer("accountid", client.account_id).put_password(
                        client.encodedpass
                    )
                    params.put_local(1)

                params.put_definer("search", user_id)  # override the 'str' parameter in request

            elif filters.strategy == SearchStrategy.FRIENDS:
                check_logged_obj(client, "search_levels_on_page(..., client=client)")
                params.put_definer("accountid", client.account_id).put_password(client.encodedpass)

        payload = params.finish()

        resp = await self.http.request(
            Route.LEVEL_SEARCH, payload, exclude=exclude, error_codes=codes
        )

        if not resp:
            return [], [], []

        resp, parser = resp.split("#"), Parser().with_split("~|~").should_map()

        try:
            lvdata, cdata, sdata = resp[:3]
        except ValueError:
            return [], [], []

        songs = list(map(parser.parse, filter(is_not_empty, sdata.split("~:~"))))

        creators = [
            ExtDict(zip(("id", "name", "account_id"), creator.split(":")))
            for creator in filter(is_not_empty, cdata.split("|"))
        ]

        parser.with_split(":").add_ext({"101": 0, "102": -1, "103": -1})

        levels = list(map(parser.parse, filter(is_not_empty, lvdata.split("|"))))

        return levels, creators, songs

    async def search_levels(
        self,
        query: str = "",
        filters: Optional[Filters] = None,
        user_id: Optional[int] = None,
        pages: Optional[Sequence[int]] = None,
        gauntlet: Optional[int] = None,
        *,
        client: Client,
    ) -> List[ExtDict]:
        to_run = [
            self.search_levels_on_page(
                query=query,
                filters=filters,
                user_id=user_id,
                page=page,
                gauntlet=gauntlet,
                exclude=excluding(Exception),
                client=client,
            )
            for page in pages
        ]
        levels, creators, songs = [], [], []

        for (level_part, creator_part, song_part) in await asyncio.gather(*to_run):
            levels.extend(level_part)
            creators.extend(creator_part)
            songs.extend(song_part)

        return levels, creators, songs

    async def report_level(self, level_id: int) -> None:
        payload = Params().create_new("web").put_definer("levelid", level_id).finish()
        codes = {-1: MissingAccess(f"Failed to report a level by ID: {level_id!r}.")}

        await self.http.request(Route.REPORT_LEVEL, payload, error_codes=codes)

    async def delete_level(self, level_id: int, *, client: Client) -> None:
        payload = (
            Params()
            .create_new()
            .put_definer("accountid", client.account_id)
            .put_definer("levelid", level_id)
            .put_password(client.encodedpass)
            .finish_level()
        )

        resp = await self.http.request(Route.DELETE_LEVEL, payload)

        if resp != 1:
            raise MissingAccess(f"Failed to delete a level by ID: {level_id}.")

    async def update_level_desc(self, level_id: int, content: str, *, client: Client) -> None:
        payload = (
            Params()
            .create_new()
            .put_definer("accountid", client.account_id)
            .put_password(client.encodedpass)
            .put_definer("levelid", level_id)
            .put_level_desc(content)
            .finish()
        )

        resp = await self.http.request(Route.UPDATE_LEVEL_DESC, payload)

        if resp != 1:
            raise MissingAccess(f"Failed to update description of the level by ID: {level_id}.")

    async def rate_level(self, level_id: int, rating: int, *, client: Client) -> None:
        assert 0 < rating <= 10, "Invalid star value given."

        rs, udid, uuid = Coder.gen_rs(), Params.gen_udid(), Params.gen_uuid()
        values = [level_id, rating, rs, client.account_id, udid, uuid]
        chk = Coder.gen_chk(type="like_rate", values=values)

        payload = (
            Params()
            .create_new()
            .put_definer("levelid", level_id)
            .put_definer("accountid", client.account_id)
            .put_password(client.encodedpass)
            .put_udid(udid)
            .put_uuid(uuid)
            .put_definer("stars", rating)
            .put_rs(rs)
            .put_chk(chk)
            .finish()
        )

        resp = await self.http.request(Route.RATE_LEVEL_STARS, payload)

        if resp != 1:
            raise MissingAccess(f"Failed to rate level by ID: {level_id}.")

    async def rate_demon(
        self, level_id: int, demon_rating: DemonDifficulty, mod: bool, *, client: Client
    ) -> bool:
        rating_level = demon_rating.value

        payload = (
            Params()
            .create_new()
            .put_definer("accountid", client.account_id)
            .put_password(client.encodedpass)
            .put_definer("levelid", level_id)
            .put_definer("rating", rating_level)
            .put_mode(int(mod))
            .finish_mod()
        )
        codes = {-2: MissingAccess("Attempt to rate as mod without mod permissions.")}

        resp = await self.http.request(Route.RATE_LEVEL_DEMON, payload, error_codes=codes)

        if not resp:
            return False

        elif isinstance(resp, int) and resp > 0:
            return True

    async def send_level(
        self, level_id: int, rating: int, featured: bool, *, client: Client
    ) -> None:
        payload = (
            Params()
            .create_new()
            .put_definer("accountid", client.account_id)
            .put_password(client.encodedpass)
            .put_definer("levelid", level_id)
            .put_definer("stars", rating)
            .put_feature(int(featured))
            .finish_mod()
        )
        codes = {
            -2: MissingAccess(f"Missing moderator permissions to send a level by ID: {level_id!r}.")
        }

        resp = await self.http.request(Route.SUGGEST_LEVEL_STARS, payload, error_codes=codes)

        if resp != 1:
            raise MissingAccess(f"Failed to send a level by ID: {level_id!r}.")

    async def like(
        self, item_id: int, typeid: int, special: int, dislike: bool = False, *, client: Client
    ) -> None:
        like = dislike ^ 1

        rs, udid, uuid = Coder.gen_rs(), Params.gen_udid(), Params.gen_uuid()
        values = [special, item_id, like, typeid, rs, client.account_id, udid, uuid]
        chk = Coder.gen_chk(type="like_rate", values=values)

        payload = (
            Params()
            .create_new(game_version=20)
            .put_definer("accountid", client.account_id)
            .put_password(client.encodedpass)
            .put_udid(udid)
            .put_uuid(uuid)
            .put_definer("itemid", item_id)
            .put_like(like)
            .put_type(typeid)
            .put_special(special)
            .put_rs(rs)
            .put_chk(chk)
            .finish()
        )

        resp = await self.http.request(Route.LIKE_ITEM, payload)

        if resp != 1:
            raise MissingAccess(f"Failed to like an item by ID: {item_id}.")

    async def get_page_messages(
        self,
        sent_or_inbox: str,
        page: int,
        *,
        exclude: Tuple[Type[BaseException]] = (),
        client: Client,
    ) -> List[ExtDict]:
        assert sent_or_inbox in ("inbox", "sent")
        inbox = 0 if sent_or_inbox != "sent" else 1

        payload = (
            Params()
            .create_new()
            .put_definer("accountid", client.account_id)
            .put_password(client.encodedpass)
            .put_page(page)
            .put_total(0)
            .get_sent(inbox)
            .finish()
        )
        codes = {-1: MissingAccess("Failed to get messages."), -2: NothingFound("gd.Message")}

        resp = await self.http.request(
            Route.GET_PRIVATE_MESSAGES, payload, error_codes=codes, exclude=exclude
        )
        resp = Parser().split("#").take(0).check_empty().split("|").parse(resp)

        if resp is None:
            return []

        parser = Parser().with_split(":").should_map()
        return list(map(parser.parse, resp))

    async def get_messages(
        self, sent_or_inbox: str, pages: Optional[Sequence[int]] = None, *, client: Client
    ) -> List[ExtDict]:
        assert sent_or_inbox in ("inbox", "sent")

        to_run = [
            self.get_page_messages(
                sent_or_inbox=sent_or_inbox, page=page, exclude=excluding(Exception), client=client
            )
            for page in pages
        ]

        return await self.run_many(to_run)

    async def post_comment(self, content: str, *, client: Client) -> None:
        to_gen = [client.name, 0, 0, 1]

        payload = (
            Params()
            .create_new()
            .put_definer("accountid", client.account_id)
            .put_username(client.name)
            .put_password(client.encodedpass)
            .put_comment(content, to_gen)
            .comment_for("profile")
            .finish()
        )
        codes = {-1: MissingAccess("Failed to post a comment.")}

        await self.http.request(Route.UPLOAD_ACC_COMMENT, payload, error_codes=codes)

    async def comment_level(
        self, level_id: int, content: str, percentage: int, *, client: Client
    ) -> None:
        if percentage > 100:
            raise ValueError(f"{percentage}% > 100% percentage arg was received.")

        percentage = round(percentage)  # just in case
        to_gen = [client.name, level_id, percentage, 0]

        payload = (
            Params()
            .create_new()
            .put_definer("accountid", client.account_id)
            .put_username(client.name)
            .put_password(client.encodedpass)
            .put_comment(content, to_gen)
            .comment_for("level", level_id)
            .put_percent(percentage)
            .finish()
        )
        codes = {-1: MissingAccess(f"Failed to post a comment on a level by ID: {level_id!r}.")}

        await self.http.request(Route.UPLOAD_COMMENT, payload, error_codes=codes)

    async def delete_comment(
        self, typeof: CommentType, comment_id: int, level_id: int, *, client: Client
    ) -> None:
        cases = {0: Route.DELETE_LEVEL_COMMENT, 1: Route.DELETE_ACC_COMMENT}
        route = cases.get(typeof.value)
        payload = (
            Params()
            .create_new()
            .put_definer("commentid", comment_id)
            .put_definer("accountid", client.account_id)
            .put_password(client.encodedpass)
            .comment_for(typeof.name.lower(), level_id)
            .finish()
        )
        resp = await self.http.request(route, payload)

        if resp != 1:
            raise MissingAccess(f"Failed to delete a comment by ID: {comment_id!r}.")

    async def send_friend_request(
        self, target_id: int, message: str = "", *, client: Client
    ) -> None:
        payload = (
            Params()
            .create_new()
            .put_definer("accountid", client.account_id)
            .put_recipient(target_id)
            .put_fr_comment(message)
            .put_password(client.encodedpass)
            .finish()
        )
        resp = await self.http.request(Route.SEND_REQUEST, payload)

        if not resp:  # if request is already sent
            return

        elif resp != 1:
            raise MissingAccess(f"Failed to send a friend request to user by ID: {target_id!r}.")

    async def delete_friend_request(
        self, typeof: MessageOrRequestType, user_id: int, client: Client
    ) -> None:
        payload = (
            Params()
            .create_new()
            .put_definer("accountid", client.account_id)
            .put_definer("user", user_id)
            .put_password(client.encodedpass)
            .put_is_sender(typeof.name.lower())
            .finish()
        )
        resp = await self.http.request(Route.DELETE_REQUEST, payload)

        if resp != 1:
            raise MissingAccess(
                f"Failed to delete a friend request by User (with ID): {user_id!r}."
            )

    async def accept_friend_request(
        self, typeof: MessageOrRequestType, request_id: int, user_id: int, client: Client
    ) -> None:
        if typeof.value:  # is gd.MessageOrRequestType.SENT
            raise MissingAccess(
                "Failed to accept a friend request. Reason: request is sent, not received one."
            )
        payload = (
            Params()
            .create_new()
            .put_definer("accountid", client.account_id)
            .put_password(client.encodedpass)
            .put_definer("user", user_id)
            .put_definer("requestid", request_id)
            .finish()
        )
        resp = await self.http.request(Route.ACCEPT_REQUEST, payload)

        if resp != 1:
            raise MissingAccess(f"Failed to accept a friend request by ID: {request_id!r}.")

    async def read_friend_request(self, request_id: int, client: Client) -> None:
        payload = (
            Params()
            .create_new()
            .put_definer("accountid", client.account_id)
            .put_password(client.encodedpass)
            .put_definer("requestid", request_id)
            .finish()
        )
        resp = await self.http.request(Route.READ_REQUEST, payload)

        if resp != 1:
            raise MissingAccess(f"Failed to read a friend request by ID: {request_id!r}.")

    async def read_message(
        self, typeof: MessageOrRequestType, message_id: int, client: Client
    ) -> str:
        payload = (
            Params()
            .create_new()
            .put_definer("accountid", client.account_id)
            .put_definer("messageid", message_id)
            .put_is_sender(typeof.name.lower())
            .put_password(client.encodedpass)
            .finish()
        )
        codes = {-1: MissingAccess(f"Failed to read a message by ID: {message_id!r}.")}
        resp = await self.http.request(Route.READ_PRIVATE_MESSAGE, payload, error_codes=codes,)
        mapped = Parser().with_split(":").should_map().parse(resp)

        return Coder.decode(type="message", string=mapped.get(Index.MESSAGE_BODY, ""))

    async def delete_message(
        self, typeof: MessageOrRequestType, message_id: int, client: Client
    ) -> None:
        payload = (
            Params()
            .create_new()
            .put_definer("accountid", client.account_id)
            .put_definer("messageid", message_id)
            .put_password(client.encodedpass)
            .put_is_sender(typeof.name.lower())
            .finish()
        )
        resp = await self.http.request(Route.DELETE_PRIVATE_MESSAGE, payload)

        if resp != 1:
            raise MissingAccess(f"Failed to delete a message by ID: {message_id!r}.")

    async def get_gauntlets(self) -> List[ExtDict]:
        payload = Params().create_new().finish()

        resp = await self.http.request(Route.GET_GAUNTLETS, payload)

        splitted = Parser().split("#").take(0).split("|").parse(resp)
        parser = Parser().with_split(":").should_map()

        return list(map(parser.parse, filter(is_not_empty, splitted)))

    async def get_page_map_packs(
        self, page: int = 0, *, exclude: Tuple[Type[BaseException]] = (),
    ) -> List[ExtDict]:
        payload = Params().create_new().put_page(page).finish()

        resp = await self.http.request(Route.GET_MAP_PACKS, payload)

        splitted = Parser().split("#").take(0).split("|").check_empty().should_map().parse(resp)

        if not splitted:
            if issubclass(NothingFound, exclude):
                return []
            raise NothingFound("gd.MapPack")

        parser = Parser().with_split(":").should_map()

        return list(map(parser.parse, splitted))

    async def get_map_packs(self, pages: Sequence[int]) -> List[ExtDict]:
        to_run = [
            self.get_page_map_packs(page=page, exclude=excluding(Exception)) for page in pages
        ]
        return await self.run_many(to_run)

    async def get_page_friend_requests(
        self,
        sent_or_inbox: str = "inbox",
        page: int = 0,
        *,
        exclude: Tuple[Type[BaseException]] = (),
        client: Client,
    ) -> List[ExtDict]:
        inbox = int(sent_or_inbox == "sent")

        payload = (
            Params()
            .create_new()
            .put_definer("accountid", str(client.account_id))
            .put_password(client.encodedpass)
            .put_page(page)
            .put_total(0)
            .get_sent(inbox)
            .finish()
        )
        codes = {
            -1: MissingAccess(f"Failed to get friend requests on page {page}."),
            -2: NothingFound("gd.FriendRequest"),
        }

        resp = await self.http.request(
            Route.GET_FRIEND_REQUESTS, payload, error_codes=codes, exclude=exclude
        )
        splitted = Parser().split("#").take(0).split("|").check_empty().parse(resp)

        if resp is None:
            return []

        parser = Parser().split(":").add_ext({"101": inbox}).should_map()

        return list(map(parser.parse, splitted))

    async def get_friend_requests(
        self, pages: Sequence[int], sent_or_inbox: str = "inbox", *, client: Client
    ) -> List[ExtDict]:
        assert sent_or_inbox in ("sent", "inbox")

        to_run = [
            self.get_page_friend_requests(
                sent_or_inbox=sent_or_inbox, page=page, exclude=excluding(Exception), client=client
            )
            for page in pages
        ]

        return await self.run_many(to_run)

    async def retrieve_page_comments(
        self,
        account_id: int,
        id: int,
        type: str = "profile",
        page: int = 0,
        *,
        strategy: CommentStrategy,
        exclude: Tuple[Type[BaseException]] = (),
    ) -> List[ExtDict]:
        assert isinstance(page, int) and page >= 0
        assert type in ("profile", "level")

        is_level = type == "level"

        typeid = is_level ^ 1
        definer = "userid" if is_level else "accountid"
        selfid = id if is_level else account_id
        route = Route.GET_COMMENT_HISTORY if is_level else Route.GET_ACC_COMMENTS

        parser = Parser().add_ext({"101": typeid}).should_map()

        if is_level:
            parser.split(":").take(0).split("~")
        else:
            parser.with_split("~")

        param_obj = Params().create_new().put_definer(definer, selfid).put_page(page).put_total(0)
        if is_level:
            param_obj.put_mode(strategy.value)
        payload = param_obj.finish()

        codes = {
            -1: MissingAccess(f"Failed to retrieve comment for user by Account ID: {account_id!r}.")
        }

        resp = await self.http.request(route, payload, error_codes=codes, exclude=exclude)

        if not resp:
            return []

        splitted = resp.split("#").pop(0)

        if not splitted:
            if issubclass(NothingFound, exclude):
                return []
            raise NothingFound("gd.Comment")

        return list(map(parser.parse, filter(is_not_empty, splitted.split("|"))))

    async def retrieve_comments(
        self,
        account_id: int,
        id: int,
        pages: Sequence[int],
        type: str = "profile",
        *,
        strategy: CommentStrategy,
    ) -> List[ExtDict]:
        assert type in ("profile", "level")

        to_run = [
            self.retrieve_page_comments(
                type=type,
                account_id=account_id,
                id=id,
                page=page,
                exclude=excluding(Exception),
                strategy=strategy,
            )
            for page in pages
        ]

        return await self.run_many(to_run)

    async def get_level_comments(
        self,
        level_id: int,
        strategy: CommentStrategy,
        amount: int,
        exclude: Tuple[Type[BaseException]] = (),
    ) -> List[Tuple[ExtDict, ExtDict]]:
        # comment, user
        payload = (
            Params()
            .create_new()
            .put_definer("levelid", level_id)
            .put_page(0)
            .put_total(0)
            .put_mode(strategy.value)
            .put_count(amount)
            .finish()
        )
        codes = {
            -1: MissingAccess(f"Failed to get comments of a level by ID: {level_id!r}."),
            -2: NothingFound("gd.Comment"),
        }

        resp = await self.http.request(
            Route.GET_COMMENTS, payload, error_codes=codes, exclude=exclude
        )

        if resp is None:
            return []

        splitted = Parser().split("#").take(0).split("|").parse(resp)
        parser = Parser().with_split("~").should_map()

        res = []

        for elem in filter(is_not_empty, splitted):
            com_data, user_data, *_ = map(parser.parse, elem.split(":"))
            com_data.update({"1": level_id, "101": 0, "102": 0})

            user_data = ExtDict(
                account_id=user_data.getcast(Index.USER_ACCOUNT_ID, 0, int),
                id=com_data.getcast(Index.COMMENT_AUTHOR_ID, 0, int),
                name=user_data.get(Index.USER_NAME, "unknown"),
            )

            res.append((com_data, user_data))

        return res

    async def block_user(self, account_id: int, unblock: bool = False, *, client: Client) -> None:
        route = Route.UNBLOCK_USER if unblock else Route.BLOCK_USER
        payload = (
            Params()
            .create_new()
            .put_definer("accountid", client.account_id)
            .put_password(client.encodedpass)
            .put_definer("user", account_id)
            .finish()
        )
        resp = await self.http.request(route, payload)

        if resp != 1:
            raise MissingAccess(
                f"Failed to {'un' if unblock else ''}block a user by Account ID: {account_id!r}."
            )

    async def unfriend_user(self, account_id: int, *, client: Client) -> None:
        payload = (
            Params()
            .create_new()
            .put_definer("accountid", client.account_id)
            .put_password(client.encodedpass)
            .put_definer("user", account_id)
            .finish()
        )
        resp = await self.http.request(Route.REMOVE_FRIEND, payload)

        if resp != 1:
            raise MissingAccess(f"Failed to unfriend a user by Account ID: {account_id!r}.")

    async def send_message(
        self, account_id: int, subject: str, body: str, *, client: Client
    ) -> None:
        payload = (
            Params()
            .create_new()
            .put_definer("accountid", client.account_id)
            .put_message(subject, body)
            .put_recipient(account_id)
            .put_password(client.encodedpass)
            .finish()
        )
        resp = await self.http.request(Route.SEND_PRIVATE_MESSAGE, payload)

        if resp != 1:
            raise MissingAccess(
                f"Failed to send a message to a user by Account ID: {account_id!r}."
            )

    async def update_profile(self, settings: Dict[str, int], *, client: Client) -> None:
        settings_cased = {Converter.snake_to_camel(name): value for name, value in settings.items()}

        rs = Coder.gen_rs()

        req_chk_params = [client.account_id]
        req_chk_params.extend(
            settings.get(param, 0)
            for param in (
                "user_coins",
                "demons",
                "stars",
                "coins",
                "icon_type",
                "icon",
                "diamonds",
                "acc_icon",
                "acc_ship",
                "acc_ball",
                "acc_bird",
                "acc_dart",
                "acc_robot",
                "acc_glow",
                "acc_spider",
                "acc_explosion",
            )
        )

        chk = Coder.gen_chk(type="userscore", values=req_chk_params)

        payload = (
            Params()
            .create_new()
            .put_definer("accountid", client.account_id)
            .put_password(client.encodedpass)
            .put_username(client.name)
            .put_seed(rs)
            .put_seed(chk, suffix=str(2))
            .finish()
        )

        payload.update(settings_cased)

        resp = await self.http.request(Route.UPDATE_USER_SCORE, payload)

        if not resp > 0:
            raise MissingAccess(f"Failed to update profile of a client: {client!r}")

    async def update_settings(
        self,
        message_policy: MessagePolicyType,
        friend_request_policy: FriendRequestPolicyType,
        comment_policy: CommentPolicyType,
        youtube: str,
        twitter: str,
        twitch: str,
        *,
        client: Client,
    ) -> None:
        payload = (
            Params()
            .create_new("web")
            .put_definer("accountid", client.account_id)
            .put_password(client.encodedpass)
            .put_profile_upd(
                message_policy.value,
                friend_request_policy.value,
                comment_policy.value,
                youtube,
                twitter,
                twitch,
            )
            .finish_login()
        )
        resp = await self.http.request(Route.UPDATE_ACC_SETTINGS, payload)

        if resp != 1:
            raise MissingAccess(f"Failed to update profile settings of a client: {client!r}.")

    async def get_quests(self, *, client: Client) -> List[ExtDict]:
        udid, uuid = Params.gen_udid(), Params.gen_uuid()
        rn = Coder.gen_rs(5, charset=string.digits)
        chk = Coder.gen_chk(type="challenges", values=[rn])

        codes = {-1: MissingAccess("Failed to get quests.")}

        payload = (
            Params()
            .create_new()
            .put_definer("accountid", client.account_id)
            .put_password(client.encodedpass)
            .put_udid(udid)
            .put_uuid(uuid)
            .put_chk(chk[:REWARD_CHALLENGE_CHK_LENGTH])
            .finish()
        )

        resp = await self.http.request(Route.GET_CHALLENGES, payload, error_codes=codes)

        resp = Parser().split("|").take(0).check_empty().parse(resp)

        if resp is None:
            return []

        data = Coder.decode(
            type="challenges", string=resp[REWARD_CHALLENGE_SLICE_LENGTH:], use_bytes=True
        )
        time_left, *quests = data.split(":")[-QUEST_AMOUNT - 1 :]

        time_left = int(time_left)
        result = []

        for quest in quests:
            try:
                id, type, amount, reward, name, *_ = quest.split(",")
            except ValueError:
                continue

            result.append(
                ExtDict(
                    id=int(id),
                    type=QuestType.from_value(int(type), "unknown"),
                    amount=int(amount),
                    reward=int(reward),
                    name=name,
                    seconds=time_left,
                )
            )

        return result

    async def get_chests(self, reward_type: RewardType, *, client: Client) -> List[ExtDict]:
        udid, uuid = Params.gen_udid(), Params.gen_uuid()
        rn = Coder.gen_rs(5, charset=string.digits)
        chk = Coder.gen_chk(type="rewards", values=[rn])

        codes = {-1: MissingAccess("Failed to get chests.")}

        payload = (
            Params()
            .create_new()
            .put_definer("accountid", client.account_id)
            .put_password(client.encodedpass)
            .put_udid(udid)
            .put_uuid(uuid)
            .put_definer("reward", reward_type.value)
            .put_chk(chk[:REWARD_CHALLENGE_CHK_LENGTH])
            .put_seed(0, prefix="r", suffix=1)
            .put_seed(0, prefix="r", suffix=2)
            .finish()
        )

        resp = await self.http.request(Route.GET_REWARDS, payload, error_codes=codes)

        resp = Parser().split("|").take(0).check_empty().parse(resp)

        if resp is None:
            return []

        data = Coder.decode(
            type="rewards", string=resp[REWARD_CHALLENGE_SLICE_LENGTH:], use_bytes=True
        )
        chest_parts = data.split(":")[-CHEST_AMOUNT * CHEST_INNER_PARTS - 1 : -1]

        result = []

        for chest_id, (time_left, chest_info, chest_count) in enumerate(
            group(chest_parts, CHEST_INNER_PARTS), 1
        ):
            try:
                orbs, diamonds, shard_id, keys, *_ = chest_info.split(",")
            except ValueError:
                continue

            result.append(
                ExtDict(
                    id=chest_id,
                    seconds=int(time_left),
                    count=int(chest_count),
                    orbs=int(orbs),
                    diamonds=int(diamonds),
                    shard_id=int(shard_id),
                    shard_type=ShardType.from_value(int(shard_id), "unknown"),
                    keys=int(keys),
                )
            )

        return result

    async def run_many(self, tasks: List[asyncio.Task]) -> Any:
        res = await asyncio.gather(*tasks)

        res = [elem for elem in res if elem]

        if all(iterable(elem) for elem in res):
            res = list(chain.from_iterable(res))

        return res


def excluding(*args: Tuple[Type[BaseException]]) -> Tuple[Type[BaseException]]:
    return args


def group(some_iterable: Iterable[Any], group_size: int = 2) -> Iterable[Tuple[Any]]:
    return zip(*(iter(some_iterable),) * group_size)


def iterable(maybe_iterable: Iterable) -> bool:
    try:
        iter(maybe_iterable)
        return True
    except Exception:
        return False


def is_not_empty(sequence: Sequence) -> bool:
    return len(sequence) != 0
