
class MetricsRecord:

    def __init__(self, alignments, processing_time, network_requests, heap_size):
        self.alignments=alignments
        self.processing_time=processing_time
        self.network_requests=network_requests
        self.heap_size=heap_size
