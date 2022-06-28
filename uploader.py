from datetime import datetime
import sys
import time
from abstraction.IDataBaseService import IDataBaseService
from analyzer import Analyzer
from analyzerProcessor import AnalyzerProcessor
from models.event import Event
from models.uploader import UploaderModel
from streamLauncher import StreamLauncher
from multiprocessing.pool import ThreadPool

class Uploader:
    def __init__(self, clusterName : str, language : str, dataBaseService : IDataBaseService) -> None:
        self.dataBaseService = dataBaseService
        self.language = language
        self.clusterName = clusterName
        self.id = 0
        
        newUploaderModel = dataBaseService.addUploader(clusterName, UploaderModel(clusterName, language, datetime.now()))
        self.id = newUploaderModel.id
    
    def runStreaming(self, event : Event) -> None:
        streamLauncher = StreamLauncher(event)
        streamAnalyzer = Analyzer(event)
        pool = ThreadPool(processes=1)
        asyncResult = pool.apply_async(streamAnalyzer.launchAnalyzer, ())
        streamLauncher.runStreaming()
        allStatistics = asyncResult.get()
        analyszerProcessor = AnalyzerProcessor(allStatistics)
        result = analyszerProcessor.launchAnalyze()
        print(result)
        
    
    def run(self) -> None:
        try:
            while(True):
                nextEvent = self.dataBaseService.getNextEvent(self.clusterName, self.id, self.language)
                if(nextEvent is not None):
                    print(nextEvent)
                    self.runStreaming(nextEvent)
                else:
                    print(f"{datetime.now()} : No event found...")
                    time.sleep(10)
        except KeyboardInterrupt:
            self.dataBaseService.deleteUploaderByID(self.clusterName, self.id)
            sys.exit(0)