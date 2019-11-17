import asyncio
import itertools
import re  # for NG songs
import time  # for perf_counter in ping

from typing import Union, Sequence, Tuple, Dict

from .unreguser import UnregisteredUser
from .errors import *

from .utils.captcha_solver import Captcha
from .utils.converter import Converter
from .utils.enums import SearchStrategy
from .utils.filters import Filters
from .utils.http_request import http
from .utils.indexer import Index as i
from .utils.mapper import mapper_util
from .utils.params import Parameters as Params
from .utils.routes import Route
from .utils.save_parser import SaveParser
from .utils.wrap_tools import check
from .utils.crypto.coders import Coder

from . import utils

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
            -1: MissingAccess(message='No songs were found with ID: {}.'.format(song_id)),
            -2: SongRestrictedForUsage(song_id)
        }
        resp = await http.request(
            Route.GET_SONG_INFO, parameters, splitter='~|~', error_codes=codes, should_map=True)
        return ClassConverter.song_convert(resp)


    async def get_ng_song(self, song_id: int = 0):
        # just like get_song(), but gets anything available on NG.
        from .classconverter import ClassConverter

        song_id = int(song_id)  # ensure type

        link = Route.NEWGROUNDS_SONG_LISTEN + str(song_id)
        resp = await http.normal_request(link)
        content = await resp.content.read()
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
            raise MissingAccess(message='No song found under ID: {}.'.format(song_id))

        return ClassConverter.song_from_kwargs(
            name=name, author=author, id=song_id, size=size_mb, links=(link, dl_link), custom=True
        )


    async def get_user(self, account_id: int = 0, return_only_stats: bool = False, *, client):
        from .classconverter import ClassConverter

        if account_id == -1:
            return UnregisteredUser()

        parameters = Params().create_new().put_definer('user', account_id).finish()
        codes = {
            -1: MissingAccess(message='No users were found with ID: {}.'.format(account_id))
        }

        resp = await http.request(
            Route.GET_USER_INFO, parameters, splitter=':', error_codes=codes, should_map=True)

        if return_only_stats:
            return ClassConverter.user_stats_convert(resp, client)

        another = (
            Params().create_new().put_definer('search', resp.get(i.USER_PLAYER_ID))
            .put_total(0).put_page(0).finish()
        )
        some_resp = await http.request(Route.USER_SEARCH, another, splitter='#')

        item = some_resp[0]
        if not item:
            return

        new_resp = mapper_util.map(item.split(':'))
        to_add = (i.USER_NAME, i.USER_ICON, i.USER_ICON_TYPE)
        new_dict = {k: new_resp.get(k) for k in to_add}
        resp.update(new_dict)

        return ClassConverter.user_convert(resp, client)


    def to_user(self, conv_dict: dict = None, *, client):
        from .classconverter import ClassConverter

        if conv_dict is None:
            conv_dict = {}

        return ClassConverter.abstractuser_convert(conv_dict, client)


    async def search_user(self, param: Union[str, int] = None, return_abstract: bool = False, *, client):
        from .classconverter import ClassConverter

        assert param is not None

        parameters = (
            Params().create_new().put_definer('search', param)
            .put_total(0).put_page(0).finish()
        )
        codes = {
            -1: MissingAccess(message='Searching for {} returned -1.'.format(param))
        }

        resp = await http.request(Route.USER_SEARCH, parameters, splitter='#', error_codes=codes)
        item = resp[0]
        if not item:
            return

        mapped = mapper_util.map(item.split(':'))

        name = mapped.get(i.USER_NAME, '') or 'UnregisteredUser'
        id = mapped.get(i.USER_PLAYER_ID, 0) or 0
        account_id = mapped.get(i.USER_ACCOUNT_ID, 0) or 0

        if not id or not account_id:
            return UnregisteredUser(name=name, id=id)

        if return_abstract:
            ret = dict(name=name, id=id, account_id=account_id)
            return ClassConverter.abstractuser_convert(ret, client)

        # ok if we should not return abstract, let's find all other parameters
        parameters = Params().create_new().put_definer('user', mapped.get(i.USER_ACCOUNT_ID, 0)).finish()

        resp = await http.request(
            Route.GET_USER_INFO, parameters, splitter=':', error_codes=codes, should_map=True
        )

        resp.update(
            {k: mapped.get(k) for k in (i.USER_NAME, i.USER_ICON, i.USER_ICON_TYPE)}
        )

        return ClassConverter.user_convert(resp, client)


    async def get_level(
        self, level_id: int = 0, timetuple: Tuple[int, int, int] = (0, -1, -1), *, client
    ):
        from .classconverter import ClassConverter

        assert level_id >= -2

        type, number, cooldown = map(str, timetuple)
        ext = ['101', type, '102', number, '103', cooldown, '104', '0']

        codes = {
            -1: MissingAccess(message='Failed to get a level. Given ID: {}'.format(level_id))
        }

        parameters = Params().create_new().put_definer('levelid', level_id).finish()
        resp = await http.request(Route.DOWNLOAD_LEVEL, parameters, error_codes=codes, splitter='#')

        level_data = mapper_util.map(resp[0].split(':') + ext)

        real_id = level_data.get(i.LEVEL_ID)

        parameters = (
            Params().create_new().put_definer('search', real_id)
            .put_filters(Filters.setup_empty()).finish()
        )
        resp = await http.request(Route.LEVEL_SEARCH, parameters, error_codes=codes, splitter='#')

        # getting song
        song_data = resp[2]
        song = (
            Converter.to_normal_song(level_data.get(i.LEVEL_AUDIO_TRACK)) if not song_data
            else ClassConverter.song_convert(mapper_util.map(song_data.split('~|~')))
        ).attach_client(client)

        # getting creator
        creator_data = resp[1]
        creator = (
            UnregisteredUser(level_data.get(i.LEVEL_CREATOR_ID)) if not creator_data
            else ClassConverter.abstractuser_convert(
                {k: v for k, v in zip(('id', 'name', 'account_id'), creator_data.split(':'))}
            )
        ).attach_client(client)

        return ClassConverter.level_convert(
            level_data, song=song, creator=creator, client=client)


    async def get_timely(self, type: str = 'daily', *, client):
        w = ('daily', 'weekly').index(type)
        parameters = Params().create_new().put_weekly(w).finish()
        codes = {
            -1: MissingAccess(message='Failed to fetch a {!r} level.'.format(type))
        }
        resp = await http.request(Route.GET_TIMELY, parameters, error_codes=codes, splitter='|')
        if len(resp) != 2:
            raise MissingAccess(message='Unknown response: {}.'.format(resp))

        num, cooldown = map(int, resp)
        num %= 100000
        w += 1

        level = await self.get_level(-w, (w, num, cooldown), client=client)
        return level.attach_client(client)


    async def upload_level(
        self, data: str, name: str, level_id: int, version: int, length: int, audio_track: int,
        desc: str, song_id: int, is_auto: bool, original: int, two_player: bool, objects: int, coins: int,
        stars: int, unlisted: bool, ldm: bool, password: int, copyable: bool, *, load_after: bool, client
    ):
        data = Coder.zip(data)
        extra_string = ('_'.join(map(str, (0 for _ in range(55)))))
        desc = Coder.do_base64(desc)

        upload_seed = Coder.gen_level_upload_seed(data)
        seed2 = Coder.gen_chk(type='level', values=[upload_seed])
        seed = Coder.gen_rs()

        if not copyable:
            password = 0

        elif not password:
            password = 1

        else:
            password = '1{:06}'.format(password)

        parameters = (
            Params().create_new().put_definer('accountid', client.account_id)
            .put_definer('levelid', level_id).put_definer('song', song_id)
            .put_seed(seed).put_seed(seed2, suffix=2).put_seed(0, prefix='wt')
            .put_seed(0, prefix='wt', suffix=2).put_password(client.encodedpass)
            .put_username(client.name).finish()
        )

        payload = {
            'level_name': name, 'level_desc': desc, 'level_version': version,
            'level_length': length, 'audio_track': audio_track, 'auto': int(is_auto),
            'original': int(original), 'two_player': int(two_player), 'objects': objects,
            'coins': coins, 'requested_stars': stars, 'unlisted': int(unlisted), 'ldm': int(ldm),
            'password': password, 'level_string': data, 'extra_string': extra_string,
            'level_info': 'H4sIAAAAAAAAC8tLzc4sUShPLFbISC1K1dPTswYA5G9QUhIAAAA='
        }

        payload_cased = {
            Converter.snake_to_camel(key): str(value) for key, value in payload.items()
        }

        parameters.update(payload_cased)

        level_id = await http.request(Route.UPLOAD_LEVEL, parameters)

        if level_id == -1:
            raise MissingAccess(message='Failed to upload a level.')

        elif load_after:
            return await client.get_level(level_id)

        else:
            from .classconverter import Level
            return Level(id=level_id).attach_client(client)


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
                ClassConverter.abstractuser_convert(parse_dict, client)
            )

        return ret


    async def get_leaderboard(self, level, strategy, *, client):
        from .classconverter import ClassConverter

        parameters = (
            Params().create_new().put_definer('accountid', client.account_id)
            .put_definer('levelid', level.id)
            .put_password(client.encodedpass).put_type(strategy.value).finish()
        )

        codes = {
            -1: MissingAccess(message='Failed to get leaderboard of the level: {!r}.'.format(level))
        }

        resp = await http.request(Route.GET_LEVEL_SCORES, parameters, error_codes=codes, splitter='|')

        if not resp:
            return list()

        ext = ['101', str(level.id)]

        res = []

        for data in filter(_is_not_empty, resp):
            mapped = mapper_util.map(data.split(':') + ext)
            record = ClassConverter.level_record_convert(mapped, strategy, client)
            res.append(record)

        return res


    async def get_top(self, strategy, count: int, *, client):
        from .classconverter import ClassConverter

        needs_login = (strategy.value in (1, 2))

        # special case: map 'players' -> 'top'
        strategy = strategy.name.lower() if strategy.value else 'top'

        params = Params().create_new().put_type(strategy).put_count(count)
        codes = {
            -1: MissingAccess(message='Failed to fetch leaderboard for strategy: {!r}.'.format(strategy))
        }

        if needs_login:
            check.is_logged_obj(client, 'get_top')
            params.put_definer('accountid', client.account_id).put_password(client.encodedpass)

        parameters = params.finish()

        resp = await http.request(Route.GET_USER_TOP, parameters, error_codes=codes, splitter='|')

        res = []
        for data in filter(_is_not_empty, resp):
            mapped = mapper_util.map(data.split(':'))
            stats = ClassConverter.user_stats_convert(mapped, client)
            res.append(stats)

        return res

    async def test_captcha(self):
        image_bytes = await http.request(Route.CAPTCHA)
        res = await Captcha.aio_solve(image_bytes, should_log=True)
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
            'account_id': int(account_id), 'id': int(id)
        }
        for attr, value in prepared.items():
            client._upd(attr, value)


    async def load_save(self, client):
        link = Route.GD_URL

        parameters = (
            Params().create_new().put_username(client.name).put_definer('password', client.password)
            .finish_login()
        )
        codes = {
            -11: MissingAccess(message='Failed to load data for client: {!r}.'.format(client))
        }

        resp = await http.request(Route.LOAD_DATA, parameters, error_codes=codes, custom_base=link, run_decoding=False)

        try:
            main, levels, *_ = resp.split(b';')
            main_save, level_save = (
                Coder.decode_save(save, needs_xor=False).decode(errors='replace')
                for save in (main, levels)
            )
            save = SaveParser.parse(main_save)

            client._upd('raw_save', (main_save, level_save))
            client._upd('save', save)

            return True

        except Exception:
            return False


    async def do_save(self, client, data):
        link = Route.GD_URL

        parameters = (
            Params().create_new().put_username(client.name).put_definer('password', client.password)
            .put_save_data(data).finish_login()
        )

        resp = await http.request(Route.SAVE_DATA, parameters, custom_base=link)

        if resp != 1:
            raise MissingAccess(
                message='Failed to do backup for client: {!r}. [ERROR: {}]'.format(client, resp)
            )


    async def search_levels_on_page(
        self, page: int = 0, query: str = '', filters: Filters = None,
        user=None, gauntlet: int = None, *, raise_errors: bool = True, client
    ):
        from .classconverter import ClassConverter

        if filters is None:
            filters = Filters.setup_empty()

        params = (
            Params().create_new().put_definer('search', query)
            .put_page(page).put_total(0).put_filters(filters)
        )
        codes = {
            -1: MissingAccess(message='No levels were found.')
        }
        if filters.strategy == SearchStrategy.BY_USER:

            if user is None:
                check.is_logged_obj(client, 'search_levels_on_page(...)')

                id = client.id

                params.put_definer('accountid', client.account_id).put_password(client.encodedpass)
                params.put_local(1)

            else:
                id = user if isinstance(user, int) else user.id

            params.put_definer('search', id)  # override the 'str' parameter in request

        elif filters.strategy == SearchStrategy.FRIENDS:
            check.is_logged_obj(client, 'search_levels_on_page(..., client=client)')
            params.put_definer('accountid', client.account_id).put_password(client.encodedpass)

        if gauntlet is not None:
            params.put_definer('gauntlet', gauntlet)

        parameters = params.finish()

        resp = await http.request(
            Route.LEVEL_SEARCH, parameters, raise_errors=raise_errors,
            error_codes=codes, splitter='#')

        if not resp:
            return list()

        lvdata, cdata, sdata = resp[:3]

        songs = []
        for s in filter(_is_not_empty, sdata.split('~:~')):
            song = ClassConverter.song_convert(mapper_util.map(s.split('~|~')))
            songs.append(song)

        creators = []
        for c in filter(_is_not_empty, cdata.split('|')):
            creator = ClassConverter.abstractuser_convert(
                {k: v for k, v in zip(('id', 'name', 'account_id'), c.split(':'))}, client=client
            )
            creators.append(creator)

        levels = []
        ext = ['101', '0', '102', '-1', '103', '-1']

        for lv in filter(_is_not_empty, lvdata.split('|')):
            data = mapper_util.map(lv.split(':') + ext)

            song_id = data.get(i.LEVEL_SONG_ID)
            song = Converter.to_normal_song(
                data.get(i.LEVEL_AUDIO_TRACK)
            ) if not song_id else utils.get(songs, id=song_id)

            creator_id = data.get(i.LEVEL_CREATOR_ID)
            creator = utils.get(creators, id=creator_id)
            if creator is None:
                creator = UnregisteredUser(creator_id)

            levels.append(ClassConverter.level_convert(data, song, creator, client))

        return levels


    async def search_levels(self, query: str = '', filters: Filters = None, user=None,
        pages: Sequence[int] = None, *, client
    ):
        to_run = [
            self.search_levels_on_page(
                query=query, filters=filters, user=user, page=page, raise_errors=False, client=client
            ) for page in pages
        ]

        return await self.run_many(to_run)


    async def report_level(self, level):
        parameters = Params().create_new('web').put_definer('levelid', level.id).finish()
        codes = {
            -1: MissingAccess(message='Failed to report a level: {!r}.'.format(level))
        }

        await http.request(Route.REPORT_LEVEL, parameters, error_codes=codes)

    async def delete_level(self, level, *, client):
        parameters = (
            Params().create_new().put_definer('accountid', client.account_id)
            .put_definer('levelid', level.id).put_password(client.encodedpass).finish_level()
        )

        resp = await http.request(Route.DELETE_LEVEL, parameters)

        if resp != 1:
            raise MissingAccess(message='Failed to delete a level: {}.'.format(level))

        # update level's is_alive coroutine to return False only.
        async def is_alive(*args):
            return False

        level.is_alive = is_alive


    async def update_level_desc(self, level, content, *, client):
        parameters = (
            Params().create_new().put_definer('accountid', client.account_id)
            .put_password(client.encodedpass).put_definer('levelid', level.id)
            .put_level_desc(content).finish()
        )

        resp = await http.request(Route.UPDATE_LEVEL_DESC, parameters)

        if resp != 1:
            raise MissingAccess(message='Failed to update description of the level: {}.'.format(level))

        # update level's description on success
        level.options['description'] = content


    async def rate_level(self, level, rating: int, *, client):
        assert 0 < rating <= 10, 'Invalid star value given.'

        rs = Coder.gen_rs()
        values = [level.id, rating, rs, client.account_id, 0, 0]
        chk = Coder.gen_chk(type='like_rate', values=values)

        parameters = (
            Params().create_new().put_definer('levelid', level.id)
            .put_definer('accountid', client.account_id).put_password(client.encodedpass)
            .put_udid(0).put_uuid(0).put_definer('stars', rating).put_rs(rs).put_chk(chk).finish()
        )

        resp = await http.request(Route.RATE_LEVEL_STARS, parameters)

        if resp != 1:
            raise MissingAccess(message='Failed to rate level: {}.'.format(level))


    async def rate_demon(self, level, demon_rating, mod: bool, *, client):
        rating_level = demon_rating.value

        parameters = (
            Params().create_new().put_definer('accountid', client.account_id)
            .put_password(client.encodedpass).put_definer('levelid', level.id)
            .put_definer('rating', rating_level).put_mode(int(mod)).finish_mod()
        )
        codes = {
            -2: MissingAccess(message='Attempt to rate as mod without mod permissions.')
        }

        resp = await http.request(Route.RATE_LEVEL_DEMON, parameters, error_codes=codes)

        if not resp:
            return False
        elif isinstance(resp, int) and resp > 0:
            return True


    async def send_level(self, level, rating: int, featured: bool, *, client):
        parameters = (
            Params().create_new().put_definer('accountid', client.account_id)
            .put_password(client.encodedpass).put_definer('levelid', level.id)
            .put_definer('stars', rating).put_feature(int(featured)).finish_mod()
        )
        codes = {
            -2: MissingAccess(message='Missing moderator permissions to send a level: {!r}.'.format(level))
        }

        resp = await http.request(Route.SUGGEST_LEVEL_STARS, parameters, error_codes=codes)

        if resp != 1:
            raise MissingAccess(message='Failed to send a level: {!r}.'.format(level))


    async def like(self, item, dislike: bool = False, *, client):
        if hasattr(item, 'is_featured'):  # level
            typeid = 1
            special = 0

        elif hasattr(item, 'is_spam'):  # comment
            if not item.type.value:  # level comment
                typeid = 2
                special = item.level_id

            else:  # profile comment
                typeid = 3
                special = item.id

        else:  # wrong type?!
            return

        like = dislike ^ 1

        rs = Coder.gen_rs()
        values = [special, item.id, typeid, like, rs, client.account_id, 0, 0]
        chk = Coder.gen_chk(type='like_rate', values=values)

        parameters = (
            Params().create_new().put_definer('accountid', client.account_id)
            .put_password(client.encodedpass).put_udid(0).put_uuid(0)
            .put_definer('itemid', item.id).put_like(like).put_type(typeid)
            .put_special(special).put_rs(rs).put_chk(chk).finish()
        )

        resp = await http.request(Route.LIKE_ITEM, parameters)

        if resp != 1:
            raise MissingAccess(message='Failed to like an item: {}.'.format(item))


    async def get_page_messages(
        self, sent_or_inbox: str, page: int, *, raise_errors: bool = True, client
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
            mapped = mapper_util.map(elem.split(':'))
            res.append(
                ClassConverter.message_convert(
                    mapped, client.get_parse_dict(), client
                )
            )

        return res


    async def get_messages(self, sent_or_inbox: str, pages: Sequence[int] = None, *, client):
        assert sent_or_inbox in ('inbox', 'sent')

        to_run = [
            self.get_page_messages(
                sent_or_inbox=sent_or_inbox, page=page, raise_errors=False, client=client
            ) for page in pages
        ]

        return await self.run_many(to_run)


    async def post_comment(self, content: str, *, client):
        to_gen = [client.name, 0, 0, 1]

        parameters = (
            Params().create_new().put_definer('accountid', client.account_id)
            .put_username(client.name).put_password(client.encodedpass)
            .put_comment(content, to_gen).comment_for('profile').finish()
        )
        codes = {
            -1: MissingAccess(message='Failed to post a comment.')
        }

        await http.request(Route.UPLOAD_ACC_COMMENT, parameters, error_codes=codes)


    async def comment_level(self, level, content: str, percentage: int, *, client):
        assert percentage <= 100, '{}% > 100% percentage arg was recieved.'.format(percentage)

        percentage = round(percentage)  # just in case
        to_gen = [client.name, level.id, percentage, 0]

        parameters = (
            Params().create_new().put_definer('accountid', client.account_id)
            .put_username(client.name).put_password(client.encodedpass)
            .put_comment(content, to_gen).comment_for('level', level.id)
            .put_percent(percentage).finish()
        )
        codes = {
            -1: MissingAccess(message='Failed to post a comment on a level: {!r}.'.format(level))
        }

        await http.request(Route.UPLOAD_COMMENT, parameters, error_codes=codes)


    async def edit(self, name: str, password: str, *, client):
        _, cookie = await http.request(Route.MANAGE_ACCOUNT, get_cookies=True)
        captcha = await http.request(Route.CAPTCHA, cookie=cookie)
        number = await Captcha.aio_solve(captcha, should_log=True)
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


    async def delete_comment(self, comment, *, client):
        cases = {
            0: Route.DELETE_LEVEL_COMMENT,
            1: Route.DELETE_ACC_COMMENT
        }
        route = cases.get(comment.type.value)
        parameters = (
            Params().create_new().put_definer('commentid', comment.id)
            .put_definer('accountid', client.account_id).put_password(client.encodedpass)
            .comment_for(comment.type.name.lower(), comment.level_id).finish()
        )
        resp = await http.request(route, parameters)
        if resp != 1:
            raise MissingAccess(message='Failed to delete a comment: {!r}.'.format(comment))


    async def send_friend_request(self, target, message, client):
        if message is None:
            message = ''

        parameters = (
            Params().create_new().put_definer('accountid', client.account_id)
            .put_recipient(target.account_id).put_fr_comment(message)
            .put_password(client.encodedpass).finish()
        )
        resp = await http.request(Route.SEND_REQUEST, parameters)

        if not resp:  # if request is already sent
            return

        elif resp != 1:
            raise MissingAccess(message='Failed to send a friend request to user: {!r}.'.format(target))


    async def delete_friend_req(self, req):
        client = req._client
        user = req.author if not req.type.value else req.recipient
        parameters = (
            Params().create_new().put_definer('accountid', client.account_id)
            .put_definer('user', user.account_id).put_password(client.encodedpass)
            .put_is_sender(req.type.name.lower()).finish()
        )
        resp = await http.request(Route.DELETE_REQUEST, parameters)
        if resp != 1:
            raise MissingAccess(message='Failed to delete a friend request: {!r}.'.format(req))


    async def accept_friend_req(self, req):
        client = req._client
        if req.type.value:  # is gd.MessageOrRequestType.SENT
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
            raise MissingAccess(message='Failed to accept a friend request: {!r}.'.format(req))


    async def read_friend_req(self, req):
        client = req._client
        parameters = (
            Params().create_new().put_definer('accountid', client.account_id)
            .put_password(client.encodedpass).put_definer('requestid', req.id).finish()
        )
        resp = await http.request(Route.READ_REQUEST, parameters)
        if resp != 1:
            raise MissingAccess(message='Failed to read a friend request: {!r}.'.format(req))
        req.options.update({'is_read': True})


    async def read_message(self, msg):
        client = msg._client
        parameters = (
            Params().create_new().put_definer('accountid', client.account_id)
            .put_definer('messageid', msg.id).put_is_sender(msg.type.name.lower())
            .put_password(client.encodedpass).finish()
        )
        codes = {
            -1: MissingAccess(message='Failed to read a message: {!r}.'.format(msg))
        }
        resp = await http.request(
            Route.READ_PRIVATE_MESSAGE, parameters, error_codes=codes,
            splitter=':', should_map=True
        )

        ret = Coder.decode(
            type='message', string=mapper_util.normalize(resp.get(i.MESSAGE_BODY))
        )
        msg._body = ret
        return ret


    async def delete_message(self, msg):
        client = msg._client
        parameters = (
            Params().create_new().put_definer('accountid', client.account_id)
            .put_definer('messageid', msg.id).put_password(client.encodedpass)
            .put_is_sender(msg.type.name.lower()).finish()
        )
        resp = await http.request(Route.DELETE_PRIVATE_MESSAGE, parameters)
        if resp != 1:
            raise MissingAccess(message='Failed to delete a message: {!r}.'.format(msg))


    async def get_gauntlets(self, *, client):
        from .classconverter import ClassConverter

        parameters = Params().create_new().finish()

        resp = await http.request(
            Route.GET_GAUNTLETS, parameters, splitter_func=lambda s: s.split('#')[0].split('|')
        )

        res = []
        for gdata in filter(_is_not_empty, resp):
            mapped = mapper_util.map(gdata.split(':'))
            res.append(
                ClassConverter.gauntlet_convert(mapped, client)
            )

        return res


    async def get_page_map_packs(self, page: int = 0, *, raise_errors: bool = True, client):
        from .classconverter import ClassConverter

        parameters = Params().create_new().put_page(page).finish()

        resp = await http.request(
            Route.GET_MAP_PACKS, parameters, splitter_func=lambda s: s.split('#')[0].split('|')
        )

        if resp and not resp[0]:
            if raise_errors:
                raise NothingFound('gd.MapPack')
            return list()

        res = []
        for elem in resp:
            mapped = mapper_util.map(elem.split(':'))
            res.append(
                ClassConverter.map_pack_convert(mapped, client)
            )

        return res


    async def get_map_packs(self, pages: Sequence[int] = None, *, client):
        to_run = [
            self.get_page_map_packs(
                page=page, raise_errors=False, client=client
            ) for page in pages
        ]

        return await self.run_many(to_run)


    async def get_page_friend_requests(self, sent_or_inbox: str = 'inbox',
        page: int = 0, *, raise_errors: bool = True, client):
        from .classconverter import ClassConverter

        inbox = 1 if sent_or_inbox == 'sent' else 0

        parameters = (
            Params().create_new().put_definer('accountid', str(client.account_id))
            .put_password(client.encodedpass).put_page(page).put_total(0).get_sent(inbox).finish()
        )
        codes = {
            -1: MissingAccess(message='Failed to get friend requests on page {}.'.format(page)),
            -2: NothingFound('gd.FriendRequest')
        }

        resp = await http.request(
            Route.GET_FRIEND_REQUESTS, parameters, error_codes=codes, raise_errors=raise_errors,
            splitter_func=lambda s: s.split('#')[0].split('|')
        )

        if not resp:
            return list()

        res = []
        for elem in resp:
            mapped = mapper_util.map(
                elem.split(':') + ['101', str(inbox)]
            )
            res.append(
                ClassConverter.request_convert(
                    mapped, client.get_parse_dict(), client
                )
            )

        return res


    async def get_friend_requests(
        self, sent_or_inbox: str = 'inbox', pages: Sequence[int] = None, *, client
    ):
        assert sent_or_inbox in ('sent', 'inbox')

        to_run = [
            self.get_page_friend_requests(
                sent_or_inbox=sent_or_inbox, page=page, raise_errors=False, client=client
            ) for page in pages
        ]

        return await self.run_many(to_run)


    async def retrieve_page_comments(
        self, user, type: str = 'profile', page: int = 0, *, raise_errors: bool = True, strategy
    ):
        from .classconverter import ClassConverter

        assert isinstance(page, int) and page >= 0
        assert type in ("profile", "level")

        is_level = (type == "level")

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
            param_obj.put_mode(strategy.value)
        parameters = param_obj.finish()

        resp = await http.request(route, parameters, splitter='#')
        thing = resp[0]

        if not thing:
            if raise_errors:
                raise NothingFound('gd.Comment')
            return list()

        to_map = thing.split('|')

        res = []
        for elem in to_map:
            prepared = mapper_util.map(
                func(elem) + ['101', str(typeid)]
            )
            res.append(
                ClassConverter.comment_convert(
                    prepared, user._dict_for_parse, user._client
                )
            )

        return res


    async def retrieve_comments(
        self, user, type: str = 'profile', pages: Sequence[int] = None, *, strategy
    ):
        assert type in ('profile', 'level')

        to_run = [
            self.retrieve_page_comments(
                type=type, user=user, page=page, raise_errors=False, strategy=strategy
            ) for page in pages
        ]

        return await self.run_many(to_run)


    async def get_level_comments(self, level, strategy, amount: int):
        from .classconverter import ClassConverter

        st_value = strategy.value

        parameters = (
            Params().create_new().put_definer('levelid', level.id).put_page(0)
            .put_total(0).put_mode(st_value).put_count(amount).finish()
        )
        codes = {
            -1: MissingAccess(message='Failed to get comments of a level: {!r}.'.format(level)),
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
                    com_data, user_dict, level._client
                )
            )

        return res


    async def block_user(self, user, unblock: bool = False, *, client):
        route = Route.UNBLOCK_USER if unblock else Route.BLOCK_USER
        parameters = (
            Params().create_new().put_definer('accountid', client.account_id)
            .put_password(client.encodedpass)
            .put_definer('user', user.account_id).finish()
        )
        resp = await http.request(route, parameters)
        if resp != 1:
            raise MissingAccess(message='Failed to (un)block a user: {!r}.'.format(user))


    async def unfriend_user(self, user, *, client):
        parameters = (
            Params().create_new().put_definer('accountid', client.account_id)
            .put_password(client.encodedpass).put_definer('user', user.account_id).finish()
        )
        resp = await http.request(Route.REMOVE_FRIEND, parameters)
        if resp != 1:
            raise MissingAccess(message='Failed to unfriend a user: {!r}.'.format(user))


    async def send_message(self, target, subject: str, body: str, *, client):
        parameters = (
            Params().create_new().put_definer('accountid', client.account_id)
            .put_message(subject, body).put_recipient(target.account_id)
            .put_password(client.encodedpass).finish()
        )
        resp = await http.request(Route.SEND_PRIVATE_MESSAGE, parameters)
        if resp != 1:
            raise MissingAccess(message='Failed to send a message to a user: {!r}.'.format(target))


    async def update_profile(self, settings: Dict[str, int], *, client):
        settings_cased = {Converter.snake_to_camel(name): value for name, value in settings.items()}

        rs = Coder.gen_rs()

        req_chk_params = [client.account_id]
        for param in (
            'user_coins', 'demons', 'stars', 'coins', 'icon_type',
            'icon', 'diamonds', 'acc_icon', 'acc_ship', 'acc_ball',
            'acc_bird', 'acc_dart', 'acc_robot', 'acc_glow',
            'acc_spider', 'acc_explosion'
        ):
            req_chk_params.append(settings[param])

        chk = Coder.gen_chk(type='userscore', values=req_chk_params)

        parameters = (
            Params().create_new().put_definer('accountid', client.account_id)
            .put_password(client.encodedpass).put_username(client.name)
            .put_seed(rs).put_seed(chk, suffix=str(2)).finish()
        )

        parameters.update(settings_cased)

        resp = await http.request(Route.UPDATE_USER_SCORE, parameters)

        if not resp > 0:
            raise MissingAccess(message='Failed to update profile of a client: {!r}'.format(client))


    async def update_settings(
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
            raise MissingAccess(message='Failed to update profile settings of a client: {!r}.'.format(client))


    async def run_many(self, tasks):
        res = await asyncio.gather(*tasks)

        res = [elem for elem in res if elem]

        if all(isinstance(elem, list) for elem in res):
            res = list(itertools.chain.from_iterable(res))

        return res


def _is_not_empty(sequence):
    return bool(len(sequence))

_session = GDSession()
