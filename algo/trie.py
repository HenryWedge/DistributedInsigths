from typing import List

from algo.trie_metrics import TrieMetrics
from algo.trie_node import TrieNode, EndActivity

class Trie:
    def __init__(self, data=None):
        if data is None:
            self.data = {}
        else:
            self.data = data
        self.node_metrics = None

    def build(self, traces: List[List[TrieNode]]):
        for trace in traces:
            self.insert(trace)

    def insert(self, trace: List[TrieNode]):
        node = self.data
        for activity in trace:
            if activity not in node: node[activity] = Trie()
            node = node[activity]
        node[EndActivity()] = None

    def annotate_path_to_end_cost(self, trie) -> TrieMetrics:
        child_metrics = [self.annotate_path_to_end_cost(v) for k, v in trie.items() if not k.is_end()]
        number_of_leaves = len([k for k, v in trie.items() if k.is_end()])
        if EndActivity() in trie:
            if len(trie) == 1 and not child_metrics:
                return self._mark_leave()
            else:
                return self._mark_inner_node_with_leaf(child_metrics, number_of_leaves)
        return self._mark_inner_node(child_metrics)

    def _mark_leave(self) -> TrieMetrics:
        metrics = TrieMetrics(min_cost=0, avg_cost=0)
        self.node_metrics = metrics
        return metrics

    def _mark_inner_node_with_leaf(self, child_metrics, number_of_leaves) -> TrieMetrics:
        average_cost = 1 + sum([child_metric.avg_cost for child_metric in child_metrics]) / (len(child_metrics) + number_of_leaves)

        metrics = TrieMetrics(min_cost=0, avg_cost=average_cost)
        self.node_metrics = metrics

        return metrics

    def _mark_inner_node(self, child_metrics) -> TrieMetrics:
        min_dist = 1 + min([child_metric.min_cost for child_metric in child_metrics])
        average_cost = 1 + sum([child_metric.avg_cost for child_metric in child_metrics]) / len(child_metrics)

        metrics = TrieMetrics(min_cost=min_dist, avg_cost=average_cost)
        self.node_metrics = metrics
        return metrics

    def next_items(self) -> List[TrieNode]:
        return list(self.data.keys())

    def next_children(self) -> List['Trie']:
        return list(self.data.values())

    def traverse(self, activity: TrieNode) -> 'Trie':
        return self.data[activity]

    def is_empty(self):
        return len(self.data) == 1 and EndActivity() in self.data

    def get_rest_cost(self):
        return self.node_metrics

    def __str__(self):
        result = "["
        if self.next_children():
            for key in self.data:
                result += f"{str(key)}->{str(self.data[key])}"
        result += "]"
        return result

    def __hash__(self):
        return hash(self.data)

    def __setitem__(self, key, value):
        self.data[key] = value

    def __getitem__(self, key):
        return self.data[key]

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def items(self):
        return self.data.items()

