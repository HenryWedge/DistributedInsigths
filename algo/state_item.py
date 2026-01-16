from algo.alignment_timestamped import AlignmentInformation
from algo.trie import Trie

class StateItem:

    def __init__(
        self,
        trie: Trie,
        alignment_information: AlignmentInformation
    ):
        self.trie: Trie = trie
        self.alignment: AlignmentInformation = alignment_information

    def get_timestamp(self):
        return self.alignment.timestamp

    def __str__(self):
        return f"Cost: {self.alignment.alignment.cost}\n{self.alignment}\n{self.trie}"

    def get_cost(self):
        return self.alignment.alignment.cost

    def __lt__(self, other):
        return self.get_cost() < other.get_cost()

    def __eq__(self, other):
        return self.trie == other.trie and self.alignment == other.alignment
