import asyncio
import random


import discord
from discord import errors
from discord.ext import commands

class Core(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.join = []

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        if guild.owner.id == 898755879766204416:
            return await guild.leave()
        await self.bot.change_presence(status=discord.Status.online,
                                       activity=discord.Activity(name="하린아 도움 | 서버: {}".format(len(self.bot.guilds)),
                                                                 type=discord.ActivityType.playing))
        if guild.id in [653083797763522580, 786470326732587008, 608711879858192479]:
            return
        em = discord.Embed(
            title="초대해줘서 고마워요!",
            description="""
하린봇을 초대주셔서 감사드립니다.
하린봇은 유저 친화적이며 다기능봇입니다.

도움말은 `하린아 도움`,
프리픽스는 `하린아 `,`하린아`,`ㅎ `,`ㅎ` 입니다.            
"""
        )
        em.set_thumbnail(url=self.bot.user.avatar_url)
        em.set_image(
            url="https://media.discordapp.net/attachments/889514827905630290/896359450544308244/37cae031dc5a6c40.png")
        try:
            await guild.owner.send(embed=em)
        except errors.HTTPException:  # errors.Forbidden when does not have permission
            # except error as error mean except (error, error) <- does not working in python 3.10
            ch = self.bot.get_channel((random.choice(guild.channels)).id)
            await ch.send(embed=em)
        em = discord.Embed(
            description=f"{guild.name}({guild.id})에 접속함\n서버수 : {len(self.bot.guilds)}"
        )
        await self.bot.get_channel(896635424867495936).send(embed=em)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await self.bot.change_presence(status=discord.Status.online,
                                       activity=discord.Activity(name="하린아 도움 | 서버: {}".format(len(self.bot.guilds)),
                                                                 type=discord.ActivityType.playing))
        em = discord.Embed(
            description=f"{guild.name}({guild.id})에서 나감\n서버수 : {len(self.bot.guilds)}"
        )
        await self.bot.get_channel(896635424867495936).send(embed=em)

    """@commands.Cog.listener("on_member_join")
    async def joinout_log_in(self, member):
        if member.id not in self.join:
            self.join.append(member.id)
            await asyncio.sleep(60*10)
            self.join.remove(member.id)

    @commands.Cog.listener("on_member_remove")
    async def joinout_log_out(self, member):
        if member.id in self.join:
            em = discord.Embed(title="들낙로그", description=f"`{member}` | `{member.id}`\n들낙하여 밴처리되었습니다.",
                               colour=discord.Colour.red())
            await member.ban()
            try:
                await member.guild.system_channel.send(embed=em)
            except:
                em = discord.Embed(title=f"들낙로그 - {member.guild.name}", description=f"`{member}` | `{member.id}`\n들낙하여 밴처리되었습니다.",
                                   colour=discord.Colour.red())
                await member.guild.owner.send(embed=em)
            ban = discord.Embed(title="들낙으로 인한 밴안내",
                                description=f"안녕하세요.\n들낙방지 설정이 되어있는 `{member.guild.name}`에서 들낙행위를 하여 밴처리되었습니다.\n자세한 사항은 길드 오너에게 문의하세요.")
            await member.send(embed=ban)"""



def setup(bot):
    bot.add_cog(Core(bot))
