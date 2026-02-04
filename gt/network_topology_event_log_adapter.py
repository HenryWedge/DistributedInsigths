import string
from collections.abc import Callable

from algo.event_log import EventLog
from algo.network import Network
from algo.strategy.collect_previous_alignments_strategy import CollectPreviousAlignmentsStrategy
from gt.network_topology import NetworkTopology


class NetworkTopologyEventLogAdapter:

    def __init__(
            self,
            max_heap_size: int,
            collect_alignments_strategy: Callable[[Network, string], CollectPreviousAlignmentsStrategy]
    ):
        self.network_topology: NetworkTopology = NetworkTopology(
            max_heap_size,
            collect_alignments_strategy=collect_alignments_strategy
        )

    def distribute_event_log_discovery(self, event_log: EventLog):
        for trace in event_log.traces:
            for event in event_log.traces[trace]:
                self.network_topology.process_discovery_event(event)

    def distribute_event_log_insights(self, event_log: EventLog):
        for trace in event_log.traces:
            for event in event_log.traces[trace]:
                self.network_topology.process_insights(event)
