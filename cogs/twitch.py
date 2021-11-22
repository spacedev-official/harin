import asyncio
import json
import os
import time
import traceback

import aiohttp
import aiosqlite
import discord
import discordSuperUtils
import requests
from PycordPaginator import Paginator
from discord.ext import commands
from typing import List

from discord_components import Select, SelectOption, Button
from dotenv import load_dotenv
load_dotenv(verbose=True)


def mTwitchOauth2():
    key = ''
    try:
        key = requests.post("https://id.twitch.tv/oauth2/token?client_id=" + os.getenv('TWITCH_CLIENT_ID') +
                            "&client_secret=" + os.getenv('twitch_client_secret') + "&grant_type=client_credentials")
    except requests.exceptions.Timeout as te:
        print(te)
    except requests.exceptions.ConnectionError as ce:
        print(ce)
    except requests.exceptions.HTTPError as he:
        print(he)
    # Any Error except upper exception
    except requests.exceptions.RequestException as re:
        print(re)
    access_token = json.loads(key.text)["access_token"]
    print(access_token)
    return access_token
class twitch(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.live = {}
        self.access_token = mTwitchOauth2()
        self.TwitchManager = discordSuperUtils.TwitchManager(bot, os.getenv('TWITCH_CLIENT_ID'), self.access_token)
        self.bot.loop.create_task(self.twitch_loop())

    @staticmethod
    def add_stream_fields(embed: discord.Embed, stream: dict):
        embed.add_field(
            name="Title",
            value=f"[{stream['title']}](https://twitch.tv/{stream['user_name']})",
            inline=False,
        )
        embed.add_field(name="Game", value=stream["game_name"], inline=False)
        embed.add_field(name="Viewers", value=str(stream["viewer_count"]), inline=False)
        embed.add_field(
            name="Started At", value=stream["started_at"], inline=False
        )  # You can format it.
        embed.add_field(
            name="Mature",
            value="Yes" if stream["is_mature"] else "No",
            inline=False,
        )
        embed.add_field(name="Language", value=stream["language"].upper(), inline=False)
        embed.set_image(url=stream["thumbnail_url"].format(height=248, width=440))

    @staticmethod
    def loop_stream_fields(embed: discord.Embed, stream: dict):
        embed.add_field(
            name="Title",
            value=f"[{stream['title']}](https://twitch.tv/{stream['broadcaster_login']})",
            inline=False,
        )
        embed.add_field(name="Game", value=stream["game_name"], inline=False)
        embed.add_field(
            name="Started At", value=stream["started_at"], inline=False
        )  # You can format it.
        embed.add_field(name="Language", value=stream["broadcaster_language"].upper(), inline=False)
        embed.set_image(url=stream["thumbnail_url"].format(height=248, width=440))

    @commands.group(name="트위치", invoke_without_command=True)
    async def twitch_(self,ctx):
        db = await aiosqlite.connect("db/db.sqlite")
        twitch_cur = await db.execute("SELECT * FROM twitch WHERE guild = ?",(ctx.guild.id,))
        premium_cur = await db.execute("SELECT * FROM premium WHERE guild = ?",(ctx.guild.id,))
        twitch_resp = await twitch_cur.fetchall()
        premium_resp = await premium_cur.fetchone()
        if twitch_resp == []:
            return await ctx.reply("등록된 채널이 하나도 없어요! `하린아 트위치 등록 [채널ID]`로 등록하세요!")
        if premium_resp == None:
            em = discord.Embed(title="트위치 채널 목록 | 프리플랜(채널 개수 1개 제한)",colour=discord.Colour.random())
            for i in twitch_resp:
                status = await self.TwitchManager.get_channel_status([i[3]])
                stream_info = next(iter(status), None)
                if not stream_info:
                    em.add_field(name=f"채널: {stream_info['user_name']}({i[3]})",value="스트리밍 상태: <:Offline:911928110381953074>오프라인")
                else:
                    em.add_field(
                        name=f"채널: {stream_info['user_name']}({i[3]})",value=f"스트리밍 상태: <:streaming:911928055197478912>스트리밍중 [{stream_info['title']}](https://twitch.tv/{stream_info['user_name']})")
            return await ctx.reply(embed=em)
        formatted_leaderboard = []
        for i in twitch_resp:
            status = await self.TwitchManager.get_channel_status([i[3]])
            stream_info = next(iter(status), None)
            try:
                formatted_leaderboard.append(
                    f"채널: {stream_info['user_name']}({i[3]})\n스트리밍 상태: <:streaming:911928055197478912>스트리밍중 [{stream_info['title']}](https://twitch.tv/{stream_info['user_name']})")
            except:
                formatted_leaderboard.append(f"채널: {i[3]}\n스트리밍 상태: <:Offline:911928110381953074>오프라인")

        e = Paginator(
            client=self.bot.components_manager,
            embeds=discordSuperUtils.generate_embeds(
                formatted_leaderboard,
                title="트위치 채널 목록 | <:supporter_badge:904937799701110814>프리미엄플랜(채널 개수 5개 제한)",
                fields=3,
                description=f"{ctx.guild}의 트위치 알림 채널 목록",
            ),
            channel=ctx.channel,
            only=ctx.author,
            ctx=ctx,
            use_select=False)
        await e.start()

    @twitch_.command(name="검색")
    async def twitch_lookup(self,ctx,*, channel: str):
        status = await self.TwitchManager.get_channel_status([channel])
        stream_info = next(iter(status), None)
        if not stream_info:
            await ctx.send(f"<:Offline:911928110381953074> '{channel}'은 오프라인이거나 존재하지않는 채널이에요.")
            return

        embed = discord.Embed(title=f"<:streaming:911928055197478912> '{stream_info['user_name'] or channel}' 은 스트리밍중이에요!", color=0x00FF00)

        self.add_stream_fields(embed, stream_info)

        await ctx.reply(embed=embed)

    @twitch_.command(name="등록")
    async def twitch_add(self,ctx,role:discord.Role,notice_channel:discord.TextChannel,*, channel: str):
        db = await aiosqlite.connect("db/db.sqlite")
        twitch_cur = await db.execute("SELECT * FROM twitch WHERE guild = ?", (ctx.guild.id,))
        premium_cur = await db.execute("SELECT * FROM premium WHERE guild = ?", (ctx.guild.id,))
        twitch_resp = await twitch_cur.fetchall()
        premium_resp = await premium_cur.fetchone()
        if premium_resp == None:
            if twitch_resp == []:
                await db.execute("INSERT INTO twitch(guild, notice_channel, notice_role, channel) VALUES (?, ?, ?, ?)",
                                 (ctx.guild.id, notice_channel.id, role.id, channel))
                await db.commit()
                await self.TwitchManager.add_channel(ctx.guild, channel)
                return await ctx.reply(f"성공적으로 '{channel}'을 등록했어요.")
            else:
                return await ctx.reply("프리미엄을 사용중이지않아 추가 등록하지못했어요. 추가 등록을 원하시면 프리미엄을 구매해주세요.")
        else:
            if twitch_resp == [] or len(list(twitch_resp)) <= 5:
                await db.execute("INSERT INTO twitch(guild, notice_channel, notice_role, channel) VALUES (?, ?, ?, ?)",
                                 (ctx.guild.id, notice_channel.id, role.id, channel))
                await db.commit()
                #await self.TwitchManager.add_channel(ctx.guild, channel)
                return await ctx.reply(f"성공적으로 '{channel}'을 등록했어요.")
            else:
                return await ctx.reply("앗! 등록된 채널 개수가 5개여서 등록하지 못했어요..😥")

    @twitch_.command(name="해제")
    async def twitch_del(self,ctx):
        db = await aiosqlite.connect("db/db.sqlite")
        twitch_cur = await db.execute("SELECT * FROM twitch WHERE guild = ?", (ctx.guild.id,))
        twitch_resp = await twitch_cur.fetchall()
        if twitch_resp == []:
            return await ctx.reply("등록된 채널이 하나도 없어요! `하린아 트위치 등록 [채널ID]`로 등록하세요!")
        msg = await ctx.send(f"{ctx.author.mention}, 아래의 목록중 알림 해제하고싶은 채널을 선택하세요.",
                             components=[
                                 Select(placeholder="알림 해제 채널 선택",
                                        options=[
                                            SelectOption(label=i[3],
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
        await db.execute("DELETE FROM twitch WHERE guild = ? AND channel = ?",(ctx.guild.id,value))
        await db.commit()
        await msg.edit("성공적으로 알림해제를 하였어요!",components=[])

    @staticmethod
    async def channel_statues(url,headers):
        async with aiohttp.ClientSession(headers=headers) as cs2:
            async with cs2.get(url) as res2:
                pr2 = await res2.read()
                sid2 = pr2.decode('utf-8')
                return json.loads(sid2)

    async def twitch_loop(self):
        await self.bot.wait_until_ready()
        db = await aiosqlite.connect("db/db.sqlite")
        while not self.bot.is_closed():
            await asyncio.sleep(5)
            twitch_cur = await db.execute("SELECT * FROM twitch")
            datas = await twitch_cur.fetchall()
            headers = {'Client-Id': os.getenv("TWITCH_CLIENT_ID"),
                       'Authorization': "Bearer " + self.access_token}
            for i in datas:
                url = "https://api.twitch.tv/helix/users?login=" + i[3]
                async with aiohttp.ClientSession(headers=headers) as cs2:
                    async with cs2.get(url) as res2:
                        pr2 = await res2.read()
                        sid2 = pr2.decode('utf-8')
                        answer2 = json.loads(sid2)
                        try:
                            url2 = "https://api.twitch.tv/helix/search/channels?query=" + i[3]
                            jsons = await self.channel_statues(url2,headers)
                            for j in jsons['data']:
                                if j['display_name'] == answer2['data'][0]['display_name']:
                                    if j['is_live']:
                                        try:
                                            if self.live[j['broadcaster_login']]:
                                                pass
                                            else:
                                                self.live[j['broadcaster_login']] = True
                                                status = await self.TwitchManager.get_channel_status([j['broadcaster_login']])
                                                stream_info = next(iter(status), None)
                                                embed = discord.Embed(
                                                    title=f"<:streaming:911928055197478912> '{j['display_name']}'님이 스트리밍을 시작하였어요!",
                                                    color=0x00FF00)

                                                #self.loop_stream_fields(embed, j)
                                                self.add_stream_fields(embed,stream_info)
                                                channel = self.bot.get_channel(i[1])
                                                await channel.send(content=f"<@&{i[2]}>",embed=embed,components=[Button(style=5,
                                                                                                                        url=f"https://twitch.tv/{j['broadcaster_login']}",
                                                                                                                        label=f"{j['display_name']}님의 방송 보러가기",
                                                                                                                        emoji=self.bot.get_emoji(911928055197478912))])
                                        except:
                                            self.live[j['broadcaster_login']] = False
                                    else:
                                        try:
                                            if self.live[j['broadcaster_login']]:
                                                embed = discord.Embed(
                                                    title=f"<:Offline:911928110381953074> '{j['display_name']}'님이 스트리밍을 종료했어요!",
                                                    color=0x00FF00)
                                                embed.add_field(
                                                    name="채널 방문하기",
                                                    value=f"[{j['display_name']}](https://twitch.tv/{j['broadcaster_login']})",
                                                    inline=False,
                                                )
                                                embed.set_image(
                                                    url=j["thumbnail_url"].format(height=248, width=440))
                                                channel = self.bot.get_channel(i[1])
                                                await channel.send(embed=embed,components=[Button(style=5,
                                                                                                    url=f"https://twitch.tv/{j['broadcaster_login']}",
                                                                                                    label=f"{j['display_name']}님의 채널 방문하기")])
                                                self.live[j['broadcaster_login']] = False
                                        except:
                                            self.live[j['broadcaster_login']] = False
                        except:
                            user = await self.bot.fetch_user(281566165699002379)
                            await user.send(str(traceback.format_exc()))

def setup(bot):
    bot.add_cog(twitch(bot))
