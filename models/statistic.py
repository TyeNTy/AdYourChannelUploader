from datetime import datetime

from models.followEvent import FollowEvent

class Statistic:
    def __init__(self, date : datetime, listOfViewersOurChannel : list[str], listOfViewersOtherChannel : list[str], listNewFollowers : list[FollowEvent], nbOfSubTier1 : int, nbOfSubTier2 : int, nbOfSubTier3 : int) -> None:
        self.date = date
        self.listOfViewersOurChannel = listOfViewersOurChannel
        self.listOfViewersOtherChannel = listOfViewersOtherChannel
        self.listNewFollowers = listNewFollowers
        self.nbOfSubTier1 = nbOfSubTier1
        self.nbOfSubTier2 = nbOfSubTier2
        self.nbOfSubTier3 = nbOfSubTier3
        