from datetime import datetime
import os
import time
import sys
from livestreamer import Livestreamer, StreamError, PluginError, NoPluginError
from twitchstream.outputvideo import TwitchBufferedOutputStream
from models.event import Event
import pylivestream.api as pls
from threading import Timer

class StreamLauncher:
    knownTwitchEncoding = ["1080p60", "1080p30", "720p60", "720p30", "480p60", "480p30", "high", "best"]
    pathToTmpVideoPipe = "tmp"
    tmpVideoPipeName = "tmpVideoPipe"
    
    def __init__(self, event : Event):
        self.event = event
        self.fullPathVideoPipe = os.path.join(self.pathToTmpVideoPipe, self.tmpVideoPipeName)
    
    def launchListeningPipe(self):
        try:
            pls.stream_file("pylivestream.ini", websites=["twitch"], video_file=self.fullPathVideoPipe, loop=False, assume_yes=True)
        except KeyError:
            print("End of stream :")
            print(self.event)

    def runStreaming(self):
        # Collect arguments
        channelName = self.event.twitchUserName
        url = f"twitch.tv/{channelName}"

        # Create the Livestreamer session
        livestreamer = Livestreamer()

        # Enable logging
        livestreamer.set_loglevel("info")
        livestreamer.set_logoutput(sys.stdout)
        
        livestreamer.set_option("http-headers", 'Client-ID=jzkbprff40iqj646a697cyrvl0zt2m6')
        
        # Attempt to fetch streams
        for _ in range(10):
            try:
                streams = livestreamer.streams(url)
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
        
        timer = Timer(1, self.launchListeningPipe)
        
        stream = streams[maxQuality]
        fd = stream.open()
        timer.start()
        
        while(datetime.now() < self.event.endTime):
            data = fd.read(1024)
            video_pipe.write(data)
        video_pipe.close()
        fd.close()