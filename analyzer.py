from datetime import datetime, timedelta
from time import sleep
from abstraction.IDataBaseService import IDataBaseService
from models.analyze import Analyze
from models.event import Event
from twitchAPI import Twitch
from models.statistic import Statistic
from utils.twitchAPI import getIDOfAChannel, createListOfChatters

class Analyzer:
    def __init__(self, event : Event, appID : str, appSecret : str) -> None:
        self.event = event
        self.allStatistics = []
        self.alreadyFollowed = []
        self.alreadyChatting = []
        
        self.appID = appID
        self.appSecret = appSecret
        
        self.twitchAPI = Twitch(self.appID, self.appSecret)
        self.idOfChannel = getIDOfAChannel(self.twitchAPI, self.event.twitchUserName)
    
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
            print(f"Loading followers... {nbLoaded/total*100}%")
        print("Loading followers... 100%")
    
    def initAlreadyChatting(self) -> None:
        """Initialize the list of already chatting users."""
        self.alreadyChatting = createListOfChatters(self.event.twitchUserName)
    
    def launchAnalyzer(self) -> list[Statistic]:
        """Get the number of viewers of a streamer, the number of followers, the number of subscribers every 5s."""
        # self.initAlreadyFollowed()
        print(f"Starting to analyze the channel {self.event.twitchUserName}...")
        self.initAlreadyChatting()
        allStats = []
        while(datetime.utcnow() < self.event.endTime):
            currentChattersOurChannel = createListOfChatters("adyourchanneldev")
            currentChattersOtherChannel = createListOfChatters(self.event.twitchUserName)
            currentStistic = Statistic(datetime.utcnow(), currentChattersOurChannel, currentChattersOtherChannel, self.alreadyFollowed, len(currentChattersOtherChannel), len(self.alreadyFollowed), 0)
            allStats.append(currentStistic)
            sleep(5)
        print(f"Analyzing the channel {self.event.twitchUserName}... Done")
        return allStats