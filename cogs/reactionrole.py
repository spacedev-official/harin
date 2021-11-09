import aiosqlite
import discord
from discord.ext import commands
import discordSuperUtils
class reactionrole(commands.Cog,discordSuperUtils.CogManager.Cog):
    def __init__(self, bot:commands.Bot):
        super().__init__()
        self.bot = bot
        self.ReactionManager = discordSuperUtils.ReactionManager(bot)

    @discordSuperUtils.CogManager.event(discordSuperUtils.ReactionManager)
    async def on_reaction_event(self, guild, channel, message, member, emoji):
        print('reaction role event')

    @commands.Cog.listener("on_ready")
    async def rr_on_ready(self):
        database = discordSuperUtils.DatabaseManager.connect(
            await aiosqlite.connect("db/db.sqlite")
        )
        await self.ReactionManager.connect_to_database(database, ["reaction_roles"])

    @commands.command()
    async def reaction(
            self, ctx, message, emoji: str, remove_on_reaction, role: discord.Role = None
    ):
        message = await ctx.channel.fetch_message(message)

        await self.ReactionManager.create_reaction(
            ctx.guild, message, role, emoji, remove_on_reaction
        )



def setup(bot):
    bot.add_cog(reactionrole(bot))
