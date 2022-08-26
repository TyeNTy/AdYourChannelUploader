from __future__ import annotations
from datetime import datetime
from models.entity import Entity

class Event(Entity):
    def __init__(self, id : str,
                 twitchUserName : str,
                 refreshToken : str,
                 clusterName : str,
                 uploaderID : int,
                 startTime : datetime,
                 endTime : datetime,
                 language :str,
                 streamTitle : str = "",
                 tags = []):
        Entity.__init__(self, id)
        self.twitchUserName : str = twitchUserName
        self.refreshToken : str = refreshToken
        self.clusterName : str = clusterName
        self.uploaderID : int = uploaderID
        self.startTime : datetime = startTime
        self.endTime : datetime = endTime
        self.language = language
        
        self.streamTitle : str = streamTitle
        self.tags : list[str] = tags
    
    def loadFromDictionary(dictionary : dict) -> Event:
        return Event(dictionary["_id"],
                     dictionary["twitchUserName"],
                     dictionary["refreshToken"],
                     dictionary["clusterName"],
                     dictionary["uploaderID"],
                     dictionary["startTime"],
                     dictionary["endTime"],
                     dictionary["language"],
                     dictionary["streamTitle"],
                     dictionary["tags"])
    
    def __str__(self) -> str:
        return f"{self.twitchUserName}({self.language}) : {self.startTime}-{self.endTime} {self.streamTitle}, {self.tags} ({self.clusterName} - {self.id})"