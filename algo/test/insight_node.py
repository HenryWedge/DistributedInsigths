import unittest

from algo.event import Event
from algo.insight_node import InsightNode
from algo.network import Network
from algo.trie import Trie
from algo.trie_node import Activity, Node


class InsightNodeTestCase(unittest.TestCase):

    def test_insight_node(self):
        network = Network()

        trie1: Trie = Trie()
        trie1.insert([Activity("A")])
        trie1.insert([Node("n3"), Activity("D")])

        trie2: Trie = Trie()
        trie2.insert([Node("n1"), Activity("B")])

        trie3: Trie = Trie()
        trie3.insert([Node("n2"), Activity("C")])

        n1 = InsightNode(trie=trie1, node_id="n1", network=network)
        n2 = InsightNode(trie=trie2, node_id="n2", network=network)
        n3 = InsightNode(trie=trie3, node_id="n3", network=network)

        network.add_node("n1", n1)
        network.add_node("n2", n2)
        network.add_node("n3", n3)

        n1.process_event(Event(activity=Activity("A"), location="n1", time=0))
        n2.process_event(Event(activity=Activity("B"), location="n2", time=1))
        #n3.process_event(Event(activity=Activity("C"), location="n3", time=2))
        n1.process_event(Event(activity=Activity("D"), location="n1", time=3))

        print(n1.get_alignment())

if __name__ == '__main__':
    unittest.main()
