from datetime import datetime
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
    
    uploader = Uploader(properties["CLUSTER_NAME"], properties["LANGUAGE"], databaseService)
    uploader.run()