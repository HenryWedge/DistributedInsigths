from datetime import datetime

Activity = str


class Event:
    def __init__(self, case_id, activity, location, time):
        self.activity: Activity = activity
        self.location: str = location
        self.time: datetime = time
        self.case_id: str = case_id
