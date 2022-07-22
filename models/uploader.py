from __future__ import annotations
from datetime import datetime

from models.uploaderStatus import UploaderStatus

class UploaderModel:
    def __init__(self, id : int, language : str, lastHealthCheck : datetime, status : UploaderStatus = UploaderStatus.INIT) -> None:
        self.id = id
        self.language = language
        self.lastHealthCheck = lastHealthCheck
        self.status = status
    
    def __str__(self) -> str:
        return f"{self.id} ({self.language}) : {self.lastHealthCheck}"
    
    def loadFromDict(dictionary : dict) -> UploaderModel:
        if(dictionary is None):
            return None
        id = dictionary["id"]
        language = dictionary["language"]
        lastHealthCheck = dictionary["lastHealthCheck"]
        status = UploaderStatus[dictionary["status"]]
        return UploaderModel(id, language, lastHealthCheck, status)