from copy import deepcopy
from typing import List

from algo.alignment import LOG_MOVE_COST, MDL_MOVE_COST
from algo.alignment_timestamped import AlignmentTimestamped
from algo.state_explorer import StateExplorer
from algo.state_item import StateItem
from algo.trie_node import Node, TrieNode
from algo.trie_traverser import TrieTraverser

class AlignmentBuilder:

    def build_alignment(self, node: TrieNode, time, state_explorer: StateExplorer) -> List[StateItem]:
        new_state_items: List[StateItem] = []
        while not state_explorer.is_empty():
            state: StateItem = state_explorer.get_next_state()
            if not node.is_activity() and state.last_activity == node.get_activity():
                if state.trie and state.trie.has_child_with_label(node):
                    state.trie = state.trie.traverse(Node(node.content, node.get_activity()))
                new_state_items.append(state)
                continue
            if not state.trie:
                new_state_items.append(self._log_move(node, time, state))
            elif state.trie.has_child_with_label(node):
                new_state_items.append(self._sync_move(node, time, state))
            else:
                new_state_items.append(self._log_move(node, time, state))
                new_state_items.extend(self._model_move_v2(node, time, state))
        return new_state_items

    def _sync_move(self, node: TrieNode, time, state: StateItem):
        current_alignment = self._move_event_data_to_alignment(node, time, state)
        current_alignment.alignment.sync_move(node)
        return StateItem(state.cost, state.trie.traverse(node), current_alignment, node.get_activity())

    def _log_move(self, node: TrieNode, time, state: StateItem):
        current_alignment = self._move_event_data_to_alignment(node, time, state)
        current_alignment.alignment.log_move(node)
        return StateItem(state.cost + LOG_MOVE_COST, state.trie, current_alignment, node.get_activity())

    def _model_move(self, node: TrieNode, time, state: StateItem):
        current_alignment = self._move_event_data_to_alignment(node, time, state)
        trie_traverser = TrieTraverser(state.trie)

        new_trie, cost = trie_traverser.find_activity_in_trie(node)
        current_alignment.alignment.model_move(node, cost)
        if not new_trie:
            return None
        return StateItem(state.cost + cost * MDL_MOVE_COST, new_trie, current_alignment, node.get_activity())

    def _model_move_v2(self, node: TrieNode, time, state: StateItem) -> List[StateItem]:
        current_alignment = self._move_event_data_to_alignment(node, time, state)
        new_states_items = []
        for child in state.trie.get_children():
            new_alignment = deepcopy(current_alignment)
            new_alignment.alignment.model_move(node, 1, state.trie.label)
            new_states_items.append(StateItem(state.cost + MDL_MOVE_COST, child, new_alignment, node.get_activity()))
        return new_states_items

    def _move_event_data_to_alignment(self, node: TrieNode, time, state: StateItem) -> AlignmentTimestamped:
        current_alignment = deepcopy(state.alignment)
        current_alignment.timestamp = time
        #current_alignment.node = Node(event.location)
        return current_alignment