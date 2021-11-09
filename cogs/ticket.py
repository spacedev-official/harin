import asyncio
import datetime
import random
import io
import chat_exporter
import aiosqlite
import discord
from discord import errors
from discord.ext import commands
from pycord_components import (
    Button,
    ButtonStyle,
    Interaction
)
import html
class badword(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ticket_channel = []
        self.ticket_msg = []
        self.ticket_opentime = {}
        chat_exporter.init_exporter(self.bot)


    @commands.command(name="티켓설정")
    async def create_ticket_set(self,ctx,channel:discord.TextChannel,role:discord.Role,*,text):
        em = discord.Embed(description=text,colour=discord.Colour.random())
        msg = await channel.send(embed=em,components=[
                                            [
                                                Button(label="📩 티켓 열기",custom_id="ticket_open")
                                            ]
                                         ])
        new_category = await ctx.guild.create_category(name="🎫-티켓")
        db = await aiosqlite.connect('db/db.sqlite')
        await db.execute("INSERT INTO ticket(guild,channel,message,category,role) VALUES (?,?,?,?,?)",
                         (ctx.guild.id,channel.id,msg.id,new_category.id,role.id))
        await db.commit()
        await ctx.reply("설정이 완료되었어요!")

    @commands.command(name="티켓삭제")
    async def create_ticket_delete(self, ctx, channel:discord.TextChannel,msg: int):
        await (await channel.fetch_message(msg)).delete()
        db = await aiosqlite.connect('db/db.sqlite')
        await db.execute("DELETE FROM ticket WHERE message = ?",
                         (msg,))
        await db.commit()
        await ctx.reply("티켓이 삭제되었어요!")


    @commands.Cog.listener('on_button_click')
    async def ticket_create(self,interaction:Interaction):
        custom_id = interaction.custom_id
        message_id = interaction.message.id
        channel_id = interaction.channel_id
        guild_id = interaction.guild_id
        if custom_id == "ticket_open":
            db = await aiosqlite.connect('db/db.sqlite')
            cur = await db.execute("SELECT * FROM ticket WHERE guild = ? AND channel = ? AND message = ?",
                                   ((guild_id,channel_id,message_id)))
            res = await cur.fetchone()
            if not res is None:
                guild = self.bot.get_guild(guild_id)
                member = discord.utils.find(lambda m: m.id == interaction.user.id, guild.members)
                support_role = guild.get_role(res[4])
                get_category = self.bot.get_channel(res[3])
                overwrites = {
                    member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                    support_role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                }
                channel = await get_category.create_text_channel(name="티켓 - " + member.display_name,overwrites=overwrites,topic=f"{res[4]} {member.id}")
                await channel.set_permissions(guild.default_role,read_messages=False)
                await interaction.send(content=f"티켓이 생성되었어요!\n아래 채널로 이동해주세요!\n생성된 티켓 - {channel.mention}",delete_after=5)
                self.ticket_channel.append(channel.id)
                now = datetime.datetime.now()
                year = now.year
                month = now.month
                date = now.day
                hour = now.hour
                minute = now.minute
                second = now.second
                open_time = f"{year}년 {month}월 {date}일 {hour}시 {minute}분 {second}초"
                self.ticket_opentime[channel.id] = open_time
                embed = discord.Embed(title="무엇을 도와드릴까요?",
                                      description=f"```fix\n티켓 개설일시: {open_time}\n티켓 개설 요청자: {member}({member.id})```",
                                      color=0xf7fcfd)
                embed.add_field(name="🔒 티켓 잠금",
                                value="```현재 티켓을 잠궈요.```",
                                inline=False)
                embed.add_field(name="🖨 티켓 추출",
                                value="```티켓에서 오간 채팅내용을 추출해요.```",
                                inline=False)
                embed.add_field(name="❌ 티켓 종료",
                                value="```현재 티켓을 종료하고 채널을 삭제해요.```",
                                inline=False)

                msg = await channel.send(content=f"{support_role.mention}\n{member.mention}",
                                         embed=embed,
                                         components=[
                                            [
                                                Button(label="🔒 티켓 잠금",custom_id="ticket_lock",style=4),
                                                Button(label="🖨 티켓 추출",custom_id="ticket_export",style=3),
                                                Button(label="❌ 티켓 종료",custom_id="ticket_cancel",style=4)
                                            ]
                                         ])
                self.ticket_msg.append(msg.id)
        if custom_id == "ticket_lock":
            if message_id in self.ticket_msg:
                guild = self.bot.get_guild(guild_id)
                channel = self.bot.get_channel(channel_id)
                message = await channel.fetch_message(message_id)
                member = discord.utils.find(lambda m: m.id == interaction.user.id, guild.members)
                if not int(channel.topic.split(" ")[0]) in [r.id for r in member.roles]:
                    return await interaction.respond(content="지원팀만 사용할 수 있어요!")
                await interaction.respond(content=f"티켓잠금요청을 하셨어요!")
                open_time = self.ticket_opentime[channel.id]
                member = discord.utils.find(lambda m: m.id == int(channel.topic.split(" ")[1]), guild.members)
                await channel.set_permissions(member,read_messages=True,send_messages=False)
                embed = discord.Embed(title="무엇을 도와드릴까요?",
                                      description=f"```fix\n티켓 개설일시: {open_time}\n티켓 개설 요청자: {member}({member.id})```",
                                      color=0xf7fcfd)
                embed.add_field(name="🔓 티켓 잠금해제",
                                value="```현재 티켓을 잠금해제요.```",
                                inline=False)
                embed.add_field(name="🖨 티켓 추출",
                                value="```티켓에서 오간 채팅내용을 추출해요.```",
                                inline=False)
                embed.add_field(name="❌ 티켓 종료",
                                value="```현재 티켓을 종료하고 채널을 삭제해요.```",
                                inline=False)
                em = discord.Embed(description="🔒 현재 이 티켓은 잠겨있는 상태입니다.", colour=discord.Colour.red())
                await channel.send(embed=em)
                await message.edit(embed=embed,
                                 components=[
                                    [
                                        Button(label="🔓 티켓 잠금해제",custom_id="ticket_unlock",style=4),
                                        Button(label="🖨 티켓 추출",custom_id="ticket_export",style=3),
                                        Button(label="❌ 티켓 종료",custom_id="ticket_cancel",style=4)
                                    ]
                                 ])
        if custom_id == "ticket_unlock":
            if message_id in self.ticket_msg:
                guild = self.bot.get_guild(guild_id)
                channel = self.bot.get_channel(channel_id)
                message = await channel.fetch_message(message_id)
                member = discord.utils.find(lambda m: m.id == interaction.user.id, guild.members)
                if not int(channel.topic.split(" ")[0]) in [r.id for r in member.roles]:
                    return await interaction.respond(content="지원팀만 사용할 수 있어요!")
                await interaction.respond(content=f"티켓잠금해제요청을 하셨어요!")
                open_time = self.ticket_opentime[channel.id]
                member = discord.utils.find(lambda m: m.id == int(channel.topic.split(" ")[1]), guild.members)
                await channel.set_permissions(member,read_messages=True,send_messages=True)
                embed = discord.Embed(title="무엇을 도와드릴까요?",
                                      description=f"```fix\n티켓 개설일시: {open_time}\n티켓 개설 요청자: {member}({member.id})```",
                                      color=0xf7fcfd)
                embed.add_field(name="🔒 티켓 잠금",
                                value="```현재 티켓을 잠궈요.```",
                                inline=False)
                embed.add_field(name="🖨 티켓 추출",
                                value="```티켓에서 오간 채팅내용을 추출해요.```",
                                inline=False)
                embed.add_field(name="❌ 티켓 종료",
                                value="```현재 티켓을 종료하고 채널을 삭제해요.```",
                                inline=False)
                em = discord.Embed(description="🔓 티켓이 다시 열렸어요!", colour=discord.Colour.red())
                await channel.send(embed=em)
                await message.edit(embed=embed,
                                 components=[
                                    [
                                        Button(label="🔒 티켓 잠금",custom_id="ticket_lock",style=4),
                                        Button(label="🖨 티켓 추출",custom_id="ticket_export",style=3),
                                        Button(label="❌ 티켓 종료",custom_id="ticket_cancel",style=4)
                                    ]
                                 ])
        if custom_id == "ticket_export":
            if message_id in self.ticket_msg:
                channel = self.bot.get_channel(channel_id)
                transcript = await chat_exporter.export(channel,set_timezone="Asia/Seoul")

                if transcript is None:
                    return
                transcript_file = discord.File(io.BytesIO(transcript.encode()),
                                               filename=f"ticket-{channel.id}.html")

                await interaction.send(content="추출이 완료되었어요! \n아래 파일을 다운받아 브라우저에서 열어주세요!",file=transcript_file)
        if custom_id == "ticket_cancel":
            if message_id in self.ticket_msg:
                channel = self.bot.get_channel(channel_id)
                await interaction.respond(content=f"❌ 티켓 종료 요청을 하셨어요!\n잠시후 채널이 삭제됩니다.")
                em = discord.Embed(description="❌ 티켓 종료 요청을 하셨어요!\n잠시후 채널이 삭제됩니다.",colour=discord.Colour.red())
                await channel.send(embed=em)
                await asyncio.sleep(5)
                self.ticket_channel.remove(channel.id)
                self.ticket_msg.remove(message_id)
                del self.ticket_opentime[channel_id]
                await channel.delete()


def setup(bot):
    bot.add_cog(badword(bot))
