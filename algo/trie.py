from typing import List

from algo.trie_metrics import TrieMetrics

END_MARKER = "<end>"

class Trie:
    def __init__(self, trie=None):
        if trie is None:
            self.trie = {}
        else:
            self.trie = trie
        self.node_metrics = {}

    def build(self, traces):
        for trace in traces:
            self.insert(trace)

    def insert(self, trace: List[str]):
        node = self.trie
        for activity in trace:
            if activity not in node: node[activity] = {}
            node = node[activity]
        node[END_MARKER] = True

    def annotate_path_to_end_cost(self, trie):
        child_metrics = [self.annotate_path_to_end_cost(v) for k, v in trie.items() if k != END_MARKER]
        number_of_leaves = len([k for k, v in trie.items() if k == END_MARKER])
        if END_MARKER in trie:
            if len(trie) == 1 and not child_metrics:
                return self._mark_leave(trie)
            else:
                return self._mark_inner_node_with_leaf(trie, child_metrics, number_of_leaves)

        return self._mark_inner_node(trie, child_metrics)

    def _mark_leave(self, trie) -> TrieMetrics:
        metrics = TrieMetrics(min_cost=0, avg_cost=0)
        self.node_metrics[str(Trie(trie))] = metrics
        return metrics

    def _mark_inner_node_with_leaf(self, trie, child_metrics, number_of_leaves) -> TrieMetrics:
        average_cost = 1 + sum([child_metric.avg_cost for child_metric in child_metrics]) / (len(child_metrics) + number_of_leaves)

        metrics = TrieMetrics(min_cost=0, avg_cost=average_cost)
        self.node_metrics[str(Trie(trie))] = metrics

        return metrics

    def _mark_inner_node(self, trie, child_metrics) -> TrieMetrics:
        min_dist = 1 + min([child_metric.min_cost for child_metric in child_metrics])
        average_cost = 1 + sum([child_metric.avg_cost for child_metric in child_metrics]) / len(child_metrics)

        metrics = TrieMetrics(min_cost=min_dist, avg_cost=average_cost)
        self.node_metrics[str(Trie(trie))] = metrics

        return metrics

    def get_rest_cost(self, trie):
        return self.node_metrics[str(Trie(trie))]

    def __str__(self):
        return str(self.trie)

    def __hash__(self):
        return hash(self.trie)