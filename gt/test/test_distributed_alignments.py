import unittest
from statistics import median
from typing import Dict

from algo.event_distribution_function import EventLocationBasedDistributionFunction, EventConstantDistributionFunction
from algo.strategy.collect_previous_alignments_strategy import CollectPreviousAlignmentsStrategyAskAll, \
    CollectPreviousAlignmentsStrategyAskOptimistically
from algo.strategy.heap_pruning_strategy import DoNotPruneStrategy, PruneHighestCostStrategy
from gt.event_log_splitter import EventLogSplitter
from gt.network_topology_event_log_adapter import NetworkTopologyEventLogAdapter


class TestGroundTruthAlignments(unittest.TestCase):

    def test_ground_truth_alignments(self):
        event_log_splitter = EventLogSplitter("./datasets/Sepsis.xes", location_key="org:group")
        test_traces_count = 100

        decentral_topology = NetworkTopologyEventLogAdapter(
            event_distribution_function=EventLocationBasedDistributionFunction(),
            pruning_strategy=PruneHighestCostStrategy(10),
            collect_alignments_strategy=
            lambda network, node_id:
            CollectPreviousAlignmentsStrategyAskAll(
                network,
                node_id
            )
        )

        central_topology = NetworkTopologyEventLogAdapter(
            event_distribution_function=EventConstantDistributionFunction(),
            pruning_strategy=PruneHighestCostStrategy(10),
            #pruning_strategy=DoNotPruneStrategy(),
            collect_alignments_strategy=
            lambda network, node_id:
            CollectPreviousAlignmentsStrategyAskOptimistically(
                network,
                node_id
            )
        )

        decentral_topology.discovery(event_log_splitter.get_training_data())
        decentral_topology.insights(event_log_splitter.get_test_data(test_traces_count))
        #decentral_topology.insights(event_log_splitter.get_case("KG"))

        central_topology.discovery(event_log_splitter.get_training_data())
        central_topology.insights(event_log_splitter.get_test_data(test_traces_count))
        #central_topology.insights(event_log_splitter.get_case("KG"))

        central_alignments: Dict[str, int] = central_topology.network_topology.get_cumulated_alignment_cost()
        decentral_alignments: Dict[str, int] = decentral_topology.network_topology.get_cumulated_alignment_cost()

        total_network_requests: int = decentral_topology.network_topology.get_network_requests()

        distributed_monitor = decentral_topology.network_topology.monitor
        central_monitor = central_topology.network_topology.monitor
        print(max(distributed_monitor))
        print(median(distributed_monitor))
        print(max(central_monitor))
        print(median(central_monitor))
        print(f"Network requests: {total_network_requests}")

        accumulated_error = []
        correct_classified = 0
        #for case_id in decentral_alignments:
        #    print(f"Case Id: {case_id} {(decentral_alignments[case_id], central_alignments[case_id])}")

        avg_recall = 0
        avg_precision = 0
        avg_accuracy = 0

        for threshold in range(12):
            tp = 0
            tn = 0
            fp = 0
            fn = 0
            for case_id in central_alignments:
                if central_alignments[case_id] > threshold and decentral_alignments[case_id] > threshold:
                    tp += 1
                elif central_alignments[case_id] > threshold:
                    fn += 1
                elif decentral_alignments[case_id] > threshold:
                    fp += 1
                else:
                    tn += 1
            print(f"-----{threshold}-----")
            print(tp, tn, fp, fn)
            recall = tp / max(1, tp + fn)
            precision = tp / max(1, tp + fp)
            accuracy = (tp + tn) / max(1, tp + fp + tn + fn)
            avg_recall += recall
            avg_precision += precision
            avg_accuracy += accuracy
            print(f"Recall: {recall}")
            print(f"Precision: {precision}")
            print(f"Accuracy: {accuracy}")

        print(f"Avg Recall: {avg_recall / 12}")
        print(f"Avg Precision: {avg_precision / 12}")
        print(f"Avg Accuracy: {avg_accuracy / 12}")

        print("Total error: ", sum(accumulated_error) / len(central_alignments))
        print("Correct classified: ", correct_classified / test_traces_count)
        print("Finished")


if __name__ == '__main__':
    unittest.main()
