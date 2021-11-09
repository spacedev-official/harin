import aiosqlite
import discord
import discordSuperUtils
from discord.ext import commands


class InviteTracker(commands.Cog,discordSuperUtils.CogManager.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.ImageManager = discordSuperUtils.ImageManager()
        self.InviteTracker = discordSuperUtils.InviteTracker(bot)

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

    @commands.Cog.listener("on_ready")
    async def ivt_on_ready(self):
        database = discordSuperUtils.DatabaseManager.connect(
            await aiosqlite.connect("db/db.sqlite")
        )
        await self.InviteTracker.connect_to_database(database, ["invites"])

    @commands.Cog.listener("on_member_join")
    async def invite_tracker(self, member):
        database_one = await aiosqlite.connect("db/db.sqlite")
        cur = await database_one.execute("SELECT * FROM invite_tracker WHERE guild = ?", (member.guild.id,))
        data = await cur.fetchone()
        if data is not None:
            invite = await self.InviteTracker.get_invite(member)
            inviter = await self.InviteTracker.fetch_inviter(invite)
            await self.InviteTracker.register_invite(invite, member, inviter)

            channel = self.bot.get_channel(data[1])
            await channel.send(
                f"{member.mention}님은 {inviter.display_name if inviter else '알수없는 사용자'}님의 초대로 오셨어요! 코드 - {invite.code}"
            )

    @commands.command(name="초대정보")
    async def info(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        invited_members = await self.InviteTracker.get_user_info(member).get_invited_users()

        await ctx.send(
            f"{member.mention}님이 초대한 멤버들({len(invited_members)}명): "
            + ", ".join(str(x) for x in invited_members)
        )


def setup(bot):
    bot.add_cog(InviteTracker(bot))
