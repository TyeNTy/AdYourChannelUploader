from datetime import datetime, timedelta
import os
import time
from streamlink import Streamlink, NoPluginError, PluginError
from models.event import Event
import pylivestream.api as pls
from threading import Timer
from twitchAPI import Twitch
from utils.twitchAPI import changeChannelInformation, getIDOfAChannel
from models.videoEncoding import Encoding, VideoEncoding, Resolution
import ffmpeg

class StreamLauncher:
    knownTwitchEncoding : list[Encoding] = Resolution.values()
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
        
        self.twitchIniFile = "twitch.ini"
        self.streamingServer = "rtmp://cdg10.contribute.live-video.net/app/"
        
        self.streamKey = self.twitchAPI.get_stream_key(getIDOfAChannel(self.twitchAPI, self.streamChannel))["data"][0]["stream_key"]

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
        while(datetime.utcnow() < self.event.endTime):
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

        maxQuality = None
        for quality in self.knownTwitchEncoding:
            if quality in streams:
                maxQuality = quality
                break

        # Look for specified stream
        if maxQuality not in streams:
            print("Unable to find '{0}' stream on URL '{1}'".format(maxQuality, url))
        print(f"Starting to stream with quality : {maxQuality}")
        self.initChannelInformation()
        
        stream = streams[maxQuality]
        while(datetime.utcnow() < self.event.endTime):
            try:
                fd = stream.open()
                break
            except BaseException as err:
                print(err)
                time.sleep(2)
        
        process = (
            ffmpeg.input("pipe:")
            .output(f"{self.streamingServer}{self.streamKey}", vcodec="copy", acodec="copy", f="flv", loglevel="quiet")
            .run_async(pipe_stdin=True)
        )
        
        while(datetime.utcnow() < self.event.endTime):
            process.stdin.write(fd.read(2**16))
        process.stdin.close()
        fd.close()
        
        self.resetChannelInformation()

        