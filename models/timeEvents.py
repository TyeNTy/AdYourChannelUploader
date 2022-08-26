from datetime import datetime


class TimeEvents:
    def __init__(self, startDate : datetime, endDate : datetime, newviewers : list[str], newFollowers : list[str], newSubscribersTier1 : list[str], newSubscribersTier2 : list[str], newSubscribersTier3 : list[str]):
        self.startTime = startDate
        self.endTime = endDate
        self.newViewers = newviewers
        self.newFollowers = newFollowers
        self.newSubscribersTier1 = newSubscribersTier1
        self.newSubscribersTier2 = newSubscribersTier2
        self.newSubscribersTier3 = newSubscribersTier3
    
    def toDictionary(self) -> dict:
        return {
            "startTime": self.startTime,
            "endTime": self.endTime,
            "newViewers": self.newViewers,
            "newFollowers": self.newFollowers,
            "newSubscribersTier1": self.newSubscribersTier1,
            "newSubscribersTier2": self.newSubscribersTier2,
            "newSubscribersTier3": self.newSubscribersTier3
        }