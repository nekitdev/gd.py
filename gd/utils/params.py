import random
import uuid

from gd.typing import Any, Dict, Filters, List, Optional, Parameters, Sequence, Union

from gd.utils.crypto.coders import Coder

__all__ = ("Parameters", "enter_gdworld", "leave_gdworld")


def enter_gdworld() -> None:
    Parameters.GDW = 1


def leave_gdworld() -> None:
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

    def __init__(self) -> None:
        self.secret = "Wmfd2893gb7"
        self.level_secret = "Wmfv2898gc9"
        self.login_secret = "Wmfv3899gc9"
        self.mod_secret = "Wmfp3879gc3"
        self.dict = {}

    def create_new(
        self, game_version: int = 21, binary_version: int = 35, add_basic: bool = True
    ) -> Parameters:
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
        if add_basic:
            self.dict = {
                "gameVersion": str(game_version),
                "binaryVersion": str(binary_version),
                "gdw": str(self.GDW),
            }
        else:
            self.dict = {}

        return self

    def finish(self) -> Dict[str, str]:
        """Finishes creating parameters dictionary, and adds ``secret`` parameter.

        Puts :attr:`.Parameters.secret` as *secret* parameter.

        Returns
        -------
        :class:`dict`
            Fully formatted dictionary.
        """
        self.dict["secret"] = self.secret
        return self.dict

    def finish_level(self) -> Dict[str, str]:
        """Same as :meth:`.Parameters.finish`, but adds :attr:`.Parameters.level_secret` instead.

        Returns
        -------
        :class:`dict`
            Fully formatted dictionary.
        """
        self.dict["secret"] = self.level_secret
        return self.dict

    def finish_login(self) -> Dict[str, str]:
        """Same as :meth:`.Parameters.finish`, but adds :attr:`.Parameters.login_secret` instead.

        Returns
        -------
        :class:`dict`
            Fully formatted dictionary.
        """
        self.dict["secret"] = self.login_secret
        return self.dict

    def finish_mod(self) -> Dict[str, str]:
        """Same as :meth:`.Parameters.finish`, but adds :attr:`.Parameters.mod_secret` instead.

        Returns
        -------
        :class:`dict`
            Fully formatted dictionary.
        """
        self.dict["secret"] = self.mod_secret
        return self.dict

    def close(self) -> Dict[str, str]:
        """Finishes creating parameters dictionary, without adding anything.

        Returns
        -------
        :class:`dict`
            Fully formatted parameters dictionary.
        """
        return self.dict

    def put_definer(self, for_what: str, item: Any) -> Parameters:
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
                'gauntlet'   -> 'gauntlet'
                'password'   -> 'password'
                'levelid'    -> 'levelID'
                'accountid'  -> 'accountID'
                'itemid'     -> 'itemID'
                'messageid'  -> 'messageID'
                'commentid'  -> 'commentID'
                'requestid'  -> 'requestID'
                'userid'     -> 'userID'
                'reward'     -> 'rewardType'
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
            "song": "songID",
            "user": "targetAccountID",
            "search": "str",
            "gauntlet": "gauntlet",
            "password": "password",
            "levelid": "levelID",
            "accountid": "accountID",
            "itemid": "itemID",
            "messageid": "messageID",
            "commentid": "commentID",
            "requestid": "requestID",
            "userid": "userID",
            "stars": "stars",
            "rating": "rating",
        }
        try:
            self.dict[params_dict[for_what]] = str(item)
        except KeyError:
            pass
        return self

    def put_recipient(self, account_id: int) -> Parameters:
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
        self.dict["toAccountID"] = str(account_id)
        return self

    def put_is_sender(self, t: str) -> Parameters:
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
        if t == "sent":
            self.dict["isSender"] = str(1)

        return self

    def put_message(self, subject: str, body: str) -> Parameters:
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
        self.dict["subject"] = Coder.do_base64(subject)
        self.dict["body"] = Coder.encode(type="message", string=body)
        return self

    def put_password(self, item: str) -> Parameters:
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
        self.dict["gjp"] = item
        return self

    def put_username(self, item: str) -> Parameters:
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
        self.dict["userName"] = item
        return self

    def put_fr_comment(self, item: str) -> Parameters:
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
        self.dict["comment"] = Coder.do_base64(item)
        return self

    def put_save_data(self, data_seq: Sequence[Union[bytes, str]]) -> Parameters:
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
            if isinstance(data, bytes):
                data = data.decode(errors="ignore")

            if "?xml" in data:  # not encoded
                data = Coder.encode_save(data, needs_xor=False)

            parts.append(data)

        self.dict["saveData"] = ";".join(parts)

        return self

    def put_type(self, number: Union[int, str] = 0) -> Parameters:
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
        self.dict["type"] = str(number)
        return self

    def put_percent(self, number: int = 0) -> Parameters:
        """Same as :meth:`.Parameters.put_type`, but for `'percent'`."""
        self.dict["percent"] = str(number)
        return self

    def put_page(self, number: int = 0) -> Parameters:
        """Same as :meth:`.Parameters.put_type`, but for `'page'`."""
        self.dict["page"] = str(number)
        return self

    def put_weekly(self, number: int = 0) -> Parameters:
        """Same as :meth:`.Parameters.put_type`, but for `'weekly'`."""
        self.dict["weekly"] = str(number)
        return self

    def put_total(self, number: int = 0) -> Parameters:
        """Same as :meth:`.Parameters.put_type`, but for `'total'`."""
        self.dict["total"] = str(number)
        return self

    def put_mode(self, number: int = 0) -> Parameters:
        """Same as :meth:`.Parameters.put_type`, but for `'mode'`."""
        self.dict["mode"] = str(number)
        return self

    def put_like(self, number: int = 0) -> Parameters:
        """Same as :meth:`.Parameters.put_type`, but for `'like'`."""
        self.dict["like"] = str(number)
        return self

    def put_count(self, number: int = 0) -> Parameters:
        """Same as :meth:`.Parameters.put_type`, but for `'count'`."""
        self.dict["count"] = str(number)
        return self

    def put_feature(self, number: int = 0) -> Parameters:
        """Same as :meth:`.Parameters.put_type`, but for `'feature'`."""
        self.dict["feature"] = str(number)
        return self

    def put_special(self, number: int = 0) -> Parameters:
        """Same as :meth:`.Parameters.put_type`, but for `'special'`."""
        self.dict["special"] = str(number)
        return self

    def put_local(self, number: int = 0) -> Parameters:
        """Same as :meth:`.Parameters.put_type`, but for `'local'`."""
        self.dict["local"] = str(number)
        return self

    def put_seed(self, seed: Union[int, str], prefix: str = "seed", suffix: str = "") -> Parameters:
        """Puts ``'{prefix}{suffix}'`` parameter.

        Parameters
        ----------
        seed: Union[:class:`int`, :class:`str`]
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
        self.dict[str(prefix) + str(suffix)] = str(seed)
        return self

    def put_rs(self, rs: str) -> Parameters:
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
        self.dict["rs"] = str(rs)
        return self

    def put_chk(self, chk: str) -> Parameters:
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
        self.dict["chk"] = str(chk)
        return self

    def put_comment(self, content: str, values: List[Any]) -> Parameters:
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
        comment = Coder.do_base64(content)
        self.dict["comment"] = comment
        values.insert(1, comment)
        self.put_chk(Coder.gen_chk(type="comment", values=values))
        return self

    def comment_for(self, type: str, number: int = 0) -> Parameters:
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
        if type == "profile":
            self.dict["cType"] = str(1)

        elif type == "level":
            self.dict["levelID"] = str(number)

        return self

    def put_login_definer(self, username: str, password: str) -> Parameters:
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
        self.dict.pop("gdw")  # it is not needed in login request
        self.dict["password"] = password
        self.put_udid()
        self.put_username(username)
        return self

    def put_udid(self, udid_string: Optional[str] = None) -> Parameters:
        """Puts ``'udid'`` parameter.

        Parameters
        ----------
        udid_string: :class:`str`
            UDID to put.

        Returns
        -------
        :class:`.Parameters`
            ``self``
        """
        if udid_string is None:
            udid_string = self.gen_udid()

        self.dict["udid"] = str(udid_string)
        return self

    @staticmethod
    def gen_udid(id: int = -1) -> str:
        if id == -1:
            id = random.randint(100000, 100000000000)
        return "S" + str(id)

    @staticmethod
    def gen_uuid() -> str:
        return str(uuid.uuid4())

    def put_uuid(self, uuid_string: Optional[str] = None) -> Parameters:
        """Same as :meth:`.Parameters.put_udid`, but puts ``'uuid'``.

        Parameters
        ----------
        uuid_string: :class:`str`
            UUID to put.

        Returns
        -------
        :class:`.Parameters`
            ``self``
        """
        if uuid_string is None:
            uuid_string = self.gen_uuid()

        self.dict["uuid"] = str(uuid_string)
        return self

    def put_level_desc(self, content: str) -> Parameters:
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
            content = ""

        desc = Coder.do_base64(content)

        self.dict["levelDesc"] = desc
        return self

    def put_profile_upd(
        self, msg: int, friend_req: int, comments: int, youtube: str, twitter: str, twitch: str
    ) -> Parameters:
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
            "mS": str(msg),
            "frS": str(friend_req),
            "cS": str(comments),
            "yt": youtube,
            "twitter": twitter,
            "twitch": twitch,
        }
        self.dict.update(to_put)
        return self

    def put_filters(self, filters: Union[dict, Filters]) -> Parameters:
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
        if hasattr(filters, "to_parameters"):
            filters = filters.to_parameters()
        self.dict.update(filters)
        return self

    def get_sent(self, indicator: int) -> Parameters:
        """Put ``'getSent'`` parameter if needed.

        Parameters
        ----------
        indicator: :class:`int`
            Indicates whether to put the parameter.

        Returns
        -------
        :class:`.Parameters`
            ``self``
        """
        if indicator == 1:
            self.dict["getSent"] = str(1)
        else:
            pass
        return self
