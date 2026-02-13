from datetime import datetime, timedelta

from algo.event import Event
from algo.event_distribution_function import EventConstantDistributionFunction, EventLocationBasedDistributionFunction
from algo.event_log import EventLog
from algo.strategy.collect_previous_alignments_strategy import CollectPreviousAlignmentsStrategyAskAll
from algo.strategy.heap_pruning_strategy import DoNotPruneStrategy
from gt.network_topology_event_log_adapter import NetworkTopologyEventLogAdapter


class SyntheticLogsSpecialCases:

    def get_training_data(self):
        event_log = EventLog()
        t = datetime.now()
        event_log.add_event(Event(case_id="c1", activity="A", location="N1", time=t+timedelta(0, 1)))
        event_log.add_event(Event(case_id="c1", activity="B", location="N1", time=t+timedelta(0, 2)))
        event_log.add_event(Event(case_id="c1", activity="E", location="N2", time=t+timedelta(0, 3)))
        event_log.add_event(Event(case_id="c1", activity="F", location="N2", time=t+timedelta(0, 4)))
        event_log.add_event(Event(case_id="c1", activity="H", location="N2", time=t+timedelta(0, 5)))
        event_log.add_event(Event(case_id="c1", activity="G", location="N4", time=t+timedelta(0, 6)))

        event_log.add_event(Event(case_id="c2", activity="A", location="N1", time=t+timedelta(0, 7)))
        event_log.add_event(Event(case_id="c2", activity="C", location="N1", time=t+timedelta(0, 8)))
        event_log.add_event(Event(case_id="c2", activity="D", location="N3", time=t+timedelta(0, 9)))
        event_log.add_event(Event(case_id="c2", activity="G", location="N4", time=t+timedelta(0, 10)))
        return event_log

    def get_test_data(self):
        event_log = EventLog()
        t = datetime.now()
        event_log.add_event(Event(case_id="c1", activity="A", location="N1", time=t+timedelta(0, 1)))
        event_log.add_event(Event(case_id="c1", activity="B", location="N1", time=t+timedelta(0, 2)))
        event_log.add_event(Event(case_id="c1", activity="D", location="N3", time=t+timedelta(0, 3)))
        event_log.add_event(Event(case_id="c1", activity="F", location="N2", time=t+timedelta(0, 4)))
        event_log.add_event(Event(case_id="c1", activity="G", location="N4", time=t+timedelta(0, 5)))
        return event_log

    def test(self):
        central = NetworkTopologyEventLogAdapter(
            event_distribution_function=EventConstantDistributionFunction(),
            pruning_strategy=DoNotPruneStrategy(),
            collect_alignments_strategy=
            lambda network, node_id:
            CollectPreviousAlignmentsStrategyAskAll(
                network,
                node_id
            )
        )
        decentral = NetworkTopologyEventLogAdapter(
                event_distribution_function=EventLocationBasedDistributionFunction(),
                pruning_strategy=DoNotPruneStrategy(),
                collect_alignments_strategy=
                lambda network, node_id:
                CollectPreviousAlignmentsStrategyAskAll(
                    network,
                    node_id
                )
            )
        #central.discovery(self.get_training_data())
        #central.init_insight_nodes()
        #central.insights(self.get_test_data())

        decentral.discovery(self.get_training_data())
        decentral.init_insight_nodes()
        decentral.insights(self.get_test_data())

if __name__ == '__main__':
    SyntheticLogsSpecialCases().test()