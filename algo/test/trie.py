import unittest

from algo.trie import Trie


class TrieTest(unittest.TestCase):

    def test_build_trie(self):
        testee = Trie()
        testee.insert(["A"])
        testee.insert(["A", "B"])
        testee.insert(["A", "B", "D"])
        testee.insert(["A", "C", "D"])
        testee.insert(["A", "C", "E"])
        testee.insert(["B", "E", "G", "F"])
        testee.annotate_path_to_end_cost(testee.data)
        print(testee.next_items())
        print(testee.next_children())
        print(testee.get_rest_cost().min_cost)
        print(testee.get_rest_cost().avg_cost)

if __name__ == '__main__':
    unittest.main()
