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
        test_traces_count = 50

        decentral_topology = NetworkTopologyEventLogAdapter(
            event_distribution_function=EventLocationBasedDistributionFunction(),
            pruning_strategy=PruneHighestCostStrategy(10),
            collect_alignments_strategy=
            lambda network, node_id:
            CollectPreviousAlignmentsStrategyAskOptimistically(
                network,
                node_id
            )
        )

        central_topology = NetworkTopologyEventLogAdapter(
            event_distribution_function=EventConstantDistributionFunction(),
            pruning_strategy=PruneHighestCostStrategy(10000),
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

        central_topology.discovery(event_log_splitter.get_training_data())
        central_topology.insights(event_log_splitter.get_test_data(test_traces_count))

        central_alignments: Dict[str, int] = central_topology.network_topology.get_cumulated_alignment_cost()
        decentral_alignments: Dict[str, int] = decentral_topology.network_topology.get_cumulated_alignment_cost()


        # TODO hrei calculate total network costs
        total_network_requests = 0

        distributed_monitor = decentral_topology.network_topology.monitor
        central_monitor = central_topology.network_topology.monitor
        print(max(distributed_monitor))
        print(median(distributed_monitor))
        print(max(central_monitor))
        print(median(central_monitor))
        print(f"Network requests: {total_network_requests}")

        correlation_matrix = {}
        accumulated_error = 0
        correct_classified = 0
        error_threshold = 0.5
        for case_id in decentral_alignments:
            print(f"Case Id: {case_id} {(decentral_alignments[case_id], central_alignments[case_id])}")

        for case_id in central_alignments:
            relative_error = (
                    (central_alignments[case_id] - decentral_alignments[case_id]) /
                    max(1, central_alignments[case_id], decentral_alignments[case_id])
            )
            if abs(relative_error) < error_threshold:
                correct_classified += 1
            correlation_matrix[case_id] = relative_error
            accumulated_error += relative_error
            print(f"{case_id}: {correlation_matrix[case_id]}")
        print("Total error: ", accumulated_error / len(central_alignments))
        print("Correct classified: ", correct_classified / test_traces_count)
        print("Finished")


if __name__ == '__main__':
    unittest.main()
