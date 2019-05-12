class Comment:
    def __init__(self, **options):
        self._body = options.get('body')
        self._rating = options.get('rating')
        self._timestamp = options.get('timestamp')
        self._id = options.get('commentid')
        self._author = options.get('author')
    def __str__(self):
        ret = f'[gd.Comment]\n[ID:{self.id}]\n[Rating:{self.rating}]\n[Timestamp:{self.timestamp}]\n[Body:{self.body}]\n[Author:{self.author_name}]'
    @property
    def body(self):
        return self._body
    @property
    def rating(self):
        return self._rating
    @property
    def timestamp(self):
        return self._timestamp
    @property
    def id(self):
        return self._id
    @property
    def author_name(self):
        return self._author.name
    @property
    def author(self):
        return self._author
        
    def is_disliked(self):
        return abs(self.rating) != self.rating