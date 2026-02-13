from algo.alignment_timestamped import AlignmentTimestamped
from algo.new_trie import NewTrie


class StateItem:

    def __init__(
        self,
        cost: int,
        trie: NewTrie,
        alignment: AlignmentTimestamped,
        last_activity: str | None
    ):
        self.trie: NewTrie = trie
        self.last_activity: str = last_activity
        self.alignment: AlignmentTimestamped = alignment
        if self.alignment:
            self.cost: int = self.alignment.alignment.cost
        else:
            self.cost: int = 0

    def __str__(self):
        return f"Cost: {self.cost}\n{self.alignment}\n{self.trie}"

    def __lt__(self, other):
        return self.cost < other.cost
