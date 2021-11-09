import asyncio
import platform

import aiosqlite
import discord
from discord.ext import commands
from discordSuperUtils import ModMailManager
from discord_components import (
    Select,
    SelectOption, Interaction
)


class ww(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ww")
    async def select(self,ctx):
        await ctx.send(
            "Selects!",
            components=[
                Select(
                    placeholder="Select something!",
                    options=[
                        SelectOption(label="a", value="a"),
                        SelectOption(label="b", value="b"),
                    ],
                    custom_id="select1",
                )
            ],
        )

        interaction = await self.bot.wait_for(
            "select_option", check=lambda inter: inter.user.id == ctx.author.id
        )
        await ctx.send(content=f"{interaction.values[0]} selected!")



def setup(bot):
    bot.add_cog(ww(bot))
