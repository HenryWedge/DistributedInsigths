import heapq
from typing import List

from algo.network import Network

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


class NetworkNode:
    def __init__(self, model, network, node_id):
        self.observed_events = []
        self.external_alignment = []
        self.internal_alignment = []
        self.network = network
        self.model = model
        self.node_id = node_id

    def get_alignment(self, target):
        internal_alignment = calculate_alignment(
            self.observed_events,# + [LocatedActivity(target.label.activity, self.node_id)],
            self.model,
            LocatedActivity(target.label.activity, self.node_id))
        return self.external_alignment + internal_alignment

    def process_event(self, activity: LocatedActivity):
        self.observed_events.append(activity)
        entry_point = None
        for child in self.model.get_children():
            if child.label.location != self.node_id:
                self.external_alignment = self.network.get_node(child.label.location).get_alignment(child)
                entry_point = child
                break

        model = self.model.get_child(entry_point.label) if entry_point else self.model
        self.internal_alignment = calculate_alignment(self.observed_events, model)

        alignment_result = self.external_alignment + self.internal_alignment
        return alignment_result


class AlignmentElement:
    def __init__(self, model, log):
        self.model = model
        self.log = log

    def __str__(self):
        return f"Model: {self.model} | Log: {self.log}"

    def __lt__(self, other):
        return False


def calculate_alignment(trace, trie_node, target=None, costs={'sync': 0, 'model': 1, 'log': 1}):
    # Priority Queue: (cost, trie_node, trace_index, path)
    start_node = trie_node
    queue = [(0, id(start_node), start_node, 0, [])]
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
                path + [AlignmentElement(trace[trace_idx], trace[trace_idx])]
            ))

        # 2. Schritt im Modell (Skip Log / Move on Model)
        for next_node in current_node.get_children():
            heapq.heappush(queue, (
                cost + costs['model'],
                id(next_node),
                next_node,
                trace_idx,
                path + [AlignmentElement(next_node.label, ">>")]
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
                    path + [AlignmentElement(">>", trace[trace_idx])]
                ))
    return None


# --- Beispielnutzung ---
if __name__ == '__main__':
    trie = Trie()
    trie_builder = TrieBuilder(trie)
    trie_builder.insert(LocatedActivity("A", "n1"))
    trie_builder.insert(LocatedActivity("B", "n1"))
    trie_builder.insert(LocatedActivity("E", "n1"))
    trie_builder.insert(LocatedActivity("F", "n1"))
    trie_builder.insert(LocatedActivity("H", "n1"))
    trie_builder.reset()
    trie_builder.insert(LocatedActivity("A", "n1"))
    trie_builder.insert(LocatedActivity("C", "n1"))
    trie_builder.insert(LocatedActivity("D", "n1"))

    trie2 = Trie()
    trie_builder2 = TrieBuilder(trie2)
    trie_builder2.insert(LocatedActivity("H", "n1"))
    trie_builder2.insert(LocatedActivity("G", "n2"))

    observed_trace = [
        LocatedActivity("A", "n1"),
        LocatedActivity("B", "n1"),
        LocatedActivity("E", "n1"),
        LocatedActivity("G", "n2"),
        LocatedActivity("I", "n2")
    ]
    observed_trace2 = []
    network = Network()
    node = NetworkNode(trie, network, "n1")
    node2 = NetworkNode(trie2, network, "n2")
    network.add_node("n1", node)
    network.add_node("n2", node2)

    for located_activity in observed_trace:
        alignment = network.get_node(located_activity.location).process_event(located_activity)
        for element in alignment:
            print(element)
        print("---")