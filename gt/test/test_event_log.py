import unittest
from datetime import datetime, timedelta

from algo.event import Event
from algo.event_log import EventLog


class TestEventLog(unittest.TestCase):

    def get_training_data(self):
        event_log = EventLog()
        t = datetime.now()
        event_log.add_event(Event(case_id="1",location="N1",activity="A",time=t))
        event_log.add_event(Event(case_id="1",location="N2",activity="B",time=t + timedelta(0,1)))
        event_log.add_event(Event(case_id="1",location="N1",activity="C",time=t + timedelta(0,2)))
        event_log.add_event(Event(case_id="1",location="N2",activity="D",time=t + timedelta(0,3)))
        event_log.add_event(Event(case_id="1",location="N1",activity="E",time=t + timedelta(0,4)))
        return event_log

    def get_test_data(self):
        event_log = EventLog()
        t = datetime.now()
        event_log.add_event(Event(case_id="1", location="N1", activity="A", time=t))
        event_log.add_event(Event(case_id="1", location="N2", activity="B", time=t + timedelta(0, 1)))
        event_log.add_event(Event(case_id="1", location="N1", activity="C", time=t + timedelta(0, 2)))
        event_log.add_event(Event(case_id="1", location="N2", activity="D", time=t + timedelta(0, 3)))
        event_log.add_event(Event(case_id="1", location="N1", activity="E", time=t + timedelta(0, 4)))
        return event_log


