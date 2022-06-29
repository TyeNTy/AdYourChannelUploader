from datetime import datetime, timedelta
from models.ListUploaders import ListUploaders
from pymongo import MongoClient
from models.uploader import UploaderModel
from models.event import Event

class DataBaseService:
    
    def __init__(self, mongoDBConnectionString : str, dataBaseName : str):
        self.client = MongoClient(mongoDBConnectionString)
        self.database = self.client[dataBaseName]
        self.uploadersCollection = self.database.get_collection("uploaders")
    
    def getEvent(self, event : Event) -> Event:
        """Try to get the event."""
        raise NotImplementedError
    
    def getNextEvent(self, clusterName : str, uploaderID : int, language : str) -> Event|None:
        """Try to get the next event to take place in the uploaderID uploader inside of the cluster clusterName."""
        result = self.database.get_collection(language).find({"clusterName" : clusterName, "uploaderID" : uploaderID, "language" : language})
        if (result is None):
            return None
        else:
            result = sorted(filter(lambda event : event["startTime"] > datetime.utcnow() - timedelta(minutes=1) and event["startTime"] < datetime.utcnow() + timedelta(minutes=1), result), key=lambda event : event["startTime"])
            if(len(result) == 0):
                return None
            return Event.loadFromDictionary(result[0])

    def createEvent(self, event : Event) -> Event:
        """Create an event in the data set."""
        collection = self.database.get_collection(event.language)
        alreadyExistingEvent = collection.find({"clusterName" : event.clusterName, "uploaderID" : event.uploaderID, "language" : event.language, "startTime" : {'$gte' : event.startTime, '$lte' : event.endTime}})
        if alreadyExistingEvent is not None:
            toSend = vars(event)
            toSend.pop("id")
            collection.insert_one(vars(event))
            return event
        print(f"Event already exists : {alreadyExistingEvent}")
        return None

    def deleteEvent(self, Event):
        """Delete the event in the data set."""
        raise NotImplementedError

    def getCurrentUploaders(self, clusterName : str) -> ListUploaders:
        """Get the list of all uploaders."""
        document = self.uploadersCollection.find_one({"clusterName" : clusterName})
        if(document is None):
            print(f"No uploaders found with the clusterName {clusterName}...")
            listUploaders = None
        else:
            listUploaders = ListUploaders.loadFromListOfDictionary(clusterName, document["listUploaders"])
        return listUploaders
    
    def addUploader(self, clusterName : str, uploaderModel : UploaderModel) -> UploaderModel:
        """Register a new uploader."""
        document = self.uploadersCollection.find_one({"clusterName" : clusterName})
        if(document is not None):
            listUploaders = document["listUploaders"]
            listUploaders = ListUploaders.loadFromListOfDictionary(clusterName, listUploaders)
            if(len(listUploaders.listUploaders) > 0):
                uploaderModel.id = max(listUploaders.listUploaders, key=lambda x: x.id).id + 1
            else:
                uploaderModel.id = 0
            listUploaders.listUploaders.append(uploaderModel)
            self.uploadersCollection.update_one({"clusterName" : clusterName}, {"$set" : {"listUploaders":ListUploaders.toListOfDictionary(listUploaders)}}, upsert=True)
            return uploaderModel
        else:
            uploaderModel.id = 0
            listUploaders = ListUploaders([uploaderModel])
            self.uploadersCollection.insert_one({"clusterName":clusterName, "listUploaders" : ListUploaders.toListOfDictionary(listUploaders)})
            return uploaderModel
    
    def deleteUploaderByID(self, clusterName : str, id : int) -> UploaderModel|None:
        """Delete an uploader."""
        document = self.uploadersCollection.find_one({"clusterName" : clusterName})
        if(document is not None):
            listUploaders = document["listUploaders"]
            listUploaders = ListUploaders.loadFromListOfDictionary(clusterName, listUploaders)
            elementToRemove = next(filter(lambda uploader : uploader.id == id, listUploaders.listUploaders))
            listUploaders.listUploaders.remove(elementToRemove)
            self.uploadersCollection.update_one({"clusterName" : clusterName}, {"$set" : {"listUploaders":ListUploaders.toListOfDictionary(listUploaders)}}, upsert=True)
            return elementToRemove
        else:
            return None
            
                