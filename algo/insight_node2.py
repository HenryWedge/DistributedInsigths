import string
from copy import deepcopy
from datetime import datetime
from typing import Dict, List, Any, Callable
from algo.alignment import Alignment, SKIP
from algo.alignment_builder import AlignmentBuilder
from algo.alignment_timestamped import AlignmentTimestamped
from algo.event import Event
from algo.network import Network
from algo.new_trie import NewTrie
from algo.state_explorer import StateExplorer
from algo.state_item import StateItem
from algo.state_with_time import StateWithTime
from algo.strategy.collect_previous_alignments_strategy import CollectPreviousAlignmentsStrategy
from algo.strategy.heap_pruning_strategy import HeapPruningStrategy
from algo.trie_node import Node, Activity, TrieNode
from algo.trie_traverser import TrieTraverser


class InsightNode2:
    def __init__(
            self,
            trie: NewTrie,
            node_id: str,
            network: Network,
            pruning_strategy: HeapPruningStrategy,
            collect_alignments_strategy: Callable[[Network, string], CollectPreviousAlignmentsStrategy]
    ):
        self.node_id = node_id
        self.network: Network = network
        self.local_trie = trie
        self.alignment_builder: AlignmentBuilder = AlignmentBuilder()
        self.observed_events = {}
        self.external_alignment = {}
        self.internal_alignment = {}

    def get_current_state(self, case_id, target) -> tuple[int, StateWithTime | None]:
        if case_id not in self.observed_events:
            return 0, None
        alignment = self.alignment_builder.dijkstra([Activity(event.activity) for event in self.observed_events[case_id]], self.local_trie, Activity(target))
        return self.observed_events[case_id][-1].time, self.external_alignment.get(case_id).concatenate(alignment)

    def process_event(self, event):
        case_id = event.case_id

        if not case_id in self.internal_alignment:
            self.internal_alignment[case_id] = Alignment()

        if not case_id in self.external_alignment:
            self.external_alignment[case_id] = Alignment()

        if not case_id in self.observed_events:
            self.observed_events[case_id] = []
        self.observed_events[case_id].append(event)

        entry_points: List[TrieNode] = [child.label for child in self.local_trie.children if not child.label.is_activity()]

        last_alignments_per_node = []
        for entry_point in entry_points:
            last_alignments_per_node.append(
                self.network.get_node(entry_point.get()).get_current_state(case_id, entry_point.get_activity())
            )
        if last_alignments_per_node:
            self.external_alignment[case_id] = max(last_alignments_per_node)[1]

        self.internal_alignment[case_id] = self.alignment_builder.dijkstra(
            [Activity(event.activity) for event in self.observed_events[case_id]], self.local_trie, Activity(event.activity)
        )

        alignment = deepcopy(self.external_alignment[case_id])
        alignment = alignment.concatenate(self.internal_alignment[case_id])
        print(alignment)