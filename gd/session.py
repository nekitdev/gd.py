import asyncio
import functools
import itertools
import re  # for NG songs
import time  # for perf_counter in ping

from typing import Union, Sequence, Tuple

from .unreguser import UnregisteredUser
from .errors import *

from .utils.captcha_solver import Captcha
from .utils.converter import Converter
from .utils.http_request import http
from .utils.indexer import Index as i
from .utils.mapper import mapper_util
from .utils.params import Parameters as Params
from .utils.routes import Route
from .utils.crypto.coders import Coder

class GDSession:
    """Implements all requests-related functionality.
    No docstrings here yet...
    I am sorry for all in-def imports.
    - NeKitDS
    """
    async def ping_server(self, link: str):
        start = time.perf_counter()
        await http.normal_request(link)
        end = time.perf_counter()

        ping = (end-start)*1000

        return round(ping, 2)

    async def get_song(self, song_id: int = 0):
        from .classconverter import ClassConverter

        parameters = Params().create_new().put_definer('song', song_id).finish()
        codes = {
            -1: MissingAccess(type='Song', id=song_id),
            -2: SongRestrictedForUsage(song_id)
        }
        resp = await http.request(
            Route.GET_SONG_INFO, parameters, splitter="~|~", error_codes=codes, should_map=True)
        return ClassConverter.song_convert(resp)

    async def get_ng_song(self, song_id: int = 0):
        # just like get_song(), but gets anything available on NG.
        from .classconverter import ClassConverter

        song_id = int(song_id)  # ensure type

        link = Route.NEWGROUNDS_SONG_LISTEN + str(song_id)
        content = await http.normal_request(link)
        html = content.decode().replace('\\', '')

        RE = (
            'https:\/\/audio\.ngfiles\.com\/([^\'"]+)',  # searching for link
            '.filesize.:(\d+)',  # searching for size
            '<title>([^<>]+)<\/title>',  # searching for name
            '.artist.:.([^\'"]+).'  # searching for author
        )
        try:
            dl_link = re.search(RE[0], html).group(0)
            size_b = int(re.search(RE[1], html).group(1))  # in B
            size_mb = round(size_b/1024/1024, 2)  # in MB (rounded)
            name = re.search(RE[2], html).group(1)
            author = re.search(RE[3], html).group(1)
        except AttributeError:  # if re.search returned None -> Song not found
            raise MissingAccess(message=f'No song found under ID: {song_id}.')

        return ClassConverter.song_from_kwargs(
            name=name, author=author, id=song_id, size=size_mb, links=[link, dl_link], custom=True
        )

    async def get_user(self, account_id: int = 0, *, client=None):
        from .classconverter import ClassConverter

        if account_id == -1:
            return UnregisteredUser()

        parameters = Params().create_new().put_definer('user', account_id).finish()
        codes = {
            -1: MissingAccess(type='User', id=account_id)
        }

        resp = await http.request(
            Route.GET_USER_INFO, parameters, splitter=':', error_codes=codes, should_map=True)

        another = (
            Params().create_new().put_definer('search', resp.get(i.USER_PLAYER_ID))
            .put_total(0).put_page(0).finish()
        )
        some_resp = await http.request(Route.USER_SEARCH, another, splitter='#')

        item = some_resp[0]
        if not item:
            return

        new_resp = mapper_util.map(item.split(':'))
        to_add = (i.USER_GLOW_OUTLINE, i.USER_ICON, i.USER_ICON_TYPE)
        new_dict = {k: new_resp.get(k) for k in to_add}
        resp.update(new_dict)

        return ClassConverter.user_convert(resp)._attach_client(client)

    def to_user(self, conv_dict: dict = {}, *, client=None):
        from .classconverter import ClassConverter

        return ClassConverter.abstractuser_convert(conv_dict)._attach_client(client)

    async def search_user(self, param: Union[str, int] = None, *, client=None):
        from .classconverter import ClassConverter

        assert param is not None

        parameters = (
            Params().create_new().put_definer('search', param)
            .put_total(0).put_page(0).finish()
        )
        codes = {
            -1: MissingAccess(message=f'Searching for {param} returned -1.')
        }

        resp = await http.request(Route.USER_SEARCH, parameters, splitter='#', error_codes=codes)
        item = resp[0]
        if not item:
            return

        mapped = mapper_util.map(item.split(':'))
        ret = {
            'name': i.USER_NAME,
            'id': i.USER_PLAYER_ID,
            'account_id': i.USER_ACCOUNT_ID
        }
        ret = {k: mapped.get(v) for k, v in ret.items()}

        return ClassConverter.abstractuser_convert(ret)._attach_client(client)

    async def get_level(
        self, level_id: int = 0, timetuple: Tuple[int, int, int] = (0, -1, -1), *, client=None
    ):
        from .classconverter import ClassConverter

        assert level_id >= -2

        typeof, number, cooldown = map(str, timetuple)
        ext = ['101', typeof, '102', number, '103', cooldown]

        codes = {
            -1: MissingAccess(message=f'Failed to get a level. Given ID: {level_id}')
        }

        parameters = Params().create_new().put_definer('leveldata', level_id).finish()
        resp = await http.request(Route.DOWNLOAD_LEVEL, parameters, error_codes=codes, splitter='#')

        level_data = mapper_util.map(resp[0].split(':') + ext)

        real_id = level_data.get(i.LEVEL_ID)

        parameters = (
            Params().create_new().put_definer('search', real_id)
            .put_for_level().finish()
        )
        resp = await http.request(Route.LEVEL_SEARCH, parameters, error_codes=codes, splitter='#')

        # getting song
        song_data = resp[2]
        song = Converter.to_normal_song(
            level_data.get(i.LEVEL_SONG_ID)
        ) if not song_data else ClassConverter.song_convert(
            mapper_util.map(song_data.split('~|~')))

        # getting creator
        creator_data = resp[1]
        creator = UnregisteredUser() if not creator_data else ClassConverter.abstractuser_convert(
            {k: v for k, v in zip(('id', 'name', 'account_id'), creator_data.split(':'))}
        )

        return ClassConverter.level_convert(
            level_data, song=song, creator=creator)._attach_client(client)

    async def get_timely(self, typeof: str = 'daily', *, client=None):
        w = ('daily', 'weekly').index(typeof)
        parameters = Params().create_new().put_weekly(w).finish()
        codes = {
            -1: MissingAccess(message=f'Failed to fetch a {typeof!r} level.')
        }
        resp = await http.request(Route.GET_TIMELY, parameters, error_codes=codes, splitter='|')
        if len(resp) != 2:
            raise MissingAccess(message=f'Unknown response: {resp}.')

        num, cooldown = map(int, resp)
        num %= 100_000
        w += 1

        level = await self.get_level(-w, (w, num, cooldown))
        return level._attach_client(client)

    async def get_friends(self, client):
        from .classconverter import ClassConverter

        parameters = (
            Params().create_new().put_definer('accountid', client.account_id)
            .put_password(client.encodedpass).put_type(0).finish()
        )
        codes = {
            -1: MissingAccess(message='Failed to get friends.'),
            -2: NothingFound('gd.AbstractUser')
        }

        resp = await http.request(Route.GET_FRIENDS, parameters, error_codes=codes, splitter='|')

        ret = []
        for elem in resp:
            temp = mapper_util.map(elem.split(':'))

            parse_dict = {
                'name': temp[i.USER_NAME],
                'id': temp[i.USER_PLAYER_ID],
                'account_id': temp[i.USER_ACCOUNT_ID]
            }

            ret.append(
                ClassConverter.abstractuser_convert(parse_dict)._attach_client(client)
            )

        return ret

    async def test_captcha(self, client):
        resp = await http.request(Route.CAPTCHA)
        res = await Captcha.aio_solve(resp, should_log=True, loop=client.loop)
        return res

    async def login(self, client, user: str, password: str):
        parameters = (
            Params().create_new().put_login_definer(username=user, password=password)
            .finish_login()
        )
        codes = {
            -1: LoginFailure(login=user, password=password)
        }

        resp = await http.request(Route.LOGIN, parameters, splitter=',', error_codes=codes)

        account_id, id = resp

        prepared = {
            'name': user, 'password': password,
            'account_id': account_id, 'id': id
        }
        for attr, value in prepared.items():
            client._upd(attr, value)

    async def get_page_messages(
        self, sent_or_inbox: str, page: int, *, raise_errors: bool, client
    ):
        from .classconverter import ClassConverter

        assert sent_or_inbox in ('inbox', 'sent')
        inbox = 0 if sent_or_inbox != 'sent' else 1

        parameters = (
            Params().create_new().put_definer('accountid', client.account_id)
            .put_password(client.encodedpass).put_page(page).put_total(0).get_sent(inbox).finish()
        )
        codes = {
            -1: MissingAccess(message='Failed to get messages.'),
            -2: NothingFound('gd.Message')
        }

        resp = await http.request(
            Route.GET_PRIVATE_MESSAGES, parameters, error_codes=codes,
            splitter_func=lambda s: s.split('#')[0].split('|'), raise_errors=raise_errors
        )
        if resp is None:
            return list()

        res = []
        for elem in resp:
            mapped = mapper_util.map(elem.split(':') + ['101', str(page)])
            res.append(
                ClassConverter.message_convert(
                    mapped, client._get_parse_dict()
                )._attach_client(client)
            )

        return res

    async def get_messages(
        self, sent_or_inbox: str, pages: Sequence[int] = [], *,
        sort_by_page: bool = True, timeout: Union[int, float] = 10.0, client
    ):
        assert sent_or_inbox in ('inbox', 'sent')

        assert 0 < len(pages) <= 1024

        real_pages = filter(lambda n: isinstance(n, int), pages)
        to_run = [
            self.get_page_messages(
                sent_or_inbox=sent_or_inbox, page=page, raise_errors=False, client=client
            ) for page in real_pages
        ]

        finished, _ = await asyncio.wait(to_run, timeout=timeout)

        filtered = [
            fut.result() for fut in finished if fut.result()
        ]

        if sort_by_page:
            # sort the lists according to the page of the first comment in each list.
            filtered.sort(key=lambda s: s[0].page)
        return [*itertools.chain.from_iterable(filtered)]

    async def post_comment(self, content: str, *, client=None):
        to_gen = [client.name, 0, 0, 1]

        parameters = (
            Params().create_new().put_definer('accountid', client.account_id)
            .put_username(client.name).put_password(client.encodedpass)
            .put_comment(content, to_gen).comment_for('client').finish()
        )
        codes = {
            -1: MissingAccess(message='Failed to post a comment.')
        }

        await http.request(Route.UPLOAD_ACC_COMMENT, parameters, error_codes=codes)


    async def comment_level(self, level, content: str, percentage: int, *, client=None):
        assert percentage <= 100, f'{percentage}%>100% percentage arg was recieved.'

        percentage = round(percentage)  # just in case
        to_gen = [client.name, level.id, percentage, 0]

        parameters = (
            Params().create_new().put_definer('accountid', client.account_id)
            .put_username(client.name).put_password(client.encodedpass)
            .put_comment(content, to_gen).comment_for('level', level.id)
            .put_percent(percentage).finish()
        )
        codes = {
            -1: MissingAccess(message=f'Failed to post a comment on a level: {level!r}.')
        }

        await http.request(Route.UPLOAD_COMMENT, parameters, error_codes=codes)

    async def edit(self, name: str, password: str, *, client=None):
        _, cookie = await http.request(Route.MANAGE_ACCOUNT, get_cookies=True)
        captcha = await http.request(Route.CAPTCHA, cookie=cookie)
        number = await Captcha.aio_solve(captcha, loop=client.loop)
        parameters = (
            Params().create_new('web').put_for_management(
                client.name, client.password, number).close()
        )
        await http.request(Route.MANAGE_ACCOUNT, parameters, cookie=cookie)

        if name is not None:
            parameters = Params().create_new('web').put_for_username(client.name, name).close()
            resp = await http.request(Route.CHANGE_USERNAME, parameters, cookie=cookie)
            if ('Your username has been changed to' in resp):
                client._upd('name', name)
            else:
                raise FailedToChange('name')

        if password is not None:
            await http.request(Route.CHANGE_PASSWORD, cookie=cookie)
            parameters = (
                Params().create_new('web').put_for_password(
                    client.name, client.password, password).close()
            )
            resp = await http.request(Route.CHANGE_PASSWORD, parameters, cookie=cookie)
            if ('Password change failed' in resp):
                raise FailedToChange('password')
            else:
                client._upd('password', password)


    async def delete_comment(self, comment, *, client=None):
        cases = {
            'level': 0,
            'client': 1
        }
        config_type = cases.get(comment.typeof)
        cases = {
            0: Route.DELETE_LEVEL_COMMENT,
            1: Route.DELETE_ACC_COMMENT
        }
        route = cases.get(config_type)
        parameters = (
            Params().create_new().put_definer('commentid', comment.id)
            .put_definer('accountid', client.account_id).put_password(client.encodedpass)
            .comment_for(config_type, comment.level_id).finish()
        )
        resp = await http.request(route, parameters)
        if resp != 1:
            raise MissingAccess(message=f'Failed to delete a comment: {comment!r}.')


    async def delete_friend_req(self, req):
        client = req._client
        user = req.author if req.typeof == 'normal' else req.recipient
        parameters = (
            Params().create_new().put_definer('accountid', client.account_id)
            .put_definer('user', user.account_id).put_password(client.encodedpass)
            .put_is_sender(req.typeof).finish()
        )
        resp = await http.request(Route.DELETE_REQUEST, parameters)
        if resp != 1:
            raise MissingAccess(message=f'Failed to delete a friend request: {req!r}.')


    async def accept_friend_req(self, req):
        client = req._client
        if req.typeof == 'sent':
            raise MissingAccess(
                message="Failed to accept a friend request. Reason: request is sent, not recieved one."
            )
        parameters = (
            Params().create_new().put_definer('accountid', client.account_id)
            .put_password(client.encodedpass).put_definer('user', req.author.account_id)
            .put_definer('requestid', req.id).finish()
        )
        resp = await http.request(Route.ACCEPT_REQUEST, parameters)
        if resp != 1:
            raise MissingAccess(message=f"Failed to accept a friend request: {req!r}.")


    async def read_message(self, msg):
        client = msg._client
        parameters = (
            Params().create_new().put_definer('accountid', client.account_id)
            .put_definer('messageid', msg.id).put_password(client.encodedpass)
            .put_is_sender(msg.typeof).finish()
        )
        codes = {
            -1: MissingAccess(message=f"Failed to read a message: {msg!r}.")
        }
        resp = await http.request(
            Route.READ_PRIVATE_MESSAGE, parameters, error_codes=codes,
            splitter=':', should_map=True
        )
        ret = Coder.decode(
            type='message', string=mapper_util.normalize(resp.get(i.MESSAGE_BODY))
        )
        msg._body = ret
        return msg.body


    async def delete_message(self, msg):
        client = msg._client
        parameters = (
            Params().create_new().put_definer('accountid', client.account_id)
            .put_definer('messageid', msg.id).put_password(client.encodedpass)
            .put_is_sender(msg.typeof).finish()
        )
        resp = await http.request(Route.DELETE_PRIVATE_MESSAGE, parameters)
        if resp != 1:
            raise MissingAccess(message=f"Failed to delete a message: {msg!r}.")


    async def retrieve_page_comments(
        self, user, typeof: str = 'profile', page: int = 0, *, raise_errors: bool = True
    ):
        from .classconverter import ClassConverter

        assert isinstance(page, int) and page >= 0
        assert typeof in ("profile", "level")

        is_level = (typeof == "level")

        typeid = 0 if is_level else 1
        definer = "userid" if is_level else "accountid"
        selfid = user.id if is_level else user.account_id
        route = Route.GET_COMMENT_HISTORY if is_level else Route.GET_ACC_COMMENTS

        def func(elem):
            if is_level:
                return elem.split(':')[0].split('~')
            return elem.split('~')

        param_obj = Params().create_new().put_definer(definer, selfid).put_page(page).put_total(0)
        if is_level:
            param_obj.put_mode(0)
        parameters = param_obj.finish()

        resp = await http.request(route, parameters, splitter='#')
        thing = resp[0]

        if not len(thing):
            if raise_errors:
                raise NothingFound('gd.Comment')
            return list()

        to_map = mapper_util.normalize(thing).split('|')

        res = []
        for elem in to_map:
            prepared = mapper_util.map(
                func(elem) + ['101', str(typeid), '102', str(page)]
            )
            res.append(
                ClassConverter.comment_convert(
                    prepared, user._dict_for_parse
                )._attach_client(user._client)
            )

        return res

    async def retrieve_comments(
        self, user, typeof: str = 'profile', pages: Sequence[int] = [],
        *, sort_by_page: bool = True, timeout: Union[int, float] = 10.0
    ):
        assert typeof in ('profile', 'level')
        # this is the limit? can break before
        assert 0 < len(pages) <= 1024

        real_pages = filter(lambda n: isinstance(n, int), pages)
        to_run = [
            self.retrieve_page_comments(
                typeof=typeof, user=user, page=page, raise_errors=False
            ) for page in real_pages
        ]

        finished, _ = await asyncio.wait(to_run, timeout=timeout)

        filtered = [
            fut.result() for fut in finished if fut.result()
        ]

        if sort_by_page:
            # sort the lists according to the page of the first comment in each list.
            filtered.sort(key=lambda s: s[0].page)
        return [*itertools.chain.from_iterable(filtered)]

    async def get_level_comments(self, level, strategy, amount: int):
        from .classconverter import ClassConverter

        st_value = strategy.value

        parameters = (
            Params().create_new().put_definer('leveldata', level.id).put_page(0)
            .put_total(0).put_mode(st_value).put_count(amount).finish()
        )
        codes = {
            -1: MissingAccess(message=f'Failed to get comments of a level: {level!r}.'),
            -2: NothingFound('gd.Comment')
        }

        resp = await http.request(
            Route.GET_COMMENTS, parameters, error_codes=codes,
            splitter_func=lambda s: s.split('#')[0].split('|')
        )

        res = []
        for elem in resp:
            com_data, user_data = (mapper_util.map(part.split('~')) for part in elem.split(':'))
            com_data.update({1: level.id, 101: 0, 102: 0})

            user_dict = {
                'account_id': user_data[i.USER_ACCOUNT_ID],
                'id': com_data[i.COMMENT_AUTHOR_ID],
                'name': user_data[i.USER_NAME]
            }
            res.append(
                ClassConverter.comment_convert(
                    com_data, user_dict
                )._attach_client(level._client)
            )

        return res

    async def send_message(self, target, subject: str, body: str, *, client=None):
        parameters = (
            Params().create_new().put_definer('accountid', client.account_id)
            .put_message(subject, body).put_recipient(target.account_id)
            .put_password(client.encodedpass).finish()
        )
        resp = await http.request(Route.SEND_PRIVATE_MESSAGE, parameters)
        if resp != 1:
            raise MissingAccess(message=f"Failed to send a message to a user: {target!r}.")

    async def update_profile(
        self, msg: int, friend_req: int, comments: int,
        youtube: str, twitter: str, twitch: str, *, client
    ):
        parameters = (
            Params().create_new('web').put_definer('accountid', client.account_id)
            .put_password(client.encodedpass)
            .put_profile_upd(msg, friend_req, comments, youtube, twitter, twitch).finish_login()
        )
        resp = await http.request(Route.UPDATE_ACC_SETTINGS, parameters)
        if resp != 1:
            raise MissingAccess(message=f"Failed to update profile settings of a client: {client!r}.")

_session = GDSession()
