from datetime import datetime, timedelta
import os
import time
from streamlink import Streamlink, NoPluginError, PluginError
from models.event import Event
import pylivestream.api as pls
from threading import Timer
from twitchAPI import Twitch
from utils.twitchAPI import changeChannelInformation

class StreamLauncher:
    knownTwitchEncoding = ["1080p60", "1080p30", "720p60", "720p30", "480p60", "480p30", "high", "best"]
    pathToTmpVideoPipe = "tmp"
    tmpVideoPipeName = "tmpVideoPipe"
    
    def __init__(self, event : Event, twitchAPI : Twitch, appID : str, appSecret : str, getStreamID : str, streamChannel : str):
        self.event = event
        self.fullPathVideoPipe = os.path.join(self.pathToTmpVideoPipe, self.tmpVideoPipeName)
        self.appID = appID
        self.appSecret = appSecret
        self.getStreamID = getStreamID
        self.twitchAPI = twitchAPI
        self.streamChannel = streamChannel
    
    def launchListeningPipe(self):
        while(datetime.utcnow() + timedelta(seconds=10) < self.event.endTime):
            try:
                pls.stream_file("pylivestream.ini", websites=["twitch"], video_file=self.fullPathVideoPipe, loop=False, assume_yes=True)
            except KeyError:
                print("End of stream :")
                print(self.event)

    def resetChannelInformation(self):
        changeChannelInformation(self.twitchAPI, self.streamChannel, f"!{self.streamChannel}", self.event.language)

    def initChannelInformation(self):
        changeChannelInformation(self.twitchAPI, self.streamChannel, self.event.streamTitle, self.event.language)

    def runStreaming(self):
        # Collect arguments
        channelName = self.event.twitchUserName
        url = f"https://twitch.tv/{channelName}"

        # Create the StreamLink session
        streamLink = Streamlink()

        streamLink.set_option("http-headers", f"Client-Id={self.getStreamID}")
        
        # Attempt to fetch streams
        for _ in range(10):
            try:
                streams = streamLink.streams(url)
                break
            except NoPluginError:
                print("Livestreamer is unable to handle the URL '{0}'".format(url))
            except PluginError as err:
                print("Plugin error: {0}".format(err))
            time.sleep(2)
                

        if not streams:
            print("No streams found on URL '{0}'".format(url))

        maxQuality = ""
        for quality in self.knownTwitchEncoding:
            if quality in streams:
                maxQuality = quality
                break

        # Look for specified stream
        if maxQuality not in streams:
            print("Unable to find '{0}' stream on URL '{1}'".format(maxQuality, url))
        print(streams)
        print(f"Starting to write to pipe with quality : {maxQuality}")

        if(not os.path.exists(self.pathToTmpVideoPipe)):
            os.makedirs(self.pathToTmpVideoPipe)
        video_pipe = open(self.fullPathVideoPipe, 'w+b', 0)
        
        self.initChannelInformation()
        
        timer = Timer(1, self.launchListeningPipe)
        
        stream = streams[maxQuality]
        for _ in range(10):
            try:
                fd = stream.open()
            except BaseException as err:
                print(err)
        timer.start()
        
        while(datetime.utcnow() < self.event.endTime):
            data = fd.read(1024)
            video_pipe.write(data)
        video_pipe.close()
        fd.close()
        
        self.resetChannelInformation()
        