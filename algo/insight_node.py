from algo.alignment import Alignment
from algo.alignment_builder import AlignmentBuilder
from algo.alignment_timestamped import AlignmentTimestamped
from algo.network import Network
from algo.state_explorer import StateExplorer
from algo.state_item import StateItem
from algo.trie import Trie
from algo.trie_node import Node

class InsightNode:
    def __init__(self, node_id: str, network: Network):
        self.local_trie = Trie()
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

    def get_alignment(self) -> AlignmentTimestamped:
        state_item = self.state_explorer.top()
        return AlignmentTimestamped(
            alignment=state_item.alignment.alignment,
            timestamp=0,
            node=Node(self.node_id)
        )

    def process_event(self, event):
        alignments = []
        for node in self.network.get_all_nodes():
            alignments.append(node.move_event_data_to_alignment())
        latest_alignment = max(alignments)
        self.state_explorer.top()
        self.state_explorer = StateExplorer(StateItem(0, self.local_trie[latest_alignment.node], latest_alignment))
        self.alignment_builder.build_alignment(event, self.state_explorer)
