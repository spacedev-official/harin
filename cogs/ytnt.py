import asyncio
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
        self.youtube_cache = {}
        self.bot.loop.create_task(self.youtube_loop())

    @aioify
    def channelssearch(self,name,limit):
        channelsSearch = ChannelsSearch(name, limit=limit, region="KO")
        res: dict = channelsSearch.result()
        return res


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


    @commands.group(name="유튜브",invoke_without_command=True)
    async def youtube(self,ctx,*,name):
        res = await self.channelssearch(name,5)
        #li = [i for i in res["result"] if i["type"] == "channel"]
        li = []
        for i in res["result"]:
            if i["type"] == "channel":
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
        await ctx.send(embed=em,components=[
            [self.bot.components_manager.add_callback(Button(emoji="⏮",style=1,custom_id="⏮"),btn_callback),
             self.bot.components_manager.add_callback(Button(emoji="◀", style=1, custom_id="◀"),btn_callback),
             Button(label="1 / 5", disabled=True),
             self.bot.components_manager.add_callback(Button(emoji="▶", style=1, custom_id="▶"),btn_callback),
             self.bot.components_manager.add_callback(Button(emoji="⏭", style=1, custom_id="⏭"),btn_callback),
             ],
            self.bot.components_manager.add_callback(Button(emoji="❎", style=4, custom_id="❎"),
                                                     btn_callback)
        ])

    @youtube.command(name="등록")
    async def youtube_channel(self,ctx,role:discord.Role,notice_channel:discord.TextChannel,*,channel):
        #search = ChannelSearch(browseId=channel_id)
        api = pyyoutube.Api(api_key=os.getenv("YT_TOKEN"))
        channel_res = api.get_channel_info(channel_id=channel)
        #print(channel_res.items[0].snippet.title)
        db = await aiosqlite.connect("db/db.sqlite")
        twitch_cur = await db.execute("SELECT * FROM youtube WHERE guild = ?", (ctx.guild.id,))
        premium_cur = await db.execute("SELECT * FROM premium WHERE guild = ?", (ctx.guild.id,))
        twitch_resp = await twitch_cur.fetchall()
        premium_resp = await premium_cur.fetchone()
        if premium_resp == None:
            if twitch_resp == []:
                await db.execute("INSERT INTO youtube(guild, notice_channel, notice_role, channel) VALUES (?, ?, ?, ?)",
                                 (ctx.guild.id, notice_channel.id, role.id, channel))
                await db.commit()
                return await ctx.reply(f"성공적으로 '{channel_res.items[0].snippet.title}'을 등록했어요.")
            else:
                return await ctx.reply("프리미엄을 사용중이지않아 추가 등록하지못했어요. 추가 등록을 원하시면 프리미엄을 구매해주세요.")
        else:
            if twitch_resp == [] or len(list(twitch_resp)) <= 5:
                await db.execute("INSERT INTO youtube(guild, notice_channel, notice_role, channel) VALUES (?, ?, ?, ?)",
                                 (ctx.guild.id, notice_channel.id, role.id, channel))
                await db.commit()
                # await self.TwitchManager.add_channel(ctx.guild, channel)
                return await ctx.reply(f"성공적으로 '{channel_res.items[0].snippet.title}'을 등록했어요.")
            else:
                return await ctx.reply("앗! 등록된 채널 개수가 5개여서 등록하지 못했어요..😥")

    @youtube.command(name="해제")
    async def youtube_del(self,ctx):
        api = pyyoutube.Api(api_key=os.getenv("YT_TOKEN"))
        db = await aiosqlite.connect("db/db.sqlite")
        twitch_cur = await db.execute("SELECT * FROM youtube WHERE guild = ?", (ctx.guild.id,))
        twitch_resp = await twitch_cur.fetchall()
        if twitch_resp == []:
            return await ctx.reply("등록된 채널이 하나도 없어요! `하린아 트위치 등록 [채널ID]`로 등록하세요!")
        msg = await ctx.send(f"{ctx.author.mention}, 아래의 목록중 알림 해제하고싶은 채널을 선택하세요.",
                             components=[
                                 Select(placeholder="알림 해제 채널 선택",
                                        options=[
                                            SelectOption(label=api.get_channel_info(channel_id=i[3]).items[0].snippet.title,
                                                         value=i[3]) for i in twitch_resp
                                        ], )

                             ],
                             )
        try:
            interaction = await self.bot.wait_for(
                "select_option", check=lambda inter: inter.user.id == ctx.author.id
            )
            value = interaction.values[0]
        except asyncio.TimeoutError:
            await msg.edit("시간이 초과되었어요!", components=[])
            return
        ##await self.TwitchManager.remove_channel(ctx.guild, value)
        await db.execute("DELETE FROM youtube WHERE guild = ? AND channel = ?",(ctx.guild.id,value))
        await db.commit()
        await msg.edit("성공적으로 알림해제를 하였어요!",components=[])


    async def youtube_loop(self):
        await self.bot.wait_until_ready()
        db = await aiosqlite.connect("db/db.sqlite")
        api = pyyoutube.Api(api_key=os.getenv("YT_TOKEN"))
        while not self.bot.is_closed():
            await asyncio.sleep(5)
            twitch_cur = await db.execute("SELECT * FROM youtube")
            datas = await twitch_cur.fetchall()
            for i in datas:
                resp = await self.get_videos(i[3])
                #print(resp[0].snippet.title)
                try:
                    if self.youtube_cache[i[3]] != resp[0].id:
                        channel_res = api.get_channel_info(channel_id=i[3])
                        em = discord.Embed(
                            title=f"'{channel_res.items[0].snippet.title}'님이 새로운 영상을 업로드했어요!",
                            colour=discord.Colour.random()
                        )
                        if not channel_res.items[0].statistics.hiddenSubscriberCount:
                            subs = "비공개"
                        else:
                            subs = f"`{channel_res.items[0].statistics.subscriberCount}`명"
                        em.add_field(
                            name="제목",
                            value=resp[0].snippet.title
                        )
                        em.add_field(
                            name="구독자 수",
                            value=subs
                        )
                        em.add_field(
                            name="모든 영상 수",
                            value=f"`{channel_res.items[0].statistics.videoCount}`개"
                        )
                        em.add_field(
                            name="총 조회 수",
                            value=f"`{channel_res.items[0].statistics.viewCount}`회"
                        )
                        em.set_image(url=channel_res.items[0].snippet.thumbnails.high)
                        await self.bot.get_channel(i[1]).send(
                            content=f"<@&{i[2]}>",
                            embed=em,
                            components=[
                                Button(
                                    style=5,
                                    url=f"https://youtu.be/{resp[0].id}",
                                    label='영상 보러가기',
                                )
                            ],
                        )
                        self.youtube_cache[i[3]] = resp[0].id
                except:
                    self.youtube_cache[i[3]] = resp[0].id


def setup(bot):
    bot.add_cog(ytnt(bot))
