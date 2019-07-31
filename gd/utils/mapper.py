class mapper_util:
    def map(item):
        res = {}
        for i in range(0, len(item), 2):
            new = item[i+1]
            new = new if not new.replace('-', '').isdigit() else int(new)
            res[int(item[i])] = new
        return res
        
    def normalize(item):
        res = str(item).replace('-', '+').replace('_', '=')
        return res
    
    def prepare_sending(item):
        res = str(item).replace('+', '-')
        return res