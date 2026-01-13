import unittest

from algo.insight_algorithm import InsightAlgorithm
from algo.trie import Trie
from algo.trie_node import Activity


class InsightAlgorithmTestCase(unittest.TestCase):

    def test_sync_moves(self):
        trie = Trie()
        trie.insert_trace([Activity('A'), Activity('B'), Activity('C')])
        testee = InsightAlgorithm(trie)
        testee.process_event(Activity('A'))
        testee.process_event(Activity('B'))
        testee.process_event(Activity('C'))
        print(testee.state_explorer.get_next_state().alignment)

    def test_log_moves(self):
        trie = Trie()
        trie.insert_trace([Activity('A'), Activity('B'), Activity('C')])
        testee = InsightAlgorithm(trie)
        testee.process_event(Activity('A'))
        testee.process_event(Activity('B'))
        testee.process_event(Activity('D'))
        testee.process_event(Activity('C'))
        print(testee.state_explorer.get_next_state().alignment)

    def test_model_moves(self):
        trie = Trie()
        trie.insert_trace([Activity('A'), Activity('B'), Activity('C')])
        testee = InsightAlgorithm(trie)
        testee.process_event(Activity('A'))
        testee.process_event(Activity('C'))
        for state in testee.state_explorer.get_all_states():
            print(state)

if __name__ == '__main__':
    unittest.main()
