from algo.trie_node import Activity


class Event:

    def __init__(self, activity, location, time):
        self.activity: Activity = activity
        self.location: str = location
        self.time: int = time
