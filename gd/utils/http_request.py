import urllib.request
from urllib.request import urlopen
from urllib.request import Request

class http:
    def StructParams(params):
        FinalParams = ""
        for value in params:
            if value == "secret":
                FinalParams += value + "=" + params[value]
            else:
                FinalParams += value + "=" + params[value] + "&"
        FinalParams = FinalParams.encode()
        return FinalParams
    
    def SendHTTPRequest(php, params = None, cookies: str = None, cookie: str = None):
        base_url = "http://www.boomlings.com/database/"
        url = base_url + php + ".php"; url_parameters = None
        if params is not None:
            url_parameters = http.StructParams(params)
        req = Request(url) if url_parameters is None else Request(url, url_parameters)
        if cookies is 'add':
            req.add_header('Cookie', cookie)
        r = urlopen(req); data = r.read()
        try:
            res = data.decode()
        except UnicodeDecodeError:
            res = data
        if cookies is 'get':
            c = r.info().get('Set-Cookie').split('; ')[0]
            return res, c
        return res 
