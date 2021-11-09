import os
import random

import aiosqlite
import discord
import pyyoutube
from discord.ext import commands
from youtubesearchpython import ResultMode,ChannelSearch,ChannelsSearch
from pycord_components import (
    Button,
    ButtonStyle, Interaction, Select, SelectOption
)
from aioify import aioify
from dotenv import load_dotenv
load_dotenv(verbose=True)
class ytnt(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.index = 0

    @aioify
    def channelssearch(self,name,limit):
        channelsSearch = ChannelsSearch(name, limit=limit, region="KO")
        res: dict = channelsSearch.result()
        return res

    #API_KEY = "AIzaSyDjX47bnrGlxwGcLEf9PHxSQv_210GcAgs"  # replace this with your api key.

    @aioify
    def get_videos(self,channel_id):
        api = pyyoutube.Api(api_key=os.getenv("YT_TOKEN"))
        channel_res = api.get_channel_info(channel_id=channel_id)

        playlist_id = channel_res.items[0].contentDetails.relatedPlaylists.uploads

        playlist_item_res = api.get_playlist_items(
            playlist_id=playlist_id, count=10, limit=6
        )

        videos = []
        for item in playlist_item_res.items:
            video_id = item.contentDetails.videoId
            video_res = api.get_video_by_id(video_id=video_id)
            videos.extend(video_res.items)
        return videos

    @aioify
    def saveytnotify(self,channel_id):
        videos = self.get_videos(channel_id)

    @commands.group(name="유튜브",invoke_without_command=True)
    async def youtube(self,ctx,*,name):
        res = self.channelssearch(name,5)
        #li = [i for i in res["result"] if i["type"] == "channel"]
        li = []
        for i in res["result"]:
            if i["type"] == "channel":
                print(i['descriptionSnippet'])
                values = f"""
채널명: {i['title']}
구독자수: {i['subscribers']}
영상수: {i['videoCount']}  
소개글: {i['descriptionSnippet'][0]['text'] if i['descriptionSnippet'] != None else "정보없음"}
채널: [바로가기]({i['link']})
"""
                li.append(values)
        async def btn_callback(interaction:Interaction):
            if interaction.user.id != ctx.author.id:
                return await interaction.respond(content="요청자만 조작할 수 있어요!")
            custom_id = interaction.custom_id
            if custom_id == "⏮":
                if not self.index == 0:
                    self.index = 0
                    em = discord.Embed(
                        description=li[self.index],
                        colour=discord.Colour.random()
                    )
                    await interaction.edit_origin(embed=em,components=[
                            [self.bot.components_manager.add_callback(Button(emoji="⏮",style=1,custom_id="⏮"),btn_callback),
                             self.bot.components_manager.add_callback(Button(emoji="◀", style=1, custom_id="◀"),btn_callback),
                             Button(label=f"{self.index+1} / 5", disabled=True),
                             self.bot.components_manager.add_callback(Button(emoji="▶", style=1, custom_id="▶"),btn_callback),
                             self.bot.components_manager.add_callback(Button(emoji="⏭", style=1, custom_id="⏭"),btn_callback),
                             ],
                        self.bot.components_manager.add_callback(Button(emoji="❎", style=4, custom_id="❎"),
                                                                 btn_callback)
                        ])
            if custom_id == "◀":
                if not self.index == 0:
                    self.index -= 1
                    em = discord.Embed(
                        description=li[self.index],
                        colour=discord.Colour.random()
                    )
                    await interaction.edit_origin(embed=em,components=[
                            [self.bot.components_manager.add_callback(Button(emoji="⏮",style=1,custom_id="⏮"),btn_callback),
                             self.bot.components_manager.add_callback(Button(emoji="◀", style=1, custom_id="◀"),btn_callback),
                             Button(label=f"{self.index+1} / 5", disabled=True),
                             self.bot.components_manager.add_callback(Button(emoji="▶", style=1, custom_id="▶"),btn_callback),
                             self.bot.components_manager.add_callback(Button(emoji="⏭", style=1, custom_id="⏭"),btn_callback),
                             ],
                        self.bot.components_manager.add_callback(Button(emoji="❎", style=4, custom_id="❎"),
                                                                 btn_callback)
                        ])
            if custom_id == "▶":
                if not self.index == 4:
                    self.index += 1
                    em = discord.Embed(
                        description=li[self.index],
                        colour=discord.Colour.random()
                    )
                    await interaction.edit_origin(embed=em,components=[
                            [self.bot.components_manager.add_callback(Button(emoji="⏮",style=1,custom_id="⏮"),btn_callback),
                             self.bot.components_manager.add_callback(Button(emoji="◀", style=1, custom_id="◀"),btn_callback),
                             Button(label=f"{self.index+1} / 5", disabled=True),
                             self.bot.components_manager.add_callback(Button(emoji="▶", style=1, custom_id="▶"),btn_callback),
                             self.bot.components_manager.add_callback(Button(emoji="⏭", style=1, custom_id="⏭"),btn_callback),
                             ],
                        self.bot.components_manager.add_callback(Button(emoji="❎", style=4, custom_id="❎"),
                                                                 btn_callback)
                        ])
            if custom_id == "❎":
                await interaction.message.delete()
            if custom_id == "⏭":
                if not self.index == 4:
                    self.index = 4
                    em = discord.Embed(
                        description=li[self.index],
                        colour=discord.Colour.random()
                    )
                    await interaction.edit_origin(embed=em,components=[
                            [self.bot.components_manager.add_callback(Button(emoji="⏮",style=1,custom_id="⏮"),btn_callback),
                             self.bot.components_manager.add_callback(Button(emoji="◀", style=1, custom_id="◀"),btn_callback),
                             Button(label=f"{self.index+1} / 5", disabled=True),
                             self.bot.components_manager.add_callback(Button(emoji="▶", style=1, custom_id="▶"),btn_callback),
                             self.bot.components_manager.add_callback(Button(emoji="⏭", style=1, custom_id="⏭"),btn_callback),
                             ],
                        self.bot.components_manager.add_callback(Button(emoji="❎", style=4, custom_id="❎"),
                                                                 btn_callback)
                        ])
        em = discord.Embed(
            description=li[0],
            colour=discord.Colour.random()
        )
        await ctx.reply(embed=em,components=[
            [self.bot.components_manager.add_callback(Button(emoji="⏮",style=1,custom_id="⏮"),btn_callback),
             self.bot.components_manager.add_callback(Button(emoji="◀", style=1, custom_id="◀"),btn_callback),
             Button(label="1 / 5", disabled=True),
             self.bot.components_manager.add_callback(Button(emoji="▶", style=1, custom_id="▶"),btn_callback),
             self.bot.components_manager.add_callback(Button(emoji="⏭", style=1, custom_id="⏭"),btn_callback),
             ],
            self.bot.components_manager.add_callback(Button(emoji="❎", style=4, custom_id="❎"),
                                                     btn_callback)
        ])

    @youtube.command(name="알림")
    async def youtube_channel(self,ctx,channel_id):
        search = ChannelSearch(browseId=channel_id)


def setup(bot):
    bot.add_cog(ytnt(bot))
