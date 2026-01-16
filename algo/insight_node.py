from typing import Dict, List

from algo.alignment import Alignment, SKIP_NODE_COST
from algo.alignment_builder import AlignmentBuilder
from algo.alignment_timestamped import AlignmentInformation
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

    def get_alignments(self, case_id, timestamp) -> List[AlignmentInformation]:
        if case_id not in self.state_explorer:
            return []
        state_items = self.state_explorer[case_id].items_after_timestamp(timestamp)
        return [state_item.alignment for state_item in state_items]

    def process_event(self, event):
        print(event.activity)
        case_id = event.case_id
        new_alignment_states = []
        alignments = []
        for node in self.network.get_all_nodes():
            alignment = node.get_alignments(case_id, event.time - 2)
            alignments.extend(alignment)

        for alignment in alignments:
            if alignment.node in self.local_trie:
                new_alignment_states.append(
                    StateItem(
                        self.local_trie[alignment.node],
                        alignment
                    )
                )
            else:
                # TODO hrei here we have to quantify the Real Skip_node_cost
                new_alignment_states.append(
                    StateItem(self.local_trie, alignment)
                )

        if not new_alignment_states and case_id not in self.state_explorer:
            new_alignment_states.append(self._init_state_for_case())
        self.state_explorer[case_id] = StateExplorer(new_alignment_states)
        self.alignment_builder.build_alignment(event, self.state_explorer[case_id])

        for state in self.state_explorer[case_id].get_all_states():
            print(state.alignment)

    def _init_state_for_case(self):
        return StateItem(
            self.local_trie, AlignmentInformation(
                alignment=Alignment(),
                timestamp=-1,
                node=Node(self.node_id)
            )
        )
