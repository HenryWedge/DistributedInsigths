from algo.alignment_timestamped import AlignmentTimestamped
from algo.trie import Trie

class StateItem:

    def __init__(
        self,
        cost: int,
        trie: Trie,
        alignment: AlignmentTimestamped,
        last_activity: str | None
    ):
        self.cost: int = cost
        self.trie: Trie = trie
        self.last_activity: str = last_activity
        self.alignment: AlignmentTimestamped = alignment

    def __str__(self):
        return f"Cost: {self.cost}\n{self.alignment}\n{self.trie}"

    def __lt__(self, other):
        return self.cost < other.cost
