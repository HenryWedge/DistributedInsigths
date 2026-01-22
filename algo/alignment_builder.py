from copy import deepcopy
from typing import List

from algo.alignment_timestamped import AlignmentTimestamped
from algo.event import Event
from algo.state_explorer import StateExplorer
from algo.state_item import StateItem
from algo.trie_node import Node
from algo.trie_traverser import TrieTraverser

class AlignmentBuilder:

    def build_alignment(self, event: Event, state_explorer: StateExplorer) -> List[StateItem]:
        new_state_items: List[StateItem] = []
        while not state_explorer.is_empty():
            state: StateItem = state_explorer.get_next_state()
            if not state.trie:
                new_state_items.append(self._log_move(event, state))
            elif event.activity in state.trie.next_items():
                new_state_items.append(self._sync_move(event, state))
            else:
                new_state_items.append(self._log_move(event, state))
                model_move_state_item = self._model_move(event, state)
                if model_move_state_item:
                    new_state_items.append(model_move_state_item)
        return new_state_items

    def _sync_move(self, event: Event, state: StateItem):
        current_alignment = self._move_event_data_to_alignment(event, state)
        activity = event.activity
        current_alignment.alignment.sync_move(activity)
        return StateItem(state.cost, state.trie.traverse(activity), current_alignment)

    def _log_move(self, event: Event, state: StateItem):
        current_alignment = self._move_event_data_to_alignment(event, state)
        activity = event.activity
        current_alignment.alignment.log_move(activity)
        return StateItem(state.cost + 1, state.trie, current_alignment)

    def _model_move(self, event: Event, state: StateItem):
        current_alignment = self._move_event_data_to_alignment(event, state)
        activity = event.activity
        current_alignment.alignment.model_move(activity)
        trie_traverser = TrieTraverser(state.trie)
        new_trie, cost = trie_traverser.find_activity_in_trie(activity)
        if not new_trie:
            return None
        return StateItem(state.cost + cost, new_trie, current_alignment)

    def _move_event_data_to_alignment(self, event: Event, state: StateItem) -> AlignmentTimestamped:
        current_alignment = deepcopy(state.alignment)
        current_alignment.timestamp = event.time
        current_alignment.node = Node(event.location)
        return current_alignment