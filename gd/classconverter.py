from .utils.indexer import Index as i
from .song import Song
from .user import User
from .comment import Comment
from .authclient import AuthClient
from .utils.crypto.coders import Coder
import base64 as b64

class class_converter:

    def SongConvert(to_parse):
        s = to_parse #I feel more confident with shorter variables
        dl_link = (s[i.SONG_URL]).replace('%3A', ':').replace('%2F', '/')
        return Song(
            name = s[i.SONG_TITLE],
            author = s[i.SONG_AUTHOR],
            _id = int(s[i.SONG_ID]),
            size = float(s[i.SONG_SIZE]),
            size_mb = f'{s[i.SONG_SIZE]} MB',
            links = [
                f'https://www.newgrounds.com/audio/listen{s[i.SONG_ID]}',
                dl_link
            ]
        )
    def UserConvert(to_parse):
        s = to_parse #as I said, shorter variables are more comfortable
        pm_policy = s[i.USER_PRIVATE_MESSAGE_POLICY]
        pcmdict = {
            '0': 'Opened to all',
            '1': 'Opened to friends only',
            '2': 'Closed'
        }
        dm = pcmdict[pm_policy]
        friend_req_policy = s[i.USER_FRIEND_REQUEST_POLICY]
        friend_reqdict = {
            '0': 'Opened',
            '1': 'Closed'
        }
        fr_rq = friend_reqdict[friend_req_policy]
        youtube = s[i.USER_YOUTUBE]
        if youtube == '':
            yt = None
        if youtube != '':
            yt = f'https://www.youtube.com/channel/{youtube}' #TO DO: Check if it should be channel/id
        r = s[i.USER_ROLE]
        rdict = {
            '0': 'User',
            '1': 'Moderator',
            '2': 'Elder Moderator'
        }
        stat = rdict[r]
        rnk = s[i.USER_GLOBAL_RANK]
        if rnk == '': #check if it works like that
            rank = None
        if rnk != '':
            rank = int(rnk)
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
        comment = pcmdict[comment_policy]
        return User(
            name = s[i.USER_NAME], _id = int(s[i.USER_PLAYER_ID]),
            stars = int(s[i.USER_STARS]), demons = int(s[i.USER_DEMONS]),
            secret_coins = int(s[i.USER_SECRET_COINS]), user_coins = int(s[i.USER_USER_COINS]),
            cp = int(s[i.USER_CREATOR_POINTS]), diamonds = int(s[i.USER_DIAMONDS]),
            role = int(s[i.USER_ROLE]), status = stat, global_rank = rank,
            account_id = int(s[i.USER_ACCOUNT_ID]), youtube = yt, 
            twitter = [twt, twt_link], twitch = [twch, twch_link],
            messages = dm, friend_requests = fr_rq, comments = comment,
            icon_setup = {
                'icon': int(s[i.USER_ICON]),
                'color_1': int(s[i.USER_COLOR_1]),
                'color_2': int(s[i.USER_COLOR_2]),
                'icon_type': int(s[i.USER_ICON_TYPE]),
                'glow_outline': int(s[i.USER_GLOW_OUTLINE]),
                'glow_outline_2': int(s[i.USER_GLOW_OUTLINE_2]),
                'icon_cube': int(s[i.USER_ICON_CUBE]),
                'icon_ship': int(s[i.USER_ICON_SHIP]),
                'icon_ball': int(s[i.USER_ICON_BALL]),
                'icon_ufo': int(s[i.USER_ICON_UFO]),
                'icon_wave': int(s[i.USER_ICON_WAVE]),
                'icon_robot': int(s[i.USER_ICON_ROBOT]), 
                'icon_spider': int(s[i.USER_ICON_SPIDER]),
                'death_effect': int(s[i.USER_DEATH_EFFECT])
            }
        )
    
    def LevelConvert(to_parse):
        s = to_parse #mhm
        pass #I'll finish soon

    def AuthClientConvert(to_parse):
        s = to_parse
        return AuthClient(
            name = s['username'],
            password = s['password'],
            encodedpass = Coder().encode0(type='accountpass', string=s['password']),
            accountid = int(s['accountid']),
            userid = int(s['userid'])
        )
    
    def CommentConvert(to_parse, author):
        s = to_parse
        return Comment(
            body = b64.b64decode(s[i.COMMENT_BODY]).decode(),
            rating = int(s[i.COMMENT_RATING]),
            timestamp = s[i.COMMENT_TIMESTAMP],
            commentid = int(s[i.COMMENT_ID]),
            author = author
        )

#woop >.>
