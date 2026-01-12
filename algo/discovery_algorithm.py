from typing import List

from algo.trie import Trie

class DiscoveryAlgorithm:
    def __init__(self):
        self.trie: Trie = Trie()

    def process_trace(self, trace: List[str]):
        self.trie.insert(trace)

    def get_trie(self):
        return self.trie
