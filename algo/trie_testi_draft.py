import heapq
import sys
from copy import deepcopy
from typing import List, Any

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
        self.processed_events = 0

    def increment_processed_events(self):
        self.processed_events += 1

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
            if len(self.elements) == len(other.elements):
                return hash(self) < hash(other)
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

    def contains_log_moves(self):
        return len(self.get_all_log_moves()) > 0

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

    def __hash__(self):
        return hash(frozenset(self.elements))


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

    def get_children_containing_label(self, label):
        return [
            self.get_child(child.label).label
            for child in self.get_children()
            if self.get_child(child.label).contains(label)
        ]

    def contains(self, label) -> bool:
        if self.label == label:
            return True
        for child in self.children:
            if child.contains(label):
                return True
        return False

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
    def __init__(self, timestamp, alignment, entry_point, last_node):
        self.timestamp: int = timestamp
        self.alignment: Alignment = alignment
        self.entry_point = entry_point
        self.last_node = last_node

    def __lt__(self, other):
        return self.alignment > other.alignment

    def is_empty(self):
        return not self.alignment or self.alignment.is_empty()

class NetworkNode:
    def __init__(self, model, network, node_id):
        self.node_id = node_id
        self.network: Network = network
        self.network.add_node(self.node_id, self)
        self.i = -1
        self.model: Trie = model
        self.observed_events = {}
        self.cache = {}

    def _get_entry_points_containing_label(self, label):
        return [child for child in self.model.get_children() if
                child.label.location != self.node_id and child.contains(label)]

    def _get_trace(self, min_i=-1, max_i=sys.maxsize):
        filtered = {k: v for k, v in self.observed_events.items() if min_i < k < max_i}
        return [value for key, value in sorted(filtered.items())]

    def get_all_moves(self, i):
        result = []
        for key in self.observed_events:
            if key < i:
                result.append(self.observed_events[key])
        return result

    def get_alignment(self, target: LocatedActivity, i) -> AlignmentResponse:
        response: AlignmentResponse = self.find_best_alignment(target, i)
        if not response:
            return None

        return AlignmentResponse(
            max(self.i, response.timestamp),
            response.alignment,
            target,
            response.last_node
        )

    def process_event(self, located_activity: LocatedActivity, i: int) -> Alignment:
        self.i = i
        self.observed_events[i] = located_activity
        response = self.find_best_alignment(located_activity, i, is_start=True)
        return response.alignment

    def find_best_alignment(self, target: LocatedActivity = None, i=sys.maxsize, is_start=False) -> Any:
        all_candidate_alignments: List[AlignmentResponse] = []
        for entry_point in self.model.get_children_containing_label(target):
            response, model = self._request_external_alignment(entry_point, i)
            last_node = response.last_node
            trace = self._get_relevant_local_trace(i, is_start, last_node, response.timestamp)
            local_alignment = calculate_alignment(trace, model, target)

            if local_alignment.contains_log_moves():
                last_node = self.node_id

            candidate_alignment = response.alignment + local_alignment
            all_candidate_alignments.append(
                AlignmentResponse(response.timestamp, candidate_alignment, target, last_node))

        if not all_candidate_alignments:
            return calculate_alignment(self._get_trace(), self.model, target)
        all_candidate_alignments = self._add_external_log_moves(all_candidate_alignments, i)
        best_alignment_response = min(all_candidate_alignments, key=lambda x: x.alignment)

        return AlignmentResponse(
            best_alignment_response.timestamp,
            best_alignment_response.alignment,
            target, best_alignment_response.last_node
        )

    def _add_external_log_moves(self, responses: List[AlignmentResponse], i):
        all_log_moves = []
        #for response in responses:
        #    for log_move in response.alignment.get_all_log_moves():
        #        if log_move not in all_log_moves:
        #            all_log_moves.append(log_move)
        response_with_external_log_moves = []
        for node in self.network.get_all_nodes(self.node_id):
            all_log_moves.extend(node.get_all_moves(i))
        for response in responses:
            alignment_with_log_moves = response.alignment.append_missing_log_moves(all_log_moves)
            response.alignment = alignment_with_log_moves
            response_with_external_log_moves.append(response)
        return response_with_external_log_moves

    def _request_external_alignment(self, entry_point: Trie, i: int) -> tuple[AlignmentResponse, Trie]:
        model = self.model
        if self.node_id == entry_point.location:
            alignment_response = AlignmentResponse(-1, Alignment(), entry_point, None)
        else:
            if entry_point in self.cache:
                alignment_response = self.cache[entry_point]
            else:
                alignment_response = (
                    self.network.get_node(entry_point.location).get_alignment(entry_point, i))
            model = self.model.get_child(entry_point)

        self.cache[entry_point] = alignment_response
        return alignment_response, model

    def _get_relevant_local_trace(self, i: int, is_start: bool, last_node, timestamp: int) -> list[Any]:
        max_time = i if not is_start and i == self.i else sys.maxsize
        min_time = timestamp - 1 if last_node == self.node_id else timestamp
        return self._get_trace(min_time, max_time)


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
            if (
                    target
                    or trace_idx != len(trace) - 1
                    or not queue
            ):
                heapq.heappush(queue, (
                    path.move_on_log_skip_model(trace[trace_idx]),
                    id(current_node),
                    current_node,
                    trace_idx + 1
                ))

    return None
