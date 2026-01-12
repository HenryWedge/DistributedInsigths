import unittest

from algo.insight_algorithm import InsightAlgorithm
from algo.trie import Trie


class InsightAlgorithmTestCase(unittest.TestCase):

    def test_sync_moves(self):
        trie = Trie()
        trie.insert(['A', 'B', 'C'])
        testee = InsightAlgorithm(trie)
        testee.process_event('A')
        testee.process_event('B')
        testee.process_event('C')
        print(testee.state_explorer.get_next_state().alignment)

    def test_log_moves(self):
        trie = Trie()
        trie.insert(['A', 'B', 'C'])
        testee = InsightAlgorithm(trie)
        testee.process_event('A')
        testee.process_event('B')
        testee.process_event('D')
        testee.process_event('C')
        print(testee.state_explorer.get_next_state().alignment)

    def test_model_moves(self):
        trie = Trie()
        trie.insert(['A', 'B', 'C'])
        testee = InsightAlgorithm(trie)
        testee.process_event('A')
        testee.process_event('C')
        for state in testee.state_explorer.get_all_states():
            print(state)

if __name__ == '__main__':
    unittest.main()
