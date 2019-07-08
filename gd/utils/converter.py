class Converter:
    """Some weird class where NeKit holds his converters for everything"""

    def convert_difficulty(value1, value2, value3):
        pass

    def convert_length(value):
        some_dict = {
            "0": "Tiny",
            "1": "Short",
            "2": "Medium",
            "3": "Long",
            "4": "XL"
        }
        length = some_dict.get(value)
        return length

    def to_ordinal(number):
        sn = str(number)
        cases = {
            sn.endswith('1'): 'st',
            sn.endswith('2'): 'nd',
            sn.endswith('3'): 'rd'
        }
        res = sn + cases.get(True, 'th')
        return res