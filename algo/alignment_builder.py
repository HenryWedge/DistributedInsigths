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
                state.trie = state.trie.traverse(Node(node.content, node.get_activity()))
                new_state_items.append(state)
                continue
            if not state.trie:
                new_state_items.append(self._log_move(node, time, state))
            elif state.trie.has_child_with_label(node):
                new_state_items.append(self._sync_move(node, time, state))
            else:
                new_state_items.append(self._log_move(node, time, state))
                model_move_state_item = self._model_move(node, time, state)
                if model_move_state_item:
                    new_state_items.append(model_move_state_item)
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
        current_alignment.alignment.model_move(node)
        trie_traverser = TrieTraverser(state.trie)
        new_trie, cost = trie_traverser.find_activity_in_trie(node)
        if not new_trie:
            return None
        return StateItem(state.cost + cost * MDL_MOVE_COST, new_trie, current_alignment, node.get_activity())

    def _move_event_data_to_alignment(self, node: TrieNode, time, state: StateItem) -> AlignmentTimestamped:
        current_alignment = deepcopy(state.alignment)
        current_alignment.timestamp = time
        #current_alignment.node = Node(event.location)
        return current_alignment