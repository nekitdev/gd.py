import base64 as b64
import urllib.parse

from ._typing import Any, Client, Dict, Type, Union

from .song import Song
from .user import UserStats, User
from .colors import Color, colors
from .comment import Comment
from .abstractuser import AbstractUser, LevelRecord
from .level import Level
from .message import Message
from .iconset import IconSet
from .friend_request import FriendRequest
from .level_packs import MapPack, Gauntlet

from .utils.converter import Converter
from .utils.enums import LeaderboardStrategy
from .utils.indexer import Index
from .utils.crypto.coders import Coder
from .utils.routes import Route

# MapperUtil.map attempts to convert keys and values to integer objects.
# That is why ClassConverter does not do int() conversions.

ParseMap = Dict[Union[int, str], Union[int, str]]


class ClassConverter:

    @staticmethod
    def song_convert(odict: ParseMap) -> Song:
        quoted_url = odict.get(Index.SONG_URL, '')
        dl_link = urllib.parse.unquote(quoted_url)
        return Song(
            name=str(odict.get(Index.SONG_TITLE, 'unknown')),
            author=str(odict.get(Index.SONG_AUTHOR, 'unknown')),
            id=odict.get(Index.SONG_ID, 0),
            size=float(odict.get(Index.SONG_SIZE, 0)),
            links={
                'normal': Route.NEWGROUNDS_SONG_LISTEN + str(odict.get(Index.SONG_ID, 0)),
                'download': dl_link
            },
            custom=True,
        )

    @staticmethod
    def song_from_kwargs(**kwargs) -> Song:
        return Song(**kwargs)

    @staticmethod
    def user_stats_convert(odict: ParseMap, client: Client = None) -> UserStats:
        return UserStats(
            account_id=odict.get(Index.USER_ACCOUNT_ID, 0),
            name=str(odict.get(Index.USER_NAME, 'unknown')),
            id=odict.get(Index.USER_PLAYER_ID, 0),
            stars=odict.get(Index.USER_STARS, 0),
            demons=odict.get(Index.USER_DEMONS, 0),
            cp=odict.get(Index.USER_CREATOR_POINTS, 0),
            diamonds=odict.get(Index.USER_DIAMONDS, 0),
            coins=odict.get(Index.USER_COINS, 0),
            secret_coins=odict.get(Index.USER_SECRET_COINS, 0),
            lb_place=odict.get(Index.USER_TOP_PLACE, 0), client=client
        )

    @staticmethod
    def user_convert(odict: ParseMap, client: Client = None) -> User:
        youtube = str(odict.get(Index.USER_YOUTUBE))
        yt = {
            'normal': youtube,
            'link': 'https://www.youtube.com/channel/' + youtube
        }
        twitter = str(odict.get(Index.USER_TWITTER))
        twt = {
            'normal': twitter,
            'link': 'https://twitter.com/' + twitter
        }
        twitch = str(odict.get(Index.USER_TWITCH))
        twch = {
            'normal': twitch,
            'link': 'https://twitch.tv/' + twitch
        }

        return User(
            name=str(odict.get(Index.USER_NAME, 'unknown')), id=odict.get(Index.USER_PLAYER_ID, 0),
            stars=odict.get(Index.USER_STARS, 0), demons=odict.get(Index.USER_DEMONS, 0),
            secret_coins=odict.get(Index.USER_SECRET_COINS, 0), coins=odict.get(Index.USER_COINS, 0),
            cp=odict.get(Index.USER_CREATOR_POINTS, 0), diamonds=odict.get(Index.USER_DIAMONDS, 0),
            role=odict.get(Index.USER_ROLE, 0), global_rank=(odict.get(Index.USER_GLOBAL_RANK) or None),
            account_id=odict.get(Index.USER_ACCOUNT_ID, 0), youtube=yt, twitter=twt, twitch=twch,
            messages=odict.get(Index.USER_PRIVATE_MESSAGE_POLICY, 0),
            friend_requests=odict.get(Index.USER_FRIEND_REQUEST_POLICY, 0),
            comments=odict.get(Index.USER_COMMENT_HISTORY_POLICY, 0),
            icon_setup=IconSet(
                main_icon=odict.get(Index.USER_ICON, 1),
                color_1=colors[odict.get(Index.USER_COLOR_1, 0)],
                color_2=colors[odict.get(Index.USER_COLOR_2, 0)],
                main_icon_type=odict.get(Index.USER_ICON_TYPE, 0),
                has_glow_outline=bool(odict.get(Index.USER_GLOW_OUTLINE_2)),
                icon_cube=odict.get(Index.USER_ICON_CUBE, 1),
                icon_ship=odict.get(Index.USER_ICON_SHIP, 1),
                icon_ball=odict.get(Index.USER_ICON_BALL, 1),
                icon_ufo=odict.get(Index.USER_ICON_UFO, 1),
                icon_wave=odict.get(Index.USER_ICON_WAVE, 1),
                icon_robot=odict.get(Index.USER_ICON_ROBOT, 1),
                icon_spider=odict.get(Index.USER_ICON_SPIDER, 1),
                icon_explosion=odict.get(Index.USER_EXPLOSION, 1),
            ).attach_client(client),
            client=client
        )

    @staticmethod
    def level_convert(
        odict: ParseMap, song: Song, creator: AbstractUser, client: Client = None
    ) -> Level:
        string = odict.get(Index.LEVEL_PASS)

        if string is None:
            copyable, password = False, None
        else:
            try:
                # decode password
                password = Coder.decode(type='levelpass', string=string)
            except Exception:
                # failed to get password
                copyable, password = False, None
            else:
                copyable = True

                if not password:
                    password = None

                else:
                    password = password[1:]

                    if password.isdigit():
                        password = int(password)

                    else:
                        password = None

        desc = b64.urlsafe_b64decode(
            odict.get(Index.LEVEL_DESCRIPTION, '')
        ).decode(errors='replace')

        data = odict.get(Index.LEVEL_DATA, '')
        try:
            leveldata = Coder.unzip(data)
        except Exception:  # conversion failed
            leveldata = data

        diff = odict.get(Index.LEVEL_DIFFICULTY, 0)
        demon_diff = odict.get(Index.LEVEL_DEMON_DIFFICULTY, 0)
        is_demon = bool(odict.get(Index.LEVEL_IS_DEMON))
        is_auto = bool(odict.get(Index.LEVEL_IS_AUTO))
        difficulty = Converter.convert_level_difficulty(
            diff=diff, demon_diff=demon_diff, is_demon=is_demon, is_auto=is_auto)

        return Level(
            id=odict.get(Index.LEVEL_ID, 0),
            name=str(odict.get(Index.LEVEL_NAME, 'unknown')),
            description=desc,
            version=odict.get(Index.LEVEL_VERSION, 0),
            creator=creator,
            song=song,
            data=leveldata,
            password=password,
            copyable=copyable,
            is_demon=is_demon,
            is_auto=is_auto,
            difficulty=difficulty,
            stars=odict.get(Index.LEVEL_STARS, 0),
            coins=odict.get(Index.LEVEL_COIN_COUNT, 0),
            verified_coins=bool(odict.get(Index.LEVEL_COIN_VERIFIED)),
            is_epic=bool(odict.get(Index.LEVEL_IS_EPIC)),
            original=odict.get(Index.LEVEL_ORIGINAL, 0),
            downloads=odict.get(Index.LEVEL_DOWNLOADS, 0),
            rating=odict.get(Index.LEVEL_LIKES, 0),
            score=odict.get(Index.LEVEL_FEATURED_SCORE, 0),
            uploaded_timestamp=str(odict.get(Index.LEVEL_UPLOADED_TIMESTAMP, 'unknown')),
            last_updated_timestamp=str(odict.get(Index.LEVEL_LAST_UPDATED_TIMESTAMP, 'unknown')),
            length=odict.get(Index.LEVEL_LENGTH, 0),
            game_version=odict.get(Index.LEVEL_GAME_VERSION, 0),
            stars_requested=odict.get(Index.LEVEL_REQUESTED_STARS, 0),
            object_count=odict.get(Index.LEVEL_OBJECT_COUNT, 0),
            type=odict.get(Index.LEVEL_TIMELY_TYPE, 0),
            time_n=odict.get(Index.LEVEL_TIMELY_INDEX, -1),
            cooldown=odict.get(Index.LEVEL_TIMELY_COOLDOWN, -1),
            client=client
        )

    @staticmethod
    def map_pack_convert(odict: ParseMap, client: Client = None) -> MapPack:
        level_id_string = odict.get(Index.MAP_PACK_LEVEL_IDS, '0,0,0')
        level_ids = tuple(map(int, level_id_string.split(',')))

        color_string = odict.get(Index.MAP_PACK_COLOR, '255,255,255')
        color = Color.from_rgb(*map(int, color_string.split(',')))

        difficulty = Converter.value_to_pack_difficulty(odict.get(Index.MAP_PACK_DIFFICULTY, 0))

        return MapPack(
            id=odict.get(Index.MAP_PACK_ID, 0),
            name=str(odict.get(Index.MAP_PACK_NAME, 'unknown')),
            level_ids=level_ids,
            stars=odict.get(Index.MAP_PACK_STARS, 0),
            coins=odict.get(Index.MAP_PACK_COINS, 0),
            difficulty=difficulty,
            color=color,
            client=client
        )

    @staticmethod
    def gauntlet_convert(odict, client=None):
        level_id_string = odict.get(Index.GAUNTLET_LEVEL_IDS, '0,0,0,0,0')
        level_ids = tuple(map(int, level_id_string.split(',')))

        gid = odict.get(Index.GAUNTLET_ID, 0)
        name = Converter.get_gauntlet_name(gid)

        return Gauntlet(id=gid, name=name, level_ids=level_ids, client=client)

    @staticmethod
    def message_convert(odict: ParseMap, odict_2: ParseMap, client: Client = None) -> Message:
        useful_dict = {
            'name': odict.get(Index.MESSAGE_SENDER_NAME, 'unknown'),
            'id': odict.get(Index.MESSAGE_SENDER_ID, 0),
            'account_id': odict.get(Index.MESSAGE_SENDER_ACCOUNT_ID, 0)
        }
        user_1, user_2 = (
            ClassConverter.abstractuser_convert(elem, client) for elem in (useful_dict, odict_2)
        )

        indicator = odict.get(Index.MESSAGE_INDICATOR, 0)
        is_normal = indicator ^ 1

        subject = b64.urlsafe_b64decode(odict.get(Index.MESSAGE_SUBJECT, '')).decode()

        return Message(
            id=odict.get(Index.MESSAGE_ID, 0),
            timestamp=str(odict.get(Index.MESSAGE_TIMESTAMP, 'unknown')),
            subject=subject,
            is_read=bool(odict.get(Index.MESSAGE_IS_READ)),
            author=(user_1 if is_normal else user_2),
            recipient=(user_2 if is_normal else user_1),
            type=indicator,
            client=client
        )

    @staticmethod
    def request_convert(odict: ParseMap, odict_2: ParseMap, client: Client = None) -> FriendRequest:
        useful_dict = {
            'name': odict.get(Index.REQUEST_SENDER_NAME, 'unknown'),
            'id': odict.get(Index.REQUEST_SENDER_ID, 0),
            'account_id': odict.get(Index.REQUEST_SENDER_ACCOUNT_ID, 0)
        }

        user_1, user_2 = (
            ClassConverter.abstractuser_convert(elem, client) for elem in (useful_dict, odict_2)
        )

        indicator = odict.get(Index.REQUEST_INDICATOR, 0)
        is_normal = indicator ^ 1

        return FriendRequest(
            id=odict.get(Index.REQUEST_ID, 0),
            timestamp=str(odict.get(Index.REQUEST_TIMESTAMP, 'unknown')),
            body=b64.urlsafe_b64decode(odict.get(Index.REQUEST_BODY, '')).decode(),
            is_read=bool(bool(odict.get(Index.REQUEST_STATUS)) ^ 1),
            author=(user_1 if is_normal else user_2),
            recipient=(user_2 if is_normal else user_1),
            type=indicator,
            client=client
        )

    @staticmethod
    def comment_convert(odict: ParseMap, odict_2: ParseMap, client: Client = None) -> Comment:
        color_string = odict.get(Index.COMMENT_COLOR, '255,255,255')
        color = Color.from_rgb(*map(int, color_string.split(',')))

        return Comment(
            body=b64.urlsafe_b64decode(odict.get(Index.COMMENT_BODY, '')).decode(),
            rating=odict.get(Index.COMMENT_RATING, 0),
            timestamp=str(odict.get(Index.COMMENT_TIMESTAMP, 'unknown')),
            id=odict.get(Index.COMMENT_ID, 0),
            is_spam=bool(odict.get(Index.COMMENT_IS_SPAM, 0)),
            type=odict.get(Index.COMMENT_TYPE, 0),
            color=color,
            level_id=odict.get(Index.COMMENT_LEVEL_ID, 0),
            level_percentage=odict.get(Index.COMMENT_LEVEL_PERCENTAGE, -1),
            author=ClassConverter.abstractuser_convert(odict_2, client),
            client=client
        )

    @staticmethod
    def level_record_convert(
        odict: ParseMap, strategy: LeaderboardStrategy,
        client: Client = None
    ) -> LevelRecord:
        return LevelRecord(
            account_id=odict.get(Index.USER_ACCOUNT_ID, 0),
            name=str(odict.get(Index.USER_NAME, '')),
            id=odict.get(Index.USER_PLAYER_ID, 0),
            level_id=odict.get(Index.USER_LEVEL_ID, 0),
            lb_place=odict.get(Index.USER_TOP_PLACE, 0),
            percentage=odict.get(Index.USER_PERCENT, 0),
            coins=odict.get(Index.USER_SECRET_COINS, 0),
            timestamp=str(odict.get(Index.USER_RECORD_TIMESTAMP, 'unknown')),
            type=strategy,
            client=client
        )

    @staticmethod
    def abstractuser_convert(from_dict: Dict[str, str], client: Client = None) -> AbstractUser:
        from_dict = {k: _convert(v, int) for k, v in from_dict.items()}
        return AbstractUser(**from_dict).attach_client(client)


def _convert(obj: Any, cls: Type[Any]) -> Any:
    try:
        return cls(obj)
    except Exception:
        return obj
