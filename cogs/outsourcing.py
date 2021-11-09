import random

import aiosqlite
import discord
from discord import errors
from discord.ext import commands

class outsourcing(commands.Cog):
    def __init__(self, bot:commands.Bot):
        super().__init__()
        self.bot = bot

    @commands.group(name="거래")
    async def outsourcing(self,ctx:commands.Context):
        database = await aiosqlite.connect("db/db.sqlite")
        cur = await database.execute("SELECT * FROM blacklist WHERE user = ?", (message.author.id,))
        em = discord.Embed(
            title="하린봇 개인거래기능",
            description="하린봇으로 외주를 쉽게 받거나 의뢰해보세요.",
            colour=discord.Colour.random()
        )
        await ctx.reply

def setup(bot):
    bot.add_cog(outsourcing(bot))
