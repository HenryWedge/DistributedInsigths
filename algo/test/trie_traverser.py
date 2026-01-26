import unittest

from algo.new_trie import NewTrie, TrieBuilder
from algo.trie_node import Activity
from algo.trie_traverser import TrieTraverser


class TrieTraverserTest(unittest.TestCase):

    def test_trie_traverser(self):
        trie = NewTrie()
        trie_builder = TrieBuilder(trie)
        trie_builder.insert(Activity("A"))
        trie_builder.insert(Activity("C"))
        trie_builder.reset()
        trie_builder.insert(Activity("A"))
        trie_builder.insert(Activity("D"))
        trie_traverser = TrieTraverser(trie)
        print(trie_traverser.find_activity_in_trie(Activity("D")))

if __name__ == '__main__':
    unittest.main()
