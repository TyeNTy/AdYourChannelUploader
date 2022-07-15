from datetime import datetime
import iso8601

class FollowEvent:
    def __init__(self, eventDict : dict[str, str]) -> None:
        self.userID = eventDict["user_id"]
        self.userLogin = eventDict["user_login"]
        self.userName = eventDict["user_name"]
        self.broadcasterUserID = eventDict["broadcaster_user_id"]
        self.broadcasterUserLogin = eventDict["broadcaster_user_login"]
        self.broadcasterUserName = eventDict["broadcaster_user_name"]
        self.followedAT = iso8601.parse_date(eventDict["followed_at"])
    
    def toDictionary(self) -> dict:
        return {
            "user_id": self.userID,
            "user_login": self.userLogin,
            "user_name": self.userName,
            "broadcaster_user_id": self.broadcasterUserID,
            "broadcaster_user_login": self.broadcasterUserLogin,
            "broadcaster_user_name": self.broadcasterUserName,
            "followed_at": self.followedAT
        }