#from .errors import error
class check:
    def run_search_check(some_dict):
        arglist = list(some_dict.keys())
        for element in arglist:
            if element not in ['query', 'id_mode', 'limit']:
                raise error.InvalidArgument()
            else:
                pass
        if 'query' not in arglist:
            raise error.MissingArguments()
        else:
            if 'id_mode' in arglist:
                if not isinstance(some_dict.get('id_mode'), bool):
                    raise error.InvalidArgument()
                else:
                    mode = some_dict.get('id_mode')
            else:
                mode = False
            if 'limit' in arglist:
                if not isinstance(some_dict.get('limit'), int):
                    raise error.InvalidArgument()
                else:
                    limit = some_dict.get('limit')
            else:
                limit = 100
            return [True, mode, limit]
