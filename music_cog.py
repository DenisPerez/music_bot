import discord
from discord.ext import commands

from youtube_dl import YoutubeDL

class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
        #all the music related stuff
        self.is_playing = False

        # 2d array containing [song, channel]
        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
        self.YDL_OPTIONS_PLAYLISTS = {'format': 'bestaudio'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        self.vc = ""

    #searching the item on youtube
    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:  
                info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0] 

            except Exception: 
                return False

        return {'source': info['formats'][0]['url'], 'title': info['title']}
    
    def SearchPlaylist(self, playlist):

        returnList = []
        with YoutubeDL(self.YDL_OPTIONS_PLAYLISTS) as ydl:
            try:
                infos = ydl.extract_info(playlist, download=False)['entries']
                for info in infos:
                    returnList.append([{'source': info['formats'][0]['url'], 'title': info['title']}])
            except:
                return False
        
        return returnList
    
    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            #get the first url
            m_url = self.music_queue[0][0]['source']

            #remove the first element as you are currently playing it
            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False

    # infinite loop checking 
    async def play_music(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]['source']
            
            #try to connect to voice channel if you are not already connected

            if self.vc == "" or not self.vc.is_connected() or self.vc == None:
                self.vc = await self.music_queue[0][1].connect()
            else:
                await self.vc.move_to(self.music_queue[0][1])
            
            print(self.music_queue)
            #remove the first element as you are currently playing it
            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False

    @commands.command(aliases = ['play', 'p'], help = "Plays a selected song from youtube")
    async def Play(self, ctx, *args):
        query = " ".join(args)
        
        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            #you need to be connected so that the bot knows where to go
            await ctx.send("Connect to a voice channel!")
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                songs = self.SearchPlaylist(query)
                
                for song in songs:
                    self.music_queue.append([song[0], voice_channel])

                await ctx.send(f'%i songs were added to the queue'% len(songs))

                if (self.is_playing == False):
                    await self.play_music()

            else:
                await ctx.send("Song added to the queue")
                self.music_queue.append([song, voice_channel])
                
                
                if (self.is_playing == False):
                    await self.play_music()

    @commands.command(aliases = ['queue', 'q'], help="Displays the current songs in queue")
    async def Queue(self, ctx):
        retval = ""
        take = 9

        if(self.music_queue.isEmpty()):
            await ctx.send("No music in queue")

        if (len(self.music_queue) < take):
            for i in range(0, len(self.music_queue)):
                retval += f'[%i]'% i+1 + self.music_queue[i][0]['title'] + "\n"
        else:
            for i in range(take):
                retval += f'[%i]'% i+1 + self.music_queue[i][0]['title'] + "\n"
            
            retval += f'\n This are the following 10/%i songs in the queue'

        
        await ctx.send(retval)
        
    @commands.command(aliases = ['skip', 's'], help="Skips the current song being played")
    async def Skip(self, ctx):
        if self.vc != "" and self.vc:
            self.vc.stop()
            #try to play next in the queue if it exists
            await self.play_music()

    @commands.command(aliases=['leave','l'], help="Bot leaves the channel")
    async def Leave(self, ctx):

        self.music_queue = []

        voice_channel = ctx.author.voice.channel

        if(voice_channel is None):
            return await ctx.say("I am not connected to any voice channel")
        
        return await ctx.voice_client.disconnect()
    
    @commands.command(aliases= ['move', 'm'], help= "Move position x to position y in queue")
    async def Move(self, ctx, x, y):
        
        pos1 = int(x) - 1
        pos2 = int(y) - 1

        self.music_queue[pos1], self.music_queue[pos2] = self.music_queue[pos2], self.music_queue[pos1]

    @commands.command(aliases=['remove', 'r'], help='Remove a song from the queue')
    async def Remove(self, ctx, x):

        positionToRemove = int(x)

        del self.music_queue[positionToRemove]

    @commands.command(aliases = ['pause'], help = 'Pause the music')
    async def Pause(self):
        
        self.vc.pause()

    @commands.command(aliases = ['resume','r'], help = 'Resume the music')
    async def Resume(self):
        
        self.vc.resume()

    @commands.command(aliases= ['stop'], help= 'Stop the music')
    async def Stop(self):

        self.vc.stop()
    
    

