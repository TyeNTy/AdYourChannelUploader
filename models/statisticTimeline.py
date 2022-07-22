from datetime import datetime, timedelta


class StatisticTimeline:
    def __init__(self) -> None:
        self.timeline = []
    
    def __getMinAndMaxDatetimeInMinutes(self, date : datetime) -> tuple[datetime, datetime]:
        minDate = datetime(date.year, date.month, date.day, date.hour, date.minute)
        maxDate = minDate + timedelta(minutes=1)
        return minDate, maxDate
    
    def __findIndexBetweenMinutes(self, date : datetime) -> int:
        for i, statistic in enumerate(self.timeline):
            dateTimestamp = date.timestamp()
            startStatisticTimestamp = statistic[0].timestamp()
            endStatisticTimestamp = statistic[1].timestamp()
            if(startStatisticTimestamp < dateTimestamp and endStatisticTimestamp > dateTimestamp):
                return i
            elif(startStatisticTimestamp < dateTimestamp):
                return -1
        return -1
    
    def __sortTimelinePerMinute(self):
        self.timeline.sort(key=lambda x: x[0])
    
    def addNewViewer(self, date : datetime, viewer : str) -> None:
        index = self.__findIndexBetweenMinutes(date)
        if index == -1:
            minDate, maxDate = self.__getMinAndMaxDatetimeInMinutes(date)
            self.timeline.append((minDate, maxDate, [viewer], [], [], [], []))
            self.__sortTimelinePerMinute()
        else:
            self.timeline[index][2].append(viewer)
    
    def addNewFollow(self, date : datetime, follower : str) -> None:
        index = self.__findIndexBetweenMinutes(date)
        if index == -1:
            minDate, maxDate = self.__getMinAndMaxDatetimeInMinutes(date)
            self.timeline.append((minDate, maxDate, [], [follower], [], [], []))
            self.__sortTimelinePerMinute()
        else:
            self.timeline[index][3].append(follower)
    
    def addNewSubTier1(self, date : datetime, subTier1 : str) -> None:
        index = self.__findIndexBetweenMinutes(date)
        if index == -1:
            minDate, maxDate = self.__getMinAndMaxDatetimeInMinutes(date)
            self.timeline.append((minDate, maxDate, [], [], [subTier1], [], []))
            self.__sortTimelinePerMinute()
        else:
            self.timeline[index][4].append(subTier1)
    
    def addNewSubTier1(self, date : datetime, subTier2 : str) -> None:
        index = self.__findIndexBetweenMinutes(date)
        if index == -1:
            minDate, maxDate = self.__getMinAndMaxDatetimeInMinutes(date)
            self.timeline.append((minDate, maxDate, [], [], [subTier2], [], []))
            self.__sortTimelinePerMinute()
        else:
            self.timeline[index][4].append(subTier2)
    
    def addNewSubTier1(self, date : datetime, subTier3 : str) -> None:
        index = self.__findIndexBetweenMinutes(date)
        if index == -1:
            minDate, maxDate = self.__getMinAndMaxDatetimeInMinutes(date)
            self.timeline.append((minDate, maxDate, [], [], [subTier3], [], []))
            self.__sortTimelinePerMinute()
        else:
            self.timeline[index][4].append(subTier3)
    
    def toDictionary(self):
        return {
            "timeline": self.timeline
        }
    
    def __str__(self) -> str:
        txt = ""
        for minDate, maxDate, newViewers, newFollowers, subTier1, subTier2, subTier3 in self.timeline:
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