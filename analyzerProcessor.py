from datetime import datetime, timedelta
from models.event import Event
from models.followEvent import FollowEvent
from models.resultAnalyze import ResultAnalyze
from models.statistic import Statistic
from abstraction.IDataBaseService import IDataBaseService
from models.statisticTimeline import StatisticTimeline
from models.subscribeEvent import SubscribeEvent
from twitchAPI import Twitch
from utils.twitchAPI import checkFollow, getIDOfAChannel

class AnalyzerProcessor:
    def __init__(self, twitchAPI : Twitch, channelName : str, event : Event, data : list[Statistic], dataBaseService : IDataBaseService) -> None:
        self.event = event
        self.data = data
        self.dataBaseService = dataBaseService
        self.twitchAPI = twitchAPI
        self.channelName = channelName
        self.ourChannelID = getIDOfAChannel(self.twitchAPI, self.channelName)
    
    def __testIfViewerInList(self, viewer : str, listNewViewers : list[tuple[datetime, str]]) -> bool:
        for _, otherViewer in listNewViewers:
            if viewer == otherViewer:
                return True
        return False
    
    def getViewerWhoOnlyWentToTheOtherChannel(self) -> list[tuple[datetime, str]]:
        listOlderChatters = set([])
        listNewViewers = set([])
        for statistic in self.data:
            for viewer in statistic.listOfViewersOurChannel:
                listOlderChatters.add(viewer)
            for viewer in statistic.listOfViewersOtherChannel:
                if viewer in listOlderChatters and not self.__testIfViewerInList(viewer, listNewViewers):
                    listNewViewers.add((statistic.date, viewer))
        return listNewViewers
    
    def regroupNewViewersPerMinute(self, listNewViewers : list[tuple[datetime, str]]) -> list[list[datetime, list[str]]]:
        if(len(listNewViewers) == 0):
            return []
        listNewViewers.sort(key=lambda x: x[0])
        startTime = listNewViewers[0][0]
        allMinutes : list[list[datetime, list[str]]] = [[startTime + timedelta(minutes=i), []] for i in range(0, 1 + (listNewViewers[-1][0] - startTime).total_seconds() // 60)]
        for time, newViewer in listNewViewers:
            index = (time - startTime).total_seconds() // 60
            allMinutes[index][1].append(newViewer)
        return allMinutes
    
    def allNewFollows(self) -> list[FollowEvent]:
        newFollowers = []
        for statistic in self.data:
            for follower in statistic.listNewFollowers:
                if(checkFollow(follower.userID)):
                    newFollowers.append(follower)
        return newFollowers
    
    def allNewSubs(self) -> list[SubscribeEvent]:
        newSubscribers = []
        for statistic in self.data:
            newSubscribers.extend(statistic.listNewSubscribers)
        return newSubscribers
    
    def __createTimeline(self, listNewViewers : list[tuple[datetime, str]], listNewFollowers : list[FollowEvent], listNewSubscribers : list[SubscribeEvent]) -> StatisticTimeline:
        
        timeline = StatisticTimeline(self.event.startTime, self.event.endTime)
        for date, _ in listNewViewers:
            timeline.addNewViewer(date)
        for newFollower in listNewFollowers:
            timeline.addNewFollow(newFollower.followedAT)
        for newSubscriber in listNewSubscribers:
            timeline.addNewSubEvent(newSubscriber)
        return timeline
    
    def launchAnalyze(self) -> ResultAnalyze:
        print("Starting to analyze the data...")
        listNewViewers = self.getViewerWhoOnlyWentToTheOtherChannel()
        newFollowers = self.allNewFollows()
        newSubscribers = self.allNewSubs()
        timeline = self.__createTimeline(listNewViewers, newFollowers, newSubscribers)
        resultAnalyze = ResultAnalyze(self.event.id, timeline)
        print("Analyzing the data... Done")
        print("Sending the result to the database...")
        self.dataBaseService.addResultAnalyze(resultAnalyze)
        print("Sending the result to the database... Done")
        return resultAnalyze
    
    def launchAnalyzeAndUploadItToDatabase(self):
        self.launchAnalyze()