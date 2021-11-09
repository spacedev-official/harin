import aiosqlite
import discord
from discord.ext import commands
from pycord_components import (
    Button,
    ButtonStyle,
    Interaction
)
class whitegate(commands.Cog):
    def __init__(self, bot:commands.Bot):
        super().__init__()
        self.bot = bot

    @commands.command(name="setup")
    async def gate_setup(self, ctx:commands.Context, guild:int, channel:int):
        db = await aiosqlite.connect("db/db.sqlite")
        cur = await db.execute("SELECT * FROM whitegate WHERE guild = ? AND target_channel = ?",(ctx.guild.id,channel))
        res = await cur.fetchone()
        if res != None:
            return await ctx.reply("이미 설정되어있어요!")
        try:
            await ctx.message.delete()
        except:
            pass
        guild = await self.bot.fetch_guild(guild)
        em = discord.Embed(
            title=f"{guild.name}에 접속하기!",
            description='아래 접속 버튼을 쿨릭해 생성된 초대링크로 접속하여주세요!',
            colour=discord.Colour.random()
        )
        em.set_thumbnail(url=guild.icon_url)
        msg = await ctx.send(embed=em,components=[
            Button(label="접속하기",custom_id=str(channel))
        ])
        await db.execute("INSERT INTO whitegate(guild, channel,message,target_channel) VALUES (?,?,?,?)",(ctx.guild.id,ctx.channel.id,msg.id,channel))
        await db.commit()
        await ctx.send("✅",delete_after=3)

    @commands.command(name="edit")
    async def gate_edit(self, ctx:commands.Context, guild:int, channel:int):
        db = await aiosqlite.connect("db/db.sqlite")
        cur = await db.execute("SELECT * FROM whitegate WHERE guild = ? AND target_channel = ?",
                               (ctx.guild.id, channel))
        res = await cur.fetchone()
        if res is None:
            return await ctx.reply("설정되어있지 않아요.")
        try:
            await ctx.message.delete()
        except:
            pass
        guild = await self.bot.fetch_guild(guild)
        em = discord.Embed(
            title=f"{guild.name}에 접속하기!",
            description='아래 접속 버튼을 클릭해 생성된 초대링크로 접속하여주세요!',
            colour=discord.Colour.random()
        )
        em.set_thumbnail(url=guild.icon_url)
        msg = await self.bot.get_channel(ctx.channel.id).fetch_message(res[2])
        await msg.edit(embed=em,components=[
            Button(label="접속하기",custom_id=str(channel))
        ])
        await db.execute("UPDATE whitegate SET target_channel = ? WHERE guild = ?",(ctx.guild.id,))
        await db.commit()
        await ctx.send("✅", delete_after=3)

    @commands.command(name="delete")
    async def gate_delete(self, ctx:commands.Context, channel:int):
        db = await aiosqlite.connect("db/db.sqlite")
        cur = await db.execute("SELECT * FROM whitegate WHERE guild = ? AND target_channel = ?",
                               (ctx.guild.id, channel))
        res = await cur.fetchone()
        if res is None:
            return await ctx.reply("설정되어있지 않아요.")
        try:
            await ctx.message.delete()
        except:
            pass
        msg = await self.bot.get_channel(ctx.channel.id).fetch_message(res[2])
        await msg.delete()
        await db.execute("DELETE FROM whitegate WHERE guild = ? AND target_channel = ?", (ctx.guild.id,channel))
        await db.commit()
        await ctx.send("✅", delete_after=3)

    @commands.Cog.listener('on_button_click')
    async def gate_create(self, interaction: Interaction):
        db = await aiosqlite.connect("db/db.sqlite")
        custom_id = interaction.custom_id
        message_id = interaction.message.id
        channel_id = interaction.channel_id
        guild_id = interaction.guild_id
        if custom_id not in ["ticket_open","ticket_lock","ticket_unlock","ticket_export","ticket_cancel"]:
            cur = await db.execute("SELECT * FROM whitegate WHERE guild = ? AND channel = ? AND message = ?",
                                   (guild_id, channel_id, message_id))
            res = await cur.fetchone()
            if res != None:
                channel:discord.TextChannel = await self.bot.fetch_channel(res[3])
                invite_url = await channel.create_invite(max_uses=1,max_age=10)
                print(invite_url)
                await interaction.respond(content=f"초대링크가 생성되었어요! 이 초대링크는 __한번만 사용가능하며 10초뒤 만료됩니다__!",components=[Button(label="들어가기!",style=5,url=str(invite_url))])




def setup(bot):
    bot.add_cog(whitegate(bot))
