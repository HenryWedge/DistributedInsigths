from algo.alignment_timestamped import AlignmentTimestamped
from algo.context import Context
from algo.new_trie import NewTrie


class StateItem:

    def __init__(
        self,
        cost: int,
        trie: NewTrie,
        alignment: AlignmentTimestamped,
        last_activities: Context[str]
    ):
        self.trie: NewTrie = trie
        self.last_activity: Context[str] = last_activities
        self.alignment: AlignmentTimestamped = alignment
        self.cost: int = self.alignment.alignment.cost

    def __str__(self):
        return f"Cost: {self.cost}\n{self.alignment}\n{self.trie}"

    def __lt__(self, other):
        return self.cost < other.cost
