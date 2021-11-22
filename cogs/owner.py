import random
import time
import uuid
from datetime import datetime

import discordSuperUtils
from PycordPaginator import Paginator
from dateutil.relativedelta import relativedelta
import aiosqlite
import discord
from discord.ext import commands


class Owner(commands.Cog):
    def __init__(self, bot:commands.Bot):
        super().__init__()
        self.bot = bot

    @commands.group(name="블랙",invoke_without_command=True)
    async def blacklist(self,ctx:commands.Context):
        database = await aiosqlite.connect("db/db.sqlite")
        cur = await database.execute("SELECT * FROM blacklist WHERE user = ?", (ctx.author.id,))
        if await cur.fetchone() == None:
            return await ctx.reply(f"{ctx.author}님은 블랙리스트에 등록되어있지 않아요.")
        data = await cur.fetchone()
        await ctx.reply(f"블랙사유: {data[1]}")

    @blacklist.command(name="추가")
    @commands.is_owner()
    async def blacklist_add(self,ctx:commands.Context,user_id:int,*,reason):
        user = await self.bot.fetch_user(user_id)
        database = await aiosqlite.connect("db/db.sqlite")
        cur = await database.execute("SELECT * FROM blacklist WHERE user = ?", (user_id,))
        datas = await cur.fetchone()
        if datas != None:
            return await ctx.reply(f"{user}님은 블랙리스트에 등록되어있어요.\n사유: {datas[1]}")
        await database.execute("INSERT INTO blacklist(user,reason) VALUES (?,?)", (user_id, reason))
        await database.commit()
        try:
            await user.send(f"__관리자로부터 블랙등록됨.__\n\n"
                            f"관리자가 아래의 사유로 블랙등록하셨어요.\n\n"
                            f"사유: \n{reason}")
        except:
            pass
        await ctx.reply("등록완료!")

    @blacklist.command(name="삭제")
    @commands.is_owner()
    async def blacklist_del(self, ctx: commands.Context, user_id: int):
        user = await self.bot.fetch_user(user_id)
        database = await aiosqlite.connect("db/db.sqlite")
        cur = await database.execute("SELECT * FROM blacklist WHERE user = ?", (user_id,))
        datas = await cur.fetchone()
        if datas == None:
            return await ctx.reply(f"{user}님은 블랙리스트에 등록되어있지않아요.")
        await database.execute("DELETE FROM blacklist WHERE user = ?", (user_id,))
        await database.commit()
        try:
            await user.send(f"__관리자로부터 블랙해제됨.__\n\n"
                            f"관리자가 블랙해제하셨어요.")
        except:
            pass
        await ctx.reply("해제완료!")

    @commands.command(name="공지")
    @commands.is_owner()
    async def broadcasting(self, ctx, *, value):
        em = discord.Embed(
            title="하린 봇 공지사항!",
            description=value,
            colour=discord.Colour.random()
        )
        em.set_thumbnail(url=self.bot.user.avatar_url)
        em.set_image(
            url="https://media.discordapp.net/attachments/889514827905630290/896359450544308244/37cae031dc5a6c40.png")
        em.set_footer(text="특정 채널에 받고싶다면 '하린아 설정'으로 설정하세요! 권한 확인 필수!")
        msg = await ctx.reply("발송중...")
        guilds = self.bot.guilds
        ok = []
        ok_guild = []
        success = 0
        failed = 0
        for guild in guilds:
            channels = guild.text_channels
            for channel in channels:
                if guild.id in [653083797763522580, 786470326732587008]:
                    break
                if (
                    channel.topic is not None
                    and str(channel.topic).find("-HOnNt") != -1
                ):
                    ok.append(channel.id)
                    ok_guild.append(guild.id)
                    break

        for guild in guilds:
            channels = guild.text_channels
            for _channel in channels:
                if guild.id in ok_guild:
                    break
                if guild.id in [653083797763522580, 786470326732587008]:
                    break
                random_channel = random.choices(channels)
                ok.append(random_channel[0].id)
                break
        for i in ok:
            channel = self.bot.get_channel(i)
            try:
                await channel.send(embed=em)
                success += 1
            except discord.Forbidden:
                failed += 1
        await msg.edit("발송완료!\n성공: `{ok}`\n실패: `{no}`".format(ok=success, no=failed))

    @commands.command(name="메일작성")
    @commands.is_owner()
    async def mail(self, ctx, *, va_lue):
        database = await aiosqlite.connect("db/db.sqlite")
        cur = await database.execute('SELECT * FROM mail')
        mails = await cur.fetchall()
        print(mails)
        check = 1
        # noinspection PyBroadException
        try:
            for _ in mails:
                check += 1
        except Exception as e:
            print(e)
        await database.execute(
            'INSERT INTO mail(id,value) VALUES (?,?)', (check, va_lue)
        )

        await database.commit()
        await ctx.send('성공적으로 메일을 발송하였습니다.')

    @commands.group(name="프리미엄", invoke_without_command=True)
    async def premium(self,ctx):
        db = await aiosqlite.connect("db/db.sqlite")
        conn = await db.execute("SELECT * FROM premium WHERE guild = ?",(ctx.guild.id,))
        resp = await conn.fetchone()
        em = discord.Embed(
            title=f"{ctx.guild.name}의 프리미엄 상태",
            colour=discord.Colour.random()
        )
        em.add_field(name="맞춤법 감지 무제한",value="맞춤법 감지제한이 500회였다면 이젠 무제한으로 잘못된 맞춤법을 감지해보세요!",inline=False)
        em.add_field(name="욕설 감지 무제한",value="욕설 감지제한이 1,000회였다면 이젠 무제한으로 욕설을 감지해보세요!",inline=False)
        em.add_field(name="트위치 채널 등록가능 개수 1 -> 5개", value="트위치 방송알림을 받기위해 등록하는 채널 개수 제한이 1개에서 5개로 늘어납니다!\n다양한 스트리머를 등록해 방송알림을 받아보세요!", inline=False)
        if resp == None:
            em.add_field(name="프리미엄 상태",value="<a:cross:893675768880726017>프리미엄을 이용중인 서버가 아니거나 만료된 상태에요..😥\n자세한 사항은 제 DM으로 `하린아 문의 [문의내용]`으로 문의해주세요.")
        else:
            #endtime = str(time.mktime(datetime.strptime(resp[2], '%Y-%m-%d %H:%M:%S').timetuple()))[:-2]
            em.add_field(name="프리미엄 상태", value=f"<:supporter_badge:904937799701110814>만료일: <t:{resp[3]}>(<t:{resp[3]}:R>)")
        await ctx.reply(embed=em)

    @premium.command(name="등록")
    @commands.is_owner()
    async def add_premium(self,ctx,guild_id:int,year: int, month: int, day: int):
        code = uuid.uuid4()
        db = await aiosqlite.connect("db/db.sqlite")
        conn = await db.execute("SELECT * FROM premium WHERE guild = ?", (guild_id,))
        resp = await conn.fetchone()
        if resp == None:
            ending = datetime.now() + relativedelta(years=int(year), months=int(month), days=int(day))
            ending = ending.strftime('%Y/%m/%d %H:%M:%S')
            endtime = str(time.mktime(datetime.strptime(ending, '%Y/%m/%d %H:%M:%S').timetuple()))[:-2]
            await db.execute("INSERT INTO premium(guild, code, end_time, end_timestamp) VALUES (?, ?, ?, ?)",
                             (guild_id, str(code), str(ending), endtime))
            await db.commit()
            return await ctx.reply("✅")
        return await ctx.reply("이미 사용중이에요.")

    @premium.command(name="삭제")
    @commands.is_owner()
    async def del_premium(self, ctx, code: str):
        db = await aiosqlite.connect("db/db.sqlite")
        conn = await db.execute("SELECT * FROM premium WHERE code = ?", (code,))
        resp = await conn.fetchone()
        if resp == None:
            return await ctx.reply("사용중인 길드가 아니에요.")
        await db.execute("DELETE FROM premium WHERE code = ?",(code,))
        await db.commit()
        return await ctx.reply("✅")

    @premium.command(name="조회")
    @commands.is_owner()
    async def getinfo_premium(self, ctx, code: str = None):
        db = await aiosqlite.connect("db/db.sqlite")
        if code == None:
            conn = await db.execute("SELECT * FROM premium")
            resp = await conn.fetchall()
            formatted_leaderboard = [
                f"길드(ID): {self.bot.get_guild(x[0])}({x[0]})\n코드: {x[1]}\n만료일: <t:{x[3]}>(<t:{x[3]}:R>)" for x in resp
            ]

            e = Paginator(
                client=self.bot.components_manager,
                embeds=discordSuperUtils.generate_embeds(
                    formatted_leaderboard,
                    title="프리미엄 리스트",
                    fields=15,
                    description=f"오너전용 프리미엄 정보 리스트",
                ),
                channel=ctx.channel,
                only=ctx.author,
                ctx=ctx,
                use_select=False)
            await e.start()
        else:
            conn = await db.execute("SELECT * FROM premium WHERE code = ?",(code,))
            resp = await conn.fetchone()
            em = discord.Embed(
                title=f"{self.bot.get_guild(resp[0])}({resp[0]})의 프리미엄 상태",
                description=f"코드: {resp[1]}\n프리미엄 만료일: <t:{resp[3]}>(<t:{resp[3]}:R>)",
                colour=discord.Colour.random()
            )
            return await ctx.reply(embed=em)


def setup(bot):
    bot.add_cog(Owner(bot))
