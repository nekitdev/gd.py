from .errors import error

def indexall(iterable, item):
    data = []
    if (type(iterable) is not dict):
        res = list(iterable)
        for i in range(res.count(item)):
            data.append(res.index(item)+i)
            res.remove(item)
    else:
        res1 = list(iterable.keys())
        res2 = list(iterable.values())
        for i in range(res2.count(item)):
            data.append(
                res1[(res2.index(item)+i)]
            )
            res2.remove(item)
    return data

def select_name(iterable):
    return iterable[0]
def select_account_id(iterable):
    return iterable[1]
def select_id(iterable):
    return iterable[2]

def search(iterable, **kwargs):
    #1st-user's name, 2nd-user's account id, 3rd-user's player id
    _name = kwargs.get('name')
    _id = kwargs.get('id')
    _account_id = kwargs.get('account_id')
    account_ids = []
    for _tuple in iterable:
        account_ids.append(_tuple[1])
    if _account_id is None:
        if _id is None:
            if _name is None:
                raise error.MissingArguments()
            else:
                mapped = map(select_name, iterable)
                indexes = indexall(mapped, _name)
        else:
            mapped = map(select_id, iterable)
            indexes = indexall(mapped, _id)
    else:
        mapped = map(select_account_id, iterable)
        indexes = indexall(mapped, _account_id)
    final_res = []
    for _index in indexes:
        final_res.append(account_ids[_index])
    return final_res
