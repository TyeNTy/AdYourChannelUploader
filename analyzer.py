from datetime import datetime, timedelta
from multiprocessing import Queue
from time import sleep
from abstraction.IDataBaseService import IDataBaseService
from models.analyze import Analyze
from models.event import Event
from twitchAPI import Twitch
from models.followEvent import FollowEvent
from models.statistic import Statistic
from models.subscribeEvent import SubscribeEvent
from utils.twitchAPI import getIDOfAChannel, createListOfChatters
from utils.logger import getChildLogger

class Analyzer:
    def __init__(self, event : Event, twitchAPI : Twitch, appID : str, appSecret : str, ourChannelName : str, multiThreadEventQueue : Queue) -> None:
        self.logger = getChildLogger("analyzer")
        
        self.event = event
        self.allStatistics = []
        self.alreadyFollowed = []
        self.alreadyChatting = []
        
        self.eventMessageIDs = set()
        
        self.appID = appID
        self.appSecret = appSecret
        self.ourChannelName = ourChannelName
        
        self.twitchAPI = twitchAPI
        self.idOfChannel = getIDOfAChannel(self.twitchAPI, self.event.twitchUserName)
        
        self.multiThreadEventQueue = multiThreadEventQueue
    
    def initAlreadyFollowed(self) -> None:
        """Initialize the list of already followed users."""
        self.alreadyFollowed = []
        pagination = None
        stillHavePagination = True
        nbLoaded = 0
        while(stillHavePagination):
            data = self.twitchAPI.get_users_follows(to_id = self.idOfChannel, after=pagination, first=100)
            followers = data['data']
            nbLoaded += len(followers)
            total = data['total']+1
            try:
                pagination = data['pagination']['cursor']
            except KeyError:
                stillHavePagination = False
            for follower in followers:
                self.alreadyFollowed.append(follower)
            self.logger.debug(f"Loading followers... {nbLoaded/total*100}%")
        self.logger.debug("Loading followers... 100%")
    
    def initAlreadyChatting(self) -> None:
        """Initialize the list of already chatting users."""
        self.alreadyChatting = createListOfChatters(self.event.twitchUserName)
        
    def launchAnalyzer(self) -> list[Statistic]:
        """Get the number of viewers of a streamer, the number of followers, the number of subscribers every 5s."""
        # self.initAlreadyFollowed()
        self.logger.info(f"Starting to analyze the channel {self.event.twitchUserName}...")
        self.initAlreadyChatting()
        allStats = []
        while(datetime.utcnow() < self.event.endTime):
            currentChattersOurChannel = createListOfChatters(self.ourChannelName)
            currentChattersOtherChannel = createListOfChatters(self.event.twitchUserName)
            listNewFollowers = []
            listNewSubscribers = []
            while(not self.multiThreadEventQueue.empty()):
                headers, event = self.multiThreadEventQueue.get()
                if(headers["twitch-eventsub-message-id"] not in self.eventMessageIDs):
                    self.eventMessageIDs.add(headers["twitch-eventsub-message-id"])
                    if(event["subscription"]["type"] == "channel.follow"):
                        followEvent = FollowEvent(event["event"])
                        listNewFollowers.append(followEvent)
                    elif(event["subscription"]["type"] == "channel.subscribe"):
                        subscribeEvent = SubscribeEvent(event["event"])
                        listNewSubscribers.append(subscribeEvent)
            currentStatistic = Statistic(datetime.utcnow(), currentChattersOurChannel, currentChattersOtherChannel, listNewFollowers, listNewSubscribers)
            allStats.append(currentStatistic)
            sleep(5)
        self.logger.info(f"Analyzing the channel {self.event.twitchUserName}... Done")
        return allStats