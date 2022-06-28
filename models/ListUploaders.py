from __future__ import annotations
from models.uploader import UploaderModel

class ListUploaders:
    def __init__(self, listUploaders : list[UploaderModel]) -> None:
        self.listUploaders = listUploaders
    
    def loadFromListOfDictionary(clusterName : str, listOfDictionary : list[dict]) -> ListUploaders:
        if(listOfDictionary is None):
            return None
        listUploaders = []
        for dictionary in listOfDictionary:
            uploader = UploaderModel.loadFromDict(dictionary)
            listUploaders.append(uploader)
        return ListUploaders(listUploaders)

    def toListOfDictionary(listUploaders : ListUploaders) -> list[dict]:
        listDictionary = []
        for uploadModel in listUploaders.listUploaders:
            dictionary = {}
            dictionary["id"] = uploadModel.id
            dictionary["language"] = uploadModel.language
            dictionary["lastHealthCheck"] = uploadModel.lastHealthCheck
            listDictionary.append(dictionary)
        return listDictionary
        

    def __str__(self) -> str:
        txt = ""
        for uploader in self.listUploaders:
            txt += str(uploader) + "\n"
        return txt