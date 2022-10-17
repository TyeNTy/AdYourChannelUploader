import abc
from models.ListUploaders import ListUploaders
from models.uploaderStatus import UploaderStatus
from models.resultAnalyze import ResultAnalyze
from models.uploader import UploaderModel
from models.event import Event
from models.UserModel import UserModel

class IDataBaseService(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (
                hasattr(subclass, 'getEvent') and 
                callable(subclass.getEvent) and 
                hasattr(subclass, 'getNextEvent') and 
                callable(subclass.getNextEvent) and 
                hasattr(subclass, 'createEvent') and 
                callable(subclass.createEvent) and 
                hasattr(subclass, 'deleteEvent') and 
                callable(subclass.deleteEvent) and 
                hasattr(subclass, 'getCurrentUploaders') and 
                callable(subclass.getCurrentUploaders) and 
                hasattr(subclass, 'addUploader') and 
                callable(subclass.addUploader) and
                hasattr(subclass, 'addResultAnalyze') and 
                callable(subclass.addResultAnalyze) and
                hasattr(subclass, 'updateStatusUploader') and 
                callable(subclass.updateStatusUploader) and
                hasattr(subclass, "getUserByName") and
                callable(subclass.getUserByName))
    
    @abc.abstractmethod
    def getEvent(self, event : Event) -> Event:
        """Try to get the event."""
        raise NotImplementedError

    @abc.abstractmethod
    def getNextEvent(self, clusterName : str, uploaderID : int, language : str) -> Event|None:
        """Try to get the next event to take place in the uploaderID uploader inside of the cluster clusterName."""
        raise NotImplementedError

    @abc.abstractmethod
    def createEvent(self, event : Event) -> Event:
        """Create an event in the data set."""
        raise NotImplementedError

    @abc.abstractmethod
    def deleteEvent(self, Event):
        """Delete the event in the data set."""
        raise NotImplementedError

    @abc.abstractmethod
    def getCurrentUploaders(self, clusterName) -> ListUploaders:
        """Get the list of all uploaders inside of a uploaders cluster."""
        raise NotImplementedError
    
    @abc.abstractmethod
    def addUploader(self, clusterName : str, uploaderModel : UploaderModel) -> UploaderModel:
        """Add a new uploader."""
        raise NotImplementedError
    
    @abc.abstractmethod
    def deleteUploaderByID(self, clusterName : str, id : int) -> UploaderModel|None:
        """Delete an uploader."""
        raise NotImplementedError
    
    @abc.abstractmethod
    def addResultAnalyze(self, resultAnalyze : ResultAnalyze) -> ResultAnalyze|None:
        """Add a resultAnalyze."""
        raise NotImplementedError
    
    @abc.abstractmethod
    def updateStatusUploader(self, clusterName : str, uploaderID : int, status : UploaderStatus) -> UploaderModel|None:
        """Update the status of an uploader."""
        raise NotImplementedError
    
    @abc.abstractmethod
    def getUserByName(self, twitchUserName : str) -> UserModel|None:
        """Get a User by his Twitch user name."""
        raise NotImplementedError