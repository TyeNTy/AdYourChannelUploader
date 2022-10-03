import multiprocessing
from twitchio.ext import commands, routines
from multiprocessing import Queue
from models.event import Event



class ChatBot(commands.Bot):

    def __init__(self, channelName : str, oauthToken : str, newHostQueue : Queue):
        super().__init__(token=oauthToken, prefix='!', initial_channels=[channelName])
        self.newHostQueue = newHostQueue
        self.channelName = channelName
        
        self.currentEvent : Event = None
        self.change_channel.start()
    
    @routines.routine(seconds=10.0)
    async def change_channel(self):
        while(not self.newHostQueue.empty()):
            self.currentEvent : Event = self.newHostQueue.get()
            print(f"Chat bot : getting new channel {self.currentEvent.twitchUserName}")
    
    def run(self):
        # self.change_host_task = self.change_host.start()
        return super().run()
    
    async def event_ready(self):
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')

    @commands.command(name="adyourchannel")
    async def adyourchannel(self, message : commands.core.Context):
        await self.get_channel(self.channelName).send(f'AdYourChannel is a project that aims to ad new streamers ! Please visit the website for more information : https://adyourchannel.com .')
    
    @commands.command(name="channel")
    async def channel(self, message : commands.core.Context):
        twitchName = self.currentEvent.twitchUserName if self.currentEvent is not None else "no channel streamed yet"
        await self.get_channel(self.channelName).send(f'You are currently watching : {twitchName}. If you want, please go visit the channel : https://www.twitch.tv/{twitchName} .')
        