import random

import discord
from discord import errors
from discord.ext import commands
from badword_check import BadWord

model = BadWord.load_badword_model()

class badword(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener('on_message')
    async def badword_listen(self,message):
        if message.author.bot:
            return
        if message.channel.id == 884407186854404106:
            data = BadWord.preprocessing(str(message.content))
            await message.channel.send(model.predict(data))
        else:
            pass
        await self.bot.process_commands(message)


def setup(bot):
    bot.add_cog(badword(bot))
