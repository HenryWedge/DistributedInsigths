import csv
import io
from statistics import median, mean
from typing import Dict, List

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from algo.event_distribution_function import EventLocationBasedDistributionFunction, EventConstantDistributionFunction
from algo.strategy.collect_previous_alignments_strategy import CollectPreviousAlignmentsStrategyAskAll, \
    CollectPreviousAlignmentsStrategyAskOptimistically
from algo.strategy.heap_pruning_strategy import PruneHighestCostStrategy, DoNotPruneStrategy
from evaluation.metrics_record import MetricsRecord
from gt.event_log_splitter import EventLogSplitter
from gt.network_topology_event_log_adapter import NetworkTopologyEventLogAdapter


def write_results(filename, data):
    dataframe = pd.DataFrame(data)
    dataframe.to_csv(filename, index=False)
    #with open("datei.csv", "w", newline="", encoding="utf-8") as f:
    #    writer = csv.writer(f)
    #    for element in data:
    #        writer.writerow([element])

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
    training_traces_count = 1000
    test_traces_count = 100

    event_log_splitter = EventLogSplitter("../gt/test/datasets/BPI_Challenge_2012.xes", location_key="org:resource")
    #event_log_splitter = EventLogSplitter("../gt/test/datasets/Sepsis.xes", location_key="org:group")
    #event_log_splitter = EventLogSplitter("../gt/test/datasets/PermitLog.xes", location_key="org:resource")
    #event_log_splitter = EventLogSplitter("../gt/test/datasets/MainProcess.xes", location_key="org:resource")

    training = event_log_splitter.get_training_data(training_traces_count)
    test = event_log_splitter.get_test_data(test_traces_count)
    number_of_topologies = 5

    decentral_topology_variants = []
    for i in range(number_of_topologies - 1):
        decentral_topology_variants.append(
            NetworkTopologyEventLogAdapter(
                event_distribution_function=EventLocationBasedDistributionFunction(),
                pruning_strategy=PruneHighestCostStrategy(10**i),
                collect_alignments_strategy=
                lambda network, node_id:
                CollectPreviousAlignmentsStrategyAskAll(
                    network,
                    node_id
                )
            )
        )

    #decentral_topology_variants.append(NetworkTopologyEventLogAdapter(
    #    event_distribution_function=EventLocationBasedDistributionFunction(),
    #    pruning_strategy=DoNotPruneStrategy(),
    #    collect_alignments_strategy=
    #    lambda network, node_id:
    #    CollectPreviousAlignmentsStrategyAskAll(
    #        network,
    #        node_id
    #    )
    #))

    central_topology_variants = []

    for i in range(number_of_topologies-1):
        central_topology_variants.append(
            NetworkTopologyEventLogAdapter(
                event_distribution_function=EventConstantDistributionFunction(),
                pruning_strategy=PruneHighestCostStrategy(10**i),
                collect_alignments_strategy=
                lambda network, node_id:
                CollectPreviousAlignmentsStrategyAskAll(
                    network,
                    node_id
                )
            )
        )

    central_topology_variants.append(
        NetworkTopologyEventLogAdapter(
            event_distribution_function=EventConstantDistributionFunction(),
            pruning_strategy=DoNotPruneStrategy(),
            collect_alignments_strategy=
            lambda network, node_id:
            CollectPreviousAlignmentsStrategyAskAll(
                network,
                node_id
            )
        )
    )

    #topology1_metrics = calculate_metrics(central_topology, training, test)

    metrics = []
    for i in range(number_of_topologies-1):
        metrics.append(calculate_metrics(decentral_topology_variants[i], training, test))

    #accuracy, precision, recall = compare_topologies(topology1_metrics.alignments, topology2_metrics.alignments)
    #accuracy2, precision2, recall2 = compare_topologies(topology1_metrics.alignments, topology3_metrics.alignments)

    results_dictionary_alignments = {}
    results_dictionary_processing_times = {}
    results_dictionary_heap_sizes = {}
    results_dictionary_network_requests = {}
    for i in range(number_of_topologies-1):
        results_dictionary_alignments[f"prune_{10**i}_alignments"] = list(metrics[i].alignments.values())
        results_dictionary_processing_times[f"prune{10**i}_processing_time"] = list(metrics[i].processing_time)
        results_dictionary_heap_sizes[f"prune{10**i}_heap_size"] = list(metrics[i].heap_size)
        results_dictionary_network_requests[f"prune{10**i}_heap_size"] = list(metrics[i].network_requests)

    write_results("result_alignment_decentral2.csv", results_dictionary_alignments)
    write_results("result_processing_time_decentral2.csv", results_dictionary_processing_times)
    write_results("result_heap_size_decentral2.csv", results_dictionary_heap_sizes)
    write_results("result_network_requests_decentral.csv", results_dictionary_network_requests)

    ##visualize_result([
    ##    #(topology1_metrics.network_requests, "network requests 1"),
    ##    (topology2_metrics.heap_size, "Heap size 2"),
    ##    (topology3_metrics.heap_size, "Heap size 3"),
    ##    #(accuracy, 'Accuracy1'),
    ##    #(accuracy2, 'Accuracy2'),
    ##    #(recall, 'Recall1'),
    ##    #(recall2, 'Recall2'),
    ##    #(precision, 'Precision1'),
    ##    #(precision2, 'Precision2'),
    ##])
