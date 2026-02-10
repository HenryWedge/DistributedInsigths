import csv
from statistics import median, mean
from typing import Dict, List

import numpy as np
from matplotlib import pyplot as plt

from algo.event_distribution_function import EventLocationBasedDistributionFunction, EventConstantDistributionFunction
from algo.strategy.collect_previous_alignments_strategy import CollectPreviousAlignmentsStrategyAskAll, \
    CollectPreviousAlignmentsStrategyAskOptimistically
from algo.strategy.heap_pruning_strategy import PruneHighestCostStrategy, DoNotPruneStrategy
from evaluation.metrics_record import MetricsRecord
from gt.event_log_splitter import EventLogSplitter
from gt.network_topology_event_log_adapter import NetworkTopologyEventLogAdapter


def write_results(data):
    with open("results.txt", "wb") as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        for line in data:
            writer.writerow(line)

def compare_topologies(alignments1, alignments2):
    return calculate_accuracy(alignments1, alignments2)

def calculate_metrics(topology, training_data, test_data):
    topology.discovery(training_data)
    topology.init_insight_nodes()
    topology.insights(test_data)
    alignments = topology.network_topology.get_cumulated_alignment_cost()
    network_requests = topology.network_topology.get_network_requests()
    heap_sizes = topology.network_topology.heap_size_monitor
    monitor = topology.network_topology.monitor

    return MetricsRecord(
        alignments=alignments,
        processing_time=monitor,
        network_requests=network_requests,
        heap_size=heap_sizes
    )

def calculate_accuracy(central_alignments, decentral_alignments) -> tuple[List[int], List[int], List[int]]:
    total_recall = []
    total_precision = []
    total_accuracy = []
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
        total_recall.append(recall)
        total_precision.append(precision)
        total_accuracy.append(accuracy)
        print(f"Recall: {mean(total_recall)}")
        print(f"Precision: {mean(total_precision)}")
        print(f"Accuracy: {mean(total_accuracy)}")
    return total_accuracy, total_precision, total_recall


def visualize_result(dataset):
    indices = np.arange(len(dataset[0][0]))

    plt.figure(figsize=(10, 6))
    markers = ['o', 's', '^', 'v', '<', '>', 'D', 'p', 'h', '*']
    linestyles = ['-', '--', ':', '-.']

    colors = plt.cm.tab10.colors

    for i, data in enumerate(dataset):
        plt.plot(
            indices,
            data[0],
            label=data[1],
            marker=markers[i % len(markers)],
            linestyle=linestyles[i % len(linestyles)],
            linewidth=2,
            color=colors[i % len(colors)]
        )

    plt.title('Visualization of Three Arrays by Index', fontsize=14)
    plt.xlabel('Threshold', fontsize=12)
    plt.ylabel('Values', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()  # Shows the labels defined in the plot functions

    # 5. Display the plot
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    test_traces_count = 100

    #event_log_splitter = EventLogSplitter("../gt/test/datasets/BPI_Challenge_2012.xes", location_key="org:resource")
    event_log_splitter = EventLogSplitter("../gt/test/datasets/Sepsis.xes", location_key="org:group")
    #event_log_splitter = EventLogSplitter("../gt/test/datasets/PermitLog.xes", location_key="org:resource")
    #event_log_splitter = EventLogSplitter("../gt/test/datasets/MainProcess.xes", location_key="org:resource")

    training = event_log_splitter.get_training_data()
    test = event_log_splitter.get_test_data(test_traces_count)

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

    #central_topology = NetworkTopologyEventLogAdapter(
    #    event_distribution_function=EventConstantDistributionFunction(),
    #    pruning_strategy=PruneHighestCostStrategy(10),
    #    # pruning_strategy=DoNotPruneStrategy(),
    #    collect_alignments_strategy=
    #    lambda network, node_id:
    #    CollectPreviousAlignmentsStrategyAskAll(
    #        network,
    #        node_id
    #    )
    #)
    training_data = event_log_splitter.get_training_data()
    test_data = event_log_splitter.get_test_data(test_traces_count)

    #topology1_metrics = calculate_metrics(central_topology, training_data, test_data)
    topology2_metrics = calculate_metrics(decentral_topology, training_data, test_data)
    topology3_metrics = calculate_metrics(decentral_topology2, training_data, test_data)

    #accuracy, precision, recall = compare_topologies(topology1_metrics.alignments, topology2_metrics.alignments)
    #accuracy2, precision2, recall2 = compare_topologies(topology1_metrics.alignments, topology3_metrics.alignments)
    visualize_result([
        #(topology1_metrics.network_requests, "network requests 1"),
        (topology2_metrics.heap_size, "Heap size 2"),
        (topology3_metrics.heap_size, "Heap size 3"),
        #(accuracy, 'Accuracy1'),
        #(accuracy2, 'Accuracy2'),
        #(recall, 'Recall1'),
        #(recall2, 'Recall2'),
        #(precision, 'Precision1'),
        #(precision2, 'Precision2'),
    ])
