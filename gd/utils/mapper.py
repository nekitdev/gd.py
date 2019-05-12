class mapper_util:
    def map(item):
        res = {}
        for i in range(0, len(item), 2):
            res[item[i]] = item[i+1]
        return res