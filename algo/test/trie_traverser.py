import unittest

from algo.trie import Trie
from algo.trie_traverser import TrieTraverser


class TrieTraverserTest(unittest.TestCase):

    def test_trie_traverser(self):
        trie = Trie()
        trie.insert_trace(["A", "B", "C", "D"])
        trie.insert_trace(["A", "B", "C", "E"])
        trie_traverser = TrieTraverser(trie)
        print(trie_traverser.find_activity_in_trie("E"))

if __name__ == '__main__':
    unittest.main()
