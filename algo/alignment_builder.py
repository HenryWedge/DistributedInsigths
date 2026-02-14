import heapq
from copy import deepcopy
from typing import List

from algo.alignment import LOG_MOVE_COST, MDL_MOVE_COST, Alignment
from algo.alignment_timestamped import AlignmentTimestamped
from algo.new_trie import NewTrie
from algo.state_explorer import StateExplorer
from algo.state_item import StateItem
from algo.trie_node import Node, TrieNode, Activity
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
                model_move = self._model_move(node, time, state)
                if model_move:
                    new_state_items.append(self._model_move(node, time, state))
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

        new_trie, cost, path = trie_traverser.find_activity_in_trie(node)
        for child in path[:-1]:
            current_alignment.alignment.model_move(child, cost, None)
        current_alignment.alignment.sync_move(path[-1])
        if not new_trie:
            return None
        return StateItem(state.cost + cost * MDL_MOVE_COST, new_trie, current_alignment, node.get_activity())

    def _model_move_v2(self, node: TrieNode, time, state: StateItem) -> List[StateItem]:
        current_alignment = self._move_event_data_to_alignment(node, time, state)
        new_states_items = []
        for child in state.trie.get_children():
            new_alignment = deepcopy(current_alignment)
            new_alignment.alignment.model_move(node, 1, child.label)
            new_states_items.append(StateItem(state.cost + MDL_MOVE_COST, child, new_alignment, node.get_activity()))
        return new_states_items

    def _move_event_data_to_alignment(self, node: TrieNode, time, state: StateItem) -> AlignmentTimestamped:
        current_alignment = deepcopy(state.alignment)
        current_alignment.timestamp = time
        return current_alignment

    def find_alignment_for_trace(self, trace: List[Activity], trie: NewTrie, target_label):
        queue = [(0, trie, 0, Alignment())]
        visited = set()
        while queue:
            (cost, current_node, trace_idx, history) = heapq.heappop(queue)
            if current_node.label == target_label:
                final_history = history
                final_cost = cost
                while trace_idx < len(trace):
                    final_history.log_move(trace[trace_idx])
                    final_cost += 1
                    trace_idx += 1
                return final_history

            state = (id(current_node), trace_idx)
            if state in visited:
                continue
            visited.add(state)

            if trace_idx < len(trace):
                current_event = trace[trace_idx]
                if current_node.has_child_with_label(current_event):
                    child = current_node.get_child(current_event)
                    this_history = deepcopy(history)
                    this_history.sync_move(current_event)
                    heapq.heappush(queue, (
                        cost,
                        child,
                        trace_idx + 1,
                        this_history
                    ))

            for child in current_node.get_children():
                this_history = deepcopy(history)
                if child.label.is_activity():
                    this_history.model_move(child)
                heapq.heappush(queue, (
                    cost + 1,
                    child,
                    trace_idx,
                    this_history
                ))

            if trace_idx < len(trace):
                this_history = deepcopy(history)
                if trace[trace_idx] == Activity("D"):
                    print("Stop")
                this_history.log_move(trace[trace_idx])
                heapq.heappush(queue, (
                    cost + 1,
                    current_node,
                    trace_idx + 1,
                    this_history
                ))

        return None

    def dijkstra(self, trace: List[Activity], trie: NewTrie, target_label):
        queue = [(0, trie, Alignment())]
        for activity in trace:
            while queue:
                new_state = []
                (cost, current_trie, alignment) = heapq.heappop(queue)
                if current_trie.label == target_label:
                    return alignment
                if current_trie.has_child_with_label(activity):
                    this_alignment = deepcopy(alignment)
                    this_alignment.sync_move(activity)
                    new_state.append((cost, current_trie.traverse(activity), this_alignment))
                next_trie, cost, path = TrieTraverser(trie).find_activity_in_trie(activity)
                if next_trie:
                    this_alignment = deepcopy(alignment)
                    for a in path:
                        this_alignment.model_move(a, 1, None)
                    new_state.append((cost + len(path), next_trie, this_alignment))
                this_alignment = deepcopy(alignment)
                this_alignment.log_move(activity)
                new_state.append((cost + 1, current_trie, this_alignment))
                for s in new_state:
                    heapq.heappush(queue, s)

        return heapq.nsmallest(1, queue)[0][2]