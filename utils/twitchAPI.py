import requests

def getIDOfAChannel(twitchAPI, channelName : str) -> int:
    return int(twitchAPI.get_users(logins = [channelName])['data'][0]['id'])

def getListOfChatters(channelName : str) -> dict:
    return requests.get(f"https://tmi.twitch.tv/group/user/{channelName}/chatters").json()

def createListOfChatters(channelName : str) -> list[str]:
        """Get the list of chatters of a streamer."""
        result = getListOfChatters(channelName)
        allChattersName = []
        for chatters in result['chatters'].values():
            allChattersName.extend(chatters)
        return allChattersName