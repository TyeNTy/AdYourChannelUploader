from __future__ import annotations
from datetime import datetime

class UploaderModel:
    def __init__(self, id : int, language : str, lastHealthCheck : datetime) -> None:
        self.id = id
        self.language = language
        self.lastHealthCheck = lastHealthCheck
    
    def __str__(self) -> str:
        return f"{self.id} ({self.language}) : {self.lastHealthCheck}"
    
    def loadFromDict(dictionary : dict) -> UploaderModel:
        if(dictionary is None):
            return None
        id = dictionary["id"]
        language = dictionary["language"]
        lastHealthCheck = dictionary["lastHealthCheck"]
        return UploaderModel(id, language, lastHealthCheck)