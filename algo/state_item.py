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

    def __str__(self):
        return f"Cost: {self.cost}\n{self.alignment}\n{self.trie}"

    def __lt__(self, other):
        return self.cost < other.cost
