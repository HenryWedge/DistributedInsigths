import heapq
from copy import deepcopy
from typing import List

from algo.network import Network

SKIP = ">"
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


class LocatedActivity:
    def __init__(self, activity, location):
        self.activity = activity
        self.location = location

    def __str__(self):
        return f"{self.activity}@{self.location}"

    def __eq__(self, other):
        return self.activity == other.activity

    def __hash__(self):
        return hash(self.activity)


class AlignmentResponse:
    def __init__(self, timestamp, alignment, entry_point):
        self.timestamp = timestamp
        self.alignment = alignment
        self.entry_point = entry_point

    def __lt__(self, other):
        return self.timestamp < other.timestamp


class NetworkNode:
    def __init__(self, model, network, node_id):
        self.observed_events = []
        self.external_alignment = Alignment()
        self.internal_alignment = Alignment()
        self.node_id = node_id
        self.network: Network = network
        self.network.add_node(self.node_id, self)
        self.model = model
        self.i = 0

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

    def get_alignment(self, target):
        target_activity = LocatedActivity(target.label.activity, self.node_id)
        internal_alignment = calculate_alignment(
            self.observed_events,
            self._trie_without_entrypoints(),
            target_activity
        )
        return AlignmentResponse(self.i, self.external_alignment + internal_alignment, target_activity)

    def _construct_alignment_from_responses(self, alignment_responses: List[AlignmentResponse]):
        return max(alignment_responses)

    def process_event(self, located_activity: LocatedActivity, i: int):
        self.i = i
        self.observed_events.append(located_activity)
        external_alignments: List[AlignmentResponse] = []
        for possible_entry_point in self._get_entry_points():
            external_alignments.append(
                self.network.get_node(possible_entry_point.label.location).get_alignment(possible_entry_point)
            )
        entry_point = None
        if external_alignments:
            latest_alignment = self._construct_alignment_from_responses(external_alignments)
            entry_point = latest_alignment.entry_point
            self.external_alignment = latest_alignment.alignment

        if entry_point:
            model = self.model.get_child(entry_point)
        else:
            model = self.model
        self.internal_alignment = calculate_alignment(self.observed_events, model)

        alignment_result = self.external_alignment + self.internal_alignment
        return alignment_result

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

    def __add__(self, other):
        this_self = deepcopy(self)
        resulting_alignment = Alignment()
        resulting_alignment.elements.extend(this_self.elements)
        resulting_alignment.elements.extend(other.elements)
        return resulting_alignment

    def get_all_log_moves(self):
        all_log_moves = []
        for element in self.elements:
            all_log_moves.append(element.log)
        return all_log_moves

    def __str__(self):
        final_string = ""
        for element in self.elements:
            final_string += str(element) + "\n"
        return final_string

class AlignmentElement:
    def __init__(self, model, log):
        self.model = model
        self.log = log

    def __str__(self):
        return f"Model: {self.model} | Log: {self.log}"

    def __lt__(self, other):
        return False


def calculate_alignment(trace, trie_node: Trie, target=None, costs={'sync': 0, 'model': 1, 'log': 3}):
    # Priority Queue: (cost, trie_node, trace_index, path)
    start_node = trie_node
    queue = [(0, id(start_node), start_node, 0, Alignment())]
    visited = set()

    while queue:
        cost, _, current_node, trace_idx, path = heapq.heappop(queue)

        # Zielzustand: Ende der Trace UND Ende eines Pfades im Trie
        if target:
            # If we have a target we force to reach it
            if not current_node.is_root() and current_node.label.activity == target.activity:
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
                cost + costs['sync'],
                id(next_node),
                next_node,
                trace_idx + 1,
                path.sync_move(trace[trace_idx])
                #path + [AlignmentElement(trace[trace_idx], trace[trace_idx])]
            ))

        # 2. Schritt im Modell (Skip Log / Move on Model)
        for next_node in current_node.get_children():
            heapq.heappush(queue, (
                cost + costs['model'],
                id(next_node),
                next_node,
                trace_idx,
                path.move_on_model_skip_log(next_node.label)
                #path + [AlignmentElement(next_node.label, ">>")]
            ))

        # 3. Schritt im Log (Skip Model / Move on Log)
        if trace_idx < len(trace):
            # If we want to reach a specific target it should not be allowed to skip it to move on in the log
            if not (target and trace_idx == len(trace) - 1):
                heapq.heappush(queue, (
                    cost + costs['log'],
                    id(current_node),
                    current_node,
                    trace_idx + 1,
                    path.move_on_log_skip_model(trace[trace_idx])
                    #path + [AlignmentElement(">>", trace[trace_idx])]
                ))
    return None


# --- Beispielnutzung ---
if __name__ == '__main__':
    trie = Trie()
    trie_builder = TrieBuilder(trie)
    trie_builders = {
        "n1": TrieBuilder(Trie()),
        "n2": TrieBuilder(Trie()),
        "n3": TrieBuilder(Trie()),
        "n4": TrieBuilder(Trie()),
    }

    training_traces = [
        [
            LocatedActivity("A", "n1"),
            LocatedActivity("B", "n1"),
            LocatedActivity("E", "n2"),
            LocatedActivity("F", "n2"),
            LocatedActivity("H", "n2"),
            LocatedActivity("G", "n4")
        ],
        [
            LocatedActivity("A", "n1"),
            LocatedActivity("C", "n1"),
            LocatedActivity("D", "n3"),
            LocatedActivity("G", "n4")
        ]
    ]
    last_event = None
    for trace in training_traces:
        for located_activity in trace:
            if last_event and last_event.location != located_activity.location:
                trie_builders[located_activity.location].insert(last_event)
            trie_builders[located_activity.location].insert(located_activity)
            last_event = located_activity
        for trie_id in trie_builders:
            trie_builders[trie_id].reset()
        last_event = None

    network = Network()
    node = NetworkNode(trie_builders["n1"].root_trie, network, "n1")
    node2 = NetworkNode(trie_builders["n2"].root_trie, network, "n2")
    node3 = NetworkNode(trie_builders["n3"].root_trie, network, "n3")
    node4 = NetworkNode(trie_builders["n4"].root_trie, network, "n4")

    observed_trace = [
        LocatedActivity("A", "n1"),
        LocatedActivity("B", "n1"),
        LocatedActivity("D", "n3"),
        LocatedActivity("F", "n2"),
        LocatedActivity("G", "n4")
    ]
    for i, located_activity in enumerate(observed_trace):
        alignment = network.get_node(located_activity.location).process_event(located_activity, i)
#        for element in alignment:
        print(alignment)
        print("---")
