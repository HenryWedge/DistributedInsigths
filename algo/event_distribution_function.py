from algo.event import Event

class EventDistributionFunction:
    def distribute(self, event: Event) -> str:
        pass

class EventLocationBasedDistributionFunction(EventDistributionFunction):
    def distribute(self, event: Event) -> str:
        return event.location

class EventActivityBasedDistributionFunction(EventDistributionFunction):
    def distribute(self, event: Event) -> str:
        return event.activity.get_activity()

class EventConstantDistributionFunction(EventDistributionFunction):
    def distribute(self, event: Event) -> str:
        return "central-location"