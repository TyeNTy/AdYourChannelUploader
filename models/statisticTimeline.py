from datetime import datetime, timedelta
from tracemalloc import Statistic
from typing import Dict
from models.subscribeEvent import SubscribeEvent
from models.subscriberTiers import SubscriberTiers

from models.timeEvents import TimeEvents


class StatisticTimeline:
    def __init__(self, startTime : datetime, endTime : datetime) -> None:
        self.startTime = startTime
        self.endTime = endTime
        self.timeline : list[TimeEvents] = []
    
    def __getMinAndMaxDatetimeInMinutes(self, date : datetime) -> tuple[datetime, datetime]:
        minDate = datetime(date.year, date.month, date.day, date.hour, date.minute)
        maxDate = minDate + timedelta(minutes=1)
        return minDate, maxDate
    
    def __findIndexBetweenMinutes(self, date : datetime) -> int:
        for i, timeEvent in enumerate(self.timeline):
            dateTimestamp = date.timestamp()
            startStatisticTimestamp = timeEvent.startTime.timestamp()
            endStatisticTimestamp = timeEvent.endTime.timestamp()
            if(startStatisticTimestamp < dateTimestamp and endStatisticTimestamp > dateTimestamp):
                return i
            elif(startStatisticTimestamp < dateTimestamp):
                return -1
        return -1
    
    def __sortTimelinePerMinute(self):
        self.timeline.sort(key=lambda x: x.startTime)
    
    def addNewViewer(self, date : datetime) -> None:
        index = self.__findIndexBetweenMinutes(date)
        if index == -1:
            minDate, maxDate = self.__getMinAndMaxDatetimeInMinutes(date)
            self.timeline.append(TimeEvents(minDate, maxDate, 1, 0, 0, 0, 0))
            self.__sortTimelinePerMinute()
        else:
            self.timeline[index].newViewers += 1
    
    def addNewFollow(self, date : datetime) -> None:
        index = self.__findIndexBetweenMinutes(date)
        if index == -1:
            minDate, maxDate = self.__getMinAndMaxDatetimeInMinutes(date)
            self.timeline.append(TimeEvents(minDate, maxDate, 0, 1, 0, 0, 0))
            self.__sortTimelinePerMinute()
        else:
            self.timeline[index].newFollowers += 1
    
    def addNewSubEvent(self, subEvent : SubscribeEvent) -> None:
        if(subEvent.tier == SubscriberTiers.TIER1):
            self.addNewSubTier1(subEvent.subscribedAT)
        elif(subEvent.tier == SubscriberTiers.TIER2):
            self.addNewSubTier2(subEvent.subscribedAT)
        elif(subEvent.tier == SubscriberTiers.TIER3):
            self.addNewSubTier3(subEvent.subscribedAT)
    
    def addNewSubTier1(self, date : datetime) -> None:
        index = self.__findIndexBetweenMinutes(date)
        if index == -1:
            minDate, maxDate = self.__getMinAndMaxDatetimeInMinutes(date)
            self.timeline.append(TimeEvents(minDate, maxDate, 0, 0, 1, 0, 0))
            self.__sortTimelinePerMinute()
        else:
            self.timeline[index].newSubTier1 += 1
    
    def addNewSubTier2(self, date : datetime) -> None:
        index = self.__findIndexBetweenMinutes(date)
        if index == -1:
            minDate, maxDate = self.__getMinAndMaxDatetimeInMinutes(date)
            self.timeline.append(TimeEvents(minDate, maxDate, 0, 0, 0, 1, 0))
            self.__sortTimelinePerMinute()
        else:
            self.timeline[index].newSubTier2 += 1
    
    def addNewSubTier3(self, date : datetime) -> None:
        index = self.__findIndexBetweenMinutes(date)
        if index == -1:
            minDate, maxDate = self.__getMinAndMaxDatetimeInMinutes(date)
            self.timeline.append(TimeEvents(minDate, maxDate, 0, 0, 0, 0, 1))
            self.__sortTimelinePerMinute()
        else:
            self.timeline[index].newSubTier3 += 1
    
    def toDictionary(self) -> Dict:
        return {
            "timeline": [timeEvent.toDictionary() for timeEvent in self.timeline],
            "startTime": self.startTime,
            "endTime": self.endTime
        }
    
    def __str__(self) -> str:
        txt = ""
        for timeEvent in self.timeline:
            minDate, maxDate, newViewers, newFollowers, subTier1, subTier2, subTier3 = timeEvent.startTime, timeEvent.endTime, timeEvent.newViewers, timeEvent.newFollowers, timeEvent.newSubTier1, timeEvent.newSubTier2, timeEvent.newSubTier3
            txt += f"{minDate} - {maxDate}\n"
            txt += "\tNew viewers :\n"
            for newViewer in newViewers:
                txt += f"\t\t{newViewer}\n"
            txt += "\tNew followers :\n"
            for newFollower in newFollowers:
                txt += f"\t\t{newFollower}\n"
            txt += "\tNew sub tier 1 :\n"
            for subTier1 in subTier1:
                txt += f"\t\t{subTier1}\n"
            txt += "\tNew sub tier 2 :\n"
            for subTier2 in subTier2:
                txt += f"\t\t{subTier2}\n"
            txt += "\tNew sub tier 3 :\n"
            for subTier3 in subTier3:
                txt += f"\t\t{subTier3}\n"
        return txt