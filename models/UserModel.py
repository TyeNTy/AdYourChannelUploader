from __future__ import annotations
from xmlrpc.client import DateTime
from models.entity import Entity

class UserModel(Entity):
    def __init__(self, id, twitchUserName : str = None, firstConnectionDate : DateTime = None, lastConnectionDate : DateTime = None, refreshToken : str = None, accessToken : str = None) -> None:
        Entity.__init__(self, id)
        self.twitchUserName : str = twitchUserName
        self.firstConnectionDate : DateTime = firstConnectionDate
        self.lastConnectionDate : DateTime = lastConnectionDate
        self.refreshToken : str = refreshToken
        self.accessToken : str = accessToken
    
    def loadFromDictionary(dictionary : dict) -> UserModel:
        return UserModel(dictionary["_id"],
                     dictionary["twitchUserName"],
                     dictionary["firstConnectionDate"],
                     dictionary["lastConnectionDate"],
                     dictionary["refreshToken"],
                     dictionary["accessToken"])