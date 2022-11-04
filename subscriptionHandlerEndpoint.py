from http.server import BaseHTTPRequestHandler
import json
from multiprocessing import Queue
from utils.twitchAPI import validateSignature
from utils.logger import getChildLogger

class SubscriptionHandlerEndPoint(BaseHTTPRequestHandler):
    def __init__(self, secretSubscriptionOurChannel : str, multiThreadEventQueue : Queue, *args, **kwargs) -> None:
        self.logger = getChildLogger("subscriptionHandlerEndPoint")
        self.secretSubscriptionOurChannel = secretSubscriptionOurChannel
        self.multiThreadEventQueue = multiThreadEventQueue
        super().__init__(*args, **kwargs)
    
    def do_POST(self):
        body = str(self.rfile.read(int(self.headers['Content-Length'])), "utf-8")
        bodyDict = json.loads(body)
        is_valid = validateSignature(self.secretSubscriptionOurChannel, self.headers, body)
        
        if(is_valid):
            if(self.headers["twitch-eventsub-message-type"] == "webhook_callback_verification"):
                if (is_valid):
                    challenge : str = bodyDict['challenge']
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(bytes(challenge, "utf-8"))
                    self.logger.info(f"Creation of {bodyDict['subscription']['type']} subscription successful")
                return
            elif(self.headers["twitch-eventsub-message-type"] == "notification"):
                self.multiThreadEventQueue.put((self.headers, bodyDict))
                self.send_response(200)
                self.end_headers()
        else:
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"FORBIDDEN")
            self.logger.warning(f"Get request from {self.client_address}")