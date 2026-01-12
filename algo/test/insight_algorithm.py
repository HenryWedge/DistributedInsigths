import unittest

from algo.insight_algorithm import InsightAlgorithm
from algo.trie import Trie


class InsightAlgorithmTestCase(unittest.TestCase):

    def test_sync_moves(self):
        trie = Trie()
        trie.insert(['A', 'B', 'C'])
        trie.insert(['A', 'B', 'D'])
        testee = InsightAlgorithm(trie)
        testee.process_event('A')
        testee.process_event('B')
        testee.process_event('C')
        print(testee.state_explorer.get_next_state().alignment)

if __name__ == '__main__':
    unittest.main()
