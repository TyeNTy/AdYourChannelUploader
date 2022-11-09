from datetime import datetime
import time
from streamlink import Streamlink, NoPluginError, PluginError
from models.event import Event
from twitchAPI import Twitch
from translation import Translation
from utils.twitchAPI import changeChannelInformation, getIDOfAChannel
from models.videoEncoding import Encoding, Resolution
import ffmpeg
from utils.logger import getChildLogger

class StreamLauncher:
    knownTwitchEncoding : list[Encoding] = Resolution.values()
    nameClass = "streamLauncher"
    
    def __init__(self, event : Event, twitchAPI : Twitch, appID : str, appSecret : str, getStreamID : str, streamChannel : str):
        self.logger = getChildLogger(self.nameClass)
        self.exitInstruction = False

        self.event = event
        self.appID = appID
        self.appSecret = appSecret
        self.getStreamID = getStreamID
        self.twitchAPI = twitchAPI
        self.streamChannel = streamChannel
        self.translations = Translation(self.event.language, self.nameClass)
        
        self.streamingServer = "rtmp://cdg10.contribute.live-video.net/app/"
        
        self.streamKey = self.twitchAPI.get_stream_key(getIDOfAChannel(self.twitchAPI, self.streamChannel))["data"][0]["stream_key"]

    def resetChannelInformation(self):
        changeChannelInformation(self.twitchAPI, self.streamChannel, self.translations['baseTitle'] , self.event.language)

    def initChannelInformation(self):
        changeChannelInformation(self.twitchAPI, self.streamChannel, self.event.streamTitle, self.event.language)
    
    def cutStream(self):
        self.exitInstruction = True

    def runStreaming(self):
        # Collect arguments
        channelName = self.event.twitchUserName
        url = f"https://twitch.tv/{channelName}"

        # Create the StreamLink session
        streamLink = Streamlink()

        streamLink.set_option("http-headers", f"Client-Id={self.getStreamID}")
        
        # Attempt to fetch streams
        foundStream = False
        maxQuality = None
        while(datetime.utcnow() < self.event.endTime and not foundStream and not self.exitInstruction):
            try:
                streams = streamLink.streams(url)
            except NoPluginError:
                self.logger.info("Livestreamer is unable to handle the URL '{0}'".format(url))
            except PluginError as err:
                self.logger.info("Plugin error: {0}".format(err))
                

            if not streams:
                self.logger.info("No streams found on URL '{0}'".format(url))
                time.sleep(20)
            else:
                for quality in self.knownTwitchEncoding:
                    if quality in streams:
                        maxQuality = quality
                        break

                if maxQuality is not None:
                    foundStream = True
                else:
                    time.sleep(20)
                
        self.logger.info(f"Starting to stream with quality : {maxQuality}")
        self.initChannelInformation()
        
        if(maxQuality is not None):
            stream = streams[maxQuality]
            fd = None
            
            while(datetime.utcnow() < self.event.endTime and not self.exitInstruction):
                try:
                    fd = stream.open()
                    break
                except BaseException as err:
                    self.logger.error(err)
                    time.sleep(10)
            self.logger.info("Stream opened.")
            
            process = (
                ffmpeg.input("pipe:")
                .output(f"{self.streamingServer}{self.streamKey}", vcodec="copy", acodec="copy", f="flv", loglevel="quiet")
                .run_async(pipe_stdin=True)
            )
            
            if(fd is not None):
                while(datetime.utcnow() < self.event.endTime and not self.exitInstruction):
                    process.stdin.write(fd.read(2**8))
                process.stdin.close()
                fd.close()
        
        self.resetChannelInformation()

        