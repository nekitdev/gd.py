class AbstractEntity:
    def __init__(self, **options):
        self._id = options.get('id', 0)

    def __str__(self):
        res = f'[AbstractEntity]\n[ID:{self.id}]'
        return res
    
    def __repr__(self):
        ret = f'<gd.AbstractEntity: id={self.id}>'
        return ret
    
    @property
    def id(self):
        return self._id