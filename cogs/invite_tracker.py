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
        if ctx.command.name != 'λ©μΌ':
            database = await aiosqlite.connect("db/db.sqlite")
            cur = await database.execute(
                'SELECT * FROM uncheck WHERE user_id = ?', (ctx.author.id,)
            )

            if await cur.fetchone() is None:
                cur = await database.execute("SELECT * FROM mail")
                mails = await cur.fetchall()
                check = sum(1 for _ in mails)
                mal = discord.Embed(
                    title=f'π«νλ¦°λ΄ λ©μΌν¨ | {check}κ° μμ λ¨',
                    description="μμ§ μ½μ§ μμ λ©μΌμ΄ μμ΄μ.'`νλ¦°μ λ©μΌ`'λ‘ νμΈνμΈμ.\nμ£ΌκΈ°μ μΌλ‘ λ©μΌν¨μ νμΈν΄μ£ΌμΈμ! μμν μλ°μ΄νΈ λ° μ΄λ²€νΈκ°μ΅λ± μ¬λ¬μμμ νμΈν΄λ³΄μΈμ.",
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
                    title=f'π«νλ¦°λ΄ λ©μΌν¨ | {int(check) - int(check2[1])}κ° μμ λ¨',
                    description="μμ§ μ½μ§ μμ λ©μΌμ΄ μμ΄μ.'`νλ¦°μ λ©μΌ`'λ‘ νμΈνμΈμ.\nμ£ΌκΈ°μ μΌλ‘ λ©μΌν¨μ νμΈν΄μ£ΌμΈμ! μμν μλ°μ΄νΈ λ° μ΄λ²€νΈκ°μ΅λ± μ¬λ¬μμμ νμΈν΄λ³΄μΈμ.",
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
                f"{member.mention}λμ {inviter.display_name if inviter else 'μμμλ μ¬μ©μ'}λμ μ΄λλ‘ μ€μ¨μ΄μ! μ½λ - {invite.code}"
            )

    @commands.command(name="μ΄λμ λ³΄")
    async def info(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        invited_members = await self.InviteTracker.get_user_info(member).get_invited_users()

        await ctx.send(
            f"{member.mention}λμ΄ μ΄λν λ©€λ²λ€({len(invited_members)}λͺ): "
            + ", ".join(str(x) for x in invited_members)
        )


def setup(bot):
    bot.add_cog(InviteTracker(bot))
