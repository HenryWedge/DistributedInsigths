import unittest

from algo.context_protocol import ModelTrainer, ContextProtocolNode
from algo.network import Network
from algo.alignment_node import LocatedActivity, NetworkNode, Trie
from algo.alignments.trie_builder import TrieBuilder
from algo.utility.event_log_splitter import EventLogSplitter


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
                LocatedActivity("A", "c" if c else "n1"),
                LocatedActivity("C", "c" if c else "n1"),
                LocatedActivity("D", "c" if c else "n3"),
                LocatedActivity("G", "c" if c else "n4")
            ]
        ]

    def _get_validation_trace(self, c: bool):
        return [
            LocatedActivity("A", "c" if c else "n1"),
            LocatedActivity("B", "c" if c else "n1"),
            LocatedActivity("D", "c" if c else "n3"),
            LocatedActivity("F", "c" if c else "n2"),
            LocatedActivity("G", "c" if c else "n4")
        ]

    def _get_training_traces_context_sensitive(self, c: bool):
        return [
            [
                LocatedActivity("A", "c" if c else "n1"),
                LocatedActivity("C", "c" if c else "n1"),
                LocatedActivity("E", "c" if c else "n2")
            ],
            [
                LocatedActivity("B", "c" if c else "n1"),
                LocatedActivity("C", "c" if c else "n1"),
                LocatedActivity("D", "c" if c else "n2"),
            ]
        ]

    def _get_validation_trace_context_sensitive(self, c: bool):
        return [
            LocatedActivity("A", "c" if c else "n1"),
            LocatedActivity("C", "c" if c else "n1"),
            LocatedActivity("D", "c" if c else "n2")
        ]

    def _get_training_traces_alternating(self, c: bool):
        return [
            [
                LocatedActivity("A", "c" if c else "n1"),
                LocatedActivity("A2", "c" if c else "n1"),
                LocatedActivity("B", "c" if c else "n2"),
                LocatedActivity("C", "c" if c else "n2"),
                LocatedActivity("D", "c" if c else "n1"),
                LocatedActivity("D2", "c" if c else "n1"),
                LocatedActivity("E", "c" if c else "n2"),
                LocatedActivity("E2", "c" if c else "n2"),
                LocatedActivity("E3", "c" if c else "n1"),
                LocatedActivity("E4", "c" if c else "n1")
            ]
        ]

    def _get_validation_traces_alternating(self, c: bool):
        return [
            LocatedActivity("A", "c" if c else "n1"),
            LocatedActivity("B", "c" if c else "n2"),
            LocatedActivity("C", "c" if c else "n2"),
            LocatedActivity("D", "c" if c else "n1"),
            LocatedActivity("D2", "c" if c else "n1"),
            LocatedActivity("E", "c" if c else "n2"),
            # LocatedActivity("E2", "c" if c else "n2"),
            LocatedActivity("E3", "c" if c else "n1"),
            LocatedActivity("E4", "c" if c else "n1")
        ]

    def _get_training_traces_skip_after_entry_point(self, c: bool):
        return [
            [
                LocatedActivity("A", "c" if c else "n1"),
                LocatedActivity("C", "c" if c else "n1"),
                LocatedActivity("D", "c" if c else "n2"),
                LocatedActivity("D2", "c" if c else "n2"),
                LocatedActivity("D3", "c" if c else "n2"),
                LocatedActivity("D4", "c" if c else "n2"),
                LocatedActivity("F", "c" if c else "n2")
            ],
            [
                LocatedActivity("A", "c" if c else "n1"),
                LocatedActivity("B", "c" if c else "n1"),
                LocatedActivity("E", "c" if c else "n2"),
                LocatedActivity("E2", "c" if c else "n2"),
                LocatedActivity("E3", "c" if c else "n2"),
                LocatedActivity("F", "c" if c else "n2")
            ]
        ]

    def _get_validation_traces_skip_after_entry_point(self, c: bool):
        return [
            LocatedActivity("A", "c" if c else "n1"),
            LocatedActivity("B", "c" if c else "n1"),
            LocatedActivity("D2", "c" if c else "n2"),
            LocatedActivity("D4", "c" if c else "n2"),
            LocatedActivity("F", "c" if c else "n2")
        ]

    def _get_training_traces_skip_node_simple(self, c: bool):
        return [
            [
                LocatedActivity("A", "c" if c else "n1"),
                LocatedActivity("B", "c" if c else "n2"),
                LocatedActivity("B2", "c" if c else "n2"),
                LocatedActivity("C", "c" if c else "n1"),
            ]
        ]

    def _get_real_dataset(self, c: bool):
        event_log_splitter = EventLogSplitter("gt/test/datasets/Sepsis.xes",
                                              location_key="org:group")
        training = event_log_splitter.get_training_data(10)
        result = []

        for key in training.traces:
            trace = []
            occurrences = {}
            for event in training.traces[key]:
                if not event.activity in occurrences:
                    occurrences[event.activity] = 1
                else:
                    occurrences[event.activity] = occurrences[event.activity] + 1
                trace.append(LocatedActivity(event.activity + "-" +  event.location + str(occurrences[event.activity]), "c" if c else event.location))
                if len(trace) >= 10:
                    break
            result.append(trace)

        return result

    def _get_real_dataset_validation(self, c: bool, record_index):
        event_log_splitter = EventLogSplitter(
            "gt/test/datasets/Sepsis.xes",
            location_key="org:group"
        )
        training = event_log_splitter.get_test_data(record_index)
        result = []

        for key in training.traces:
            trace = []
            occurrences = {}
            for event in training.traces[key]:
                if not event.activity in occurrences:
                    occurrences[event.activity] = 1
                else:
                    occurrences[event.activity] = occurrences[event.activity] + 1
                trace.append(LocatedActivity(event.activity + "-" +  event.location + str(occurrences[event.activity]), "c" if c else event.location))
                if len(trace) >= 10:
                    break
            result.append(trace)
        return result[0]

    def _get_validation_traces_skip_node_simple(self, c: bool):
        return [
            LocatedActivity("A", "c" if c else "n1"),
            LocatedActivity("C", "c" if c else "n1"),
        ]

    def _get_training_traces_skip_node(self, c: bool):
        return [
            [
                LocatedActivity("A", "c" if c else "n1"),
                LocatedActivity("B", "c" if c else "n2"),
                LocatedActivity("C", "c" if c else "n3"),
                LocatedActivity("D", "c" if c else "n1"),
                LocatedActivity("E", "c" if c else "n2"),
                LocatedActivity("F", "c" if c else "n1"),
            ]
        ]

    def _get_validation_traces_skip_node(self, c: bool):
        return [
            LocatedActivity("A", "c" if c else "n1"),
            LocatedActivity("C", "c" if c else "n3"),
        ]

    def _get_validation_traces_skip_node2(self, c: bool):
        return [
            LocatedActivity("A", "c" if c else "n1"),
            LocatedActivity("B", "c" if c else "n2"),
            LocatedActivity("C", "c" if c else "n3"),
            LocatedActivity("D", "c" if c else "n1"),
            LocatedActivity("F", "c" if c else "n1"),
        ]

    def _run(self, training_trace, validation_trace):
        trie_builders = {}
        last_event = None
        for trace in training_trace:
            for located_activity in trace:
                if located_activity.location not in trie_builders:
                    trie_builders[located_activity.location] = TrieBuilder(Trie())
                if last_event and last_event.location != located_activity.location:
                    trie_builders[located_activity.location].reset()
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

    def _run2(self, training_trace, validation_trace):
        network: Network = ModelTrainer().learn(training_trace)
        alignments = []
        for i, located_activity in enumerate(validation_trace):
            if not network.has_node(located_activity.location):
                network.add_node(located_activity.location, ContextProtocolNode(located_activity.location, network))
            alignment = network.get_node(located_activity.location).process_activity(located_activity.activity, i)
            alignments.append(alignment)
            print(located_activity)
            print(alignment)
        return alignments

    def _assert_equality_of_alignments(self, alignments_decentral, alignments_central):
        fail = False
        for i in range(len(alignments_decentral)):
            #self.assertEqual(len(alignments_central[i].elements), len(alignments_decentral[i].elements))
            set_central = set(alignments_central[i].elements)
            set_decentral = set(alignments_decentral[i].elements)
            not_matching = set_central.difference(set_decentral)
            if not_matching:
                print(
                    f"Alignments do not match.\nDecentral:\n{alignments_decentral[i]}\nCentral:\n{alignments_central[i]}")
                print("Difference:")
                print(''.join(f'{x}\n' for x in not_matching))
                fail = True
        self.assertFalse(fail)

    def test_example(self):
        alignments_decentral = self._run2(self._get_training_traces(False), self._get_validation_trace(False))
        alignments_central = self._run2(self._get_training_traces(True), self._get_validation_trace(True))
        self._assert_equality_of_alignments(alignments_decentral, alignments_central)

    def test_alternating(self):
        alignments_decentral = self._run2(
            self._get_training_traces_alternating(False),
            self._get_validation_traces_alternating(False)
        )
        alignments_central = self._run2(
            self._get_training_traces_alternating(True),
            self._get_validation_traces_alternating(True)
        )
        self._assert_equality_of_alignments(alignments_decentral, alignments_central)

    def test_validation_traces_skip_after_entry_point(self):
        alignments_decentral = self._run2(self._get_training_traces_skip_after_entry_point(False),
                                          self._get_validation_traces_skip_after_entry_point(False))
        alignments_central = self._run2(self._get_training_traces_skip_after_entry_point(True),
                                       self._get_validation_traces_skip_after_entry_point(True))
        self._assert_equality_of_alignments(alignments_decentral, alignments_central)

    def test_validation_traces_skip_node(self):
        alignments_decentral = self._run2(self._get_training_traces_skip_node(False),
                                          self._get_validation_traces_skip_node(False))
        alignments_central = self._run2(self._get_training_traces_skip_node(True),
                                       self._get_validation_traces_skip_node(True))
        self._assert_equality_of_alignments(alignments_decentral, alignments_central)

    def test_validation_traces_skip_node2(self):
        alignments_decentral = self._run2(self._get_training_traces_skip_node(False),
                                          self._get_validation_traces_skip_node2(False))
        alignments_central = self._run2(self._get_training_traces_skip_node(True),
                                       self._get_validation_traces_skip_node2(True))
        self._assert_equality_of_alignments(alignments_decentral, alignments_central)

    def test_validation_traces_skip_node_simple(self):
        alignments_decentral = self._run2(self._get_training_traces_skip_node_simple(False),
                                          self._get_validation_traces_skip_node_simple(False))
        alignments_central = self._run2(self._get_training_traces_skip_node_simple(True),
                                       self._get_validation_traces_skip_node_simple(True))
        self._assert_equality_of_alignments(alignments_decentral, alignments_central)

    def test_validation_traces_real(self):
        for i in range (1):
            alignments_decentral = self._run2(self._get_real_dataset(False),
                                              self._get_real_dataset_validation(False, i+1))
            print("-----")
            alignments_central = self._run2(self._get_real_dataset(True),
                                           self._get_real_dataset_validation(True, i+1))
            self._assert_equality_of_alignments(alignments_decentral, alignments_central)

    def test_context_sensitive(self):
      alignments_decentral = self._run2(self._get_training_traces_context_sensitive(False),
                                       self._get_validation_trace_context_sensitive(False))
      alignments_central = self._run2(self._get_training_traces_context_sensitive(True),
                                     self._get_validation_trace_context_sensitive(True))
      self._assert_equality_of_alignments(alignments_decentral, alignments_central)

    # TODO please consider all activities even though they are no entrypoints