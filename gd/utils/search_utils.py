from .errors import error

def indexall(iterable, item):
    import builtins
    data = []
    item = item.lower() if (type(item) is str) else item
    res = list(iterable)
    if any(type(e).__name__ not in dir(builtins) for e in res): # if object is an instance of not built-in class
        attr = {
            type(item) is int: 'account_id',
            type(item) is str: 'name'
        }.get(True)
        res = [getattr(elem, attr) for elem in res]
    for element in res:
        run_thing(data, res, element, item)
    return data

def run_thing(data, res, elem, item):
    if type(item) in [int, bool]:
        if item == elem:
            data.append(res.index(elem))
    if type(item) is str:
        if str(elem).lower().startswith(item):
            data.append(res.index(elem))

def search(iterable, **kwargs):
    _strategy = list(kwargs.keys())[0]
    _search = list(kwargs.values())[0]
    if (_strategy is None) or (_search is None):
        raise error.MissingArguments()
    mapped = []
    for i in range(len(iterable)):
        attr = getattr(iterable[i], _strategy)
        if callable(attr):
            mapped.append(attr())
        else:
            mapped.append(attr)
    indexes = indexall(mapped, _search)
    final_res = [iterable[_index] for _index in indexes]
    return final_res[0] if len(final_res) is 1 else final_res