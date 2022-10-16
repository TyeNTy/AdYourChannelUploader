class FollowRequestResult:
    def __init__(self, resultDictionary : dict[str, str]) -> None:
        self.followed_at = resultDictionary["followed_at"]
        self.from_login = resultDictionary["from_login"]
        self.from_name = resultDictionary["from_name"]
        self.to_id = resultDictionary["to_id"]
        self.to_name = resultDictionary["to_name"]
        self.followed_at = resultDictionary["followed_at"]