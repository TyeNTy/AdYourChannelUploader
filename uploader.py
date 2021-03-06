from datetime import datetime
from multiprocessing import Queue
import sys
from threading import Thread
import time
from abstraction.IDataBaseService import IDataBaseService
from analyzer import Analyzer
from analyzerProcessor import AnalyzerProcessor
from chatBot import ChatBot
from models.uploaderStatus import UploaderStatus
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
        
        target_scope = [AuthScope.CHANNEL_MANAGE_BROADCAST, AuthScope.CHANNEL_READ_SUBSCRIPTIONS, AuthScope.CHANNEL_READ_STREAM_KEY]
        auth = UserAuthenticator(self.twitchAPI, target_scope, force_verify=False, url='http://localhost:17563')
        # this will open your default browser and prompt you with the twitch verification website
        token, refresh_token = auth.authenticate()
        # add User authentication
        self.twitchAPI.set_user_authentication(token, target_scope, refresh_token)
        
        newUploaderModel = dataBaseService.addUploader(clusterName, UploaderModel(clusterName, language, datetime.utcnow()))
        self.id = newUploaderModel.id
    
        self.multiThreadChangeHostQueue : Queue = None
        self.multiThreadEventQueue : Queue = None
    
    def __createSubscriptions(self, event : Event) -> None:
        self.multiThreadEventQueue = Queue()
        self.subscriptionHandler = SubscriptionHandler(self.twitchAPI, self.appID, self.myIP, 443, self.multiThreadEventQueue)
        self.subscriptionHandler.createFollowerSubscription(event.twitchUserName)
        self.subscriptionHandler.createSubscriptionSubscription(event.twitchUserName)
    
    def __deleteSubscriptions(self) -> None:
        allEvents = listAllEventSub(self.twitchAPI)
        for event in allEvents:
            self.subscriptionHandler.deleteSubscription(event['id'])

    def __initChatBot(self) -> None:
        scopes = [AuthScope.CHAT_EDIT, AuthScope.CHAT_READ, AuthScope.CHANNEL_MANAGE_BROADCAST]
        twitchAPIChat = Twitch(self.appID, self.appSecret)
        auth = UserAuthenticator(twitchAPIChat, scopes, force_verify=False, url='http://localhost:17563')
        token, refresh_token = auth.authenticate()
        self.multiThreadChangeHostQueue = Queue()
        self.chatBot = ChatBot(self.streamChannel, token, self.multiThreadChangeHostQueue)
        self.chatBotThreadPool = ThreadPool(processes=1)
        self.chatBotThreadPool.apply_async(self.chatBot.run, ())
        
    def runStreaming(self, event : Event) -> None:
        
        self.__createSubscriptions(event)
        
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
        self.__deleteSubscriptions()
        
    
    def run(self) -> None:
        isStreaming = False
        self.__initChatBot()
        try:
            while(True):
                try:
                    nextEvent = self.dataBaseService.getNextEvent(self.clusterName, self.id, self.language)
                    if(nextEvent is not None):
                        print(nextEvent)
                        isStreaming = True
                        self.multiThreadChangeHostQueue.put(nextEvent)
                        self.dataBaseService.updateStatusUploader(self.clusterName, self.id, UploaderStatus.STREAMING)
                        self.runStreaming(nextEvent)
                        self.dataBaseService.updateStatusUploader(self.clusterName, self.id, UploaderStatus.IDLE)
                        isStreaming = False
                    else:
                        self.dataBaseService.updateStatusUploader(self.clusterName, self.id, UploaderStatus.IDLE)
                        print(f"{datetime.utcnow()} : No event found...")
                        time.sleep(10)
                except Exception as err:
                    print(f"{datetime.utcnow()} : {err}")
        finally:
            self.dataBaseService.updateStatusUploader(self.clusterName, self.id, UploaderStatus.DELETING)
            if(isStreaming):
                print("Deleting the subscriptions...")
                self.__deleteSubscriptions()
            print("Closing the chat bot...")
            # self.chatBotThreadPool.terminate()
            # self.chatBotThreadPool.join()
            print("Deleting the uploader in the database...")
            self.dataBaseService.deleteUploaderByID(self.clusterName, self.id)
            print("Stopping webserver...")
            self.subscriptionHandler.shutdown()
            sys.exit(0)