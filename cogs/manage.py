import aiosqlite
import discord
import discordSuperUtils
from PycordPaginator import Paginator
from discord.ext import commands


class Manage(commands.Cog,discordSuperUtils.CogManager.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.InfractionManager = discordSuperUtils.InfractionManager(bot)
        self.BanManager = discordSuperUtils.BanManager(bot)
        self.KickManager = discordSuperUtils.KickManager(bot)
        self.MuteManager = discordSuperUtils.MuteManager(bot)

        self.InfractionManager.add_punishments(
            [
                discordSuperUtils.Punishment(self.KickManager, punish_after=4),
                discordSuperUtils.Punishment(self.MuteManager, punish_after=2),
                discordSuperUtils.Punishment(self.BanManager, punish_after=5),
            ]
        )
        super().__init__()

    @commands.Cog.listener("on_ready")
    async def mn_on_ready(self):
        database = discordSuperUtils.DatabaseManager.connect(
            await aiosqlite.connect("db/db.sqlite")
        )
        await self.InfractionManager.connect_to_database(database, ["infractions"])
        await self.BanManager.connect_to_database(database, ["bans"])
        await self.MuteManager.connect_to_database(database, ["mutes"])

    @staticmethod
    async def make_infraction_embed(member_infractions, member) -> list:
        return discordSuperUtils.generate_embeds(
            [
                f"**사유: **{await infraction.reason()}\n"
                f"**처리ID: **{infraction.infraction_id}\n"
                f"**처벌일자: **{await infraction.datetime()}"
                for infraction in member_infractions
            ],
            title=f"{member}의 처벌목록",
            fields=25,
            description=f"{member}의 처벌목록"
        )

    @commands.command(name="뮤트")
    @commands.has_permissions(administrator=True)
    async def mute(
            self,
            ctx,
            member: discord.Member,
            time_of_mute: discordSuperUtils.TimeConvertor,
            *,
            reason: str = "No reason specified.",
    ):
        try:
            await self.MuteManager.mute(member, reason, time_of_mute)
        except discordSuperUtils.AlreadyMuted:
            await ctx.send(f"{member}님은 이미 뮤트되어있어요.")
        else:
            await ctx.send(f"{member}님은 뮤트되었어요. 뮤트 사유: {reason}")

    @commands.command(name="언뮤트")
    @commands.has_permissions(administrator=True)
    async def unmute(self, ctx, member: discord.Member):
        if await self.MuteManager.unmute(member):
            await ctx.send(f"{member.mention}님이 언뮤트되었어요.")
        else:
            await ctx.send(f"{member.mention}은 뮤트되어있지 않아요!")

    @commands.command(name="밴")
    @commands.has_permissions(administrator=True)
    async def ban(
            self,
            ctx,
            member: discord.Member,
            time_of_ban: discordSuperUtils.TimeConvertor,
            *,
            reason: str = "No reason specified.",
    ):
        await ctx.send(f"{member}님이 밴되셨어요. 사유: {reason}")
        await self.BanManager.ban(member, reason, time_of_ban)

    @commands.command(name="언밴")
    @commands.has_permissions(administrator=True)
    async def unban(self, ctx, user: discord.User):
        if await self.BanManager.unban(user, guild=ctx.guild):
            await ctx.send(f"{user}님은 언밴되셨어요.")
        else:
            await ctx.send(f"{user}은 밴되어있지않아요.")

    @commands.group(name="처벌", invoke_without_command=True)
    async def infractions(self, ctx, member: discord.Member):
        member_infractions = await self.InfractionManager.get_infractions(member)
        embeds = await self.make_infraction_embed(member_infractions, member)
        print(embeds)
        e = Paginator(
            client=self.bot.components_manager,
            embeds=embeds,
            channel=ctx.channel,
            only=ctx.author,
            ctx=ctx)
        await e.start()

    @infractions.command(name="추가")
    @commands.has_permissions(administrator=True)
    async def add(self, ctx, member: discord.Member, *,reason: str = "No reason specified."):
        infraction = await self.InfractionManager.warn(ctx, member, reason)

        embed = discord.Embed(title=f"{member} has been warned.", color=0x00FF00)

        embed.add_field(name="Reason", value=await infraction.reason(), inline=False)
        embed.add_field(name="Infraction ID", value=infraction.id, inline=False)
        embed.add_field(
            name="Date of Infraction", value=str(await infraction.datetime()), inline=False
        )
        # Incase you don't like the Date of Infraction format you can change it using datetime.strftime

        await ctx.send(embed=embed)

    @infractions.command(name="조회")
    async def get(self, ctx, member: discord.Member, infraction_id: str):
        infractions_found = await self.InfractionManager.get_infractions(
            member, infraction_id=infraction_id
        )

        if not infractions_found:
            await ctx.send(
                f"다음 처리ID `{infraction_id}`를 가진 데이터를 찾을 수 없어요. "
            )
            return

        infraction = infractions_found[0]

        embed = discord.Embed(
            title=f"Infraction found on {member}'s account!", color=0x00FF00
        )

        embed.add_field(name="Reason", value=await infraction.reason(), inline=False)
        embed.add_field(name="Infraction ID", value=infraction.id, inline=False)
        embed.add_field(
            name="Date of Infraction", value=str(await infraction.datetime()), inline=False
        )
        # Incase you don't like the Date of Infraction format you can change it using datetime.strftime

        await ctx.send(embed=embed)

    @infractions.command(name="제거", aliases=["삭제", "취소"])
    @commands.has_permissions(administrator=True)
    async def remove(self, ctx, member: discord.Member, infraction_id: str):
        infractions_found = await self.InfractionManager.get_infractions(
            member, infraction_id=infraction_id
        )

        if not infractions_found:
            await ctx.send(
                f"다음 처리ID `{infraction_id}`를 가진 데이터를 찾을 수 없어요. "
            )
            return

        removed_infraction = await infractions_found[0].delete()

        embed = discord.Embed(
            title=f"{member}로부터 처벌이 최소되었습니다!", color=0x00FF00
        )

        embed.add_field(name="사유", value=removed_infraction.reason, inline=False)
        embed.add_field(
            name="처벌 ID", value=removed_infraction.id, inline=False
        )
        embed.add_field(
            name="처벌 일시",
            value=str(removed_infraction.date_of_infraction),
            inline=False,
        )

        await ctx.send(embed=embed)

    @commands.command(name="청소")
    @commands.has_permissions(administrator=True)
    async def channel_purge(self, ctx, limit: int):
        if limit <= 99:
            await ctx.channel.purge(limit=limit)
            await ctx.send(f"`{limit}`개의 메세지를 지웠어요.", delete_after=5)
        else:
            await ctx.reply('99개 이하의 수를 입력해주세요')

    @commands.command(name="서버공지")
    @commands.has_permissions(administrator=True)
    async def notice_server(self, ctx, channel: discord.TextChannel, *, value):
        em = discord.Embed(
            title=f"{ctx.guild}공지사항",
            description=value,
            colour=discord.Colour.random()
        )
        em.set_footer(text="이 공지는 하린봇과 무관한 서버별 공지기능입니다.")
        await channel.send(embed=em)
        await ctx.message.add_reaction("✅")

    @commands.group(name="출퇴", invoke_without_command=True)
    async def chulgeun(self,ctx):
        await ctx.send("관리자의 출퇴근 상태를 알려주는 기능입니다.")

    @chulgeun.command(name="등록")
    @commands.has_permissions(administrator=True)
    async def chulgeun_add(self,ctx,member:discord.Member):
        db = await aiosqlite.connect("db/db.sqlite")
        cur = await db.execute("SELECT * FROM chulgeun WHERE guild = ? AND user = ?",(ctx.guild.id,member.id))
        res = await cur.fetchone()
        if res is not None:
            return await ctx.reply(f"{member.mention}님은 이미 등록이 되어있어요!")
        category = await ctx.guild.create_category(name="관리자 출퇴근 상태", position=0)
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(connect=False,send_messages=False)
        }
        all_channel = await category.create_voice_channel(name="현재 출근한 관리자: 0명",
                                                          overwrites=overwrites)
        await db.execute("INSERT INTO chulgeun(guild, user, category, channel, yn, stime) VALUES (?, ?, ?, ?, ?,?)",
                         ())


    """@staticmethod
    async def make_infraction_infoembed_and_send(ctx, infraction, member):
        embed = discord.Embed(title=f"{member}님이 경고를 받으셨어요.", color=0x00FF00)

        embed.add_field(name="사유", value=await infraction.reason(), inline=False)
        embed.add_field(name="처리ID", value=infraction.id, inline=False)
        embed.add_field(
            name="처리 일시", value=str(await infraction.datetime()), inline=False
        )
        # Incase you don't like the Date of Infraction format you can change it using datetime.strftime

        await ctx.send(embed=embed)


    @staticmethod
    async def make_infraction_embed_and_send(ctx, infraction, member):
        embed = discord.Embed(title=f"{member}님이 경고를 받으셨어요.", color=0x00FF00)

        embed.add_field(name="사유", value=await infraction.reason(), inline=False)
        embed.add_field(name="처리ID", value=infraction.id, inline=False)
        embed.add_field(
            name="처리 일시", value=str(await infraction.datetime()), inline=False
        )
        # Incase you don't like the Date of Infraction format you can change it using datetime.strftime

        await ctx.send(embed=embed)"""


def setup(bot):
    bot.add_cog(Manage(bot))
