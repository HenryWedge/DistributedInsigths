from gt.event_log_splitter import EventLogSplitter

if __name__ == '__main__':
    event_log_splitter = EventLogSplitter("../gt/test/datasets/Sepsis.xes", location_key="org:group")

    training = event_log_splitter.get_training_data(100)
    test = event_log_splitter.get_test_data(1)

