class Converter:
    def GetDifficulty(List):
        pass #LOOK AT: [11, 21, 25, 27]

    def GetLength(lengthint):
        some_dict = {
            "0": "Tiny",
            "1": "Short",
            "2": "Medium",
            "3": "Long",
            "4": "XL"
        }
        length = some_dict[lengthint]
        return length
    
    def write_per_page(**kwargs):
        if kwargs.get('paginate') is None:
            per_page = None
        else:
            if kwargs.get('per_page') is None:
                per_page = 10
            else:
                per_page = int(kwargs.get('per_page'))
        return per_page