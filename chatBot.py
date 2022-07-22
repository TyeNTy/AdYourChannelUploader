from twitchio.ext import commands, routines
from multiprocessing import Queue
from models.event import Event

class ChatBot(commands.Bot):

    def __init__(self, channelName : str, oauthToken : str, newHostQueue : Queue):
        super().__init__(token=oauthToken, prefix='!', initial_channels=[channelName])
        self.newHostQueue = newHostQueue
        self.channelName = channelName
        
        # self.change_host_task = None
    
    # @routines.routine(seconds=5.0)
    # async def change_host(self):
    #     newHostName = None
    #     print("getting new host")
    #     while(not self.newHostQueue.empty()):
    #         nextEvent : Event = self.newHostQueue.get()
    #         newHostName = nextEvent.twitchUserName
    #     if(newHostName is not None):
    #         await self.get_channel(self.channelName).send(f"/host {newHostName}")
    #         print("Changed host to {}".format(newHostName))
    
    def run(self):
        # self.change_host_task = self.change_host.start()
        return super().run()
    
    async def event_ready(self):
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')

    @commands.command(name="test")
    async def test(self, message : commands.core.Context):
        await self.get_channel(self.channelName).send(f'{message.author.name} : {message.message.content}')
        