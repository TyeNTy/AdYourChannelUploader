from datetime import datetime
from models.followEvent import FollowEvent
from models.subscribeEvent import SubscribeEvent

class Statistic:
    def __init__(self, date : datetime, listOfViewersOurChannel : list[str], listOfViewersOtherChannel : list[str], listNewFollowers : list[FollowEvent], listNewSubscribers : list[SubscribeEvent]) -> None:
        self.date = date
        self.listOfViewersOurChannel = listOfViewersOurChannel
        self.listOfViewersOtherChannel = listOfViewersOtherChannel
        self.listNewFollowers = listNewFollowers
        self.listNewSubscribers = listNewSubscribers
        