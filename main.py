import discord
import os
import ffmpeg
import youtube_dl
import asyncio
import random
import functools
import itertools
import math
import opus
import pypl
from discord.ext import commands
from keep_alive import keep_alive
from discord.voice_client import VoiceClient
from discord.ext import commands, tasks
from async_timeout import timeout
from discord.ext import commands,tasks

client = commands.Bot(command_prefix="!")


players = {}

filtered_words = ["Bitch"]
@client.event
async def on_ready():
  print("Bot is Ready")


@client.event
async def on_message(msg):
  for word in filtered_words:
    if word in msg.content:
      await msg.delete()

    await client.process_commands(msg)

@client.event
async def on_command_error(ctx,error):
  if isinstance(error,commands.MissingPermissions):
    await ctx.send("You don't have the correct Permissions to complete that action!")
    await ctx.message.delete()

  elif isinstance(error,commands.MissingRequiredArgument):
    await ctx.send("Please enter all of the required arguments for that command!")
    await ctx.message.delete()


@client.command()
async def hello(ctx):
    await ctx.send("Hello!")

@client.command
@commands.has_permissions(kick_members=True)
async def user(ctx, member : discord.member):
  embed = discord.Embed(title = member.name, description = member.mention , color = discord.colour.green())
  embed.add_field(name = "ID", value = member.id , inline = True)
  await ctx.send(embed=embed)


@client.command()
async def website(ctx):
  await ctx.send("https://moneybrozbot.xyz")


@client.command()
@commands.has_permissions(manage_messages = True)
async def clear(ctx,amount=100):
  await ctx.channel.purge(limit = amount)

@client.command()
@commands.has_permissions(kick_members = True)
async def kick(ctx,member : discord.Member,*,reason= " No Reason Provided."):
  await ctx.send("You have been kicked from the server, Because" +reason)
  await member.kick(reason=reason)

@client.command()
@commands.has_permissions(ban_members = True)
async def ban(ctx,member : discord.Member,*,reason= " No Reason Provided."):
  await ctx.send(member.name + " has been banned from the server, Because: " + reason)
  await member.ban(reason=reason)

  @client.command()
  @commands.has_permissions(ban_members = True)
  async def unban(ctx,*,member):

    banned_users = await ctx.guild.bans()
    member_name, member_disc = member.split('#')

    for banned_entry in banned_users:
      user = banned_entry.user

      if(user.name, user.discriminator)==(member_name,member_disc):

        await ctx.guild.unban(user)
        await ctx.send(member_name +" has been unbanned!")
        return

    await ctx.send(member+" was not found")

@client.command()
@commands.has_permissions(kick_members = True)
async def mute(ctx,member : discord.Member):
  muted_role = ctx.guild.get_role(822030323972964372)

  await member.add_roles(muted_role)

  await ctx.send(member.mention + " has been muted!")

@client.command()
async def invite(ctx):
    await ctx.send("https://moneybrozbot.xyz/invite")

@client.command()
async def github(ctx):
    await ctx.send("https://github.com/MoneyBrozYT/moneybrozbotdiscord")



@client.command(name='ping', help='This command returns the latency')
async def ping(ctx):
    await ctx.send(f'**Pong!** Latency: {round(client.latency * 1000)}ms')


youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename

@client.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        return await ctx.send(f"{ctx.author.name} is not connected to a voice channel")
    
    else:
        try:
            channel = ctx.message.author.voice.channel
            await channel.connect()
        except Exception as e:
            await ctx.send(e)

@client.command(name='leave', help='To make the bot leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")


@client.command(name='pause', help='This command pauses the song')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.pause()
    else:
        await ctx.send("The bot is not playing anything at the moment.")


@client.command(name='resume', help='Resumes the song')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await voice_client.resume()
    else:
        await ctx.send("The bot was not playing anything before this. Use play_song command")

@client.command(name='stop', help='Stops the song')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        await ctx.send("The bot is not playing anything at the moment.")

@client.command(name='play', help='To play song')
async def play(ctx,url):
    try :
        server = ctx.message.guild
        voice_channel = server.voice_client
        async with ctx.typing():
            filename = await YTDLSource.from_url(url, loop=client.loop)
            voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=filename))
        await ctx.send('**Now playing:** {}'.format(filename))
    except:
        await ctx.send("The bot is not connected to a voice channel.")

@client.command(help = "Prints details of the Server")
async def server(ctx):
    owner=str(ctx.guild.owner)
    region = str(ctx.guild.region)
    guild_id = str(ctx.guild.id)
    memberCount = str(ctx.guild.member_count)
    icon = str(ctx.guild.icon_url)
    desc=ctx.guild.description
    
    embed = discord.Embed(
        title=ctx.guild.name + " Server Information",
        description=desc,
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=icon)
    embed.add_field(name="Owner", value=owner, inline=True)
    embed.add_field(name="Server ID", value=guild_id, inline=True)
    embed.add_field(name="Region", value=region, inline=True)
    embed.add_field(name="Member Count", value=memberCount, inline=True)
    await ctx.send(embed=embed)
    members=[]
    async for member in ctx.guild.fetch_members(limit=150) :
        await ctx.send('Name : {}\t Status : {}\n Joined at {}'.format(member.display_name,str(member.status),str(member.joined_at)))

#end
keep_alive()
client.run(os.getenv('TOKEN'))
