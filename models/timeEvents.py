from datetime import datetime


class TimeEvents:
    def __init__(self, startDate : datetime, endDate : datetime, newviewers : int, newFollowers : int, newSubscribersTier1 : int, newSubscribersTier2 : int, newSubscribersTier3 : int):
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