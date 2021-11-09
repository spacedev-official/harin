import asyncio
import platform

import aiosqlite
import discord
import discordSuperUtils
from PycordPaginator import Paginator
from discord.ext import commands
from discordSuperUtils import ModMailManager
from discord_components import (
    Select,
    SelectOption, Interaction
)
import aiosqlite

class info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="서버정보")
    async def serverinfo(self, ctx):
        server = ctx.guild
        roles = [x.name for x in server.roles]
        role_length = len(roles)
        if role_length > 50:
            roles = roles[:50]
            roles.append(f">>>> [50/{len(roles)}]")
        roles = ", ".join(roles)
        channels = len(server.channels)
        time = str(server.created_at)
        time = time.split(" ")
        time = time[0]

        embed = discord.Embed(
            title="**서버 이름:**",
            description=f"{server}",
            color=0x42F56C
        )
        embed.set_thumbnail(
            url=server.icon_url
        )
        embed.add_field(
            name="서버 ID",
            value=server.id
        )
        embed.add_field(
            name="멤버수",
            value=server.member_count
        )
        embed.add_field(
            name="텍스트/보이스 채널수",
            value=f"{channels}"
        )
        embed.add_field(
            name=f"역할 `({role_length})`개",
            value=roles
        )
        embed.set_footer(
            text=f"생성일시: {time}"
        )
        await ctx.reply(embed=embed)

    @commands.command(name="봇정보")
    async def botinfo(self, ctx):
        """
        Get some useful (or not) information about the bot.
        """

        # This is, for now, only temporary

        embed = discord.Embed(
            description="하린봇 정보",
            color=0x42F56C
        )
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.set_image(
            url="https://media.discordapp.net/attachments/889514827905630290/896359450544308244/37cae031dc5a6c40.png")
        embed.add_field(
            name="주인:",
            value="gawi#9537(281566165699002379)",
            inline=True
        )
        embed.add_field(
            name="Pycord Version:",
            value=f"{discord.__version__}",
            inline=True
        )
        embed.add_field(
            name="Python Version:",
            value=f"{platform.python_version()}",
            inline=False
        )
        embed.add_field(
            name="OS Platform:",
            value=f"{platform.platform()}",
            inline=False
        )
        embed.add_field(name="Prefix:", value='하린아', inline=True)
        embed.add_field(
            name="Ping:",
            value=str(round(self.bot.latency * 1000)) + "ms",
            inline=True
        )
        await ctx.reply(embed=embed)

    @commands.group(name="뱃지", aliases=["배지"],invoke_without_command=True)
    async def badge(self,ctx):
        bughunter = "<:bughunter_1:905247256926621736><:bughunter_2:905247257207644180><:bughunter_3:905247257480290314>\n<:bughunter_badge:905249754122965042>\n봇의 버그를 많이 찾아 제보할시 부여되는 배지입니다."
        contributor = "<:contributor_1:904885744814948353><:contributor_2:904885745070800969><:contributor_3:904885745066602570>\n<:contributor_badge:904937799571079199>\n팀 프로젝트에 많이 기여할시 부여되는 배지입니다."
        partner = "<:partner_1:904888203100692601><:partner_2:904888203025186926><:partner_3:904888203310411776>\n<:partner_badge:904937799705305108>\n저희 팀과 파트너를 맺을시 부여되는 배지입니다."
        supporter = "<:supporter_1:904879569004265563><:supporter_2:904879568677117964><:supporter_3:904879568958144623>\n<:supporter_badge:904937799701110814>\n저희팀 공식서버를 부스트하시거나 후원금을 주셨을시 부여되는 배지입니다."
        heartverify = "<:heartverify_1:905318776407478283><:heartverify_2:905318776864649236><:heartverify_3:905318776424255501>\n<:heartverify_badge:905321990183874560>\n`ㅎ하트인증`을 통해 하트를 누른것이 확인될경우 부여되는 배지입니다."
        res = f"{bughunter}\n\n{contributor}\n\n{partner}\n\n{supporter}\n\n{heartverify}"
        await ctx.reply(res)

    @badge.command(name="목록")
    @commands.is_owner()
    async def badge_list(self,ctx):
        dicts = {
            "supporter": "<:supporter_badge:904937799701110814>",
            "partner": "<:partner_badge:904937799705305108>",
            "contributor": "<:contributor_badge:904937799571079199>",
            "bughunter": "<:bughunter_badge:905249754122965042>",
            "heartverify": "<:heartverify_badge:905321990183874560>"
        }
        db = await aiosqlite.connect("db/db.sqlite")
        cur = await db.execute("SELECT * FROM badge")
        res = await cur.fetchall()
        formatted_leaderboard = [
            f"유저(ID): {self.bot.get_user(x[0])}({x[0]})\n소유 배지: {dicts[x[1]]}" for x in res
        ]

        e = Paginator(
            client=self.bot.components_manager,
            embeds=discordSuperUtils.generate_embeds(
                formatted_leaderboard,
                title="배지 소유 리스트",
                fields=15,
                description=f"오너전용 배지 소유 정보 리스트",
            ),
            channel=ctx.channel,
            only=ctx.author,
            ctx=ctx,
            use_select=False)
        await e.start()

    @badge.command(name="등록")
    @commands.is_owner()
    async def badge_add(self, ctx, user_id:int, badge_type):
        dicts = {
            "supporter":"<:supporter_1:904879569004265563><:supporter_2:904879568677117964><:supporter_3:904879568958144623>",
            "partner":"<:partner_1:904888203100692601><:partner_2:904888203025186926><:partner_3:904888203310411776>",
            "contributor":"<:contributor_1:904885744814948353><:contributor_2:904885745070800969><:contributor_3:904885745066602570>",
            "bughunter":"<:bughunter_1:905247256926621736><:bughunter_2:905247257207644180><:bughunter_3:905247257480290314>",
            "heartverify":"<:heartverify_1:905318776407478283><:heartverify_2:905318776864649236><:heartverify_3:905318776424255501>"
        }
        user = await self.bot.fetch_user(user_id)
        db = await aiosqlite.connect("db/db.sqlite")
        cur = await db.execute("SELECT * FROM badge WHERE user = ? AND badge_type = ?", (user_id,badge_type))
        res = await cur.fetchone()
        if res is not None:
            return await ctx.reply("이미 소유하고 있어요.")
        user_em = discord.Embed(
            title="축하드립니다!🎉",
            description=f"관리자님이 {dicts[badge_type]}배지를 부여하셨어요!",
            colour=discord.Colour.random()
        )
        await db.execute("INSERT INTO badge(user,badge_type) VALUES (?,?)",(user_id,badge_type))
        await db.commit()
        await user.send(embed=user_em)
        await ctx.message.add_reaction("✅")

    @badge.command(name="제거")
    @commands.is_owner()
    async def badge_remove(self,ctx,user_id:int):
        dicts = {
            "supporter": self.bot.get_emoji(904937799701110814),
            "partner": self.bot.get_emoji(904937799705305108),
            "contributor": self.bot.get_emoji(904937799571079199),
            "bughunter": self.bot.get_emoji(905249754122965042),
            "heartverify":self.bot.get_emoji(905321990183874560)
        }
        db = await aiosqlite.connect("db/db.sqlite")
        cur = await db.execute("SELECT * FROM badge WHERE user = ?", (user_id,))
        res = await cur.fetchall()
        msg = await ctx.send("제거할 배지를 선택하세요.",
                             components=[
                                 Select(placeholder="제거할 배지 선택",
                                        options=[
                                            SelectOption(label=i[1],
                                                         value=i[1], emoji=dicts[i[1]]) for i in res
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
        await db.execute("DELETE FROM badge WHERE user = ? AND badge_type = ?",(user_id, value))
        await db.commit()
        await msg.edit(content="✅", components = [])

    @commands.command(name="유저정보",aliases=['내정보'])
    async def myinfo(self, ctx, member:discord.Member = None):
        dicts = {
            "supporter": "<:supporter_badge:904937799701110814>",
            "partner": "<:partner_badge:904937799705305108>",
            "contributor": "<:contributor_badge:904937799571079199>",
            "bughunter": "<:bughunter_badge:905249754122965042>",
            "heartverify":"<:heartverify_badge:905321990183874560>"
        }
        member = ctx.author if not member else member
        db = await aiosqlite.connect("db/db.sqlite")
        cur = await db.execute("SELECT * FROM badge WHERE user = ?",(member.id,))
        res = await cur.fetchall()
        if res != []:
            li = [dicts[i[1]] for i in res]
            vl = " ".join(li)
        else:
            vl = "<a:cross:893675768880726017> 소유한 배지 없음"
        em = discord.Embed(
            title=f"{member}의 정보",
            colour=discord.Colour.random()
        )
        em.add_field(
            name="디스코드 가입일",
            value=f"{member.created_at.strftime('%Y-%m-%d  %H:%M:%S')}\n최초 가입일로부터 `{(ctx.message.created_at - member.created_at).days}`일 지남."
        )
        em.add_field(
            name="서버 가입일",
            value=member.joined_at.strftime('%Y-%m-%d  %H:%M:%S') + "\n최초 서버 가입일로 부터 `" + str((ctx.message.created_at - member.joined_at).days) + "`일 지남."
        )
        em.add_field(
            name="소유 역할",
            value=", ".join([role.mention for role in list(reversed(member.roles)) if not role.is_default()]),
            inline=False
        )
        em.add_field(
            name="소유 배지",
            value= vl
        )
        await ctx.reply(embed=em)



def setup(bot):
    bot.add_cog(info(bot))
