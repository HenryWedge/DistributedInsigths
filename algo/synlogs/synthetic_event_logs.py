import datetime

from algo.event import Event
from algo.event_log import EventLog


class SyntheticEventLogs:

    def get_training_data(self):
        event_log = EventLog()
        t = datetime.now()
        # Case c1
        event_log.add_event(Event(case_id="c1", activity="A", location="N1", time=t + datetime.timedelta(0, 1)))
        event_log.add_event(Event(case_id="c1", activity="B", location="N3", time=t + datetime.timedelta(0, 2)))
        event_log.add_event(Event(case_id="c1", activity="C", location="N1", time=t + datetime.timedelta(0, 3)))
        event_log.add_event(Event(case_id="c1", activity="D", location="N4", time=t + datetime.timedelta(0, 4)))
        event_log.add_event(Event(case_id="c1", activity="A", location="N1", time=t + datetime.timedelta(0, 5)))
        event_log.add_event(Event(case_id="c1", activity="E", location="N2", time=t + datetime.timedelta(0, 6)))
        event_log.add_event(Event(case_id="c1", activity="F", location="N1", time=t + datetime.timedelta(0, 7)))

        # Case c2
        event_log.add_event(Event(case_id="c2", activity="A", location="N2", time=t + datetime.timedelta(0, 8)))
        event_log.add_event(Event(case_id="c2", activity="G", location="N5", time=t + datetime.timedelta(0, 9)))
        event_log.add_event(Event(case_id="c2", activity="H", location="N6", time=t + datetime.timedelta(0, 10)))
        event_log.add_event(Event(case_id="c2", activity="C", location="N1", time=t + datetime.timedelta(0, 11)))
        event_log.add_event(Event(case_id="c2", activity="D", location="N4", time=t + datetime.timedelta(0, 12)))
        event_log.add_event(Event(case_id="c2", activity="I", location="N7", time=t + datetime.timedelta(0, 13)))
        event_log.add_event(Event(case_id="c2", activity="F", location="N1", time=t + datetime.timedelta(0, 14)))

        # Case c3
        event_log.add_event(Event(case_id="c3", activity="B", location="N3", time=t + datetime.timedelta(0, 15)))
        event_log.add_event(Event(case_id="c3", activity="C", location="N1", time=t + datetime.timedelta(0, 16)))
        event_log.add_event(Event(case_id="c3", activity="J", location="N8", time=t + datetime.timedelta(0, 17)))
        event_log.add_event(Event(case_id="c3", activity="D", location="N4", time=t + datetime.timedelta(0, 18)))
        event_log.add_event(Event(case_id="c3", activity="E", location="N2", time=t + datetime.timedelta(0, 19)))
        event_log.add_event(Event(case_id="c3", activity="K", location="N6", time=t + datetime.timedelta(0, 20)))
        event_log.add_event(Event(case_id="c3", activity="F", location="N1", time=t + datetime.timedelta(0, 21)))

        # Case c4
        event_log.add_event(Event(case_id="c4", activity="A", location="N1", time=t + datetime.timedelta(0, 22)))
        event_log.add_event(Event(case_id="c4", activity="L", location="N5", time=t + datetime.timedelta(0, 23)))
        event_log.add_event(Event(case_id="c4", activity="C", location="N1", time=t + datetime.timedelta(0, 24)))
        event_log.add_event(Event(case_id="c4", activity="D", location="N4", time=t + datetime.timedelta(0, 25)))
        event_log.add_event(Event(case_id="c4", activity="M", location="N7", time=t + datetime.timedelta(0, 26)))
        event_log.add_event(Event(case_id="c4", activity="E", location="N2", time=t + datetime.timedelta(0, 27)))
        event_log.add_event(Event(case_id="c4", activity="F", location="N1", time=t + datetime.timedelta(0, 28)))

        # Case c5
        event_log.add_event(Event(case_id="c5", activity="B", location="N3", time=t + datetime.timedelta(0, 29)))
        event_log.add_event(Event(case_id="c5", activity="A", location="N1", time=t + datetime.timedelta(0, 30)))
        event_log.add_event(Event(case_id="c5", activity="C", location="N1", time=t + datetime.timedelta(0, 31)))
        event_log.add_event(Event(case_id="c5", activity="G", location="N5", time=t + datetime.timedelta(0, 32)))
        event_log.add_event(Event(case_id="c5", activity="D", location="N4", time=t + datetime.timedelta(0, 33)))
        event_log.add_event(Event(case_id="c5", activity="E", location="N2", time=t + datetime.timedelta(0, 34)))
        event_log.add_event(Event(case_id="c5", activity="F", location="N1", time=t + datetime.timedelta(0, 35)))

        # Case c6
        event_log.add_event(Event(case_id="c6", activity="A", location="N2", time=t + datetime.timedelta(0, 36)))
        event_log.add_event(Event(case_id="c6", activity="H", location="N6", time=t + datetime.timedelta(0, 37)))
        event_log.add_event(Event(case_id="c6", activity="C", location="N1", time=t + datetime.timedelta(0, 38)))
        event_log.add_event(Event(case_id="c6", activity="I", location="N7", time=t + datetime.timedelta(0, 39)))
        event_log.add_event(Event(case_id="c6", activity="D", location="N4", time=t + datetime.timedelta(0, 40)))
        event_log.add_event(Event(case_id="c6", activity="E", location="N2", time=t + datetime.timedelta(0, 41)))
        event_log.add_event(Event(case_id="c6", activity="F", location="N1", time=t + datetime.timedelta(0, 42)))

    def get_validation_log_perfect_fit(self, t):
        event_log = EventLog()
        case_id = "v1"
        event_log.add_event(Event(case_id=case_id, activity="A", location="N1", time=t + datetime.timedelta(0, 1)))
        event_log.add_event(Event(case_id=case_id, activity="B", location="N3", time=t + datetime.timedelta(0, 2)))
        event_log.add_event(Event(case_id=case_id, activity="C", location="N1", time=t + datetime.timedelta(0, 3)))
        event_log.add_event(Event(case_id=case_id, activity="D", location="N4", time=t + datetime.timedelta(0, 4)))
        event_log.add_event(Event(case_id=case_id, activity="A", location="N1", time=t + datetime.timedelta(0, 5)))
        event_log.add_event(Event(case_id=case_id, activity="E", location="N2", time=t + datetime.timedelta(0, 6)))
        event_log.add_event(Event(case_id=case_id, activity="F", location="N1", time=t + datetime.timedelta(0, 7)))

    def get_validation_log_skip_start(event_log, t):
        event_log = EventLog()
        case_id = "v2"
        event_log.add_event(Event(case_id=case_id, activity="B", location="N3", time=t + datetime.timedelta(0, 1)))
        event_log.add_event(Event(case_id=case_id, activity="C", location="N1", time=t + datetime.timedelta(0, 2)))
        event_log.add_event(Event(case_id=case_id, activity="D", location="N4", time=t + datetime.timedelta(0, 3)))
        event_log.add_event(Event(case_id=case_id, activity="A", location="N1", time=t + datetime.timedelta(0, 4)))
        event_log.add_event(Event(case_id=case_id, activity="E", location="N2", time=t + datetime.timedelta(0, 5)))
        event_log.add_event(Event(case_id=case_id, activity="F", location="N1", time=t + datetime.timedelta(0, 6)))

    def get_validation_log_skip_end(event_log, t):
        event_log = EventLog()
        case_id = "v3"
        event_log.add_event(Event(case_id=case_id, activity="A", location="N1", time=t + datetime.timedelta(0, 1)))
        event_log.add_event(Event(case_id=case_id, activity="B", location="N3", time=t + datetime.timedelta(0, 2)))
        event_log.add_event(Event(case_id=case_id, activity="C", location="N1", time=t + datetime.timedelta(0, 3)))
        event_log.add_event(Event(case_id=case_id, activity="D", location="N4", time=t + datetime.timedelta(0, 4)))
        event_log.add_event(Event(case_id=case_id, activity="A", location="N1", time=t + datetime.timedelta(0, 5)))

    def get_validation_log_additional_events(event_log, t):
        event_log = EventLog()
        case_id = "v4"
        event_log.add_event(Event(case_id=case_id, activity="A", location="N1", time=t + datetime.timedelta(0, 1)))
        event_log.add_event(Event(case_id=case_id, activity="B", location="N3", time=t + datetime.timedelta(0, 2)))
        event_log.add_event(Event(case_id=case_id, activity="C", location="N1", time=t + datetime.timedelta(0, 3)))
        event_log.add_event(Event(case_id=case_id, activity="J", location="N8", time=t + datetime.timedelta(0, 4)))
        event_log.add_event(Event(case_id=case_id, activity="D", location="N4", time=t + datetime.timedelta(0, 5)))
        event_log.add_event(Event(case_id=case_id, activity="A", location="N1", time=t + datetime.timedelta(0, 6)))
        event_log.add_event(Event(case_id=case_id, activity="E", location="N2", time=t + datetime.timedelta(0, 7)))
        event_log.add_event(Event(case_id=case_id, activity="K", location="N6", time=t + datetime.timedelta(0, 8)))
        event_log.add_event(Event(case_id=case_id, activity="F", location="N1", time=t + datetime.timedelta(0, 9)))

    def get_validation_log_unseen_behavior(event_log, t):
        event_log = EventLog()
        case_id = "v5"
        event_log.add_event(Event(case_id=case_id, activity="A", location="N1", time=t + datetime.timedelta(0, 1)))
        event_log.add_event(Event(case_id=case_id, activity="B", location="N3", time=t + datetime.timedelta(0, 2)))
        event_log.add_event(Event(case_id=case_id, activity="L", location="N5", time=t + datetime.timedelta(0, 3)))  # neu
        event_log.add_event(Event(case_id=case_id, activity="M", location="N7", time=t + datetime.timedelta(0, 4)))  # neu
        event_log.add_event(Event(case_id=case_id, activity="C", location="N1", time=t + datetime.timedelta(0, 5)))
        event_log.add_event(Event(case_id=case_id, activity="D", location="N4", time=t + datetime.timedelta(0, 6)))
        event_log.add_event(Event(case_id=case_id, activity="E", location="N2", time=t + datetime.timedelta(0, 7)))
        event_log.add_event(Event(case_id=case_id, activity="F", location="N1", time=t + datetime.timedelta(0, 8)))

    def get_validation_log_two_model_moves(event_log, t):
        event_log = EventLog()
        case_id = "v6"
        event_log.add_event(Event(case_id=case_id, activity="A", location="N1", time=t + datetime.timedelta(0, 1)))
        event_log.add_event(Event(case_id=case_id, activity="B", location="N3", time=t + datetime.timedelta(0, 2)))
        event_log.add_event(Event(case_id=case_id, activity="D", location="N4", time=t + datetime.timedelta(0, 3)))  # C fehlt
        event_log.add_event(Event(case_id=case_id, activity="E", location="N2", time=t + datetime.timedelta(0, 4)))  # A fehlt
        event_log.add_event(Event(case_id=case_id, activity="F", location="N1", time=t + datetime.timedelta(0, 5)))

    def get_validation_log_wrong_location(event_log, t):
        event_log = EventLog()
        case_id = "v7"
        event_log.add_event(Event(case_id=case_id, activity="A", location="N1", time=t + datetime.timedelta(0, 1)))
        event_log.add_event(Event(case_id=case_id, activity="B", location="N3", time=t + datetime.timedelta(0, 2)))
        event_log.add_event(Event(case_id=case_id, activity="C", location="N1", time=t + datetime.timedelta(0, 3)))
        event_log.add_event(Event(case_id=case_id, activity="D", location="N7", time=t + datetime.timedelta(0, 4)))  # falsch
        event_log.add_event(Event(case_id=case_id, activity="A", location="N1", time=t + datetime.timedelta(0, 5)))
        event_log.add_event(Event(case_id=case_id, activity="E", location="N2", time=t + datetime.timedelta(0, 6)))
        event_log.add_event(Event(case_id=case_id, activity="F", location="N1", time=t + datetime.timedelta(0, 7)))
