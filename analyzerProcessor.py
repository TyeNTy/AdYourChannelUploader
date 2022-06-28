from datetime import datetime
from models.statistic import Statistic

class AnalyzerProcessor:
    def __init__(self, data : list[Statistic]) -> None:
        self.data = data
    
    def __testIfViewerInList(self, viewer : str, listNewViewers : list[tuple[datetime, str]]) -> bool:
        for _, otherViewer in listNewViewers:
            if viewer == otherViewer:
                return True
        return False
    
    def launchAnalyze(self):
        print("Starting to analyze the data...")
        listOlderChatters = []
        listNewViewers = []
        for statistic in self.data:
            listOlderChatters.extend(statistic.listOfViewersOurChannel)
            for viewer in statistic.listOfViewersOtherChannel:
                if viewer in listOlderChatters and not self.__testIfViewerInList(viewer, listNewViewers):
                    listNewViewers.append((statistic.date, viewer))
        print("Analyzing the data... Done")
        return listNewViewers