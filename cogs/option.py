import asyncio
import platform
import random

import aiosqlite
import discord
from discord.ext import commands
from discordSuperUtils import ModMailManager
from discord_components import (
    Select,
    SelectOption, Interaction
)


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.option_dict = {
            "-HOnLv": "레벨링",
            "wlc": "환영인사",
            "ivt": "초대추적",
            "-HOnNt": "공지수신",
            "-HOnBtd": "생일알림",
            "-HOnBdWld": "욕설감지"
            # "-HNoAts":"안티스팸 무시"
        }
        self.option_dict_db = {
            "wlc": "welcome",
            "ivt": "invite_tracker"
        }
        self.ModmailManager = ModMailManager(bot, trigger="-modmail")

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
            cur = await database.execute("SELECT * FROM uncheck WHERE user_id = ?", (ctx.author.id,))
            check2 = await cur.fetchone()
            if str(check) != str(check2[1]):
                mal = discord.Embed(
                    title=f'📫하린봇 메일함 | {int(check) - int(check2[1])}개 수신됨',
                    description="아직 읽지 않은 메일이 있어요.'`하린아 메일`'로 확인하세요.\n주기적으로 메일함을 확인해주세요! 소소한 업데이트 및 이벤트개최등 여러소식을 확인해보세요.",
                    colour=ctx.author.colour,
                )

                await ctx.send(embed=mal)

    async def check_option(self, ctx):
        on_option = []
        topics = str(ctx.channel.topic).split(" ")
        if "-HOnLv" in topics:
            on_option.append(self.option_dict["-HOnLv"] + " <:activ:896255701641474068>")
        if "-HOnBdWld" in topics:
            on_option.append(self.option_dict["-HOnBdWld"] + " <:activ:896255701641474068>")
        channels = ctx.guild.text_channels
        for channel in channels:
            if (
                    channel.topic is not None
                    and str(channel.topic).find("-HOnNt") != -1
            ):
                on_option.append(self.option_dict["-HOnNt"] + f"<#{channel.id}> <:activ:896255701641474068>")
        for channel in channels:
            if (
                    channel.topic is not None
                    and str(channel.topic).find("-HOnBtd") != -1
            ):
                on_option.append(self.option_dict["-HOnBtd"] + f"<#{channel.id}> <:activ:896255701641474068>")
        database = await aiosqlite.connect("db/db.sqlite")
        cur = await database.execute("SELECT * FROM welcome WHERE guild = ?", (ctx.guild.id,))
        data = await cur.fetchone()
        if data is not None:
            on_option.append(self.option_dict["wlc"] + " <:activ:896255701641474068>")
        cur = await database.execute("SELECT * FROM invite_tracker WHERE guild = ?", (ctx.guild.id,))
        data = await cur.fetchone()
        if data is not None:
            on_option.append(self.option_dict["ivt"] + " <:activ:896255701641474068>")
        cur = await database.execute("SELECT * FROM serverstat WHERE guild = ?", (ctx.guild.id,))
        data = await cur.fetchone()
        if data is not None:
            on_option.append("서버스텟 <:activ:896255701641474068>")
        if not on_option:
            return "적용된 옵션이 없어요"
        return "\n".join(on_option)

    @commands.command(name="옵션", aliases=["설정"])
    async def option(self, ctx):
        database = self.bot.db
        check_option = await self.check_option(ctx=ctx)
        #randcode = random.randint(1111,9999)
        msg = await ctx.send("옵션을 확인하거나 셋팅하세요\n\n< 적용된 옵션 >\n" + check_option,
                              components=[
                                  Select(placeholder="옵션",
                                         options=[
                                             SelectOption(label="레벨링",
                                                          description="이 채널을 레벨링전용 채널로 설정해요.",
                                                          value="-HOnLv", emoji="🏆"),
                                             SelectOption(label="환영인사", description="유저가 서버에 입장시 자동으로 인사하는 채널로 설정해요.",
                                                          value="wlc", emoji="👋"),
                                             SelectOption(label="초대추적",
                                                          description="유저가 서버에 입장시 누구의 초대로 서버에 들어왔는지 확인할 수 있는 모드입니다.",
                                                          value="ivt", emoji="📈"),
                                             SelectOption(label="봇공지채널",
                                                          description="이 채널을 봇 공지를 받을수있는 채널로 설정해요.",
                                                          value="-HOnNt", emoji="📢"),
                                             SelectOption(label="생일알림채널",
                                                          description="이 채널을 생일알림 채널로 설정해요.",
                                                          value="-HOnBtd", emoji="🎉"),
                                             SelectOption(label="서버스텟",
                                                          description="서버스텟기능을 사용해요.",
                                                          value="serverstat", emoji="📊"),
                                             SelectOption(label="욕설감지",
                                                          description="이 채널을 욕설감지채널로 설정해요.",
                                                          value="-HOnBdWld", emoji="🤬"),
                                             SelectOption(label="리셋",
                                                          description="적용되어있는 옵션을 리셋합니다.",
                                                          value="reset", emoji="🔄"),
                                             SelectOption(label="취소",
                                                          description="명령어를 취소합니다.",
                                                          value="cancel", emoji="↩")
                                         ],)

                              ],
                              )
        try:
            interaction = await self.bot.wait_for(
                "select_option", check=lambda inter: inter.user.id == ctx.author.id
            )
            value = interaction.values[0]
        except asyncio.TimeoutError:
            await msg.edit("시간이 초과되었어요!", components=[])
            return
        if value == "wlc" or value == "ivt":
            database = await aiosqlite.connect("db/db.sqlite")
            if value == "wlc":
                cur = await database.execute("SELECT * FROM welcome WHERE guild = ?", (ctx.guild.id,))
            else:
                cur = await database.execute("SELECT * FROM invite_tracker WHERE guild = ?", (ctx.guild.id,))
            data = await cur.fetchone()
            print(data)
            if data is not None:
                await msg.edit(f"이미 설정되어있어요!\n설정되어있는 채널 - <#{data[1]}>", components=[])
                return
            await msg.delete()
            msg = await ctx.reply(
                f"{self.option_dict[value]}를 선택하셨어요!\n추가 설정을 위해 아래의 질문에 맞는 값을 보내주세요!\n메세지가 보내질 __채널 ID__를 보내주세요.(ex| 123456789)",
                components=[])
            try:
                message = await self.bot.wait_for("message",
                                                  check=lambda
                                                      i: i.author.id == ctx.author.id and i.channel.id == ctx.channel.id,
                                                  timeout=60)
                message = message.content
            except asyncio.TimeoutError:
                await msg.edit("시간이 초과되었어요!", components=[])
                return
            await msg.edit("저장중이에요!", components=[])
            try:
                await database.execute(f"INSERT INTO {self.option_dict_db[value]}(guild,channel) VALUES (?, ?)",
                                       (ctx.guild.id, int(message)))
                await database.commit()
            except Exception as e:
                await msg.edit("에러가 발생했어요! \n에러내역을 개발자에게 발송하였으니 곧 고쳐질거에요!")
                print(e)
                return
            await msg.edit("저장을 완료했어요!\n채널 - <#{ch}>".format(ch=message), components=[])
        if value == "reset":
            if ctx.channel.topic is not None:
                topics = str(ctx.channel.topic).split(" ")
                values = ["-HOnLv", "-HOnNt","-HOnBdWld"]
                for x in values:
                    try:
                        topics.remove(x)
                    except ValueError:
                        pass
                # print(' '.join(topics))
                res_topic = ' '.join(topics)
                channel = ctx.channel
                if res_topic == '':
                    await channel.edit(topic="")
                else:
                    await channel.edit(topic=str(res_topic))
            # noinspection PyBroadException
            try:
                await database.execute("DELETE FROM welcome WHERE guild = ?", (ctx.guild.id,))
            except Exception as e:
                print(e)
            # noinspection PyBroadException
            try:
                await database.execute("DELETE FROM invite_tracker WHERE guild = ?", (ctx.guild.id,))
            except Exception as e:
                print(e)
            try:
                await database.execute("DELETE FROM serverstat WHERE guild = ?", (ctx.guild.id,))
            except Exception as e:
                print(e)
            await database.commit()
            await msg.edit(content="초기화를 완료했어요!", components=[])
            await asyncio.sleep(3)
            await msg.delete()

        if value == "cancel":
            await msg.delete()
        if value == "-HOnLv" or value == "-HNoAts" or value == "-HOnBdWld":
            try:
                print(value)
                if str(ctx.channel.topic).find(value) != -1:
                    return await msg.edit("이미 설정되어있어요.", components=[])
                topic = value if ctx.channel.topic is None else ctx.channel.topic + " " + value
                await ctx.channel.edit(topic=topic)
                await msg.edit("성공적으로 적용되었어요.", components=[])
            except discord.Forbidden:
                await msg.edit(content='채널 관리 권한이 없어 변경할 수 없어요! 권한을 재설정해주세요!', components=[])
        if value == "-HOnNt":
            channels = ctx.guild.text_channels
            count = []
            for channel in channels:
                if (
                        channel.topic is not None
                        and str(channel.topic).find("-HOnNt") != -1
                ):
                    count.append(channel.id)
                    break
            await self.msg_edit_channel(ctx, msg, count, value)
        if value == "-HOnBtd":
            channels = ctx.guild.text_channels
            count = []
            for channel in channels:
                if (
                        channel.topic is not None
                        and str(channel.topic).find("-HOnBtd") != -1
                ):
                    count.append(channel.id)
                    break
            await self.msg_edit_channel(ctx, msg, count, value)
        if value == "modmail":
            await msg.edit("저장중이에요!", components=[])
            await self.ModmailManager.connect_to_database(self.bot.db, ["modmail"])
            await self.ModmailManager.set_channel(ctx.channel)
            await msg.edit("성공적으로 적용되었어요.", components=[])
        if value == "serverstat":
            database = await aiosqlite.connect("db/db.sqlite")
            await self.setup_serverstat(ctx=ctx, guild=ctx.guild, msg=msg, db=database)

    @commands.command(name="프사")
    async def avatar(self, ctx, member: discord.Member = None):
        member_obj = member or ctx.author
        em = discord.Embed(
            title=f"{member}님의 프로필 사진!",
            description=f"[링크]({member_obj.avatar_url})",
            colour=discord.Colour.random()
        )
        em.set_image(url=member_obj.avatar_url)
        await ctx.reply(embed=em)


    @staticmethod
    async def msg_edit_channel(ctx, msg, count, value):
        if len(count) == 1:
            await msg.edit(f"이미 설정되어있는 채널이 있어요! 채널 - <#{count[0]}>", components=[])
            return
        else:
            topic = value if ctx.channel.topic is None else ctx.channel.topic + " " + value
            await ctx.channel.edit(topic=topic)
            await msg.edit("성공적으로 적용되었어요.", components=[])

    @staticmethod
    async def setup_serverstat(ctx: commands.Context, guild: discord.Guild, msg: discord.Message, db):
        cur = await db.execute("SELECT * FROM serverstat WHERE guild = ?", (ctx.guild.id,))
        data = await cur.fetchone()
        if data is not None:
            return await msg.edit(content="이미 서버스텟기능을 사용중이에요.", components=[])
        category_text = "📊| 서버스텟 |📊"
        all_text = "😶🤖모든인원수-{all}"
        user_text = "😶유저수-{user}"
        bot_text = "🤖봇수-{bots}"
        all_count = len(guild.members)
        user_count = len([m for m in guild.members if not m.bot])
        bot_count = len([m for m in guild.members if m.bot])
        try:
            category = await guild.create_category(name=category_text, position=0)
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(connect=False)
            }
            all_channel = await category.create_voice_channel(name=all_text.format(all=all_count),
                                                              overwrites=overwrites)
            user_channel = await category.create_voice_channel(name=user_text.format(user=user_count),
                                                               overwrites=overwrites)
            bot_channel = await category.create_voice_channel(name=bot_text.format(bots=bot_count),
                                                              overwrites=overwrites)
        except discord.Forbidden:
            return await msg.edit(content="저에게 채널관리 권한이 없어요! 권한을 부여해주세요!", components=[])
        await db.execute("""
        INSERT INTO serverstat(guild,category,all_channel,bot_channel,user_channel,category_text,all_channel_text,bot_channel_text,user_channel_text) VALUES(?,?,?,?,?,?,?,?,?)
        """,
                         (guild.id,
                          category.id,
                          all_channel.id,
                          bot_channel.id,
                          user_channel.id,
                          category_text,
                          all_text,
                          bot_text,
                          user_text))
        await db.commit()
        await msg.edit(content="성공적으로 생성 및 저장하였어요!", components=[])


def setup(bot):
    bot.add_cog(General(bot))
