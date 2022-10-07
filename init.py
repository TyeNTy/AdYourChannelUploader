from datetime import datetime, timedelta
from random import randint, random
from models.event import Event
from models.uploader import UploaderModel
from uploader import Uploader
from services.databaseService import DataBaseService

def splitPropNameAndPropValue(prop: str, separator : str) -> tuple[str, str]:
    splittedLine = prop.split(separator)
    return splittedLine[0], '='.join(splittedLine[1::])

def loadConfig() -> dict[str, str]:
    """Load a configuration file and return properties as a dictionary."""
    
    allLines = []
    with open("config.cfg", "r") as f:
        allLines = f.readlines()
    properties = {}
    for line in allLines:
        lineTrimmed = line.replace(" ", "").replace("\n", "").replace("\"", "").replace("\'", "")
        if(lineTrimmed != "" and lineTrimmed[0] != "#"):
            propName, propValue = splitPropNameAndPropValue(lineTrimmed, "=")
            properties[propName] = propValue
    return properties

def generateRandomEvents(databaseService : DataBaseService) -> None:
    numberOfHoursInAWeek = 24*7
    currentDelta = 0
    currentDate = datetime.utcnow()
    currentDate = currentDate - timedelta(microseconds=currentDate.microsecond, seconds=currentDate.second, minutes=currentDate.minute)
    while(currentDelta < numberOfHoursInAWeek):
        currentDelta += randint(1, 5)
        duration = randint(0,2)
        event = Event(None, "rlgym", "test", "cluster1", 0, currentDate + timedelta(hours=currentDelta), currentDate + timedelta(hours= currentDelta + duration, minutes=59), "fr", "test", ["this", "is", "a", "test"])
        currentDelta += duration
        databaseService.createEvent(event)
    

def initUploader() -> Uploader:
    properties = loadConfig()
    
    databaseService = DataBaseService(properties["DATABASE_CONNECTION_STRING"], properties["DATABASE_NAME"])
    
    # generateRandomEvents(databaseService)
    
    # databaseService.createEvent(Event(None, "rlgym", "alagnyglrrs8y9v3uj24dife3646xvijo5zhxvtiobhn61hrgs", "cluster1", 0, datetime.utcnow(), datetime.utcnow() + timedelta(minutes=4), "fr", "test", ["this", "is", "a", "test"]))
    # databaseService.createEvent(Event(None, "rlgym", "test", "cluster1", 0, datetime.utcnow() + timedelta(minutes=5), datetime.utcnow() + timedelta(minutes=9), "fr", "test", ["this", "is", "a", "test"]))
    
    uploader = Uploader(properties["CLUSTER_NAME"], properties["LANGUAGE"], databaseService, properties["URL_CALL_BACK"], properties["APP_ID"], properties["APP_SECRET"], properties["GET_STREAM_ID"], properties["STREAM_CHANNEL"])
    uploader.run()