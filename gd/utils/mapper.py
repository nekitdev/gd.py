class mapper_util:
    def map(item):
        res = {}
        for i in range(0, len(item), 2):
            new = item[i+1]
            new = new if not _is_str_digit(new) else int(new)
            res[int(item[i])] = new
        return res

    def normalize(item):
        res = str(item).replace('-', '+').replace('_', '/')
        return _pad(res)

    def prepare_sending(item):
        res = str(item).replace('+', '-').replace('/', '_')
        return _pad(res)

def _pad(res: str):
    # pad a string to be divisible by 4
    ilen = len(res)/4

    if not ilen.is_integer():
        n = _ceil(ilen)*4 - len(res)

        res += '=' * n

    return res

def _ceil(n: float):
    x = round(n)
    return x+1 if x < n else x

def _is_str_digit(string: str):
    return string.replace('-', '').isdigit()
