from datetime import datetime
from multiprocessing import Queue
import sys
import time
from abstraction.IDataBaseService import IDataBaseService
from analyzer import Analyzer
from analyzerProcessor import AnalyzerProcessor
from models.event import Event
from models.uploader import UploaderModel
from streamLauncher import StreamLauncher
from multiprocessing.pool import ThreadPool
from twitchAPI import Twitch, AuthScope, UserAuthenticator
from subscriptionHandler import SubscriptionHandler

from utils.twitchAPI import createNewSubscription, listAllEventSub

class Uploader:
    def __init__(self, clusterName : str, language : str, dataBaseService : IDataBaseService, myIP : str, appID : str, appSecret : str, getStreamID : str, streamChannel : str) -> None:
        self.dataBaseService = dataBaseService
        self.language = language
        self.clusterName = clusterName
        self.id = 0
        
        self.myIP = myIP
        self.appID = appID
        self.appSecret = appSecret
        self.streamChannel = streamChannel
        
        self.getStreamID = getStreamID
        
        self.twitchAPI = Twitch(self.appID, self.appSecret)
        
        target_scope = [AuthScope.CHANNEL_MANAGE_BROADCAST, AuthScope.CHANNEL_READ_SUBSCRIPTIONS]
        auth = UserAuthenticator(self.twitchAPI, target_scope, force_verify=False, url='http://localhost:17563')
        # this will open your default browser and prompt you with the twitch verification website
        token, refresh_token = auth.authenticate()
        # add User authentication
        self.twitchAPI.set_user_authentication(token, target_scope, refresh_token)
        
        newUploaderModel = dataBaseService.addUploader(clusterName, UploaderModel(clusterName, language, datetime.utcnow()))
        self.id = newUploaderModel.id
    
        self.multiThreadEventQueue : Queue = None
    
    def __createFollowerSubscription(self, event : Event) -> None:
        self.multiThreadEventQueue = Queue()
        self.subscriptionHandler = SubscriptionHandler(self.twitchAPI, self.appID, self.myIP, 443, self.multiThreadEventQueue)
        allEvents = listAllEventSub(self.twitchAPI)
        for event in allEvents:
            self.subscriptionHandler.deleteSubscription(event['id'])
        self.subscriptionHandler.createFollowerSubscription(event.twitchUserName)
    
    def __deleteFollowerSubscription(self) -> None:
        self.subscriptionHandler.deleteSubscription(self.subscriptionHandler.followerSubscriptionID)
    
    def runStreaming(self, event : Event) -> None:
        
        self.__createFollowerSubscription(event)
        
        streamLauncher = StreamLauncher(event, self.twitchAPI, self.appID, self.appSecret, self.getStreamID, self.streamChannel)
        streamAnalyzer = Analyzer(event, self.twitchAPI, self.appID, self.appSecret, self.multiThreadEventQueue)
        pool = ThreadPool(processes=1)
        asyncResult = pool.apply_async(streamAnalyzer.launchAnalyzer, ())
        pool.close()
        streamLauncher.runStreaming()
        allStatistics = asyncResult.get()
        analyzerProcessor = AnalyzerProcessor(event, allStatistics, self.dataBaseService)
        result = analyzerProcessor.launchAnalyze()
        print(result)
        self.__deleteFollowerSubscription()
        
    
    def run(self) -> None:
        isStreaming = False
        try:
            while(True):
                try:
                    nextEvent = self.dataBaseService.getNextEvent(self.clusterName, self.id, self.language)
                    if(nextEvent is not None):
                        print(nextEvent)
                        isStreaming = True
                        self.runStreaming(nextEvent)
                        isStreaming = False
                    else:
                        print(f"{datetime.utcnow()} : No event found...")
                        time.sleep(10)
                except Exception as err:
                    print(f"{datetime.utcnow()} : {err}")
        except BaseException:
            if(isStreaming):
                print("Deleting the follower subscription...")
                self.subscriptionHandler.deleteSubscription(self.subscriptionHandler.followerSubscriptionID)
            print("Deleting the uploader in the database...")
            self.dataBaseService.deleteUploaderByID(self.clusterName, self.id)
            print("Stopping webserver...")
            self.subscriptionHandler.shutdown()
            sys.exit(0)