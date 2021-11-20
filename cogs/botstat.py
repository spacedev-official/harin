import asyncio
import os
import random
import statcord
import aiosqlite
from dotenv import load_dotenv
import discord
from discord import errors
from discord.ext import commands
import koreanbots
from koreanbots.integrations import discord
load_dotenv(verbose=True)
class botstat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.krb = koreanbots.Koreanbots(api_key=os.getenv("KRB_TOKEN"))
        self._krb = discord.DiscordpyKoreanbots(client=self.bot,api_key=os.getenv("KRB_TOKEN"),run_task=True)
        self.statcord = statcord.Client(self.bot, os.getenv("STATCORD"),custom1=self.custom1,custom2=self.custom2,logging_level='INFO')
        self.statcord.start_loop()

    @commands.command(name="하트인증", aliases=["추천인증","추천","하트","ㅊㅊ"])
    async def heart_check(self,ctx):
        voted = await self.krb.is_voted(user_id=ctx.author.id,bot_id=self.bot.user.id)
        db = await aiosqlite.connect("db/db.sqlite")
        cur = await db.execute("SELECT * FROM badge WHERE user = ? AND badge_type = ?", (ctx.author.id, "heartverify"))
        res = await cur.fetchone()
        if voted.voted:
            if res is not None:
                badge_msg = "이미 <:heartverify_1:905318776407478283><:heartverify_2:905318776864649236><:heartverify_3:905318776424255501>배지를 소유하고 있어 무시되었어요."
            else:
                await db.execute("INSERT INTO badge(user,badge_type) VALUES (?,?)", (ctx.author.id, "heartverify"))
                await db.commit()
                badge_msg = "하트 인증이 확인되어 <:heartverify_1:905318776407478283><:heartverify_2:905318776864649236><:heartverify_3:905318776424255501>배지를 부여해드렸어요!"
            return await ctx.reply("> 추천해주셔서 감사해요!💕\n> " + badge_msg)
        msg = await ctx.reply("> 추천하지 않으신 것 같아요.. 아래링크로 이동하셔서 추천해주세요!\n> 링크: https://koreanbots.dev/bots/893841721958469703/vote\n> 1분후 재확인 할게요!")
        await asyncio.sleep(60)
        cur = await db.execute("SELECT * FROM badge WHERE user = ? AND badge_type = ?", (ctx.author.id, "heartverify"))
        res = await cur.fetchone()
        voted = await self.krb.is_voted(user_id=ctx.author.id, bot_id=self.bot.user.id)
        if voted.voted:
            if res is not None:
                badge_msg = "이미 <:heartverify_1:905318776407478283><:heartverify_2:905318776864649236><:heartverify_3:905318776424255501>배지를 소유하고 있어 무시되었어요."
            else:
                await db.execute("INSERT INTO badge(user,badge_type) VALUES (?,?)", (ctx.author.id, "heartverify"))
                await db.commit()
                badge_msg = "하트 인증이 확인되어 <:heartverify_1:905318776407478283><:heartverify_2:905318776864649236><:heartverify_3:905318776424255501>배지를 부여해드렸어요!"
            return await msg.edit("> 추천이 확인되었어요! 추천해주셔서 감사해요!💕\n> " + badge_msg)
        await msg.edit("> 추천이 확인되지않았어요..😢 혹시 마음에 드시지않으신가요..?🥺")

    @commands.Cog.listener()
    async def on_command(self, ctx):
        self.statcord.command_run(ctx)

    async def custom1(self):
        resp = (await self._krb.botinfo(self.bot.user.id)).votes
        return str(resp)

    async def custom2(self):
        return str(len(self.bot.voice_clients))

def setup(bot):
    bot.add_cog(botstat(bot))
