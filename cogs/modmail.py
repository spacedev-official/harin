import aiosqlite
import discord
import discordSuperUtils
from discord.ext import commands
from discordSuperUtils import ModMailManager

class modmail(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ModmailManager = ModMailManager(self.bot, trigger="ㅎ문의")

    async def cog_before_invoke(self, ctx: commands.Context):
        print(ctx.command)
        if ctx.command.name != '메일':
            database = await aiosqlite.connect("db/db.sqlite")
            cur = await database.execute(
                'SELECT * FROM uncheck WHERE user_id = ?', (ctx.author.id,)
            )

            if await cur.fetchone() is None:
                cur = await database.execute("SELECT * FROM mail")
                mails = await cur.fetchall()
                check = sum(1 for _ in mails)
                mal = discord.Embed(
                    title=f'📫하린봇 메일함 | {check}개 수신됨',
                    description="아직 읽지 않은 메일이 있어요.'`하린아 메일`'로 확인하세요.\n주기적으로 메일함을 확인해주세요! 소소한 업데이트 및 이벤트개최등 여러소식을 확인해보세요.",
                    colour=ctx.author.colour,
                )

                return await ctx.send(embed=mal)
            cur = await database.execute('SELECT * FROM mail')
            mails = await cur.fetchall()
            check = sum(1 for _ in mails)
            # noinspection DuplicatedCode
            cur = await database.execute("SELECT * FROM uncheck WHERE user_id = ?", (ctx.author.id,))
            # noinspection DuplicatedCode
            check2 = await cur.fetchone()
            if str(check) != str(check2[1]):
                mal = discord.Embed(
                    title=f'📫하린봇 메일함 | {int(check) - int(check2[1])}개 수신됨',
                    description="아직 읽지 않은 메일이 있어요.'`하린아 메일`'로 확인하세요.\n주기적으로 메일함을 확인해주세요! 소소한 업데이트 및 이벤트개최등 여러소식을 확인해보세요.",
                    colour=ctx.author.colour,
                )

                await ctx.send(embed=mal)

    @commands.command(name="문의")
    async def on_modmail_request(self,ctx: commands.Context):
        await self.ModmailManager.connect_to_database(self.bot.db, ["modmail"])
        guilds = await self.ModmailManager.get_mutual_guilds(ctx.author)
        guild = await self.ModmailManager.get_modmail_guild(ctx, guilds)
        channel = await self.ModmailManager.get_channel(guild)
        msg = await self.ModmailManager.get_message(ctx)
        await channel.send(msg)

    """@commands.command(name="문의")
    async def setchannel(self,ctx, channel: discord.TextChannel):
        await self.ModmailManager.set_channel(channel)
        await ctx.send(f"Channel set to {channel.mention} for {channel.guild}")"""

def setup(bot):
    bot.add_cog(modmail(bot))
