from algo.trie_node import Activity


class Event:

    def __init__(self, case_id, activity, location, time):
        self.activity: Activity = activity
        self.location: str = location
        self.time: int = time
        self.case_id: str = case_id
