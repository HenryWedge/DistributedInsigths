import heapq
from copy import deepcopy
from typing import List

from algo.network import Network

class LocatedActivity:
    def __init__(self, activity, location):
        self.activity = activity
        self.location = location

    def __str__(self):
        return f"{self.activity}@{self.location}"

    def __eq__(self, other):
        if not isinstance(other, LocatedActivity):
            return False
        return self.activity == other.activity

    def equals_activity(self, other):
        return self.activity == self.activity

    def __hash__(self):
        return hash(self.activity)


class Alignment:
    def __init__(self):
        self.elements: List[AlignmentElement] = []

    def sync_move(self, sync_move: LocatedActivity):
        this_alignment = deepcopy(self)
        this_alignment.elements.append(AlignmentElement(sync_move, sync_move))
        return this_alignment

    def move_on_model_skip_log(self, model_move: LocatedActivity):
        this_alignment = deepcopy(self)
        this_alignment.elements.append(AlignmentElement(model_move, SKIP))
        return this_alignment

    def move_on_log_skip_model(self, log_move: LocatedActivity):
        this_alignment = deepcopy(self)
        this_alignment.elements.append(AlignmentElement(SKIP, log_move))
        return this_alignment

    def get_cost(self):
        cost = 0
        for element in self.elements:
            if element.log == SKIP:
                cost += MODEL_COST
            elif element.model == SKIP:
                cost += LOG_COST
        return cost

    def is_empty(self):
        return not bool(self.elements)

    def __add__(self, other):
        this_self = deepcopy(self)
        if not other:
            return this_self
        resulting_alignment = Alignment()
        resulting_alignment.elements.extend(this_self.elements)
        resulting_alignment.elements.extend(other.elements)
        return resulting_alignment

    def __lt__(self, other):
        if self.get_cost() == other.get_cost():
            return len(self.elements) < len(other.elements)
        return self.get_cost() < other.get_cost()

    def __eq__(self, other):
        if len(self.elements) != len(other.elements):
            return False

        for i in range(len(self.elements)):
            if self.elements[i] != other.elements[i]:
                return False
        return True

    def __str__(self):
        final_string = ""
        for element in self.elements:
            final_string += str(element) + "\n"
        return f"[Cost:{self.get_cost()}]\n{final_string}"

    def get_all_log_moves(self):
        all_log_moves = []
        for element in self.elements:
            if element.log != SKIP:
                all_log_moves.append(element.log)
        return all_log_moves

    def append_missing_log_moves(self, log_moves):
        missing_log_moves = []
        for log_move in log_moves:
            if log_move not in self.get_all_log_moves():
                missing_log_moves.append(log_move)
        if not missing_log_moves:
            return deepcopy(self)
        for log_move in missing_log_moves:
            alignment = self.move_on_log_skip_model(log_move)
        return deepcopy(alignment)

class Trie:
    def __init__(self, label=None):
        if label:
            self.label = label
        else:
            self.label = "#"
        self.children: List[Trie] = []

    def __str__(self):
        return str(self.label)

    def is_root(self):
        return isinstance(self.label, str)

    def has_child(self, label) -> bool:
        return label in [child.label for child in self.children]

    def is_leaf(self):
        return len(self.children) == 0

    def get_child(self, label) -> 'Trie':
        return [child for child in self.children if child.label == label][0]

    def traverse(self, label):
        return self.get_child(label).children[0]

    def get_children(self):
        return self.children

    def add_child(self, trie: 'Trie'):
        self.children.append(trie)


class TrieBuilder:
    def __init__(self, trie: Trie):
        self.root_trie = trie
        self.active_trie: Trie = trie

    def insert(self, label):
        if self.active_trie.has_child(label):
            new_trie = self.active_trie.get_child(label)
        else:
            new_trie = Trie(label)
            self.active_trie.add_child(new_trie)
        self.active_trie = new_trie

    def reset(self):
        self.active_trie = self.root_trie

class AlignmentResponse:
    def __init__(self, timestamp, alignment, entry_point):
        self.timestamp: int = timestamp
        self.alignment: Alignment = alignment
        self.entry_point = entry_point

    def __lt__(self, other):
        return self.alignment > other.alignment


class NetworkNode:
    def __init__(self, model, network, node_id):
        self.observed_events = {}
        self.external_alignment = Alignment()
        self.internal_alignment = Alignment()
        self.node_id = node_id
        self.network: Network = network
        self.network.add_node(self.node_id, self)
        self.model = model
        self.current_model = model
        self.activities_to_align = []
        self.last_i = -1
        self.i = -1

    def _get_entry_points(self):
        return [child for child in self.model.get_children() if child.label.location != self.node_id]

    def _trie_without_entrypoints(self):
        trie = Trie()
        all_children = self.model.get_children()
        start_activities = [child for child in all_children if child.label.location == self.node_id]
        entry_points = self._get_entry_points()
        activity_after_entrypoint = [child for entry_point in entry_points for child in entry_point.get_children()]
        trie.children.extend(start_activities)
        trie.children.extend(activity_after_entrypoint)
        return trie

    def _get_last_processed_event(self, alignment):
        if not alignment:
            return -1
        this_alignment = deepcopy(alignment.elements)
        this_alignment.reverse()
        for element in this_alignment:
            if element.model != SKIP and element.model in self.observed_events:
                return self.observed_events[element.model]
        return -1

    def get_alignment(self, target):
        timestamp = None
        if not self.activities_to_align:
            all_alignments = []
            for entrypoint in self._get_entry_points():
                for node in self.network.get_all_nodes(self.node_id):
                    alignment: Alignment = node.get_alignment(entrypoint).alignment
                    if not alignment.is_empty():
                        all_alignments.append(node.get_alignment(entrypoint))
            latest_alignment_repsonse = max(all_alignments)
            self.external_alignment = latest_alignment_repsonse.alignment
            timestamp = latest_alignment_repsonse.timestamp

        target_activity = LocatedActivity(target.label.activity, self.node_id)
        internal_alignment = calculate_alignment(
            self.activities_to_align,
            self._trie_without_entrypoints(),
            target_activity
        )
        return AlignmentResponse(
            # IMPORTANT! timestamp is not None otherwise it would evaluate to True on timestamp 0
            timestamp if timestamp is not None else self._get_last_processed_event(internal_alignment),
            self.external_alignment + internal_alignment,
            target_activity
        )

    def get_observed_events(self):
        return list(self.observed_events.keys())

    def _construct_alignment_from_responses(self, latest_alignment_responses: List[AlignmentResponse]):
        best_alignment: Alignment = None
        additional_log_moves: List[LocatedActivity] = []
        for node in self.network.get_all_nodes(self.node_id):
            additional_log_moves.extend(node.get_observed_events())

        for response in latest_alignment_responses:
            external_alignment = response.alignment.append_missing_log_moves(additional_log_moves)
            internal_alignment = calculate_alignment(
                self.activities_to_align, self.model.get_child(response.entry_point))
            complete_alignment = external_alignment + internal_alignment

            # We follow this path only when it is reachable
            # We must implement that we somehow assign a cost to this case so we take the shortest skips within
            if internal_alignment:
                if not best_alignment or best_alignment > complete_alignment:
                    best_alignment = complete_alignment
                    best_internal_alignment = internal_alignment
                    best_external_alignment = external_alignment
                    best_entrypoint = response.entry_point

        return best_entrypoint, best_internal_alignment, best_external_alignment

    def _add_external_log_moves(
            self,
            additional_log_moves: list[LocatedActivity],
            constructed_alignment: Alignment,
            all_included_log_moves
    ):
        missing_log_moves = []
        for log_move in additional_log_moves:
            if log_move not in all_included_log_moves:
                missing_log_moves.append(log_move)
        for log_move in missing_log_moves:
            constructed_alignment = constructed_alignment.move_on_log_skip_model(log_move)
        return constructed_alignment

    def process_event(self, located_activity: LocatedActivity, i: int):
        self.i = i
        self.observed_events[located_activity] = self.i
        self.activities_to_align.append(located_activity)
        external_alignments: List[AlignmentResponse] = []

        for possible_entry_point in self._get_entry_points():
            external_alignment = (
                self.network.get_node(possible_entry_point.label.location).get_alignment(possible_entry_point))
            if external_alignment.timestamp >= 0:
                external_alignments.append(external_alignment)

        if self._is_previous_state_external(external_alignments):
            self.activities_to_align = [located_activity]
            entry_point, self.internal_alignment, self.external_alignment = (
                self._construct_alignment_from_responses(external_alignments))
            self.current_model = self.model.get_child(entry_point)
        else:
            self.internal_alignment = calculate_alignment(self.activities_to_align, self.current_model)

        self.last_i = i
        return self.external_alignment + self.internal_alignment

    def _is_previous_state_external(self, external_alignments: list[AlignmentResponse]) -> bool:
        return external_alignments and max(external_alignments, key=lambda x: x.timestamp).timestamp > self.last_i


SKIP = LocatedActivity(">>", "skip")
SYNC_COST = 0
LOG_COST = 1
MODEL_COST = 1

class AlignmentElement:
    def __init__(self, model, log):
        self.model = model
        self.log = log

    def __str__(self):
        return f"Model: {self.model} | Log: {self.log}"

    def __lt__(self, other):
        return False

    def __hash__(self):
        return 0

    def __eq__(self, other):
        return self.model == other.model and self.log == other.log


def calculate_alignment(trace, trie_node: Trie, target=None):
    # Priority Queue: (cost, trie_node, trace_index, path)
    start_node = trie_node
    queue = [(Alignment(), id(start_node), start_node, 0)]
    visited = set()

    while queue:
        path, _, current_node, trace_idx = heapq.heappop(queue)

        # Zielzustand: Ende der Trace UND Ende eines Pfades im Trie
        if target:
            # If we have a target we force to reach it
            if not current_node.is_root() and current_node.label.activity == target.activity:
                if target and trace_idx == len(trace):
                    return path
        else:
            if trace_idx == len(trace):
                return path

        state_id = (id(current_node), trace_idx)
        if state_id in visited:
            continue
        visited.add(state_id)

        # 1. Synchroner Schritt (Übereinstimmung)
        if trace_idx < len(trace) and current_node.has_child(trace[trace_idx]):
            next_node = current_node.get_child(trace[trace_idx])
            heapq.heappush(queue, (
                path.sync_move(trace[trace_idx]),
                id(next_node),
                next_node,
                trace_idx + 1,
            ))

        # 2. Schritt im Modell (Skip Log / Move on Model)
        for next_node in current_node.get_children():
            heapq.heappush(queue, (
                path.move_on_model_skip_log(next_node.label),
                id(next_node),
                next_node,
                trace_idx
            ))

        # 3. Schritt im Log (Skip Model / Move on Log)
        if trace_idx < len(trace):
            # In the central case we want to enforce that the alignment goes to the end of the trace
            if target or trace_idx != len(trace) - 1:
                heapq.heappush(queue, (
                    path.move_on_log_skip_model(trace[trace_idx]),
                    id(current_node),
                    current_node,
                    trace_idx + 1
                ))
    return None
