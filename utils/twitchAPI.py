import hmac
import hashlib
import json
import random
import string
from twitchAPI import Twitch
import requests

from models.event import Event

def getIDOfAChannel(twitchAPI : Twitch, channelName : str) -> int:
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

def checkFollow(twitchAPI : Twitch, followerID : str, otherChannelID : str):
    header = {
        "content-type": "application/json",
        "Client-Id": twitchAPI.app_id,
        "Authorization": f"Bearer {twitchAPI.get_app_token()}"
    }
    response = requests.get(f'https://api.twitch.tv/helix/users/follows?to_id={followerID}&from_id={otherChannelID}', headers=header).json()
    return response.status_code == 202

def changeChannelInformation(twitchAPI : Twitch, channelName : str, newTitle : str, broadcasterLanguage : str) -> None:
    """Change the information of a stream. Requires user authentication."""
    twitchAPI.modify_channel_information(getIDOfAChannel(twitchAPI, channelName), title = newTitle, broadcaster_language=broadcasterLanguage)

def generateRandomString(length : int) -> requests.Response:
    """Generate a random string of a given length."""
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))
    
def createNewSubscription(secret : str, twitchAPI : Twitch, clientID : str, channelName : str, typeOfSubscription : str, callBackURL, oauthToken : str) -> requests.Response:
    """Create a new subscription for a channel."""
    dictData = {
        "type":typeOfSubscription,
        "version":"1",
        "condition":{
            "broadcaster_user_id":str(getIDOfAChannel(twitchAPI, channelName))
        },
        "transport":{
            "method":"webhook",
            "callback":callBackURL,
            "secret":secret
        }
    }
    header = {
        "content-type": "application/json",
        "Client-Id": clientID,
        "Authorization": f"Bearer {oauthToken}"
    }
    body = json.dumps(dictData, indent=None)
    return requests.post(f'https://api.twitch.tv/helix/eventsub/subscriptions', headers=header, data=body)

def deleteSubscriptionByID(twitchAPI : Twitch, subscriptionID : str) -> None:
    """Delete a subscription by its ID."""
    twitchAPI.delete_eventsub_subscription(subscriptionID)

def listAllEventSub(twitchAPI : Twitch) -> list[dict]:
    """List all event sub."""
    result = twitchAPI.get_eventsub_subscriptions()['data']
    print(result)
    return result

def validateSignature(webhook_secret : str, headers : dict[str, bytes], body : str) -> bool:
    message_id = str(headers['twitch-eventsub-message-id'])
    message_timestamp = str(headers['twitch-eventsub-message-timestamp'])
    message_signature = str(headers['twitch-eventsub-message-signature'])

    hmac_message = message_id + message_timestamp + body

    key = bytes(webhook_secret, 'utf-8')
    data = bytes(hmac_message, 'utf-8')

    signature = hmac.new(key, data, hashlib.sha256)

    expected_signature_header = 'sha256=' + signature.hexdigest()

    if message_signature != expected_signature_header:
        return False

    return True