import unittest

from algo.trie import Trie


class TrieTest(unittest.TestCase):

    def test_build_trie(self):
        testee = Trie()
        testee.insert_trace(["A"])
        testee.insert_trace(["A", "B"])
        testee.insert_trace(["A", "B", "D"])
        testee.insert_trace(["A", "C", "D"])
        testee.insert_trace(["A", "C", "E"])
        testee.insert_trace(["B", "E", "G", "F"])
        testee.annotate_path_to_end_cost(testee.data)
        print(testee.next_items())
        print(testee.next_children())
        print(testee.get_rest_cost().min_cost)
        print(testee.get_rest_cost().avg_cost)

if __name__ == '__main__':
    unittest.main()
