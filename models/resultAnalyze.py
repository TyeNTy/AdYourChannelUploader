from datetime import datetime

from models.followEvent import FollowEvent
from models.statisticTimeline import StatisticTimeline


class ResultAnalyze:
    def __init__(self,
                 eventID : str,
                 statisticTimeline : StatisticTimeline) -> None:
        self.eventID = eventID
        self.statisticTimeline = statisticTimeline
    
    def toDictionary(self) -> dict:
        return {
            "eventID": self.eventID,
            "statisticTimeline": self.statisticTimeline.toDictionary()
        }
    
    def __str__(self) -> str:
        txt = f"ResultAnalyze of the event {self.eventID} :\n"
        txt += str(self.statisticTimeline)
        return txt