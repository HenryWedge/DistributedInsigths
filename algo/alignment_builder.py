from copy import deepcopy

from algo.alignment_timestamped import AlignmentInformation
from algo.event import Event
from algo.state_explorer import StateExplorer
from algo.state_item import StateItem
from algo.trie_node import Node
from algo.trie_traverser import TrieTraverser

class AlignmentBuilder:
    def build_alignment(self, event: Event, state_explorer: StateExplorer):
        this_states: StateExplorer =  deepcopy(state_explorer)
        while not this_states.is_empty():
            state: StateItem = this_states.get_next_state()
            if event.activity in state.trie.next_items():
                self._sync_move(event, state, state_explorer)
            else:
                self._log_move(event, state, state_explorer)
                self._model_move(event, state, state_explorer)

    def _sync_move(self, event: Event, state: StateItem, state_explorer: StateExplorer):
        current_alignment = self._move_event_data_to_alignment(event, state)
        activity = event.activity
        current_alignment.alignment.sync_move(activity)
        new_state = StateItem(state.trie.traverse(activity), current_alignment)
        state_explorer.insert_state(new_state)

    def _log_move(self, event: Event, state: StateItem, state_explorer: StateExplorer):
        current_alignment = self._move_event_data_to_alignment(event, state)
        activity = event.activity
        current_alignment.alignment.log_move(activity)
        new_state = StateItem(state.trie, current_alignment)
        state_explorer.insert_state(new_state)

    def _model_move(self, event: Event, state: StateItem, state_explorer: StateExplorer):
        current_alignment = self._move_event_data_to_alignment(event, state)
        activity = event.activity
        current_alignment.alignment.model_move(activity)
        trie_traverser = TrieTraverser(state.trie)
        new_trie, cost = trie_traverser.find_activity_in_trie(activity)
        new_state = StateItem(new_trie, current_alignment)
        state_explorer.insert_state(new_state)

    def _move_event_data_to_alignment(self, event: Event, state: StateItem) -> AlignmentInformation:
        current_alignment = deepcopy(state.alignment)
        current_alignment.timestamp = event.time
        current_alignment.node = Node(event.location)
        return current_alignment