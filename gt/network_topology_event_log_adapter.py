import string
from collections.abc import Callable

from algo.event_distribution_function import EventDistributionFunction
from algo.event_log import EventLog
from algo.network import Network
from algo.strategy.collect_previous_alignments_strategy import CollectPreviousAlignmentsStrategy
from algo.strategy.heap_pruning_strategy import HeapPruningStrategy
from gt.network_topology import NetworkTopology


class NetworkTopologyEventLogAdapter:

    def __init__(
            self,
            event_distribution_function: EventDistributionFunction,
            pruning_strategy: HeapPruningStrategy,
            collect_alignments_strategy: Callable[[Network, string], CollectPreviousAlignmentsStrategy]
    ):
        self.network_topology: NetworkTopology = NetworkTopology(
            event_distribution_function=event_distribution_function,
            pruning_strategy=pruning_strategy,
            collect_alignments_strategy=collect_alignments_strategy
        )

    def discovery(self, event_log: EventLog):
        for trace in event_log.traces:
            for event in event_log.traces[trace]:
                self.network_topology.process_discovery_event(event)

    def init_insight_nodes(self):
        self.network_topology.init_insight_nodes()

    def insights(self, event_log: EventLog):
        for trace in event_log.traces:
            for event in event_log.traces[trace]:
                self.network_topology.process_insights(event)
