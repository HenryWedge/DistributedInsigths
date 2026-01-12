from copy import deepcopy

from algo.alignment import Alignment
from algo.state_explorer import StateExplorer
from algo.state_item import StateItem
from algo.trie import Trie

class InsightAlgorithm:

    def __init__(self, trie: Trie):
        self.trie: Trie = trie
        self.state_explorer = StateExplorer()
        self.state_explorer.insert_state(StateItem(0, trie, Alignment()))

    def process_event(self, activity: str):
        state: StateItem = self.state_explorer.get_next_state()
        if activity in state.trie.next_items():
            self._sync_move(activity, state)

    def _sync_move(self, activity: str, state: StateItem):
        current_alignment = deepcopy(state.alignment)
        current_alignment.sync_move(activity)
        new_state = StateItem(state.cost, state.trie.traverse(activity), current_alignment)
        self.state_explorer.insert_state(new_state)

    def _log_move(self):
        pass

    def _model_move(self):
        pass