from datetime import datetime, timezone

import aiosqlite
import discord
import discordSuperUtils
import pytz
from discord.ext import commands


def ordinal(num: int) -> str:
    """
    Returns the ordinal representation of a number
    Examples:
        11: 11th
        13: 13th
        14: 14th
        3: 3rd
        5: 5th
    :param num:
    :return:
    """

    return (
        f"{num}th"
        if 11 <= (num % 100) <= 13
        else f"{num}{['th', 'st', 'nd', 'rd', 'th'][min(num % 10, 4)]}"
    )


class birthday(commands.Cog,discordSuperUtils.CogManager.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ImageManager = discordSuperUtils.ImageManager()
        self.BirthdayManager = discordSuperUtils.BirthdayManager(bot)
        super().__init__()

    # noinspection DuplicatedCode
    async def cog_before_invoke(self, ctx: commands.Context):
        print(ctx.command)
        if ctx.command.name != '메일':
            database = await aiosqlite.connect("db/db.sqlite")
            cur = await database.execute(
                'SELECT * FROM uncheck WHERE user_id = ?', (ctx.author.id,)
            )

            if await cur.fetchone() is None:
                cur = await database.execute('SELECT * FROM mail')
                mails = await cur.fetchall()
                check = sum(1 for _ in mails)
                mal = discord.Embed(
                    title=f'📫하린봇 메일함 | {check}개 수신됨',
                    description="아직 읽지 않은 메일이 있어요.'`하린아 메일`'로 확인하세요.\n주기적으로 메일함을 확인해주세요! 소소한 업데이트 및 이벤트개최등 여러소식을 확인해보세요.",
                    colour=ctx.author.colour,
                )

                return await ctx.send(embed=mal)
            cur = await database.execute("SELECT * FROM mail")
            mails = await cur.fetchall()
            check = sum(1 for _ in mails)
            cur = await database.execute("SELECT * FROM uncheck WHERE user_id = ?", (ctx.author.id,))
            check2 = await cur.fetchone()
            if str(check) != str(check2[1]):
                mal = discord.Embed(
                    title=f'📫하린봇 메일함 | {int(check) - int(check2[1])}개 수신됨',
                    description="아직 읽지 않은 메일이 있어요.'`하린아 메일`'로 확인하세요.\n주기적으로 메일함을 확인해주세요! 소소한 업데이트 및 이벤트개최등 여러소식을 확인해보세요.",
                    colour=ctx.author.colour,
                )

                await ctx.send(embed=mal)

    @commands.Cog.listener("on_ready")
    async def birthday_on_ready(self):
        database = discordSuperUtils.DatabaseManager.connect(
            await aiosqlite.connect("db/db.sqlite")
        )
        await self.BirthdayManager.connect_to_database(database, ["birthdays"])

    @discordSuperUtils.CogManager.event(discordSuperUtils.BirthdayManager)
    async def on_member_birthday(self, birthday_member):
        # Incase you want to support multiple guilds, you must create a channel system.
        # For example, to create a channel system you can make a "set_birthday_channel" command, and in on_member_birthday,
        # you can fetch the same channel and send birthday updates there.
        # Hard coding the channel ID into your code will work, but only on ONE guild (specifically, where the same channel
        # is located) other guilds wont have the same channel, meaning it wont send them birthday updates.
        # I advise of making a channel system, I do not recommend hard coding channel IDs at all unless you are SURE
        # the channel IDs wont be changed and the bot is not supposed to work on other guilds.
        channels = birthday_member.member.guild.text_channels
        for channel in channels:
            if (
                    channel.topic is not None
                    and str(channel.topic).find("-HOnBtd") != -1
            ):
                channel = birthday_member.member.guild.get_channel(channel.id)
                if channel:
                    embed = discord.Embed(
                        title="생일 축하합니다!! 🥳",
                        description=f"{ordinal(await birthday_member.age())}번째 생일을 축하드립니다!🎉, {birthday_member.member.mention}!",
                        color=0x00FF00,
                    )

                    embed.set_thumbnail(url=birthday_member.member.avatar_url)

                    await channel.send(content=birthday_member.member.mention, embed=embed)

    @commands.command(name="생일목록")
    async def upcoming(self, ctx):
        guild_upcoming = await self.BirthdayManager.get_upcoming(ctx.guild)
        print(guild_upcoming)
        formatted_upcoming = [
            f"멤버: {x.member}, 나이: {await x.age()}, 생일: {(await x.birthday_date()):'%Y %b %d'}"
            for x in guild_upcoming
        ]

        await discordSuperUtils.PageManager(
            ctx,
            discordSuperUtils.generate_embeds(
                formatted_upcoming,
                title="다가오는 생일들",
                fields=25,
                description=f"{ctx.guild}에서 다가오는 생일 목록!",
            ),
        ).run()

    @commands.command(name="생일")
    async def birthday(self, ctx, member: discord.Member = None):
        member = ctx.author if member is None else member
        member_birthday = await self.BirthdayManager.get_birthday(member)

        if not member_birthday:
            await ctx.send("지정한 유저 혹은 명령자님은 생일 등록이 되어있지 않아요!")
            return

        embed = discord.Embed(title=f"{member}님의 생일", color=0x00FF00)

        embed.add_field(
            name="생일",
            value=(await member_birthday.birthday_date()).strftime("%Y %b %d"),
            inline=False,
        )

        embed.add_field(
            name="시간대", value=await member_birthday.timezone(), inline=False
        )

        embed.add_field(name="나이", value=str(await member_birthday.age()), inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="생일삭제")
    async def delete_birthday(self, ctx):
        # You can make the command admin-only, take the member as a parameter etc.
        birthday_member = await self.BirthdayManager.get_birthday(ctx.author)
        if not birthday_member:
            await ctx.send("생일을 등록하지 않으셨어요!")
            return

        birthday_partial = await birthday_member.delete()

        embed = discord.Embed(title=f"{ctx.author}님의 생일을 삭제했어요.", color=0x00FF00)

        embed.add_field(
            name="출생일", value=str(birthday_partial.birthday_date), inline=False
        )
        embed.add_field(name="시간대", value=birthday_partial.timezone, inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="생일등록")
    async def setup_birthday(self, ctx):
        questions = [
            f"{ctx.author.mention}, 태어난 연도는 언제인가요? 예시) 2000",
            f"{ctx.author.mention}, 태어난 달은 언제인가요? 예시) 10",
            f"{ctx.author.mention}, 태어난 일은 언제인가요? 예시) 2",
            f"{ctx.author.mention}, 시간대는 뭔가요? 목록: https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568"
            "\n또는 다음 링크에 접속해서 알아볼 수 있어요.: "
            "http://scratch.andrewl.in/timezone-picker/example_site/openlayers_example.html"
            "\n한국이면 `Asia/Seoul` 입력해주세요!",
        ]
        # BirthdayManager uses pytz to save timezones and not raw UTC offsets, why?
        # well, simply, using UTC offsets will result in a lot of confusion. The user might pass an incorrect UTC offset
        # and he cloud be wished a happy birthday before his birthday. (The UTC offsets might have issues with DST, too!)
        # that's why we chose pytz, to make custom timezones user-friendly and easy to setup.

        answers, timed_out = await discordSuperUtils.questionnaire(
            ctx, questions, member=ctx.author
        )
        # The questionnaire supports embeds.

        if timed_out:
            await ctx.send("시간이 지났어요.")
            return

        for answer in answers[:-1]:
            if not answer.isnumeric():
                await ctx.send("설정이 실패했어요.")
                return

            i = answers.index(answer)
            answers[i] = int(answer)

        if answers[3] not in pytz.all_timezones:
            await ctx.send("설정을 실패했어요, 입력한 시간대를 찾지못했어요.")
            return

        try:
            now = datetime.now(tz=timezone.utc)
            date_of_birth = datetime(*answers[:-1], tzinfo=timezone.utc)
            if date_of_birth > now:
                await ctx.send("설정을 실패했어요. 입력한 달이나 일이 미래에요")
                return
        except ValueError:
            await ctx.send("설정을 실패했어요.")
            return

        member_birthday = await self.BirthdayManager.get_birthday(ctx.author)
        if member_birthday:
            await member_birthday.set_birthday_date(date_of_birth.timestamp())
            await member_birthday.set_timezone(answers[3])
        else:
            await self.BirthdayManager.create_birthday(
                ctx.author, date_of_birth.timestamp(), answers[3]
            )

        await ctx.send(f"성공적으로 생일을 다음과 같이 등록했어요! {date_of_birth:%Y %b %d }.")


def setup(bot):
    bot.add_cog(birthday(bot))
