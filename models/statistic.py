from datetime import datetime

class Statistic:
    def __init__(self, date : datetime, listOfViewersOurChannel : list[str], listOfViewersOtherChannel : list[str], listOfFollowers : list[dict], nbOfSubTier1 : int, nbOfSubTier2 : int, nbOfSubTier3 : int) -> None:
        self.date = date
        self.listOfViewersOurChannel = listOfViewersOurChannel
        self.listOfViewersOtherChannel = listOfViewersOtherChannel
        self.listOfFollowers = listOfFollowers
        self.nbOfSubTier1 = nbOfSubTier1
        self.nbOfSubTier2 = nbOfSubTier2
        self.nbOfSubTier3 = nbOfSubTier3
        