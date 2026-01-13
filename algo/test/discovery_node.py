import unittest

from algo.discovery_node import DiscoveryNode
from algo.event import Event
from algo.network import Network
from algo.trie_node import Activity


class DiscoveryNodeTest(unittest.TestCase):

    def test_discovery_node(self):
        network: Network = Network()
        n1 = DiscoveryNode(node_id="n1", network=network)
        n2 = DiscoveryNode(node_id="n2", network=network)
        n3 = DiscoveryNode(node_id="n3", network=network)

        network.add_node("n1", n1)
        network.add_node("n2", n2)
        network.add_node("n3", n3)

        n1.process_event(Event(activity=Activity("A"), location="n1", time=0))
        n2.process_event(Event(activity=Activity("B"), location="n2", time=1))
        n3.process_event(Event(activity=Activity("C"), location="n3", time=2))
        n1.process_event(Event(activity=Activity("D"), location="n1", time=3))

        print(n1.local_trie)


if __name__ == '__main__':
    unittest.main()
