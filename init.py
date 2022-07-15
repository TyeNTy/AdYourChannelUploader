from datetime import datetime, timedelta
from models.event import Event
from models.uploader import UploaderModel
from uploader import Uploader
from services.databaseService import DataBaseService

def loadConfig() -> dict[str, str]:
    """Load a configuration file and return properties as a dictionary."""
    
    allLines = []
    with open("config.cfg", "r") as f:
        allLines = f.readlines()
    properties = {}
    for line in allLines:
        lineTrimmed = line.replace(" ", "").replace("\n", "").replace("\"", "").replace("\'", "")
        if(lineTrimmed != "" and lineTrimmed[0] != "#"):
            propName, propValue = lineTrimmed.split("=")
            properties[propName] = propValue
    return properties

def initUploader() -> Uploader:
    properties = loadConfig()
    
    databaseService = DataBaseService(properties["DATABASE_CONNECTION_STRING"], properties["DATABASE_NAME"])
    
    databaseService.createEvent(Event(None, "rlgym","cluster1", 0, datetime.utcnow(), datetime.utcnow() + timedelta(minutes=2), "fr", "test", ["this", "is", "a", "test"]))
    
    uploader = Uploader(properties["CLUSTER_NAME"], properties["LANGUAGE"], databaseService, properties["URL_CALL_BACK"], properties["APP_ID"], properties["APP_SECRET"], properties["GET_STREAM_ID"], properties["STREAM_CHANNEL"])
    uploader.run()