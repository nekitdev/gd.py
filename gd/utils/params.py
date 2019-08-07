import base64
import random

from .mapper import mapper_util
from .crypto.coders import Coder

class Parameters:
    """Class that allows step-by-step parameter creation.
    Used in almost all HTTP Requests.

    A common usage of this class looks like that:

    .. code-block:: python3

        parameters = (
            Parameters().create_new()
            .put_definer('song', str(...))
            .finish()
        )
        await http.request(..., parameters)

        ...

    Attributes
    ----------
    gameVersion: :class:`str`
        Current game version.
    binaryVersion: :class:`str`
        Current binary version.
    secret: :class:`str`
        Secret used in requests.
    login_secret: :class:`str`
        Secret used in login requests.
    dict: :class:`dict`
        Dictionary where parameters are stored.
    """

    def __init__(self):
        self.gameVersion = '21'
        self.binaryVersion = '35'
        self.secret = 'Wmfd2893gb7'
        self.login_secret = 'Wmfv3899gc9'
        self.dict = {}

    def create_new(self, type0: str = None):
        """Start forming a new dictionary.

        Parameters
        ----------
        type0: :class:`str`
            Type of start, use `'web'` to start with an empty dictionary.
            When omitted or ``None``, adds *gameVersion*, *binaryVersion*
            and *gdw* to a dict.

        Returns
        -------
        :class:`.Parameters`
            ``self``
        """
        if type0 is None:
            self.dict = {
                'gameVersion': self.gameVersion,
                'binaryVersion': self.binaryVersion,
                'gdw': '0'
            }
        if type0 == 'web':
            self.dict = {}
        return self
    
    def finish(self):
        """Finishes creating parameters dictionary, and adds *secret* parameter.

        Returns
        -------
        :class:`dict`
            Fully formatted dictionary.
        """
        self.dict['secret'] = self.secret
        return self.dict
    
    def finish_login(self):
        """Same as `.Parameters.finish`, but adds ``login_secret`` instead.

        Returns
        -------
        :class:`dict`
            Fully formatted dictionary.
        """
        self.dict['secret'] = self.login_secret
        return self.dict
    
    def close(self):
        """Finishes creating parameters dictionary, without adding anything.

        Returns
        -------
        :class:`dict`
            Fully formatted parameters dictionary.
        """
        return self.dict
    
    def put_for_management(self, login: str, password: str, code: str):
        """Puts parameters for account management.

        Parameters
        ----------
        login: :class:`str`
            A username of an account.
        password: :class:`str`
            A password of an account.
        code: :class:`str`
            A solved RobTop's Captcha code.

        Returns
        -------
        :class:`.Parameters`
            ``self``
        """
        to_put = {
            'username': login,
            'password': password,
            'vercode': code,
            'cmdlogin': 'Login'
        }
        self.dict.update(to_put)
        return self
    
    def put_for_username(self, name: str, newname: str):
        """Adds parameters for username management.

        Parameters
        ----------
        name: :class:`str`
            An old username of an account.
        newname: :class:`str`
            A new username of an account.

        Returns
        -------
        :class:`.Parameters`
            ``self``
        """
        to_put = {
            'username': name,
            'newusername': newname,
            'changeusername': 'Change Username'
        }
        self.dict.update(to_put)
        return self
    
    def put_for_password(self, name: str, password: str, newpass: str):
        """Puts parameters for password management.

        Parameters
        ----------
        name: :class:`str`
            A username of an account.
        password: :class:`str`
            An old password of an account.
        newpass: :class:`str`
            A new password of an account.

        Returns
        -------
        :class:`.Parameters`
            ``self``
        """
        to_put = {
            'username': name,
            'oldpassword': password,
            'password': newpass,
            'password2': newpass,
            'change': 'Change Password'
        }
        self.dict.update(to_put)
        return self        

    def put_definer(self, for_what: str, item: str):
        """Puts a definer.

        Parameters
        ----------
        for_what: :class:`str`
            Type of parameter to add, represented as string.

            Follows this mapping:

            .. code-block:: python3

                'song'      -> 'songID'
                'user'      -> 'targetAccountID'
                'search'    -> 'str'
                'leveldata' -> 'levelID'
                'accountid' -> 'accountID'
                'messageid' -> 'messageID'
                'commentid' -> 'commentID'
                'requestid' -> 'requestID'
                'userid'    -> 'userID'

        item: :class:`str`
            Parameter to put.

        Returns
        -------
        :class:`.Parameters`
            ``self``
        """
        for_what = for_what.lower()
        params_dict = {
            'song': 'songID',
            'user': 'targetAccountID',
            'search': 'str',
            'leveldata': 'levelID',
            'accountid': 'accountID',
            'messageid': 'messageID',
            'commentid': 'commentID',
            'requestid': 'requestID',
            'userid': 'userID'
        }
        try:
            self.dict[params_dict[for_what]] = item
        except KeyError:
            pass
        return self
    
    def put_recipient(self, account_id: str):
        """Puts recipient of a message/friend request/...

        Parameters
        ----------
        account_id: :class:`str`
            An account ID of the recipient.

        Returns
        -------
        :class:`.Parameters`
            ``self``
        """
        self.dict['toAccountID'] = account_id
        return self
        
    def put_is_sender(self, t: str):
        """Puts `'isSender'` parameter.

        Parameters
        ----------
        t: :class:`str`
            Either ``'normal'`` or ``'sent'``.
            If ``'sent'``, adds ``isSender=1``.

        Returns
        -------
        :class:`.Parameters`
            ``self``
        """
        if t == 'normal':
            pass
        if t == 'sent':
            self.dict['isSender'] = '1'
        return self
    
    def put_message(self, subject: str, body: str):
        """Puts message's subject and body.

        Parameters
        ----------
        subject: :class:`str`
            NOT ENCODED message subject.
        body: :class:`str`
            NOT ENCODED message body.

        Returns
        -------
        :class:`.Parameters`
            ``self``
        """
        self.dict['subject'] = base64.b64encode(subject.encode()).decode()
        self.dict['body'] = mapper_util.prepare_sending(Coder.encode(type='message', string=body))
        return self

    def put_password(self, item: str):
        """Self explanatory. Puts `'gjp'` parameter.

        Parameters
        ----------
        item: :class:`str`
            A password to put.

        Returns
        -------
        :class:`.Parameters`
            ``self``
        """
        self.dict['gjp'] = item
        return self
    
    def put_username(self, item: str):
        """Self explanatory. Puts `'userName'` parameter.

        Parameters
        ----------
        item: :class:`str`
            A username to put.

        Returns
        -------
        :class:`.Parameters`
            ``self``
        """
        self.dict['userName'] = item
        return self
        
    def put_type(self, number: int):
        """Sets `'type'` parameter to a given number.

        Parameters
        ----------
        number: :class:`int`
            A number to set type to.

        Returns
        -------
        :class:`.Parameters`
            ``self``
        """
        self.dict['type'] = str(number)
        return self
    
    def put_page(self, number: int = 0):
        """Same as `.Parameters.put_type`, but for `'page'`."""
        self.dict['page'] = str(number)
        return self

    def put_weekly(self, number: int):
        """Same as `.Parameters.put_type`, but for `'weekly'`."""
        self.dict['weekly'] = str(number)
        return self

    def put_total(self, number: int):
        """Same as `.Parameters.put_type`, but for `'total'`."""
        self.dict['total'] = str(number)
        return self
    
    def put_mode(self, number: int):
        """Same as `.Parameters.put_type`, but for `'mode'`."""
        self.dict['mode'] = str(number)
        return self

    def put_comment(self, content: str, values: list):
        """Puts a comment.

        Parameters
        ----------
        content: :class:`str`
            The content of the comment.
        values: :class:`list`
            A list of values to generate a ``chk`` parameter with.

        Returns
        -------
        :class:`.Parameters`
            ``self``
        """
        comment = mapper_util.prepare_sending(base64.b64encode(content.encode()).decode())
        self.dict['comment'] = comment
        values.insert(1, comment)
        self.dict['chk'] = Coder.gen_chk(type='comment', values=values)
        return self
    
    def comment_for(self, type0: str, number: int = None):
        """Defines type of a comment, and puts parameters required for it.

        Parameters
        ----------
        type0: :class:`str`
            A type of the comment, either ``'client'`` or ``'level'``.
            ``'client'`` sets ``cType=1``, while ``'level'`` sets ``levelID=str(number)``.
        number: :class:`int`
            A number to put. Used as mentioned above.

        Returns
        -------
        :class:`.Parameters`
            ``self``
        """
        if type0 in ('client', 'level'):
            if (type0 == 'client'):
                self.dict['cType'] = '1'
            else:
                self.dict['levelID'] = str(number)
        return self
        
    def put_login_definer(self, username: str, password: str):
        """Puts parameters for a login request.

        Parameters
        ----------
        username: :class:`str`
            Runs :meth:`.Parameters.put_username` with it.
        password: :class:`str`
            Adds this as a `'password'` parameter.

        Returns
        -------
        :class:`.Parameters`
            ``self``
        """
        del self.dict['gdw'] # it is not needed in login request
        self.dict['udid'] = f'[{random.randint(100000, 999999)}][gd.py]' # for fun
        self.dict['password'] = password
        self.put_username(username)
        return self

    def put_profile_upd(
        self, msg: int, friend_req: int, comments: int,
        youtube: str, twitter: str, twitch: str
    ):
        """Puts all parameters required for profile update.

        Parameters
        ----------
        msg: :class:`int`
            Message indicator. Mapped in as `'mS'`.
        friend_req: :class:`int`
            Friend request indicator. Mapped in as `'frS'`.
        msg: :class:`int`
            Comment history indicator. Mapped in as `'cS'`.
        youtube: :class:`str`
            Youtube username. Mapped in as `'yt'`.
        twitter: :class:`str`
            Twitter username. Mapped in as `'twitter'`.
        twitch: :class:`str`
            Twitch username. Mapped in as `'twitch'`.

        Returns
        -------
        :class:`.Parameters`
            ``self``
        """
        to_put = {
            'mS': str(msg), 'frS': str(friend_req), 'cS': str(comments),
            'yt': youtube, 'twitter': twitter, 'twitch': twitch
        }
        self.dict.update(to_put)
        return self

    def put_for_level(self, filters: dict = None):
        """Appends level filters.

        Parameters
        ----------
        filters: :class:`dict`
            All filters as a dictionary.

        Returns
        -------
        :class:`.Parameters`
            ``self``
        """
        is_none = (filters is None)
        if not is_none:
            get = filters.get
        to_put = { #all filters will be passed through 'filters.py' formatter
            'len': '-' if is_none else get('length'),
            'type': '0' if is_none else get('type'),
            'diff': '-' if is_none else get('difficulty'),
            'featured': '0' if is_none else get('featured'),
            'original': '0' if is_none else get('original'),
            'twoPlayer': '0' if is_none else get('twoPlayer'),
            'coins': '0' if is_none else get('coins'),
            'star': '0' if is_none else get('starred')
        }
        if not is_none:
            if filters['noStar']:
                to_put['noStar'] = '1'
            if ('song' in filters.keys()):
                to_put['song'] = filters['song']
                to_put['customSong'] = filters['customSong']
            if ('demonFilter' in filters.keys()):
                to_put['demonFilter'] = filters['demonFilter']
        self.dict.update(to_put)
        return self
    
    def get_sent(self, indicator: int):
        if (indicator == 1):
            self.dict['getSent'] = '1'
        else:
            pass
        return self
