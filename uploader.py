from datetime import datetime
from multiprocessing import Queue
import os
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

from utils.twitchAPI import listAllEventSub

class Uploader:
    def __init__(self, clusterName : str, language : str, dataBaseService : IDataBaseService, myIP : str, appID : str, appSecret : str, getStreamID : str, streamChannel : str) -> None:
        self.startupFileName = "startup.cfg"
        self.startupChatFileName = "startupChat.cfg"
        
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
        self.twitchAPI.auto_refresh_auth = True
        self.otherChannelTwitchAPI = Twitch(self.appID, self.appSecret)
        
        target_scope = [AuthScope.CHANNEL_MANAGE_BROADCAST, AuthScope.CHANNEL_READ_SUBSCRIPTIONS, AuthScope.CHANNEL_READ_STREAM_KEY]
        auth = UserAuthenticator(self.twitchAPI, target_scope, force_verify=False, url='http://localhost:17563')
        # this will open your default browser and prompt you with the twitch verification website
        token, refresh_token = self._loadStartup(self.startupFileName, auth)
        self.twitchAPI.set_user_authentication(token, target_scope, refresh_token)
        self.twitchAPI.refresh_used_token()
        self._saveTokensFromTwitchAPI(self.startupFileName, self.twitchAPI)
        
        newUploaderModel = dataBaseService.addUploader(clusterName, UploaderModel(clusterName, language, datetime.utcnow()))
        self.id = newUploaderModel.id
    
        self.multiThreadChangeHostQueue : Queue = None
        self.multiThreadEventQueue : Queue = None
        self.exitInstruction = False
        
        self.stdinThread = Thread(target=self._stdinMainThread)
        self.stdinThread.start()
        self.analyzerThreads : list[Thread] = []
        
    def _stdinMainThread(self):
        for line in sys.stdin:
            if line.strip() == "exit":
                self.exitInstruction = True
                break
        
    def _saveTokensFromTwitchAPI(self, fileName : str, twitchAPI : Twitch):
        token = twitchAPI.get_user_auth_token()
        refresh_token = twitchAPI._Twitch__user_auth_refresh_token
        self._saveTokens(fileName, token, refresh_token)
        
    def _saveTokens(self, fileName : str, token : str, refresh_token : str) -> None:
        with open(fileName, "w") as f:
            f.write(token + "\n")
            f.write(refresh_token + "\n")
    
    def _loadStartup(self, fileName : str, auth : UserAuthenticator) -> tuple[str, str]:
        if(os.path.exists(fileName)):
            with open(fileName, "r") as f:
                lines = f.readlines()
            token = lines[0].replace("\n", "")
            refresh_token = lines[1].replace("\n", "")
        else:
            token, refresh_token = auth.authenticate()
            self._saveTokens(fileName, token, refresh_token)
        return token, refresh_token
    
    def __createSubscriptions(self, event : Event) -> None:
        self.multiThreadEventQueue = Queue()
        self.subscriptionHandler = SubscriptionHandler(self.otherChannelTwitchAPI, self.appID, self.myIP, 443, self.multiThreadEventQueue, event)
        self.subscriptionHandler.createFollowerSubscription(event.twitchUserName)
        self.subscriptionHandler.createSubscriptionSubscription(event.twitchUserName)
    
    def __deleteSubscriptions(self) -> None:
        allEvents = listAllEventSub(self.twitchAPI)
        for event in allEvents:
            self.subscriptionHandler.deleteSubscription(event['id'])

    def __initChatBot(self) -> None:
        scopes = [AuthScope.CHAT_EDIT, AuthScope.CHAT_READ, AuthScope.CHANNEL_MANAGE_BROADCAST]
        twitchAPIChat = Twitch(self.appID, self.appSecret)
        twitchAPIChat.auto_refresh_auth = True
        auth = UserAuthenticator(twitchAPIChat, scopes, force_verify=False, url='http://localhost:17563')
        token, refresh_token = self._loadStartup(self.startupChatFileName, auth)
        twitchAPIChat.set_user_authentication(token, scopes, refresh_token)
        twitchAPIChat.refresh_used_token()
        self._saveTokensFromTwitchAPI(self.startupChatFileName, twitchAPIChat)
        self.multiThreadChangeHostQueue = Queue()
        self.chatBot = ChatBot(self.streamChannel, twitchAPIChat, self.multiThreadChangeHostQueue, self.language)
        self.chatBotThreadPool = ThreadPool(processes=1)
        self.chatBotThreadPool.apply_async(self.chatBot.run, ())
        
    def runStreaming(self, event : Event) -> None:
        self.otherChannelTwitchAPI.__user_auth_refresh_token = event.refreshToken
        self.otherChannelTwitchAPI.refresh_used_token()
        
        self.__createSubscriptions(event)
        
        streamLauncher = StreamLauncher(event, self.twitchAPI, self.appID, self.appSecret, self.getStreamID, self.streamChannel)
        streamAnalyzer = Analyzer(event, self.otherChannelTwitchAPI, self.appID, self.appSecret, self.streamChannel, self.multiThreadEventQueue)
        pool = ThreadPool(processes=1)
        asyncResult = pool.apply_async(streamAnalyzer.launchAnalyzer, ())
        pool.close()
        streamLauncher.runStreaming()
        allStatistics = asyncResult.get()
        analyzerProcessor = AnalyzerProcessor(self.twitchAPI, self.streamChannel, event, allStatistics, self.dataBaseService)
        self.analyzerThreads.append(Thread(target=analyzerProcessor.launchAnalyze, args=()))
        self.analyzerThreads[-1].start()
        self.__deleteSubscriptions()
        
    
    def run(self) -> None:
        isStreaming = False
        self.__initChatBot()
        try:
            while(not self.exitInstruction):
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
            thread = self.dataBaseService.deleteUploaderByID(self.clusterName, self.id)
            if(isStreaming):
                print("Deleting the subscriptions...")
                self.__deleteSubscriptions()
                print("Stopping webserver...")
                self.subscriptionHandler.shutdown()
            print("Closing the chat bot...")
            # self.chatBotThreadPool.terminate()
            # self.chatBotThreadPool.join()
            print("Waiting the analyzer threads...")
            for thread in self.analyzerThreads:
                thread.join()
            print("Deleting the uploader in the database...")
            self._saveTokensFromTwitchAPI(self.startupFileName, self.twitchAPI)
            self._saveTokensFromTwitchAPI(self.startupChatFileName, self.chatBot.twitchAPI)
            sys.exit(0)