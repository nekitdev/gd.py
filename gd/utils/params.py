import base64
import random

from typing import Union, Sequence

from .mapper import mapper_util
from .crypto.coders import Coder

__all__ = ('Parameters', 'enter_gdworld', 'leave_gdworld')


def enter_gdworld():
    Parameters.GDW = 1

def leave_gdworld():
    Parameters.GDW = 0


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
    level_secret: :class:`str`
        Secret used in level operations (e.g. :meth:`.Level.delete`)
    login_secret: :class:`str`
        Secret used in login requests.
    mod_secret: :class:`str`
        Secret used in moderator requests.
    dict: :class:`dict`
        Dictionary where parameters are stored.
    """
    GDW = 0

    def __init__(self):
        self.gameVersion = '21'
        self.binaryVersion = '35'
        self.secret = 'Wmfd2893gb7'
        self.level_secret = 'Wmfv2898gc9'
        self.login_secret = 'Wmfv3899gc9'
        self.mod_secret = 'Wmfp3879gc3'
        self.dict = {}

    def create_new(self, type: str = None):
        """Start forming a new dictionary.

        Parameters
        ----------
        type: :class:`str`
            Type of start, use `'web'` to start with an empty dictionary.
            When omitted or ``None``, adds *gameVersion*, *binaryVersion*
            and *gdw* to a dict.

        Returns
        -------
        :class:`.Parameters`
            ``self``
        """
        if type is None:
            self.dict = {
                'gameVersion': self.gameVersion,
                'binaryVersion': self.binaryVersion,
                'gdw': str(self.GDW)
            }
        if type == 'web':
            self.dict = {}
        return self

    def finish(self):
        """Finishes creating parameters dictionary, and adds ``secret`` parameter.

        Puts :attr:`.Parameters.secret` as *secret* parameter.

        Returns
        -------
        :class:`dict`
            Fully formatted dictionary.
        """
        self.dict['secret'] = self.secret
        return self.dict

    def finish_level(self):
        """Same as :meth:`.Parameters.finish`, but adds :attr:`.Parameters.level_secret` instead.

        Returns
        -------
        :class:`dict`
            Fully formatted dictionary.
        """
        self.dict['secret'] = self.level_secret
        return self.dict

    def finish_login(self):
        """Same as :meth:`.Parameters.finish`, but adds :attr:`.Parameters.login_secret` instead.

        Returns
        -------
        :class:`dict`
            Fully formatted dictionary.
        """
        self.dict['secret'] = self.login_secret
        return self.dict

    def finish_mod(self):
        """Same as :meth:`.Parameters.finish`, but adds :attr:`.Parameters.mod_secret` instead.

        Returns
        -------
        :class:`dict`
            Fully formatted dictionary.
        """
        self.dict['secret'] = self.mod_secret
        return self.dict

    def close(self):
        """Finishes creating parameters dictionary, without adding anything.

        Returns
        -------
        :class:`dict`
            Fully formatted parameters dictionary.
        """
        return self.dict

    def put_for_management(self, login: str, password: str, code: int):
        """Puts parameters for account management.

        Parameters
        ----------
        login: :class:`str`
            A username of an account.
        password: :class:`str`
            A password of an account.
        code: :class:`int`
            A solved RobTop's Captcha code.

        Returns
        -------
        :class:`.Parameters`
            ``self``
        """
        to_put = {
            'username': login,
            'password': password,
            'vercode': str(code),
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

    def put_definer(self, for_what: str, item):
        """Puts a definer.

        Parameters
        ----------
        for_what: :class:`str`
            Type of parameter to add, represented as string.

            Follows this mapping:

            .. code-block:: python3

                'song'       -> 'songID'
                'user'       -> 'targetAccountID'
                'search'     -> 'str'
                'password'   -> 'password'
                'levelid'    -> 'levelID'
                'accountid'  -> 'accountID'
                'itemid'     -> 'itemID'
                'messageid'  -> 'messageID'
                'commentid'  -> 'commentID'
                'requestid'  -> 'requestID'
                'userid'     -> 'userID'
                'stars'      -> 'stars'
                'rating'     -> 'rating'

        item: `Any`
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
            'password': 'password',
            'levelid': 'levelID',
            'accountid': 'accountID',
            'itemid': 'itemID',
            'messageid': 'messageID',
            'commentid': 'commentID',
            'requestid': 'requestID',
            'userid': 'userID',
            'stars': 'stars',
            'rating': 'rating'
        }
        try:
            self.dict[params_dict[for_what]] = str(item)
        except KeyError:
            pass
        return self

    def put_recipient(self, account_id: int):
        """Puts recipient of a message/friend request/...

        Parameters
        ----------
        account_id: :class:`int`
            An account ID of the recipient.

        Returns
        -------
        :class:`.Parameters`
            ``self``
        """
        self.dict['toAccountID'] = str(account_id)
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

    def put_fr_comment(self, item: str):
        """Pretty self explanatory. Puts `'comment'` parameter.

        Parameters
        ----------
        item: :class:`str`
            A comment to put.

        Returns
        -------
        :class:`.Parameters`
            ``self``
        """
        self.dict['comment'] = mapper_util.prepare_sending(
            base64.b64encode(item.encode()).decode())
        return self

    def put_save_data(self, data_seq: Sequence[Union[bytes, str]]):
        """Self explanatory. Puts `'saveData'` parameter.

        Parameters
        ----------
        data_seq: Sequence[Union[:class:`bytes`, :class:`str`]]
            Data to put.

        Returns
        -------
        :class:`.Parameters`
            ``self``
        """
        parts = []

        for data in data_seq:
            if isinstance(data, str):
                data = data.encode()

            if b'?xml' in data:  # not encoded
                data = Coder.encode_save(data, needs_xor=False)

            data = data.decode(errors='replace')

            parts.append(data)

        self.dict['saveData'] = (';'.join(parts))

        return self

    def put_type(self, number: Union[int, str] = 0):
        """Sets `'type'` parameter to a given number or string.

        Parameters
        ----------
        number: Union[:class:`int`, :class:`str`]
            A number or string to set type to.

        Returns
        -------
        :class:`.Parameters`
            ``self``
        """
        self.dict['type'] = str(number)
        return self

    def put_percent(self, number: int = 0):
        """Same as :meth:`.Parameters.put_type`, but for `'percent'`."""
        self.dict['percent'] = str(number)
        return self

    def put_page(self, number: int = 0):
        """Same as :meth:`.Parameters.put_type`, but for `'page'`."""
        self.dict['page'] = str(number)
        return self

    def put_weekly(self, number: int = 0):
        """Same as :meth:`.Parameters.put_type`, but for `'weekly'`."""
        self.dict['weekly'] = str(number)
        return self

    def put_total(self, number: int = 0):
        """Same as :meth:`.Parameters.put_type`, but for `'total'`."""
        self.dict['total'] = str(number)
        return self

    def put_mode(self, number: int = 0):
        """Same as :meth:`.Parameters.put_type`, but for `'mode'`."""
        self.dict['mode'] = str(number)
        return self

    def put_like(self, number: int = 0):
        """Same as :meth:`.Parameters.put_type`, but for `'like'`."""
        self.dict['like'] = str(number)
        return self

    def put_count(self, number: int = 0):
        """Same as :meth:`.Parameters.put_type`, but for `'count'`."""
        self.dict['count'] = str(number)
        return self

    def put_feature(self, number: int = 0):
        """Same as :meth:`.Parameters.put_type`, but for `'feature'`."""
        self.dict['feature'] = str(number)
        return self

    def put_special(self, number: int = 0):
        """Same as :meth:`.Parameters.put_type`, but for `'special'`."""
        self.dict['special'] = str(number)
        return self

    def put_local(self, number: int = 0):
        """Same as :meth:`.Parameters.put_type`, but for `'local'`."""
        self.dict['local'] = str(number)
        return self

    def put_seed(self, seed: str, prefix: str = 'seed', suffix: str = ''):
        """Puts ``'{prefix}{suffix}'`` parameter.

        Parameters
        ----------
        seed: :class:`str`
            The seed to put, as string.

        prefix: `Any`
            The prefix to use as a parameter.

        suffix: `Any`
            The suffix to append to ``prefix``.

        Returns
        -------
        :class:`.Parameters`
            ``self``
        """
        self.dict[str(prefix)+str(suffix)] = str(seed)
        return self

    def put_rs(self, rs: str):
        """Self explanatory. Puts ``'rs'`` parameter.

        Parameters
        ----------
        rs: :class:`str`
            Random Seed parameter, as string.

        Returns
        -------
        :class:`.Parameters`
            ``self``
        """
        self.dict['rs'] = str(rs)
        return self

    def put_chk(self, chk: str):
        """Self explanatory. Puts ``'chk'`` parameter.

        Parameters
        ----------
        chk: :class:`str`
            Check parameter, as string.

        Returns
        -------
        :class:`.Parameters`
            ``self``
        """
        self.dict['chk'] = str(chk)
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
        self.put_chk(Coder.gen_chk(type='comment', values=values))
        return self

    def comment_for(self, type: str, number: int = None):
        """Defines type of a comment, and puts parameters required for it.

        Parameters
        ----------
        type: :class:`str`
            A type of the comment, either ``'profile'`` or ``'level'``.
            ``'profile'`` sets ``cType=1``, while ``'level'`` sets ``levelID=str(number)``.
        number: :class:`int`
            A number to put. Used as mentioned above.

        Returns
        -------
        :class:`.Parameters`
            ``self``
        """
        if type == 'profile':
            self.dict['cType'] = '1'

        elif type == 'level':
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
        self.dict.pop('gdw')  # it is not needed in login request
        self.dict['password'] = password
        self.put_udid()
        self.put_username(username)
        return self

    def put_udid(self, id: int = -1):
        """Puts ``'udid'`` parameter.

        .. note::

            If ``id`` is ``-1`` or omitted, random udid is generated.
            (From 100,000 to 100,000,000,000)

        Parameters
        ----------
        id: :class:`int`
            UDID to put.

        Returns
        -------
        :class:`.Parameters`
            ``self``
        """
        if not (id + 1):  # if -1
            id = random.randint(100000, 100000000000)

        self.dict['udid'] = str(id)
        return self


    def put_uuid(self, id: int = -1):
        """Same as :meth:`.Parameters.put_udid`, but puts ``'uuid'``.

        .. note::

            If ``id`` is ``-1``, generates randomly between 100,000 and 100,000,000.

        Parameters
        ----------
        id: :class:`int`
            UUID to put.

        Returns
        -------
        :class:`.Parameters`
            ``self``
        """
        if not (id + 1):
            id = random.randint(100000, 100000000)

        self.dict['uuid'] = str(id)
        return self

    def put_level_desc(self, content: str):
        """Encodes given content and puts ``'levelDesc'``.

        Parameters
        ----------
        content: :class:`str`
            Content of the new description, NOT encoded in Base64.

        Returns
        -------
        :class:`.Parameters`
            ``self``
        """
        if content is None:
            content = ''

        desc = mapper_util.prepare_sending(base64.b64encode(content.encode()).decode())

        self.dict['levelDesc'] = desc
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
        comments: :class:`int`
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

    def put_filters(self, filters: dict):
        """Appends level filters.

        Parameters
        ----------
        filters: Union[:class:`dict`, :class:`.Filters`]
            All filters as a dictionary or as a :class:`.Filters` object.

        Returns
        -------
        :class:`.Parameters`
            ``self``
        """
        if hasattr(filters, 'to_parameters'):
            filters = filters.to_parameters()
        self.dict.update(filters)
        return self

    def get_sent(self, indicator: int):
        if (indicator == 1):
            self.dict['getSent'] = '1'
        else:
            pass
        return self
