import discord
from discord.ext import commands, tasks
import os
from itertools import cycle
import time
import datetime
from datetime import datetime
import asyncio

token = ""

client = commands.Bot(command_prefix="", intents=discord.Intents.all())
client.remove_command('help')

status = cycle(['Ping me for my prefix!', '{0} servers | {1} users'])

@tasks.loop(seconds=15)
async def change_status():
    await client.wait_until_ready()
    content = next(status)
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=content.format(len(client.guilds), len(client.users))))

@client.event
async def on_ready():
    print('Im ready!')
    change_status.start()

@client.command()
@commands.is_owner()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')
    await ctx.send(f'Loaded {extension}')

@client.command()
@commands.is_owner()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    await ctx.send(f'Unloaded {extension}')

@client.command()
@commands.is_owner()
async def reload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')
    await ctx.send(f'Reloaded {extension}')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

@client.command()
@commands.is_owner()
async def reloadall(ctx):
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                client.unload_extension(f'cogs.{filename[:-3]}')
            except:
                pass

    embed = discord.Embed(title='Reloaded all!')

    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                client.load_extension(f'cogs.{filename[:-3]}')
                embed.add_field(name=filename, value=':repeat:', inline=False)
            except:
                client.load_extension(f'cogs.{filename[:-3]}')
                embed.add_field(name=filename, value=':warning:', inline=False)
                pass

    await ctx.send(embed=embed)

client.run(token)
