import discord
from pymongo import MongoClient
from discord.ext import commands
import random
from random import randint
from discord.ext.commands import BucketType
import datetime
import time
from PIL import Image, ImageFont, ImageDraw, ImageOps
from io import BytesIO

cluster = MongoClient("mongodb+srv://user:pass@setuser.vs5xa.mongodb.net/database?retryWrites=true&w=majority")
database = cluster["Cluster"]["Section"]

class xpsystem(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.last_timeStamp = datetime.datetime.utcfromtimestamp(0)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        info = database.find_one({"id":message.author.id, "guild_id":message.guild.id})
        if not info:
            database.insert_one({"id":message.author.id, "level":1, "xp":0, "guild_id":message.guild.id})
        info = database.find_one({"id":message.author.id})

        time_difference = (datetime.datetime.utcnow() - self.last_timeStamp).total_seconds()
        if time_difference < 45:
            return
        self.last_timeStamp = datetime.datetime.utcnow()

        xp = random.randint(5, 10)
        database.update_one({"id":message.author.id}, {"$inc":{"xp":xp}})
        info = database.find_one({"id":message.author.id})
        if info["xp"] >= info["level"]*100:
            database.update_one({"id":message.author.id}, {"$set":{"level":info["level"]+1, "xp":0}})
            await message.channel.send(f"{message.author.mention} Leveled up to level {info['level']+1}!")

    @commands.command()
    async def rank(self, ctx, member : discord.Member = None):
        if not member:
            member = ctx.author
        if member.bot:
            await ctx.send('This command is limited to only super cool humans, not robots')
            return

        info = database.find_one({"id":member.id, "guild_id":ctx.guild.id})
        if not info:
            database.insert_one({"id":member.id, "level":1, "xp":0, "guild_id":ctx.guild.id})
        info = database.find_one({"id":member.id, "guild_id":ctx.guild.id})

        img = Image.open('cardimg.png')
        font = ImageFont.truetype("arial.ttf", 50)
        font2 = ImageFont.truetype("arial.ttf", 40)
        draw = ImageDraw.Draw(img)
        data = database.find({"guild_id":ctx.guild.id}).sort("level",-1)
        i = 1
        for x in data:
            try:
                temp = ctx.guild.get_member(x["id"])
                xp = x["xp"]
                level = x["level"]
                if x["id"] == member.id:
                    break
                i+=1
            except:
                pass
        async with ctx.typing():
            draw.rectangle((40, 35, 1156, 360), fill=(20, 20, 20))
            text = f"{member}"
            text3 = f"Level {info['level']}"
            text4 = f"Rank {i}"
            text2 = f"{info['xp']} / {int(info['level']*100)} XP"
            draw.text((360,280), text, (255,255,255), font=font2)
            draw.text((360,230), text2, (255,255,255), font=font2)
            draw.text((360,50), text3, (100, 150, 255), font=font)
            draw.text((360,100), text4, (255, 255, 255), font=font)
            asset = member.avatar_url_as(size = 128)
            data = BytesIO(await asset.read())
            pfp = Image.open(data)
            pfp = pfp.resize((250, 250))
            draw.rectangle((50, 330, 1150, 360), fill=(100,100,100))
            draw.rectangle((50, 330, 1100*(info["xp"]+50)/int(info["level"]*100), 360), fill=(255, 255, 255), width=10000*info["xp"]/int(info["level"]*100))
            img.paste(pfp, (60, 50))
            img.save("text.png")

        await ctx.send(file = discord.File("text.png"))

    @commands.command()
    async def leaderboard(self, ctx):
        member = ctx.author
        info = database.find_one({"id":member.id, "guild_id":ctx.guild.id})
        if not info:
            database.insert_one({"id":member.id, "level":1, "xp":0, "guild_id":ctx.guild.id})
        info = database.find_one({"id":member.id, "guild_id":ctx.guild.id})
        data = database.find({"guild_id":ctx.guild.id}).sort("level",-1)
        i = 1
        embed = discord.Embed(title=f'Top 5 levelled users in {ctx.guild.name}')
        for x in data:
            try:
                temp = ctx.guild.get_member(x["id"])
                xp = x["xp"]
                level = x["level"]
                embed.add_field(name=f'{temp.name}', value=f'Level {level} with {xp} xp', inline=False)
                i+=1
            except:
                pass
            if i == 6:
                break
        await ctx.send(embed=embed)

def setup(client):
    client.add_cog(xpsystem(client))
