from twitchio.ext import commands, routines
from multiprocessing import Queue
from models.event import Event
from utils.translationHelpers import loadTranslations
from twitchAPI import Twitch



class ChatBot(commands.Bot):

    def __init__(self, channelName : str, twitchAPI : Twitch, newHostQueue : Queue, language : str):
        super().__init__(token=twitchAPI.get_user_auth_token(), prefix='!', initial_channels=[channelName])
        self.twitchAPI = twitchAPI
        self.newHostQueue = newHostQueue
        self.channelName = channelName
        self.language = language
        self.translations = loadTranslations(self.language, pathFile="chatbot")
        
        self.currentEvent : Event = None
        self.change_channel.start()
    
    @routines.routine(seconds=10.0)
    async def change_channel(self):
        while(not self.newHostQueue.empty()):
            self.currentEvent : Event = self.newHostQueue.get()
            print(f"Chat bot : getting new channel {self.currentEvent.twitchUserName}")
    
    def run(self):
        return super().run()
    
    async def event_ready(self):
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')
    
    async def event_message(self, message):
        if message.echo:
            return
        await self.handle_commands(message)

    @commands.command(name="lisquidstream")
    async def lisquidstream(self, ctx : commands.core.Context):
        await self.get_channel(self.channelName).send(self.translations['lisquidstream'].format())
        
    @commands.command(name="help")
    async def help(self, ctx : commands.core.Context):
        await self.get_channel(self.channelName).send(self.translations['help'].format())
        
    @commands.command(name="channel")
    async def channel(self, ctx : commands.core.Context):
        if(self.currentEvent is None):
            await self.get_channel(self.channelName).send(self.translations['channelNoEventYet'].format())
        else:
            await self.get_channel(self.channelName).send(self.translations['channel'].format(self.currentEvent.twitchUserName, self.currentEvent.twitchUserName))
        