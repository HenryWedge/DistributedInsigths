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
        self.local_trie = trie
        self.network: Network = network
        self.alignment_builder: AlignmentBuilder = AlignmentBuilder()
        self.node_id = node_id
        self.state_explorer = StateExplorer(
            StateItem(
                0, self.local_trie, AlignmentTimestamped(
                    alignment=Alignment(), timestamp=-1, node=Node(self.node_id)
                )
            )
        )

    def get_alignment(self) -> AlignmentTimestamped | None:
        state_item = self.state_explorer.top()
        if state_item.alignment.alignment.is_empty():
            return None
        return state_item.alignment

    def process_event(self, event):
        alignments = []
        for node in self.network.get_all_nodes():
            alignment = node.get_alignment()
            if alignment is not None:
                alignments.append(alignment)
        if alignments:
            latest_alignment = max(alignments)
            self.state_explorer.top()
            if latest_alignment.node in self.local_trie:
                self.state_explorer = StateExplorer(StateItem(latest_alignment.alignment.cost, self.local_trie[latest_alignment.node], latest_alignment))
            else:
                # TODO hrei here a special cost is needed
                self.state_explorer = StateExplorer(StateItem(latest_alignment.alignment.cost + SKIP_NODE_COST, self.local_trie, latest_alignment))
        self.alignment_builder.build_alignment(event, self.state_explorer)
