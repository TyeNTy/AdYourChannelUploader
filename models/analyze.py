from models.event import Event
from models.statistic import Statistic

class Analyze:
    def __init__(self, event : Event) -> None:
        self.event = event
        self.listOfStatistics : list[Statistic] = []