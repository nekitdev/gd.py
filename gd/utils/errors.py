class error:
    class IDNotSpecified(Exception):
        def __init__(self, _type):
            self.reply = f"ID for '{_type}' was not specified."
            Exception.__init__(self, self.reply)

    class MissingAccess(Exception):
        def __init__(self, **params):
            _type = params.get('type')
            _id = params.get('id')
            self.reply = f"No access to '{_type}' with ID: '{_id}'."
            Exception.__init__(self, self.reply)
    
    class SongRestrictedForUsage(Exception):
        def __init__(self, _id):
            self.reply = f"Song with id '{_id}' is not allowed for use."
            Exception.__init__(self, self.reply)
            
    class PagesOutOfRange(Exception):
        def __init__(self, **params):
            _page_num = params.get('page')
            _info = params.get('info')
            if str(_info).isdigit():
                self.reply = f"Pages are out of range. Requested page: '{_page_num}', Pages existing: '{_info}'"
            else:
                self.reply = f"{_info} Requested page: '{_page_num}'"
            Exception.__init__(self, self.reply)
    
    class PaginatorIsEmpty(Exception):
        def __init__(self):
            self.reply = "<'gd.Paginator' object> has no elements to operate with..."
            Exception.__init__(self, self.reply)

    class FailedLogin(Exception):
        def __init__(self, **params):
            _login = params.get('login')
            _password = params.get('password')
            self.reply = f"Failed to login with <login='{_login}', password='{_password}'>."
            Exception.__init__(self, self.reply)
    
    class NothingFound(Exception):
        def __init__(self, _type):
            self.reply = f'No {_type} were found.'
            Exception.__init__(self, self.reply)
            
    class InvalidArgument(Exception):
        pass #finish this one

    class TooManyArguments(Exception):
        pass #yeah oof

    class MissingArguments(Exception):
        pass #Oly is lit
