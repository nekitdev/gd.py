import urllib.request
from urllib.request import urlopen

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
    
    def SendHTTPRequest(php, params):
        base_url = "http://www.boomlings.com/database/"
        url = base_url + php + ".php"
        url_parameters = http.StructParams(params)
        data = urlopen(url, url_parameters).read().decode()
        return data
