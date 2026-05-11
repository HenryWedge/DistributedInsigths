from algo.network import Network


class DistributedTokenBasedReplay:

    def __init__(self, network: Network):
        self.network = network
        self.network.add_node(self.node_id, self)
        self.model =