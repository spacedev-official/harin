import asyncio
import operator
import random
import string
import time
from datetime import datetime
from typing import Union
import aiosqlite
import discord
from discord.ext import commands
from ext.core import  KkutbotContext
from ext.utils import (choose_first_word, get_DU,
                       get_word)
from ext.config import config
from pycord_components import (
    Button,
    ButtonStyle, Interaction, Select, SelectOption
)
class GameBase:
    """Base Game Model for many modes."""

    __slots__ = ("ctx", "score", "begin_time")

    def __init__(self, ctx: KkutbotContext):
        self.ctx = ctx
        self.score = 0
        self.begin_time = time.time()
class SoloGame(GameBase):
    """Game Model for single play mode"""

    __slots__ = ("player", "kkd", "score", "begin_time", "bot_word", "used_words", "ctx")

    def __init__(self, ctx: KkutbotContext, kkd: bool = False):
        super().__init__(ctx)
        self.player = ctx.author
        self.kkd = kkd
        self.bot_word = choose_first_word(special=kkd)
        self.used_words = [self.bot_word]

    async def send_info_embed(self, _msg: Union[discord.Message, KkutbotContext],
                              desc: str = "15초 안에 단어를 이어주세요!") -> discord.Message:
        _embed = discord.Embed(title=f"끝말잇기 솔로 게임",
                               description=f"현재 점수: `{self.score}` 점", color=config('colors.help'))
        _embed.add_field(name="단어", value=f"```yaml\n{self.bot_word} ({' / '.join(get_DU(self.bot_word))})```",
                         inline=False)
        _embed.add_field(name="남은 시간",
                         value=f"`{round((15) - (time.time() - self.begin_time), 1)}` 초",
                         inline=False)
        desc = desc.format(**self.ctx.bot.dict_emojis())
        try:
            return await _msg.reply(desc, embed=_embed,
                                    delete_after=(15 if self.kkd else 10) - (time.time() - self.begin_time))
        except discord.HTTPException as e:
            if e.code == 50035:
                return await self.ctx.send(f"{_msg.author.mention}님, {desc}", embed=_embed,
                                           delete_after=15 - (time.time() - self.begin_time))

    async def game_end(self, result: str):
        mode = 'rank_solo'

        if result == "승리":
            self.score += 10
            points = self.score
            desc = "봇이 대응할 단어를 찾지 못했습니다!"
            color = config('colors.general')
        elif result == "패배":
            points = round(self.score/2)
            desc = f"대답시간이 10초를 초과했습니다..."
            color = config('colors.error')
        elif result == "포기":
            points = round(self.score/3)
            desc = "게임을 포기했습니다."
            color = config('colors.error')
        else:
            raise commands.BadArgument
        db = await aiosqlite.connect("db/db.sqlite")
        cur = await db.execute("SELECT * FROM wordgame WHERE user = ? AND guild = ?",(self.player.id,self.ctx.guild.id))
        res = await cur.fetchone()
        if res is None:
            await db.execute("INSERT INTO wordgame(user,guild,point) VALUES (?,?,?)",(self.player.id,self.ctx.guild.id,points))
            await db.commit()
        else:
            await db.execute("UPDATE wordgame SET point = point + ?, dates = strftime('%Y-%m-%d %H:%M:%S', datetime('now', 'localtime')) WHERE user = ? AND guild = ?",(self.score,self.player.id,self.ctx.guild.id))
            await db.commit()
        embed = discord.Embed(title="게임 결과", description=f"**{result}**  |  {desc}", color=color)
        embed.add_field(name="점수", value=f"`{self.score}` 점")
        embed.add_field(name="보상", value=f"`{points}`")
        if result in ("패배", "포기"):
            possibles = [i for i in get_word(self.bot_word) if i not in self.used_words and (len(i) == 3 if self.kkd else True)]
            if possibles:
                random.shuffle(possibles)
                embed.add_field(name="가능했던 단어", value=f"`{'`, `'.join(possibles[:3])}` 등...", inline=False)
        await self.ctx.send(self.player.mention, embed=embed)
        del self


class MultiGame(GameBase):
    """Game Model for multiple play mode"""

    __slots__ = ("players", "ctx", "msg", "turn", "word", "used_words", "begin_time", "final_score", "score")

    def __init__(self, ctx: KkutbotContext):
        super().__init__(ctx)
        self.players = [ctx.author]
        self.msg = ctx.message
        self.turn = 0
        self.word = choose_first_word()
        self.used_words = [self.word]
        self.final_score = {}

    @property
    def host(self) -> discord.User:
        return self.players[0] if self.players else self.ctx.author

    @property
    def now_player(self) -> discord.User:
        return self.alive[self.turn % len(self.alive)]

    @property
    def alive(self) -> list:
        return [p for p in self.players if p not in self.final_score]

    def hosting_embed(self) -> discord.Embed:
        embed = discord.Embed(title=f"**{self.host}**님의 끝말잇기",
                              description=f"채널: {self.ctx.channel.mention}\n\n"
                                          "`참가` 를 입력하여 게임에 참가하기\n"
                                          "`나가기` 를 입력하여 게임에서 나가기\n"
                                          f"호스트 {self.host.mention} 님은 `시작`이라고 입력해서 게임을 시작할 수 있습니다.",
                              color=config('colors.general'))
        embed.add_field(name=f"플레이어 ({len(self.players)}/5)",
                        value="`" + '`\n`'.join([str(_x) for _x in self.players]) + "`")
        return embed

    async def update_embed(self, embed: discord.Embed):
        try:
            await self.msg.delete()
        except discord.NotFound:
            pass
        except discord.Forbidden:
            pass
        self.msg = await self.msg.channel.send(embed=embed)


    def game_embed(self) -> discord.Embed:
        embed = discord.Embed(title="끝말잇기 멀티플레이", description=f"라운드 **{(self.turn // len(self.alive)) + 1}**  |  차례: {self.now_player.mention}", color=config('colors.help'))
        embed.add_field(name="단어", value=f"```yaml\n{self.word} ({' / '.join(get_DU(self.word))})```")
        embed.add_field(name="누적 점수", value=f"`{self.score}` 점", inline=False)
        embed.add_field(name="플레이어", value=f"`{'`, `'.join([_x.name for _x in self.players if _x not in self.final_score])}`", inline=False)
        if self.final_score:
            embed.add_field(name="탈락자", value=f"`{'`, `'.join([_x.name for _x in self.final_score])}`", inline=False)
        return embed

    async def player_out(self, gg=False):
        embed = discord.Embed(description=f"{self.now_player.mention}님 {'포기' if gg else '탈락'}", color=config('colors.error'))
        possibles = [i for i in get_word(self.word) if i not in self.used_words]
        if possibles:
            random.shuffle(possibles)
            embed.add_field(name="가능했던 단어", value=f"`{'`, `'.join(possibles[:3])}` 등...", inline=False)
        await self.ctx.send(embed=embed)
        self.final_score[self.now_player] = self.score
        self.score += 2
        self.begin_time = time.time()
        self.word = choose_first_word()
        self.used_words.append(self.word)

    async def game_end(self):
        await self.msg.delete()
        desc = []
        self.final_score[self.now_player] = self.score
        self.final_score["zero"] = 0
        rank = sorted(self.final_score.items(), key=operator.itemgetter(1), reverse=True)
        for n, kv in enumerate(rank):
            if n < len(rank) - 1:
                desc.append(f"**{n + 1}** - {kv[0].mention} : +`{int(rank[n + 1][1]) * 2}` {{points}}")
        embed = discord.Embed(title="게임 종료", description="\n".join(desc), color=config('colors.general'))
        await self.ctx.send(embed=embed)
        Game.guild_multi_games.remove(self.ctx.channel.id)
        del self

    async def send_info_embed(self, desc: str = "10초 안에 단어를 이어주세요!") -> discord.Message:
        du_word = get_DU(self.word)
        desc = desc.format(**self.ctx.bot.dict_emojis())
        embed = discord.Embed(
            title=self.word,
            description=f"{round(10 - (time.time() - self.begin_time), 1)}초 안에 `{'` 또는 `'.join(du_word)}` (으)로 시작하는 단어를 이어주세요.",
            color=config('colors.general')
        )
        return await self.msg.channel.send(f"{self.now_player.mention}님, {desc}", embed=embed, delete_after=10 - (time.time() - self.begin_time))









class Game(commands.Cog, name="게임"):
    """끝봇의 메인 기능인 끝말잇기 게임에 대한 카테고리입니다."""

    __slots__ = ("bot", )
    guild_multi_games = []

    def __init__(self, bot):
        self.bot = bot



    @commands.group(name="끝말잇기", aliases=("ㄲ", "끝", "ㄲㅁㅇㄱ"), invoke_without_command=True)
    @commands.bot_has_permissions(add_reactions=True)
    @commands.bot_has_permissions(external_emojis=True)
    @commands.max_concurrency(1, per=commands.BucketType.user)
    async def game(self, ctx: KkutbotContext):
        """
        **1.게임 방법**
        서로 번갈아가며 상대방이 마지막에 제시한 단어의 마지막 글자로 시작하는 단어를 제시합니다.
        이를 계속 반복하다가 어느 한쪽이 단어를 잇지 못하게 되면 상대방의 승리!
        이미 사용한 단어, 한글자 단어, 사전에 없는 단어는 사용 불가능합니다.

        게임 도중에 "ㅈㅈ" 또는 "GG"를 입력하면 게임을 포기할 수 있습니다. (*주의: 포기시 해당 게임은 패배로 처리됩니다.*)
        "ㄲ끝말잇기" 명령어 입력 후 반응을 클릭하는 방식이 아닌, "ㄲ끝말잇기 1" 과 같은 단축 명령어도 지원합니다

        **2.점수 계산 방식**
        승리시 : (상대방과 플레이어가 주고받은 단어의 개수)에 비례해 점수 획득,
        패배, 포기시 : 30점 감점
        자신이 이길 수 있을 때 게임을 승리하여 안전하게 비교적 적은 점수를 획득할지,
        패배하여 점수를 얻지 못할 위험을 무릅쓰고 더 많은 단어를 이을지...
        당신의 선택에 달려있습니다.

        **3.기타**
        단어DB 출처 : 표준국어대사전, 단어수 약 31만개

        **4. 게임모드**
        :one: 솔로 랭킹전
        -끝봇과 끝말잇기 대결을 합니다.

        :two: 서버원들과 친선전
        -같은 서버에 있는 유저들 여러 명과 끝말잇기 대결을 합니다.

        :three: 쿵쿵따
        -끝봇과 끝말잇기 대결을 합니다. 하지만 세글자 단어만 사용 가능합니다.

        3종류의 모드 추가 개발중...
        """
        return await ctx.reply(content="버그패치로 인해 플레이가 불가능합니다.")
        def check(_x: Union[discord.Message, KkutbotContext]) -> bool:
            return _x.author == ctx.author and _x.channel == ctx.channel

        embed = discord.Embed(title="끝말잇기", description="끝말잇기 게임의 모드를 선택해 주세요.\n이 게임은 끝봇의 오픈소스를 사용하였습니다.\n[깃헙](https://github.com/janu8ry/kkutbot)", color=config('colors.general'))
        embed.add_field(name="솔로(🙂 VS 🤖)", value="저와 둘이서 랭크게임을 해요.", inline=False)
        embed.add_field(name="멀티(🙂 VS 🙂)", value="서버원들과 친선게임을 해요.", inline=False)
        mainmsg = await ctx.reply(ctx.author.mention, embed=embed,components=[[Button(label="솔로(🙂 VS 🤖)",custom_id="solo"),Button(label="멀티(🙂 VS 🙂) 고치는중",custom_id="multi",disabled=True)],[Button(emoji="❎",custom_id="cancel")]])

        try:
            interaction = await self.bot.wait_for("button_click",
                                                  check=lambda i: i.user.id == ctx.author.id and i.message.id == mainmsg.id,
                                                  timeout=30)
            name = interaction.custom_id
        except asyncio.TimeoutError:
            await mainmsg.delete()
            return
        msg = ctx.message

        if name == "solo":
            await mainmsg.delete()
            game = SoloGame(ctx)
            await game.send_info_embed(ctx)
            while True:
                try:
                    msg = await self.bot.wait_for('message', check=check, timeout=15.0 - (time.time() - game.begin_time))
                    user_word = msg.content
                except asyncio.TimeoutError:
                    await game.game_end("패배")
                    return
                else:
                    du = get_DU(game.bot_word)
                    if user_word in ("ㅈㅈ", "gg", "GG"):
                        if len(game.used_words) < 10:
                            await game.send_info_embed(msg, "{denyed} 5턴 이상 진행해야 포기할 수 있습니다.")
                            continue
                        else:
                            await game.game_end("포기")
                            return
                    elif user_word in game.used_words:
                        await game.send_info_embed(msg, f"**{user_word}** (은)는 이미 사용한 단어입니다.")
                        continue
                    elif user_word[0] not in du:
                        await game.send_info_embed(msg, f"`{'` 또는 `'.join(du)}` (으)로 시작하는 단어를 입력해 주세요.")
                        continue
                    elif user_word in get_word(game.bot_word):
                        if (game.score == 0) and (len(get_word(user_word)) == 0):
                            await game.send_info_embed(msg, "첫번째 회차에서는 한방단어를 사용할 수 없습니다.")
                            continue
                        elif user_word[0] in du:
                            game.used_words.append(user_word)
                            game.score += 1
                    else:
                        await game.send_info_embed(msg, f"**{user_word}** (은)는 없는 단어입니다.")
                        continue
                final_list = [x for x in get_word(user_word) if x not in game.used_words]
                if len(final_list) == 0:  # noqa
                    await game.game_end("승리")
                    return
                else:
                    game.bot_word = random.choice(final_list)
                    game.used_words.append(game.bot_word)
                    game.begin_time = time.time()
                    game.score += 1
                    await game.send_info_embed(msg)

        if name == "multi":
            if isinstance(ctx.channel, discord.DMChannel):
                raise commands.errors.NoPrivateMessage
            if ctx.channel.id in Game.guild_multi_games:
                raise commands.MaxConcurrencyReached(1, per=commands.BucketType.channel)

            Game.guild_multi_games.append(ctx.channel.id)
            game = MultiGame(ctx)
            await mainmsg.delete()

            while True:
                await game.update_embed(game.hosting_embed())
                try:
                    m = await self.bot.wait_for('message', check=lambda _y: _y.content in (
                    "참가", "나가기", "시작") and _y.channel == ctx.channel, timeout=120.0)
                    if m.content == "참가" and m.author not in game.players:
                        game.players.append(m.author)
                        await ctx.send(f"{m.author.mention} 님이 참가했습니다.")
                        if len(game.players) == 5:
                            await ctx.send(f"최대 인원에 도달하여 {game.host.mention} 님의 게임을 시작합니다.")
                            break

                    if m.content == "나가기" and m.author in game.players:
                        game.players.remove(m.author)
                        await ctx.send(f"{m.author}님이 나갔습니다.")
                        if len(game.players) == 0:
                            await ctx.send(f"플레이어 수가 부족하여 {game.host.mention} 님의 게임을 종료합니다.")
                            Game.guild_multi_games.remove(ctx.channel.id)
                            del game
                            return

                    if m.content == "시작" and game.host == m.author:
                        if len(game.players) < 2:
                            await ctx.send("플레이어 수가 부족하여 게임을 시작할 수 없습니다.")
                        else:
                            await ctx.send(f"{game.host.mention} 님의 게임을 시작합니다.")
                            break

                except asyncio.TimeoutError:
                    if len(game.players) < 2:  # noqa
                        await ctx.send(f"플레이어 수가 부족하여 {game.host.mention} 님의 게임을 종료합니다.")
                        Game.guild_multi_games.remove(ctx.channel.id)
                        del game
                        return
                    else:
                        await ctx.send(f"대기 시간이 초과되어 {game.host.mention} 님의 게임을 시작합니다.")
                        break

            await game.update_embed(game.game_embed())
            game.begin_time = time.time()
            await game.send_info_embed()
            while True:
                try:
                    m = await self.bot.wait_for('message', check=lambda _x: _x.author in game.players and _x.channel == ctx.channel and game.alive[game.turn % len(game.alive)] == _x.author, timeout=10.0 - (time.time() - game.begin_time))
                    user_word = m.content
                except asyncio.TimeoutError:
                    await game.player_out()
                    if len(game.players) - len(game.final_score) == 1:
                        await game.game_end()
                        return
                    else:
                        await game.update_embed(game.game_embed())
                        await game.send_info_embed()

                else:
                    du = get_DU(game.word)
                    if user_word in ("ㅈㅈ", "gg", "GG"):
                        if game.turn < 5:
                            await game.send_info_embed("{denyed} 5턴 이상 진행해야 포기할 수 있습니다.")
                            continue
                        else:
                            await game.player_out(gg=True)
                            if len(game.players) - len(game.final_score) == 1:
                                await game.game_end()
                                return
                            else:
                                await game.update_embed(game.game_embed())
                                await game.send_info_embed()
                    elif user_word in game.used_words:
                        await game.send_info_embed(f"***{user_word}*** (은)는 이미 사용한 단어입니다.")
                        continue
                    elif user_word[0] not in du:
                        await game.send_info_embed(f"`{'` 또는 `'.join(du)}` (으)로 시작하는 단어를 입력 해 주세요.")
                        continue
                    elif user_word in get_word(game.word):
                        if ((game.turn // len(game.alive)) == 0) and (len(get_word(user_word)) == 0):
                            await game.send_info_embed("첫번째 회차에서는 한방단어를 사용할 수 없습니다.")
                            continue
                        elif user_word[0] in du:
                            game.used_words.append(user_word)
                            game.word = user_word
                            game.turn += 1
                            game.score += 1
                            await game.update_embed(game.game_embed())
                            game.begin_time = time.time()
                            await game.send_info_embed()
                    else:
                        await game.send_info_embed(f"**{user_word}** (은)는 없는 단어입니다.")
                        continue

        if name == "cancel":
            await mainmsg.delete()
            return await ctx.send("취소되었습니다.")

    @game.command(name="리더보드")
    async def game_leaderboard(self,ctx):
        db = await aiosqlite.connect("db/db.sqlite")
        cur = await db.execute("SELECT * FROM wordgame WHERE guild = ? ORDER BY point DESC",(ctx.guild.id,))
        res = await cur.fetchall()
        check_list = []
        num = 0
        for i in res:
            num += 1
            check_list.append(f"{num}. {self.bot.get_user(i[0])} | {i[2]}점\n마지막 플레이 일시: {i[3]}")
        leaderboard = "\n\n".join(check_list)
        em = discord.Embed(
            title=f"끝말잇기 리더보드",
            description=f"누가 끝말잇기 고수일까요?```fix\n{leaderboard}```"
        )
        await ctx.reply(embed= em)

    @commands.command(aliases=['마피아'])
    async def mafia(self, ctx):
        #return await ctx.reply("버그패치로 인해 잠시 사용이 불가합니다.")
        global value, pending_customid,until
        try:
            self.data[ctx.channel.id]
        except KeyError:
            pass
        else:
            embed = discord.Embed(title="Mafia", color=0xED4245,
                                   description="이미 이 채널에서 게임이 진행 중입니다.")
            return await ctx.reply(embed=embed)
        start_embed = discord.Embed(title="Mafia", color=0x5865F2,
                                     description="게임을 시작하시겠습니까?")
        start_msg = await ctx.reply(embed=start_embed, components=[Button(label="시작",style=3,custom_id="start"),
                                                                   Button(label="취소",style=4,custom_id="cancel")])
        try:
            interaction:Interaction = await self.bot.wait_for("button_click", check = lambda i: i.user.id == ctx.author.id and i.message.id == start_msg.id,timeout=60)
            value = interaction.custom_id
            print(value)
            if value == "cancel":
                await start_msg.delete()
                embed = discord.Embed(title="Mafia", color=0xED4245,
                                      description="게임을 취소하셨습니다.")
                return await ctx.reply(embed=embed)
        except asyncio.TimeoutError:
            await start_msg.delete()
            embed = discord.Embed(title="Mafia", color=0xED4245,
                                   description="시간이 초과되었습니다. 다시 시도해주세요.")
            return await ctx.reply(embed=embed)




        data = self.data[ctx.channel.id] = {}
        users = data['users'] = []
        data['mafia'], data['police'], data['doctor'], data['citizen'], data['dead'] = [], [], [], [], []
        users.append(ctx.author.id)
        pending_embed = discord.Embed(title="Mafia", color=0x5865F2,
                                      description=f"{ctx.author.mention}님이 마피아 게임을 시작하셨습니다. "
                                                  f"참가를 희망하시는 분은 메시지 하단의 버튼을 클릭해주세요.\n")
        pending_embed.add_field(name="참가자", value=f"`{len(users)}명`")

        async def pending_callback(interaction: Interaction):
            pending_customid = interaction.custom_id
            if pending_customid == "join":
                if interaction.user.id not in users:
                    users.append(interaction.user.id)
                    pending_embed.set_field_at(0, name="참가자", value=f"`{len(users)}명`")
                    await pending_msg.edit(embed=pending_embed)
                    await interaction.respond(content='게임에 참가하셨습니다.', ephemeral=True)

        await start_msg.delete()
        pending_msg = await ctx.send(embed=pending_embed, components=[self.bot.components_manager.add_callback(Button(label="참가하기",style=1,custom_id="join"),pending_callback)])

        now = datetime.timestamp(datetime.now())
        until = now + 60
        await asyncio.sleep(60)
        user_count = len(users)
        if user_count < 4:
            del self.data[ctx.channel.id]
            await pending_msg.delete()
            embed = discord.Embed(title="Mafia", color=0xED4245,
                                  description="인원 수 미달로 게임이 취소되었습니다.")
            return await ctx.reply(embed=embed)

        if user_count >= 24:
            del self.data[ctx.channel.id]
            await pending_msg.delete()
            embed = discord.Embed(title="Mafia", color=0xED4245,
                                  description="인원 수 초과로 게임이 취소되었습니다.")
            return await ctx.reply(embed=embed)
        try:
            thread = await ctx.guild.create_text_channel(name='마피아')
        except discord.Forbidden:
            return await ctx.reply("채널 생성 권한이 없어요! 채널 관리권한을 부여해주세요.")
        await thread.set_permissions(ctx.guild.default_role,read_messages=False)
        for u in users:
            user = self.bot.get_user(u)
            await thread.set_permissions(user, read_messages=True)
        part_embed = discord.Embed(title="Mafia", color=0x5865F2,
                                   description=f"`{len(users)}명`이 게임에 참가합니다."
                                               f"\n참가자: {', '.join([f'<@{u}>' for u in users])}\n\n"
                                               f"잠시 후 게임이 시작됩니다.")
        part_msg = await thread.send(' '.join([f'<@{u}>' for u in users]), embed=part_embed)
        await asyncio.sleep(3)

        async def checkjob_callback(interaction: Interaction):
            embed = discord.Embed(title="Mafia", color=0x5865F2, description="")
            if interaction.user.id in data['doctor']:
                embed.description = "당신은 `의사`입니다. 매일 밤 마피아로부터 죽임을 당하는 시민을 살릴 수 있습니다."
            elif interaction.user.id in data['police']:
                embed.description = "당신은 `경찰`입니다. 매일 밤 선택한 유저가 마피아인지 아닌지를 확인할 수 있습니다."
            elif interaction.user.id in data['mafia']:
                embed.description = "당신은 `마피아`입니다. 매일 밤 한 시민을 살해할 수 있습니다."
            elif interaction.user.id in data['citizen']:
                embed.description = "당신은 `시민`입니다. 건투를 빕니다."
            else:
                embed.description = "당신은 게임 참가자가 아닙니다."
            await interaction.respond(embed=embed, ephemeral=True)
        if user_count == 4:
            self.pick(ctx.channel.id, 1, 1, 0)
        elif user_count == 5:
            self.pick(ctx.channel.id, 1, 1, 1)
        elif user_count in [6, 7]:
            self.pick(ctx.channel.id, 2, 1, 1)
        else:
            self.pick(ctx.channel.id, 3, 1, 1)

        roles_embed = discord.Embed(title="직업이 배정되었습니다.", color=0x5865F2,
                                    description=f"마피아: `{len(data['mafia'])}명`\n"
                                                f"경찰: `{len(data['police'])}명`\n"
                                                f"의사: `{len(data['doctor'])}명`\n"
                                                f"시민: `{len(data['citizen'])}명`\n"
                                                f"\n메시지 하단의 버튼을 눌러 자신의 직업을 확인해주세요.\n"
                                                f"20초 후 1일차 밤이 됩니다.")
        await thread.send(embed=roles_embed, components=[
            self.bot.components_manager.add_callback(Button(label="직업 확인하기", style=1),
                                                     checkjob_callback)])
        await asyncio.sleep(20)
        await thread.purge(limit=None)
        data['mafia-count'] = len(data['mafia'])
        data['day'] = 1
        data['days'] = {}
        data['days'][1] = {'day': {}, 'night': {}}

        while True:
            for u in users:
                user = self.bot.get_user(u)
                await thread.set_permissions(user, send_messages=False,read_messages=True)

            turn_night_embed = discord.Embed(title='Mafia', color=0x5865F2, description=f"밤이 되었습니다.")
            await thread.send(embed=turn_night_embed)
            await asyncio.sleep(0.5)

            if data['day'] == 20:
                del self.data[ctx.channel.id]
                embed = discord.Embed(title="Mafia", color=0xED4245,
                                      description="비정상적으로 게임이 길어져 강제로 종료되었습니다.")
                return await ctx.reply(embed=embed)

            target = data['days'][data['day']]['night']
            target['mafia'], target['police'], target['doctor'], target['died'] = 0, 0, 0, 0
            night = True
            async def select_callback(interaction:Interaction):
                if night is True:
                    user = discord.utils.get(users, name=interaction.values[0])
                    target = self.data['days'][self.data['day']]['night']

                    if interaction.user.id in self.data['mafia']:
                        if target['mafia'] and target['mafia'] != user.id:
                            embed = discord.Embed(title="Mafia", color=0x5865F2,
                                                  description=f"살해대상을 변경하였습니다.")
                            await interaction.respond(embed=embed, ephemeral=True)
                        target['mafia'] = user.id

                    elif interaction.user.id in self.data['doctor']:
                        target['doctor'] = user.id

                    elif interaction.user.id in self.data['police'] and not target['police']:
                        target['police'] = user.id
                        embed = discord.Embed(title="Mafia", color=0x5865F2, description="")
                        if user.id in self.data['mafia']:
                            embed.description = f"{user.mention}님은 마피아입니다."
                        else:
                            embed.description = f"{user.mention}님은 마피아가 아닙니다."
                        await interaction.respond(embed=embed, ephemeral=True)
                    else:
                        embed = discord.Embed(title="Mafia", color=0xED4245, description="이미 능력을 사용하셨습니다.")
                        await interaction.respond(embed=embed, ephemeral=True)
                else:
                    vote = self.data['days'][self.data['day']]['day']
                    embed = discord.Embed(title="Mafia", color=0x5865F2, description="")

                    user = None
                    if interaction.values[0] != '건너뛰기':
                        user = discord.utils.get(users, name=interaction.values[0]).id

                    if interaction.user.id not in vote['voted'] and user:
                        vote['voted'].append(interaction.user.id)
                        vote['votes'][user] += 1
                        embed.description = f"<@{user}>님께 투표하였습니다."
                    elif interaction.user.id not in vote['voted'] and not user:
                        vote['voted'].append(interaction.user.id)
                        vote['votes']['건너뛰기'] += 1
                        embed.description = "투표 건너뛰기에 투표하였습니다."
                    else:
                        embed.description = "이미 투표하셨습니다."
                    await interaction.respond(embed=embed, ephemeral=True)

            async def activate_role(interaction:Interaction):
                users = [self.bot.get_user(u) for u in data['users'] if u not in data['dead']]
                select_options = [Select(options=[SelectOption(label=u.name,value=u.name) for u in users])]
                if night is False:
                    select_options.insert(0, discord.SelectOption(label='건너뛰기'))
                embed = discord.Embed(title="Mafia", color=0x5865F2, description="")
                if interaction.user.id in data['dead']:
                    embed.description = "사망하셨으므로 능력을 사용할 수 없습니다."
                elif interaction.user.id in data['citizen']:
                    embed.description = "당신은 시민이므로 능력이 존재하지 않습니다."
                elif interaction.user.id in data['mafia']:
                    embed.description = "살해할 유저를 선택해주세요."
                    return await interaction.respond(embed=embed, ephemeral=True,
                                                                   components=self.bot.components_manager.add_callback(select_options,select_callback))
                elif interaction.user.id in data['doctor']:
                    embed.description = "살릴 유저를 선택해주세요."
                    return await interaction.respond(embed=embed, ephemeral=True,
                                                                   components=self.bot.components_manager.add_callback(select_options,select_callback))
                elif interaction.user.id in data['police'] and self.data['day'] != 1:
                    embed.description = "조사할 유저를 선택해주세요."
                    return await interaction.respond(embed=embed, ephemeral=True,
                                                                   components=self.bot.components_manager.add_callback(select_options,select_callback))
                else:
                    embed.description = "당신의 능력은 아직 개방되지 않았거나 게임에 참가하지 않으셨습니다."
                await interaction.respond(embed=embed, ephemeral=True)

            night_embed = discord.Embed(title=f"{data['day']}일차 - 밤", color=0x5865F2,
                                        description=f"메시지 하단의 버튼을 눌러 능력을 사용해주세요.\n"
                                                    f"\n30초 후 {data['day'] + 1}일차 낮이 됩니다.")
            night_msg = await thread.send(embed=night_embed, components=[self.bot.components_manager.add_callback(Button(label="능력 사용하기",style=1),activate_role)])
            await asyncio.sleep(30)
            await night_msg.delete()
            data['day'] += 1

            turn_day_embed = discord.Embed(title='Mafia', color=0x5865F2, description=f"낮이 되었습니다.")
            await thread.send(embed=turn_day_embed)
            await asyncio.sleep(0.5)

            dead_embed = discord.Embed(title=f"{data['day']}일차 - 낮", color=0x5865F2, description='')
            if not target['mafia'] or target['doctor'] == target['mafia']:
                dead_embed.description = "아무도 사망하지 않았습니다."
            else:
                target['died'] = target['mafia']
                data['dead'].append(target['mafia'])
                dead_embed.description = f"<@{target['mafia']}>님께서 사망하셨습니다."
            await thread.send(embed=dead_embed)

            check = await self.check_finish(ctx, target['mafia'])
            if check:
                return await self.end(check, data, thread, part_msg)

            data['days'][data['day']] = {'day': {}, 'night': {}}

            for u in data['users']:
                if u in data['dead']:
                    continue
                await thread.set_permissions(self.bot.get_user(u), send_messages=True)

            vote = data['days'][data['day']]['day']
            now = datetime.timestamp(datetime.now())
            until = int(now) + 120
            timecallback_until = until
            time_voted = vote['time-voted'] = []
            #time_view = VoteTime(until, time_voted, data['users'])
            async def time_callback(interaction: Interaction):
                global until,timecallback_until
                if interaction.custom_id == "up":
                    if interaction.user.id not in time_voted and interaction.user.id in data['users']:
                        time_voted.append(interaction.user.id)
                        timecallback_until += 30
                        embed = discord.Embed(title='Mafia', color=0x5865F2,
                                              description=f"{interaction.user.mention}님께서 시간을 증가시켰습니다.")
                        await interaction.respond(embed=embed)
                    else:
                        embed = discord.Embed(title='Mafia', color=0xED4245,
                                              description="이미 시간을 증가시키셨거나 게임에 참가하지 않으셨습니다.")
                        await interaction.respond(embed=embed, ephemeral=True)
                if interaction.custom_id == "down":
                    if interaction.user.id not in time_voted and interaction.user.id in data['users']:
                        time_voted.append(interaction.user.id)
                        timecallback_until -= 30
                        embed = discord.Embed(title='Mafia', color=0x5865F2,
                                              description=f"{interaction.user.mention}님께서 시간을 감소시켰습니다.")
                        await interaction.respond(embed=embed)
                    else:
                        embed = discord.Embed(title='Mafia', color=0xED4245,
                                              description="이미 시간을 감소시키셨거나 게임에 참가하지 않으셨습니다.")
                        await interaction.respond(embed=embed, ephemeral=True)
            time_view = [self.bot.components_manager.add_callback(Button(label="시간증가",custom_id="up",style=1),time_callback),
                         self.bot.components_manager.add_callback(Button(label="시간감소",custom_id="down",style=4),time_callback)]

            day_embed = discord.Embed(title=f"{data['day']}일차 - 낮", color=0x5865F2,
                                      description=f"120초간 자유 토론 시간이 주어집니다.\n"
                                                  f"메시지 하단의 버튼을 눌러 시간을 증가/단축시킬 수 있습니다.")
            day_embed.add_field(name="남은 시간", value=f"<t:{until}:R>")
            day_msg = await thread.send(embed=day_embed, components=time_view)

            while now <= until:
                now = datetime.timestamp(datetime.now())
                if timecallback_until != until:
                    until = timecallback_until
                    day_embed.set_field_at(0, name="남은 시간", value=f"<t:{until}>")
                    await day_msg.edit(embed=day_embed)
                await asyncio.sleep(1)

            await day_msg.delete()

            vote['voted'], vote['votes'], vote['died'] = [], {}, 0
            vote['votes']['건너뛰기'] = len(data['users']) - len(data['dead'])
            for u in [u for u in data['users'] if u not in data['dead']]:
                vote['votes'][u] = 0

            async def vote_callback(interaction:Interaction):
                global night
                users = [self.bot.get_user(u) for u in data['users'] if u not in data['dead']]
                select_options = [Select(options=[SelectOption(label=u.name, value=u.name) for u in users])]
                if interaction.user.id in data['dead']:
                    embed = discord.Embed(title="Mafia", color=0xED4245, description="사망하셨으므로 투표할 수 없습니다.")
                    await interaction.respond(embed=embed, ephemeral=True)
                elif interaction.user.id not in data['users']:
                    embed = discord.Embed(title="Mafia", color=0xED4245, description="게임에 참가하지 않으셨으므로 투표할 수 없습니다.")
                    await interaction.respond(embed=embed, ephemeral=True)
                embed = discord.Embed(title="Mafia", color=0x5865F2, description="투표로 죽일 유저를 선택해주세요.")
                night = False
                await interaction.respond(embed=embed, ephemeral=True,
                                                               components=self.bot.components_manager.add_callback(select_options,select_callback))
            vote_embed = discord.Embed(title=f"{data['day']}일차 - 투표", color=0x5865F2,
                                       description=f"30초 동안 투표로 죽일 사람을 선택해주세요.")
            await thread.send(embed=vote_embed, components=self.bot.components_manager.add_callback(Button(label="투표하기",style=1),vote_callback))
            await asyncio.sleep(30)

            for v in vote['voted']:
                vote['votes']['건너뛰기'] -= 1

            await thread.purge(limit=None)
            total = sorted(vote['votes'].items(), key=lambda k: k[1], reverse=True)
            vote_result = ''
            for t in total:
                name = t[0]
                if t[0] != '건너뛰기':
                    name = f'<@{t[0]}>'
                vote_result += f'{name}: `{t[1]}표`\n'

            vote_result_embed = discord.Embed(title=f"{data['day']}일차 - 투표 결과", color=0x5865F2, description='')
            if total[0][1] == total[1][1] or total[0][0] == '건너뛰기':
                vote_result_embed.description = "아무도 사망하지 않았습니다."
            else:
                vote['died'] = total[0][0]
                data['dead'].append(total[0][0])
                vote_result_embed.description = f"<@{total[0][0]}>님께서 사망하셨습니다."
            vote_result_embed.add_field(name="투표 결과", value=vote_result)
            await thread.send(embed=vote_result_embed)

            check = await self.check_finish(ctx, total[0][0])
            if check:
                return await self.end(check, data, thread, part_msg)
        if ctx.guild.id != 847729860881154078:
            return await ctx.reply("버그패치로 인해 잠시 사용이 불가합니다.")
        await Mafia(bot=self.bot,ctx=ctx,channel=ctx.channel).start()



def setup(bot):
    bot.add_cog(Game(bot))
