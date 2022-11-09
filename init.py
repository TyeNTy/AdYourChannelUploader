from datetime import datetime, timedelta
from random import randint
from models.event import Event
from uploader import Uploader
from services.databaseService import DataBaseService
import utils.logger

def generateRandomEvents(databaseService : DataBaseService) -> None:
    numberOfHoursInAWeek = 24*7
    currentDelta = 0
    currentDate = datetime.utcnow()
    currentDate = currentDate - timedelta(microseconds=currentDate.microsecond, seconds=currentDate.second, minutes=currentDate.minute)
    while(currentDelta < numberOfHoursInAWeek):
        currentDelta += randint(1, 5)
        duration = randint(0,2)
        event = Event(None, "rlgym", "cluster1", 0, currentDate + timedelta(hours=currentDelta), currentDate + timedelta(hours= currentDelta + duration, minutes=59), "fr", "test", ["this", "is", "a", "test"])
        currentDelta += duration
        databaseService.createEvent(event)
    

def initUploader(configuration : dict[str, str]) -> None:
    # properties = loadConfig()
    utils.logger.loadConfig()
    
    databaseService = DataBaseService(configuration["DATABASE_CONNECTION_STRING"], configuration["DATABASE_NAME"])
    
    # databaseService.getNextEvent("cluster1", 1, "fr")
    
    # generateRandomEvents(databaseService)
    
    # databaseService.createEvent(Event(None, "rlgym", "cluster1", 0, datetime.utcnow(), datetime.utcnow() + timedelta(minutes=4), "fr", "test", ["this", "is", "a", "test"]))
    # databaseService.createEvent(Event(None, "rlgym", "cluster1", 0, datetime.utcnow() + timedelta(minutes=5), datetime.utcnow() + timedelta(minutes=9), "fr", "test", ["this", "is", "a", "test"]))
    
    uploader = Uploader(configuration["CLUSTER_NAME"], configuration["LANGUAGE"], databaseService, configuration["URL_CALL_BACK"], configuration["APP_ID"], configuration["APP_SECRET"], configuration["GET_STREAM_ID"], configuration["STREAM_CHANNEL"])
    uploader.run()