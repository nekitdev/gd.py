class Filters:
    def __init__(self, **options):
        self.diff = {
            'N/A': '-1',
            'Easy': '1',
            'Normal': '2',
            'Hard': '3',
            'Harder': '4',
            'Insane': '5',
            'Demon': '-1'
        }
        self.demonFilter = {
            'Easy': '1',
            'Medium': '2',
            'Hard': '3',
            'Insane': '4',
            'Extreme': '5'
        }
        self.search_strategy = {
            'regular': '0',
            'most_downloaded': '1',
            'most_liked': '2',
            'trending': '3',
            'recent': '4',
            'by_user': '5',
            'featured': '6',
            'magic': '7',
            'awarded': '11',
            'followed': '12',
            'hall_of_fame': '16'
        }
        #I would finish it this week
