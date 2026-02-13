from algo.event_distribution_function import EventConstantDistributionFunction
from algo.strategy.collect_previous_alignments_strategy import CollectPreviousAlignmentsStrategyAskAll
from algo.strategy.heap_pruning_strategy import PruneHighestCostStrategy
from gt.network_topology_event_log_adapter import NetworkTopologyEventLogAdapter

if __name__ == '__main__':
    NetworkTopologyEventLogAdapter(
        event_distribution_function=EventConstantDistributionFunction(),
        pruning_strategy=PruneHighestCostStrategy(10 ** i),
        collect_alignments_strategy=
        lambda network, node_id:
        CollectPreviousAlignmentsStrategyAskAll(
            network,
            node_id
        )
    )