import base64 as b64

from .song import Song
from .user import User
from .comment import Comment
from .abstractuser import AbstractUser
from .level import Level
from .message import Message
from .iconset import IconSet
from .friend_request import FriendRequest

from .graphics.colors import colors

from .utils.converter import Converter
from .utils.indexer import Index as i
from .utils.crypto.coders import Coder
from .utils.mapper import mapper_util
from .utils.enums import (
    MessagePolicyType, FriendRequestPolicyType, 
    CommentPolicyType, StatusLevel,
    LevelLength, TimelyType, IconType
)

class ClassConverter:

    def song_convert(s):
        dl_link = (s[i.SONG_URL]).replace('%3A', ':').replace('%2F', '/')
        return Song(
            name = s[i.SONG_TITLE],
            author = s[i.SONG_AUTHOR],
            id = s[i.SONG_ID],
            size = float(s[i.SONG_SIZE]),
            links = (
                f'https://www.newgrounds.com/audio/listen/{s[i.SONG_ID]}',
                dl_link
            ),
            custom = True
        )

    def song_from_kwargs(**kwargs):
        return Song(**kwargs)
        
    def user_convert(s):
        dm = MessagePolicyType(s[i.USER_PRIVATE_MESSAGE_POLICY])
        fr_rq = FriendRequestPolicyType(s[i.USER_FRIEND_REQUEST_POLICY])
        comment = CommentPolicyType(s[i.USER_COMMENT_HISTORY_POLICY])

        stat = StatusLevel(s[i.USER_ROLE])
        rnk = s[i.USER_GLOBAL_RANK]
        rank = rnk if rnk else None

        youtube = s[i.USER_YOUTUBE]
        yt = (youtube, f'https://www.youtube.com/channel/{youtube}') if youtube else (None, None)

        twitter = s[i.USER_TWITTER]
        twt = (twitter, f'https://twitter.com/{twitter}') if twitter else (None, None)

        twitch = s[i.USER_TWITCH]
        twch = (twitch, f'https://twitch.tv/{twitch}') if twitch else (None, None)

        return User(
            name = s[i.USER_NAME], id = s[i.USER_PLAYER_ID],
            stars = s[i.USER_STARS], demons = s[i.USER_DEMONS],
            secret_coins = s[i.USER_SECRET_COINS], user_coins = s[i.USER_USER_COINS],
            cp = s[i.USER_CREATOR_POINTS], diamonds = s[i.USER_DIAMONDS],
            role = stat, global_rank = rank,
            account_id = s[i.USER_ACCOUNT_ID], youtube = yt, 
            twitter = twt, twitch = twch,
            messages = dm, friend_requests = fr_rq, comments = comment,
            icon_setup = IconSet(
                main_icon = s[i.USER_ICON],
                color_1 = colors[s[i.USER_COLOR_1]],
                color_2 = colors[s[i.USER_COLOR_2]],
                main_icon_type = IconType(s[i.USER_ICON_TYPE]),
                has_glow_outline = bool(s[i.USER_GLOW_OUTLINE]^1),
                icon_cube = s[i.USER_ICON_CUBE],
                icon_ship = s[i.USER_ICON_SHIP],
                icon_ball = s[i.USER_ICON_BALL],
                icon_ufo = s[i.USER_ICON_UFO],
                icon_wave = s[i.USER_ICON_WAVE],
                icon_robot = s[i.USER_ICON_ROBOT], 
                icon_spider = s[i.USER_ICON_SPIDER]
            )
        )

    # ok style
    def level_convert(s, song, creator):
        try:  # decode password
            password = Coder.decode(type='levelpass', string=s[i.LEVEL_PASS])
        except TypeError:
            password = None
        if password == '1':
            password = ''

        desc = b64.b64decode(s[i.LEVEL_DESCRIPTION]).decode()
        length = LevelLength(s[i.LEVEL_LENGTH])
        typeof = TimelyType(s[i.LEVEL_TIMELY_TYPE])
        game_version = s[i.LEVEL_GAME_VERSION]  # needs to be converted to represent real version.
        leveldata = Coder.unzip(s[i.LEVEL_DATA])

        diff = s[i.LEVEL_DIFFICULTY]
        demon_diff = s[i.LEVEL_DEMON_DIFFICULTY]
        is_demon = bool(s[i.LEVEL_IS_DEMON])
        is_auto = bool(s[i.LEVEL_IS_AUTO])
        difficulty = Converter.convert_level_difficulty(
            diff=diff, demon_diff=demon_diff, is_demon=is_demon, is_auto=is_auto)

        return Level(
            id = s[i.LEVEL_ID],
            name = s[i.LEVEL_NAME],
            description = desc,
            version = s[i.LEVEL_VERSION],
            creator = creator,
            song = song,
            data = leveldata,
            is_demon = is_demon,
            is_auto = is_auto,
            difficulty = difficulty,
            stars = s[i.LEVEL_STARS],
            coins = s[i.LEVEL_COIN_COUNT],
            verified_coins = bool(s[i.LEVEL_COIN_VERIFIED]),
            is_epic = bool(s[i.LEVEL_IS_EPIC]),
            original = s[i.LEVEL_ORIGINAL],
            downloads = s[i.LEVEL_DOWNLOADS],
            likes = s[i.LEVEL_LIKES],
            score = s[i.LEVEL_FEATURED_SCORE],
            uploaded_timestamp = s[i.LEVEL_UPLOADED_TIMESTAMP],
            last_updated_timestamp = s[i.LEVEL_LAST_UPDATED_TIMESTAMP],
            length = length,
            game_version = game_version,
            stars_requested = s[i.LEVEL_REQUESTED_STARS],
            object_count = s[i.LEVEL_OBJECT_COUNT],
            typeof = typeof,
            time_n = s[i.LEVEL_TIMELY_INDEX],
            cooldown = s[i.LEVEL_TIMELY_COOLDOWN]
        )
        
    
    def message_convert(s, s_2):
        cases = {0: 'normal', 1: 'sent'}
        type_of = cases.get(s[i.MESSAGE_INDICATOR])
        useful_dict = {
            'name': s[i.MESSAGE_SENDER_NAME],
            'id': s[i.MESSAGE_SENDER_ID],
            'account_id': s[i.MESSAGE_SENDER_ACCOUNT_ID]
        }
        user_1, user_2 = [
            ClassConverter.abstractuser_convert(elem) for elem in (useful_dict, s_2)
        ]
        is_normal = (type_of == 'normal')

        subject = b64.b64decode(mapper_util.normalize(s[i.MESSAGE_SUBJECT])).decode()
        return Message(
            id = s[i.MESSAGE_ID],
            timestamp = s[i.MESSAGE_TIMESTAMP],
            subject = subject,
            is_read = bool(s[i.MESSAGE_IS_READ]),
            author = user_1 if is_normal else user_2,
            recipient = user_2 if is_normal else user_1,
            type = type_of
        )

    def request_convert(s, s_2):
        cases = {0: 'normal', 1: 'sent'}
        type_of = cases.get(s[i.REQUEST_INDICATOR])
        useful_dict = {
            'name': s[i.REQUEST_SENDER_NAME],
            'id': s[i.REQUEST_SENDER_ID],
            'account_id': s[i.REQUEST_SENDER_ACCOUNT_ID]
        }
        user_1, user_2 = [ClassConverter.abstractuser_convert(elem) for elem in [useful_dict, s_2]]
        return FriendRequest(
            id = s[i.REQUEST_ID],
            timestamp = s[i.REQUEST_TIMESTAMP],
            body = b64.b64decode(mapper_util.normalize(s[i.REQUEST_BODY])).decode(),
            is_read = False if (s[i.REQUEST_STATUS] is '1') else True,
            author = user_1 if (type_of is 'normal') else user_2,
            recipient = user_2 if (type_of is 'normal') else user_1,
            type = type_of
        )
    
    def comment_convert(s, s_2):
        cases = {0: 'level', 1: 'client'}
        typeof = cases.get(s[i.COMMENT_TYPE])
        return Comment(
            body = b64.b64decode(mapper_util.normalize(s[i.COMMENT_BODY])).decode(),
            rating = s[i.COMMENT_RATING],
            timestamp = s[i.COMMENT_TIMESTAMP],
            id = s[i.COMMENT_ID],
            type = typeof,
            level_id = s.get(i.COMMENT_LEVEL_ID, 0),
            level_percentage = s.get(i.COMMENT_LEVEL_PERCENTAGE, -1),
            author = ClassConverter.abstractuser_convert(s_2),
            page = s[i.COMMENT_PAGE]
        )
    
    def abstractuser_convert(d):
        return AbstractUser(
            **{k: (v if k == 'name' else int(v)) for k, v in d.items()}
        )
