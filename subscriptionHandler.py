from functools import partial
from http.server import *
from multiprocessing import Queue
import ssl
from models.event import Event
from subscriptionHandlerEndpoint import SubscriptionHandlerEndPoint
from utils.twitchAPI import createNewSubscription, deleteSubscriptionByID, generateRandomString
from twitchAPI import Twitch
from threading import Thread

class SubscriptionHandler:
    
    def __init__(self, twitchAPI : Twitch, clientID : str, myIP : str, portToListen : int, multiThreadEventQueue : Queue, event : Event) -> None:
        
        self.myIP = myIP
        self.twitchAPI = twitchAPI
        self.clientID = clientID
        self.portToListen = portToListen
        
        self.isWebServerLaunched = False
        
        self.secretSubscriptionOurChannel : str = generateRandomString(100)
        self.followerSubscriptionID = None
        self.SubscriptionSubscriptionID = None
        
        self.event = event
        
        self.multiThreadEventQueue = multiThreadEventQueue
    
    def deleteSubscription(self, id : str) -> None:
        if(id is not None):
            deleteSubscriptionByID(self.twitchAPI, id)
    
    def __launchWebServer(self) -> None:
        if not self.isWebServerLaunched:
            self.subscriptionHandler = partial(SubscriptionHandlerEndPoint, self.secretSubscriptionOurChannel, self.multiThreadEventQueue)
            self.httpServer = HTTPServer(('', self.portToListen), self.subscriptionHandler)
            self.httpServer.socket = ssl.wrap_socket (self.httpServer.socket, keyfile=f"C:\\Certbot\\live\\{self.myIP}\\privkey.pem" , certfile=f'C:\\Certbot\\live\\{self.myIP}\\fullchain.pem', server_side=True)
            self.serverThread = Thread(target=self.httpServer.serve_forever)
            self.serverThread.start()
            self.isWebServerLaunched = True
    
    def createFollowerSubscription(self, channelName : str) -> None:
        response = createNewSubscription(self.secretSubscriptionOurChannel, self.twitchAPI, self.clientID, channelName, "channel.follow", f"https://{self.myIP}/followerHandler")
        if(response.status_code == 202):
            self.followerSubscriptionID = response.json()["data"][0]["id"]
            self.__launchWebServer()
        else:
            print(f"Error creating follower subscription, status code : {response.status_code}")
    
    def createSubscriptionSubscription(self, channelName : str) -> None:
        response = createNewSubscription(self.secretSubscriptionOurChannel, self.twitchAPI, self.clientID, channelName, "channel.subscribe", f"https://{self.myIP}/subscriptionHandler")
        if(response.status_code == 202):
            self.SubscriptionSubscriptionID = response.json()["data"][0]["id"]
            self.__launchWebServer()
        else:
            print(f"Error creating sub subscription, status code : {response.status_code}")
    
    def shutdown(self):
        if self.isWebServerLaunched:
            self.httpServer.shutdown()
            self.serverThread.join()
            self.isWebServerLaunched = False
        print("Web server subscription handler stopped.")