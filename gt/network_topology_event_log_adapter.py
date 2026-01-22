from algo.event_log import EventLog
from gt.network_topology import NetworkTopology


class NetworkTopologyEventLogAdapter:

    def __init__(self):
        self.network_topology: NetworkTopology = NetworkTopology()

    def distribute_event_log_discovery(self, event_log: EventLog):
        for trace in event_log.traces:
            for event in event_log.traces[trace]:
                self.network_topology.process_discovery_event(event)

    def distribute_event_log_insights(self, event_log: EventLog):
        for trace in event_log.traces:
            for event in event_log.traces[trace]:
                self.network_topology.process_insights(event)