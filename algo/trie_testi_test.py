import unittest

from algo.network import Network
from algo.trie_testi import LocatedActivity, NetworkNode, Trie, TrieBuilder

class TrieTestiTest(unittest.TestCase):
    def _get_training_traces(self, c: bool):
        return [
            [
                LocatedActivity("A", "c" if c else "n1"),
                LocatedActivity("B", "c" if c else "n1"),
                LocatedActivity("E", "c" if c else "n2"),
                LocatedActivity("F", "c" if c else "n2"),
                LocatedActivity("H", "c" if c else "n2"),
                LocatedActivity("G", "c" if c else "n4")
            ],
            [
                LocatedActivity("A", "c" if c else"n1"),
                LocatedActivity("C", "c" if c else"n1"),
                LocatedActivity("D", "c" if c else"n3"),
                LocatedActivity("G", "c" if c else"n4")
            ]
        ]

    def _get_validation_trace(self, c: bool):
        return [
            LocatedActivity("A", "c" if c else"n1"),
            LocatedActivity("B", "c" if c else"n1"),
            LocatedActivity("D", "c" if c else"n3"),
            LocatedActivity("F", "c" if c else"n2"),
            LocatedActivity("G", "c" if c else"n4")
        ]

    def _run(self, training_trace, validation_trace):
        trie_builders = {}
        last_event = None
        for trace in training_trace:
            for located_activity in trace:
                if located_activity.location not in trie_builders:
                    trie_builders[located_activity.location] = TrieBuilder(Trie())
                if last_event and last_event.location != located_activity.location:
                   trie_builders[located_activity.location].insert(last_event)
                trie_builders[located_activity.location].insert(located_activity)
                last_event = located_activity
            for trie_id in trie_builders:
                trie_builders[trie_id].reset()
            last_event = None

        network = Network()
        for key in trie_builders:
            NetworkNode(trie_builders[key].root_trie, network, key)

        alignments = []
        for i, located_activity in enumerate(validation_trace):
            alignment = network.get_node(located_activity.location).process_event(located_activity, i)
            alignments.append(alignment)
            print(alignment)
        return alignments

    def _assert_equality_of_alignments(self, alignments_decentral, alignments_central):
        fail = False
        for i in range(len(alignments_decentral)):
            set_central = set(alignments_central[i].elements)
            set_decentral = set(alignments_decentral[i].elements)
            not_matching = set_central.difference(set_decentral)
            if not_matching:
                print(f"Alignments do not match.\nDecentral:\n{alignments_decentral[i]}\nCentral:\n{alignments_central[i]}")
                print("Difference:")
                print(''.join(f'{x}\n' for x in not_matching))
                fail = True
        self.assertFalse(fail)

    def test_example(self):
        alignments_decentral = self._run(self._get_training_traces(False), self._get_validation_trace(False))
        alignments_central = self._run(self._get_training_traces(True), self._get_validation_trace(True))
        self._assert_equality_of_alignments(alignments_decentral, alignments_central)