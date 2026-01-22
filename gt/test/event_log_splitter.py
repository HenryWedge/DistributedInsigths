import unittest

from gt.event_log_splitter import EventLogSplitter
from utility.converter import Converter


class EventLogSplitterTest(unittest.TestCase):

    def test_event_log_splitter(self):
        testee = EventLogSplitter("datasets/Sepsis.xes")
        Converter().from_event_log(testee.get_training_data())
        print("Done")

if __name__ == '__main__':
    unittest.main()
