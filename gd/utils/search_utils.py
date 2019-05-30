from .errors import error

def indexall(iterable, item):
    data = []
    item = item.lower() if (type(item) is str) else item
    if (type(iterable) is not dict):
        res = list(iterable)
        for element in res:
            if str(item).isdigit() or type(item) is bool:
                if item == element:
                    data.append(res.index(element))
            else:
                if str(element).lower().startswith(item):
                    data.append(res.index(element))
    else:
        res1 = list(iterable.keys())
        res2 = list(iterable.values())
        for element in res2:
            if str(item).isdigit():
                if item == element:
                    data.append(
                        res1[res2.index(element)]
                    )
            else:
                if str(element).lower().startswith(item):
                    data.append(
                        res1[res2.index(element)]
                    )
    return data

def search(iterable, **kwargs):
    #1st-user's name, 2nd-user's account id, 3rd-user's player id
    _strategy = list(kwargs.keys())[0]
    _search = list(kwargs.values())[0]
    if (_strategy is None) or (_search is None):
        raise error.MissingArguments()
    try:
        mapped = [getattr(iterable[i], _strategy)() for i in range(len(iterable))]
    except TypeError:
        mapped = [getattr(iterable[i], _strategy) for i in range(len(iterable))]
    indexes = indexall(mapped, _search)
    final_res = [iterable[_index] for _index in indexes]
    return final_res[0] if len(final_res) is 1 else final_res
