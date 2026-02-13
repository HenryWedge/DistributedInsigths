from algo.event_distribution_function import EventLocationBasedDistributionFunction, EventConstantDistributionFunction
from algo.strategy.collect_previous_alignments_strategy import CollectPreviousAlignmentsStrategyAskAll
from algo.strategy.heap_pruning_strategy import PruneHighestCostStrategy
from gt.network_topology_event_log_adapter import NetworkTopologyEventLogAdapter


class MetricsCalculator:

    def calculate_metrics(self):
        decentral_topology = NetworkTopologyEventLogAdapter(
            event_distribution_function=EventLocationBasedDistributionFunction(),
            pruning_strategy=PruneHighestCostStrategy(100),
            collect_alignments_strategy=
            lambda network, node_id:
            CollectPreviousAlignmentsStrategyAskAll(
                network,
                node_id
            )
        )

        decentral_topology2 = NetworkTopologyEventLogAdapter(
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
            # pruning_strategy=DoNotPruneStrategy(),
            collect_alignments_strategy=
            lambda network, node_id:
            CollectPreviousAlignmentsStrategyAskAll(
                network,
                node_id
            )
        )