from algo.alignment import Alignment
from algo.trie import Trie

class StateItem:

    def __init__(
        self,
        cost: int,
        trie: Trie,
        alignment: Alignment
    ):
        self.cost = cost
        self.trie: Trie = trie
        self.alignment: Alignment = alignment

    def __lt__(self, other):
        return self.cost < other.cost
