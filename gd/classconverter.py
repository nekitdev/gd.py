import base64 as b64

from . import song
from . import user
from . import comment
from . import abstractuser
from . import level
from . import message
from . import iconset
from . import friend_request

from .graphics.colors import colors

from .utils.indexer import Index as i
from .utils.converter import Converter
from .utils.crypto.coders import Coder
from .utils.mapper import mapper_util
from .utils.types import (
    MessagePrivacyType, FriendRequestPrivacyType, 
    CommentPrivacyType, StatusLevelType
)

class ClassConverter:

    def song_convert(to_parse):
        s = to_parse #I feel more confident with shorter variables
        dl_link = (s[i.SONG_URL]).replace('%3A', ':').replace('%2F', '/')
        return song.Song(
            name = s[i.SONG_TITLE],
            author = s[i.SONG_AUTHOR],
            id = s[i.SONG_ID],
            size = float(s[i.SONG_SIZE]),
            size_mb = f'{s[i.SONG_SIZE]} MB',
            links = [
                f'https://www.newgrounds.com/audio/listen/{s[i.SONG_ID]}',
                dl_link
            ]
        )
        
    def user_convert(to_parse):
        s = to_parse #as I said, shorter variables are more comfortable
        pm_policy = s[i.USER_PRIVATE_MESSAGE_POLICY]
        dm = MessagePrivacyType(pm_policy)
        friend_req_policy = s[i.USER_FRIEND_REQUEST_POLICY]
        fr_rq = FriendRequestPrivacyType(friend_req_policy)
        youtube = s[i.USER_YOUTUBE]
        if youtube == '':
            yt = None
        if youtube != '':
            yt = f'https://www.youtube.com/channel/{youtube}'
        r = s[i.USER_ROLE]
        stat = StatusLevelType(r)
        rnk = s[i.USER_GLOBAL_RANK]
        if rnk == '': #check if it works like that
            rank = None
        if rnk != '':
            rank = rnk
        twitter = s[i.USER_TWITTER]
        if twitter == '':
            twt = None
            twt_link = None
        if twitter != '':
            twt = '@' + twitter
            twt_link = f'https://twitter.com/{twt}'
        twitch = s[i.USER_TWITCH]
        if twitch == '':
            twch = None
            twch_link = None
        if twitch != '':
            twch = twitch
            twch_link = f'https://twitch.tv/{twch}'
        comment_policy = s[i.USER_COMMENT_HISTORY_POLICY]
        comment = CommentPrivacyType(comment_policy)
        #redo a bit (for easier interaction, and not all elements are yet implemented)
        return user.User(
            name = s[i.USER_NAME], id = s[i.USER_PLAYER_ID],
            stars = s[i.USER_STARS], demons = s[i.USER_DEMONS],
            secret_coins = s[i.USER_SECRET_COINS], user_coins = s[i.USER_USER_COINS],
            cp = s[i.USER_CREATOR_POINTS], diamonds = s[i.USER_DIAMONDS],
            role = stat, global_rank = rank,
            account_id = s[i.USER_ACCOUNT_ID], youtube = yt, 
            twitter = [twt, twt_link], twitch = [twch, twch_link],
            messages = dm, friend_requests = fr_rq, comments = comment,
            icon_setup = iconset.IconSet(
                main_icon = s[i.USER_ICON],
                color_1 = colors[s[i.USER_COLOR_1]],
                color_2 = colors[s[i.USER_COLOR_2]],
                main_icon_type = s[i.USER_ICON_TYPE],
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
    
    def level_convert(to_parse):
        s = to_parse
        pass #I'll finish soon
    
    def message_convert(to_parse, to_parse_2):
        s = to_parse
        cases = {0: 'normal', 1: 'sent'}
        type_of = cases.get(s[i.MESSAGE_INDICATOR])
        useful_dict = {
            'name': s[i.MESSAGE_SENDER_NAME],
            'id': s[i.MESSAGE_SENDER_ID],
            'account_id': s[i.MESSAGE_SENDER_ACCOUNT_ID]
        }
        user_1, user_2 = [
            ClassConverter.abstractuser_convert(elem) for elem in (useful_dict, to_parse_2)
        ]
        return message.Message(
            id = s[i.MESSAGE_ID],
            timestamp = s[i.MESSAGE_TIMESTAMP],
            subject = b64.b64decode(mapper_util.normalize(s[i.MESSAGE_SUBJECT])).decode(),
            is_read = bool(s[i.MESSAGE_IS_READ]),
            author = user_1 if (type_of == 'normal') else user_2,
            recipient = user_2 if (type_of == 'normal') else user_1,
            type = type_of
        )

    def request_convert(to_parse, to_parse_2):
        s = to_parse
        cases = {0: 'normal', 1: 'sent'}
        type_of = cases.get(s[i.REQUEST_INDICATOR])
        useful_dict = {
            'name': s[i.REQUEST_SENDER_NAME],
            'id': s[i.REQUEST_SENDER_ID],
            'account_id': s[i.REQUEST_SENDER_ACCOUNT_ID]
        }
        user_1, user_2 = [ClassConverter.abstractuser_convert(elem) for elem in [useful_dict, to_parse_2]]
        return friend_request.FriendRequest(
            id = s[i.REQUEST_ID],
            timestamp = s[i.REQUEST_TIMESTAMP],
            body = b64.b64decode(mapper_util.normalize(s[i.REQUEST_BODY])).decode(),
            is_read = False if (s[i.REQUEST_STATUS] is '1') else True,
            author = user_1 if (type_of is 'normal') else user_2,
            recipient = user_2 if (type_of is 'normal') else user_1,
            type = type_of
        )
    
    def comment_convert(to_parse, to_parse_2):
        s = to_parse
        return comment.Comment(
            body = b64.b64decode(mapper_util.normalize(s[i.COMMENT_BODY])).decode(),
            rating = s[i.COMMENT_RATING],
            timestamp = s[i.COMMENT_TIMESTAMP],
            id = s[i.COMMENT_ID],
            type = s[i.COMMENT_TYPE],
            level_id = s.get(i.COMMENT_LEVEL_ID, 0),
            level_percentage = s.get(i.COMMENT_LEVEL_PERCENTAGE, -1),
            author = ClassConverter.abstractuser_convert(to_parse_2),
            page = s[i.COMMENT_PAGE]
        )
    
    def abstractuser_convert(to_parse):
        s = to_parse
        return abstractuser.AbstractUser(
            name = s['name'], id = s['id'], account_id = s['account_id']
        )

# TO_DO: refactor this to bring a nicer look
