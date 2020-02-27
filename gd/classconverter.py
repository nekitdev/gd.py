import urllib.parse

from .typing import Any, Client, Dict, Optional, Type

from .song import ArtistInfo, Song
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
from .utils.parser import ExtDict
from .utils.crypto.coders import Coder
from .utils.routes import Route


class ClassConverter:

    @staticmethod
    def artist_info_convert(odict: Dict[str, str], client: Optional[Client] = None) -> ArtistInfo:
        return ArtistInfo(**odict).attach_client(client)

    @staticmethod
    def song_convert(odict: ExtDict, client: Optional[Client] = None) -> Song:
        quoted_url = odict.get(Index.SONG_URL, '')
        dl_link = urllib.parse.unquote(quoted_url)
        return Song(
            name=odict.get(Index.SONG_TITLE, 'unknown'),
            author=odict.get(Index.SONG_AUTHOR, 'unknown'),
            id=odict.getcast(Index.SONG_ID, 0, int),
            size=odict.getcast(Index.SONG_SIZE, 0.0, float),
            links={
                'normal': Route.NEWGROUNDS_SONG_LISTEN + odict.get(Index.SONG_ID, ''),
                'download': dl_link
            },
            custom=True,
            client=client
        )

    @staticmethod
    def song_from_kwargs(**kwargs) -> Song:
        return Song(**kwargs)

    @staticmethod
    def user_stats_convert(odict: ExtDict, client: Optional[Client] = None) -> UserStats:
        return UserStats(
            account_id=odict.getcast(Index.USER_ACCOUNT_ID, 0, int),
            name=odict.get(Index.USER_NAME, 'unknown'),
            id=odict.getcast(Index.USER_PLAYER_ID, 0, int),
            stars=odict.getcast(Index.USER_STARS, 0, int),
            demons=odict.getcast(Index.USER_DEMONS, 0, int),
            cp=odict.getcast(Index.USER_CREATOR_POINTS, 0, int),
            diamonds=odict.getcast(Index.USER_DIAMONDS, 0, int),
            coins=odict.getcast(Index.USER_COINS, 0, int),
            secret_coins=odict.getcast(Index.USER_SECRET_COINS, 0, int),
            lb_place=odict.getcast(Index.USER_TOP_PLACE, 0, int), client=client
        )

    @staticmethod
    def user_convert(odict: ExtDict, client: Optional[Client] = None) -> User:
        youtube = odict.get(Index.USER_YOUTUBE, '')
        yt = {
            'normal': youtube,
            'link': 'https://www.youtube.com/channel/' + youtube
        }
        twitter = odict.get(Index.USER_TWITTER, '')
        twt = {
            'normal': twitter,
            'link': 'https://twitter.com/' + twitter
        }
        twitch = odict.get(Index.USER_TWITCH, '')
        twch = {
            'normal': twitch,
            'link': 'https://twitch.tv/' + twitch
        }

        return User(
            name=odict.get(Index.USER_NAME, 'unknown'), id=odict.getcast(Index.USER_PLAYER_ID, 0, int),
            stars=odict.getcast(Index.USER_STARS, 0, int), demons=odict.getcast(Index.USER_DEMONS, 0, int),
            secret_coins=odict.getcast(Index.USER_SECRET_COINS, 0, int), coins=odict.getcast(Index.USER_COINS, 0, int),
            cp=odict.getcast(Index.USER_CREATOR_POINTS, 0, int), diamonds=odict.getcast(Index.USER_DIAMONDS, 0, int),
            role=odict.getcast(Index.USER_ROLE, 0, int), global_rank=odict.getcast(Index.USER_GLOBAL_RANK, None, int),
            account_id=odict.getcast(Index.USER_ACCOUNT_ID, 0, int), youtube=yt, twitter=twt, twitch=twch,
            messages=odict.getcast(Index.USER_PRIVATE_MESSAGE_POLICY, 0, int),
            friend_requests=odict.getcast(Index.USER_FRIEND_REQUEST_POLICY, 0, int),
            comments=odict.getcast(Index.USER_COMMENT_HISTORY_POLICY, 0, int),
            icon_setup=IconSet(
                main_icon=odict.getcast(Index.USER_ICON, 1, int),
                color_1=colors[odict.getcast(Index.USER_COLOR_1, 0, int)],
                color_2=colors[odict.getcast(Index.USER_COLOR_2, 0, int)],
                main_icon_type=odict.getcast(Index.USER_ICON_TYPE, 0, int),
                has_glow_outline=bool(odict.getcast(Index.USER_GLOW_OUTLINE_2, 0, int)),
                icon_cube=odict.getcast(Index.USER_ICON_CUBE, 1, int),
                icon_ship=odict.getcast(Index.USER_ICON_SHIP, 1, int),
                icon_ball=odict.getcast(Index.USER_ICON_BALL, 1, int),
                icon_ufo=odict.getcast(Index.USER_ICON_UFO, 1, int),
                icon_wave=odict.getcast(Index.USER_ICON_WAVE, 1, int),
                icon_robot=odict.getcast(Index.USER_ICON_ROBOT, 1, int),
                icon_spider=odict.getcast(Index.USER_ICON_SPIDER, 1, int),
                icon_explosion=odict.getcast(Index.USER_EXPLOSION, 1, int),
            ).attach_client(client),
            client=client
        )

    @staticmethod
    def level_convert(
        odict: ExtDict, song: Song, creator: AbstractUser, client: Optional[Client] = None
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

        desc = Coder.do_base64(
            odict.get(Index.LEVEL_DESCRIPTION, ''),
            encode=False, errors='replace'
        )

        data = odict.get(Index.LEVEL_DATA, '')
        try:
            leveldata = Coder.unzip(data)
        except Exception:  # conversion failed
            leveldata = data

        diff = odict.getcast(Index.LEVEL_DIFFICULTY, 0, int)
        demon_diff = odict.getcast(Index.LEVEL_DEMON_DIFFICULTY, 0, int)
        is_demon = bool(odict.getcast(Index.LEVEL_IS_DEMON, 0, int))
        is_auto = bool(odict.getcast(Index.LEVEL_IS_AUTO, 0, int))
        difficulty = Converter.convert_level_difficulty(
            diff=diff, demon_diff=demon_diff, is_demon=is_demon, is_auto=is_auto)

        return Level(
            id=odict.getcast(Index.LEVEL_ID, 0, int),
            name=odict.get(Index.LEVEL_NAME, 'unknown'),
            description=desc,
            version=odict.getcast(Index.LEVEL_VERSION, 0, int),
            creator=creator,
            song=song,
            data=leveldata,
            password=password,
            copyable=copyable,
            is_demon=is_demon,
            is_auto=is_auto,
            difficulty=difficulty,
            stars=odict.getcast(Index.LEVEL_STARS, 0, int),
            coins=odict.getcast(Index.LEVEL_COIN_COUNT, 0, int),
            verified_coins=bool(odict.getcast(Index.LEVEL_COIN_VERIFIED, 0, int)),
            is_epic=bool(odict.getcast(Index.LEVEL_IS_EPIC, 0, int)),
            original=odict.getcast(Index.LEVEL_ORIGINAL, 0, int),
            downloads=odict.getcast(Index.LEVEL_DOWNLOADS, 0, int),
            rating=odict.getcast(Index.LEVEL_LIKES, 0, int),
            score=odict.getcast(Index.LEVEL_FEATURED_SCORE, 0, int),
            uploaded_timestamp=odict.get(Index.LEVEL_UPLOADED_TIMESTAMP, 'unknown'),
            last_updated_timestamp=odict.get(Index.LEVEL_LAST_UPDATED_TIMESTAMP, 'unknown'),
            length=odict.getcast(Index.LEVEL_LENGTH, 0, int),
            game_version=odict.getcast(Index.LEVEL_GAME_VERSION, 0, int),
            stars_requested=odict.getcast(Index.LEVEL_REQUESTED_STARS, 0, int),
            object_count=odict.getcast(Index.LEVEL_OBJECT_COUNT, 0, int),
            type=odict.getcast(Index.LEVEL_TIMELY_TYPE, 0, int),
            time_n=odict.getcast(Index.LEVEL_TIMELY_INDEX, -1, int),
            cooldown=odict.getcast(Index.LEVEL_TIMELY_COOLDOWN, -1, int),
            client=client
        )

    @staticmethod
    def map_pack_convert(odict: ExtDict, client: Optional[Client] = None) -> MapPack:
        level_id_string = odict.get(Index.MAP_PACK_LEVEL_IDS, '0,0,0')
        level_ids = tuple(map(int, level_id_string.split(',')))

        color_string = odict.get(Index.MAP_PACK_COLOR, '255,255,255')
        color = Color.from_rgb(*map(int, color_string.split(',')))

        difficulty = Converter.value_to_pack_difficulty(odict.getcast(Index.MAP_PACK_DIFFICULTY, 0, int))

        return MapPack(
            id=odict.getcast(Index.MAP_PACK_ID, 0, int),
            name=odict.get(Index.MAP_PACK_NAME, 'unknown'),
            level_ids=level_ids,
            stars=odict.getcast(Index.MAP_PACK_STARS, 0, int),
            coins=odict.getcast(Index.MAP_PACK_COINS, 0, int),
            difficulty=difficulty,
            color=color,
            client=client
        )

    @staticmethod
    def gauntlet_convert(odict: ExtDict, client: Optional[Client] = None) -> Gauntlet:
        level_id_string = odict.get(Index.GAUNTLET_LEVEL_IDS, '0,0,0,0,0')
        level_ids = tuple(map(int, level_id_string.split(',')))

        gid = odict.getcast(Index.GAUNTLET_ID, 0, int)
        name = Converter.get_gauntlet_name(gid)

        return Gauntlet(id=gid, name=name, level_ids=level_ids, client=client)

    @staticmethod
    def message_convert(odict: ExtDict, odict_2: ExtDict, client: Optional[Client] = None) -> Message:
        useful_dict = {
            'name': odict.get(Index.MESSAGE_SENDER_NAME, 'unknown'),
            'id': odict.getcast(Index.MESSAGE_SENDER_ID, 0, int),
            'account_id': odict.getcast(Index.MESSAGE_SENDER_ACCOUNT_ID, 0, int)
        }
        user_1, user_2 = (
            ClassConverter.abstractuser_convert(elem, client) for elem in (useful_dict, odict_2)
        )

        indicator = odict.getcast(Index.MESSAGE_INDICATOR, 0, int)
        is_normal = indicator ^ 1

        subject = Coder.do_base64(
            odict.get(Index.MESSAGE_SUBJECT, ''), encode=False, errors='replace'
        )

        return Message(
            id=odict.getcast(Index.MESSAGE_ID, 0, int),
            timestamp=odict.get(Index.MESSAGE_TIMESTAMP, 'unknown'),
            subject=subject,
            is_read=bool(odict.getcast(Index.MESSAGE_IS_READ, 0, int)),
            author=(user_1 if is_normal else user_2),
            recipient=(user_2 if is_normal else user_1),
            type=indicator,
            client=client
        )

    @staticmethod
    def request_convert(odict: ExtDict, odict_2: ExtDict, client: Optional[Client] = None) -> FriendRequest:
        useful_dict = {
            'name': odict.get(Index.REQUEST_SENDER_NAME, 'unknown'),
            'id': odict.getcast(Index.REQUEST_SENDER_ID, 0, int),
            'account_id': odict.getcast(Index.REQUEST_SENDER_ACCOUNT_ID, 0, int)
        }

        user_1, user_2 = (
            ClassConverter.abstractuser_convert(elem, client) for elem in (useful_dict, odict_2)
        )

        indicator = odict.getcast(Index.REQUEST_INDICATOR, 0, int)
        is_normal = indicator ^ 1

        return FriendRequest(
            id=odict.getcast(Index.REQUEST_ID, 0, int),
            timestamp=str(odict.get(Index.REQUEST_TIMESTAMP, 'unknown')),
            body=Coder.do_base64(
                odict.get(Index.REQUEST_BODY, ''), encode=False, errors='replace'
            ),
            is_read=bool(bool(odict.get(Index.REQUEST_STATUS)) ^ 1),
            author=(user_1 if is_normal else user_2),
            recipient=(user_2 if is_normal else user_1),
            type=indicator,
            client=client
        )

    @staticmethod
    def comment_convert(odict: ExtDict, odict_2: ExtDict, client: Optional[Client] = None) -> Comment:
        color_string = odict.get(Index.COMMENT_COLOR, '255,255,255')
        color = Color.from_rgb(*map(int, color_string.split(',')))

        return Comment(
            body=Coder.do_base64(
                odict.get(Index.COMMENT_BODY, ''), encode=False, errors='replace'
            ),
            rating=odict.getcast(Index.COMMENT_RATING, 0, int),
            timestamp=odict.get(Index.COMMENT_TIMESTAMP, 'unknown'),
            id=odict.getcast(Index.COMMENT_ID, 0, int),
            is_spam=bool(odict.getcast(Index.COMMENT_IS_SPAM, 0, int)),
            type=odict.getcast(Index.COMMENT_TYPE, 0, int),
            color=color,
            level_id=odict.getcast(Index.COMMENT_LEVEL_ID, 0, int),
            level_percentage=odict.getcast(Index.COMMENT_LEVEL_PERCENTAGE, -1, int),
            author=ClassConverter.abstractuser_convert(odict_2, client),
            client=client
        )

    @staticmethod
    def level_record_convert(
        odict: ExtDict, strategy: LeaderboardStrategy,
        client: Optional[Client] = None
    ) -> LevelRecord:
        return LevelRecord(
            account_id=odict.getcast(Index.USER_ACCOUNT_ID, 0, int),
            name=odict.get(Index.USER_NAME, 'unknown'),
            id=odict.getcast(Index.USER_PLAYER_ID, 0, int),
            level_id=odict.getcast(Index.USER_LEVEL_ID, 0, int),
            lb_place=odict.getcast(Index.USER_TOP_PLACE, 0, int),
            percentage=odict.getcast(Index.USER_PERCENT, 0, int),
            coins=odict.getcast(Index.USER_SECRET_COINS, 0, int),
            timestamp=odict.get(Index.USER_RECORD_TIMESTAMP, 'unknown'),
            type=strategy,
            client=client
        )

    @staticmethod
    def abstractuser_convert(from_dict: Dict[str, str], client: Optional[Client] = None) -> AbstractUser:
        from_dict = {k: _convert(v, int) for k, v in from_dict.items()}
        return AbstractUser(**from_dict).attach_client(client)


def _convert(obj: Any, cls: Type[Any]) -> Any:
    try:
        return cls(obj)
    except Exception:
        return obj
