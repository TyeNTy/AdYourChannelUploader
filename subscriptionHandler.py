from functools import partial
from http.server import *
from multiprocessing import Queue
import ssl
from subscriptionHandlerEndpoint import SubscriptionHandlerEndPoint
from utils.twitchAPI import createNewSubscription, deleteSubscriptionByID, generateRandomString
from twitchAPI import Twitch
from threading import Thread

class SubscriptionHandler:
    
    def __init__(self, twitchAPI : Twitch, clientID : str, myIP : str, portToListen : int, multiThreadEventQueue : Queue) -> None:
        
        self.myIP = myIP
        self.twitchAPI = twitchAPI
        self.clientID = clientID
        self.portToListen = portToListen
        
        self.secretSubscriptionOurChannel : str = generateRandomString(100)
        self.followerSubscriptionID = None
        
        self.multiThreadEventQueue = multiThreadEventQueue
    
    def deleteSubscription(self, id : str) -> None:
        if(id is not None):
            deleteSubscriptionByID(self.twitchAPI, id)
    
    def createFollowerSubscription(self, channelName : str) -> None:
        oauthToken = self.twitchAPI.get_app_token()
        response = createNewSubscription(self.secretSubscriptionOurChannel, self.twitchAPI, self.clientID, channelName, "channel.follow", f"https://{self.myIP}/followerHandler", oauthToken)
        self.followerSubscriptionID = response.json()["data"][0]["id"]
        self.subscriptionHandler = partial(SubscriptionHandlerEndPoint, self.secretSubscriptionOurChannel, self.multiThreadEventQueue)
        self.httpServer = HTTPServer(('', self.portToListen), self.subscriptionHandler)
        self.httpServer.socket = ssl.wrap_socket (self.httpServer.socket, keyfile=f"C:\\Certbot\\live\\{self.myIP}\\privkey.pem" , certfile=f'C:\\Certbot\\live\\{self.myIP}\\fullchain.pem', server_side=True)
        self.serverThread = Thread(target=self.httpServer.serve_forever)
        self.serverThread.start()
    
    def shutdown(self):
        self.httpServer.shutdown()
        self.serverThread.join()
        print("Server stopped")