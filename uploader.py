from datetime import datetime, timedelta
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
from twitchAPI.types import InvalidTokenException
from subscriptionHandler import SubscriptionHandler
from utils.logger import getChildLogger

from utils.twitchAPI import listAllEventSub

class Uploader:
    target_scopes = [AuthScope.CHANNEL_MANAGE_BROADCAST, AuthScope.CHANNEL_READ_SUBSCRIPTIONS, AuthScope.CHANNEL_READ_STREAM_KEY, AuthScope.CHAT_EDIT, AuthScope.CHAT_READ]
    
    def __init__(self, clusterName : str, language : str, dataBaseService : IDataBaseService, myIP : str, appID : str, appSecret : str, getStreamID : str, streamChannel : str) -> None:
        self.logger = getChildLogger("uploader")
        
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
        
        self.twitchAPI = Twitch(self.appID, self.appSecret, authenticate_app=True, target_app_auth_scope=self.target_scopes)
        self.twitchAPI.auto_refresh_auth = True
    
        self.multiThreadChangeHostQueue : Queue = Queue()
        self.multiThreadEventQueue : Queue = Queue()
        
        self.streamLauncher = None
        
        auth = UserAuthenticator(self.twitchAPI, self.target_scopes, force_verify=False, url='http://localhost:17563')
        # this will open your default browser and prompt you with the twitch verification website
        token, refresh_token = self._loadStartup(self.startupFileName, auth)
        self.twitchAPI.set_user_authentication(token, self.target_scopes, refresh_token, validate=False)
        self.twitchAPI.refresh_used_token()
        self._saveTokensFromTwitchAPI(self.startupFileName, self.twitchAPI)
        
        self.subscriptionHandler = SubscriptionHandler(self.twitchAPI, self.myIP, 443, self.multiThreadEventQueue)
        
        newUploaderModel = dataBaseService.addUploader(clusterName, UploaderModel(clusterName, language, datetime.utcnow()))
        self.id = newUploaderModel.id
        self.exitInstruction = False
        
        self.stdinThread = Thread(target=self._stdinMainThread)
        self.stdinThread.start()
        self.analyzerThreads : list[Thread] = []
        
    def _stdinMainThread(self):
        for line in sys.stdin:
            if line.strip() == "exit":
                self.logger.info("Stdin Thread received exit instruction...")
                self.exitInstruction = True
                if(self.streamLauncher is not None):
                    self.streamLauncher.cutStream()
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
        try:
            if(os.path.exists(fileName)):
                with open(fileName, "r") as f:
                    lines = f.readlines()
                token = lines[0].replace("\n", "")
                refresh_token = lines[1].replace("\n", "")
            else:
                token, refresh_token = auth.authenticate()
                self._saveTokens(fileName, token, refresh_token)
            return token, refresh_token
        except IndexError:
            token, refresh_token = auth.authenticate()
            self._saveTokens(fileName, token, refresh_token)
    
    def __createSubscriptions(self, event : Event) -> None:
        self.subscriptionHandler.createFollowerSubscription(event.twitchUserName)
        self.subscriptionHandler.createSubscriptionSubscription(event.twitchUserName)
    
    def __deleteSubscriptions(self) -> None:
        self.logger.info("Deleting the subscriptions...")
        allEvents = listAllEventSub(self.twitchAPI)
        for event in allEvents:
            self.subscriptionHandler.deleteSubscription(event['id'])
        self.logger.info("Deleting the subscriptions... DONE !")

    def __initChatBot(self) -> None:
        self.logger.info("Launching the chat bot...")
        self.chatBot = ChatBot(self.streamChannel, self.twitchAPI, self.multiThreadChangeHostQueue, self.language)
        self.chatBotThreadPool = ThreadPool(processes=1)
        self.chatBotThreadPool.apply_async(self.chatBot.run, ())
        self.logger.info("Launching the chat bot... DONE !")
        
    def runStreaming(self, event : Event) -> None:
        user = self.dataBaseService.getUserByName(event.twitchUserName)
        if(user is not None):
            self.__createSubscriptions(event)
            
            self.streamLauncher = StreamLauncher(event, self.twitchAPI, self.appID, self.appSecret, self.getStreamID, self.streamChannel)
            streamAnalyzer = Analyzer(event, self.twitchAPI, self.appID, self.appSecret, self.streamChannel, self.multiThreadEventQueue)
            pool = ThreadPool(processes=1)
            asyncResult = pool.apply_async(streamAnalyzer.launchAnalyzer, ())
            pool.close()
            self.streamLauncher.runStreaming()
            allStatistics = asyncResult.get()
            analyzerProcessor = AnalyzerProcessor(self.twitchAPI, self.streamChannel, event, allStatistics, self.dataBaseService)
            self.analyzerThreads.append(Thread(target=analyzerProcessor.launchAnalyze, args=()))
            self.analyzerThreads[-1].start()
            self.__deleteSubscriptions()
        else:
            self.logger.error(f"User {event.twitchUserName} is not found... The event cannot be launched...")
        
    
    def run(self) -> None:
        timeBetweenCheckEvent = timedelta(seconds=10)

        isStreaming = False
        self.__initChatBot()
        currentTime = datetime.utcnow()
        nextCheck = currentTime + timeBetweenCheckEvent
        try:
            while(not self.exitInstruction):
                try:
                    currentTime = datetime.utcnow()
                    if(currentTime > nextCheck):
                        nextCheck = currentTime + timeBetweenCheckEvent
                        nextEvent = self.dataBaseService.getNextEvent(self.clusterName, self.id, self.language)
                        if(nextEvent is not None):
                            self.logger.info(f"New event found - {nextEvent}")
                            isStreaming = True
                            self.multiThreadChangeHostQueue.put(nextEvent)
                            self.dataBaseService.updateStatusUploader(self.clusterName, self.id, UploaderStatus.STREAMING)
                            self.runStreaming(nextEvent)
                            self.dataBaseService.updateStatusUploader(self.clusterName, self.id, UploaderStatus.IDLE)
                            isStreaming = False
                        else:
                            self.dataBaseService.updateStatusUploader(self.clusterName, self.id, UploaderStatus.IDLE)
                            self.logger.info(f"No event found...")
                    else:
                        time.sleep(1)
                except Exception as err:
                    self.logger.error(err)
        finally:
            self.logger.info("Deleting the uploader in the database...")
            self.dataBaseService.updateStatusUploader(self.clusterName, self.id, UploaderStatus.DELETING)
            self.dataBaseService.deleteUploaderByID(self.clusterName, self.id)
            if(isStreaming):
                self.__deleteSubscriptions()
            self.logger.info("Stopping subscription handler...")
            self.subscriptionHandler.shutdown()
            self.logger.info("Stopping subscription handler... DONE !")
            self.logger.info("Waiting the analyzer threads...")
            for thread in self.analyzerThreads:
                thread.join()
            self.logger.info("Waiting the analyzer threads... DONE !")
            self._saveTokensFromTwitchAPI(self.startupFileName, self.twitchAPI)
            self.logger.info("Deleting the uploader in the database... DONE !")
            sys.exit(0)