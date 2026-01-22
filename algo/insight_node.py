from datetime import datetime, timezone
from typing import Dict

from algo.alignment import Alignment, SKIP_NODE_COST
from algo.alignment_builder import AlignmentBuilder
from algo.alignment_timestamped import AlignmentTimestamped
from algo.network import Network
from algo.state_explorer import StateExplorer
from algo.state_item import StateItem
from algo.trie import Trie
from algo.trie_node import Node

class InsightNode:

    def __init__(self, trie: Trie, node_id: str, network: Network):
        self.node_id = node_id
        self.network: Network = network
        self.local_trie = trie
        self.alignment_builder: AlignmentBuilder = AlignmentBuilder()
        self.state_explorer: Dict[str, StateExplorer] = {}

    def get_alignment(self, case_id) -> AlignmentTimestamped | None:
        if case_id not in self.state_explorer:
            return None
        state_item = self.state_explorer[case_id].top()
        return state_item.alignment

    def process_event(self, event):
        case_id = event.case_id
        if case_id not in self.state_explorer:
            self._init_state_for_case(case_id)
        alignments = []
        for node in self.network.get_all_nodes():
            alignment = node.get_alignment(case_id)
            if alignment is not None:
                alignments.append(alignment)
        if alignments:
            latest_alignment = max(alignments)
            self.state_explorer[case_id].top()
            if latest_alignment.node in self.local_trie:
                self.state_explorer[case_id] = StateExplorer(StateItem(latest_alignment.alignment.cost, self.local_trie[latest_alignment.node], latest_alignment))
            else:
                # TODO hrei here we have to quantify the Real Skip_node_cost
                self.state_explorer[case_id] = StateExplorer(StateItem(latest_alignment.alignment.cost, self.local_trie, latest_alignment))

        new_alignment_states = self.alignment_builder.build_alignment(event, self.state_explorer[case_id])
        for state in new_alignment_states:
            self.state_explorer[case_id].insert_state(state)
        self.state_explorer[case_id].prune()
        print(self.state_explorer[case_id].top())
        #print(f"size: {len(self.state_explorer[case_id].heap)}")

    def _init_state_for_case(self, case_id):
        self.state_explorer[case_id] = StateExplorer(
            StateItem(
                0, self.local_trie, AlignmentTimestamped(
                    alignment=Alignment(), timestamp=datetime(1, 1, 1, tzinfo=timezone.utc), node=Node(self.node_id)
                )
            )
        )
