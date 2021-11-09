import datetime
import time
from typing import Optional

import aiosqlite
import discord
import discordSuperUtils
from discord.ext import commands
from discordSuperUtils import MusicManager


# Format duration
def parse_duration(duration: Optional[float]) -> str:
    return (
        time.strftime("%H:%M:%S", time.gmtime(duration))
        if duration != "LIVE"
        else duration
    )


# Format view count
# noinspection DuplicatedCode
def parse_count(count):
    original_count = count

    count = float("{:.3g}".format(count))
    magnitude = 0
    matches = ["", "K", "M", "B", "T", "Qua", "Qui"]

    while abs(count) >= 1000:
        if magnitude >= 5:
            break

        magnitude += 1
        count /= 1000.0

    try:
        return "{}{}".format(
            "{:f}".format(count).rstrip("0").rstrip("."), matches[magnitude]
        )
    except IndexError:
        return original_count


class Music(commands.Cog, discordSuperUtils.CogManager.Cog, name="Music"):
    def __init__(self, bot):
        self.bot = bot
        self.skip_votes = {}  # Skip vote counter dictionary

        # self.client_secret = "" # spotify client_secret
        # self.client_id = "" # spotify client_id

        # Get your's from here https://developer.spotify.com/

        self.MusicManager = MusicManager(self.bot, spotify_support=False)

        # self.MusicManager = MusicManager(bot,
        #                                  client_id=self.client_id,
        #                                  client_secret=self.client_secret,
        #                                  spotify_support=True)

        # If using spotify support use this instead ^^^

        self.ImageManager = discordSuperUtils.ImageManager()
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

    # Play function
    async def play_cmd(self, ctx, query):
        async with ctx.typing():
            player = await self.MusicManager.create_player(query, ctx.author)

        if player:
            if not ctx.voice_client or not ctx.voice_client.is_connected():
                await self.MusicManager.join(ctx)

            await self.MusicManager.queue_add(players=player, ctx=ctx)

            if not await self.MusicManager.play(ctx):
                await ctx.send(f"{player[0].title}을 큐에 추가했어요.")
            else:
                await ctx.send("✅")
        else:
            await ctx.send("쿼리를 찾지 못했어요.")

    # cog error handler
    async def cog_command_error(
            self, ctx: commands.Context, error: commands.CommandError
    ):
        print("An error occurred: {}".format(str(error)))

    # Error handler
    @discordSuperUtils.CogManager.event(discordSuperUtils.MusicManager)
    async def on_music_error(self, ctx, error):
        errors = {
            discordSuperUtils.NotPlaying: "지금은 노래를 재생중이지 않아요..",
            discordSuperUtils.NotConnected: '제가 아직 음성채널에 접속중이지 않아요!',
            discordSuperUtils.NotPaused: "노래가 아직 멈추지않았어요!",
            discordSuperUtils.QueueEmpty: "큐가 비어있어요!",
            discordSuperUtils.AlreadyConnected: "이미 음성채널에 접속되어있어요!",
            discordSuperUtils.QueueError: "큐에 문제가 생겼어요!",
            discordSuperUtils.SkipError: "스킵할 노래가 없어요!",
            discordSuperUtils.UserNotConnected: "명령자님이 아직 음성채널에 접속중이지 않아요!",
            discordSuperUtils.InvalidSkipIndex: "스킵인덱스값은 사용할 수가 없어요!",
        }

        for error_type, response in errors.items():
            if isinstance(error, error_type):
                await ctx.send(response)
                return

        print("unexpected error")
        raise error

    # On music play event
    @discordSuperUtils.CogManager.event(discordSuperUtils.MusicManager)
    async def on_play(self, ctx, player):  # This returns a player object

        # Extracting useful data from player object
        thumbnail = player.data["videoDetails"]["thumbnail"]["thumbnails"][-1]["url"]
        title = player.data["videoDetails"]["title"]
        url = player.url
        uploader = player.data["videoDetails"]["author"]
        requester = player.requester.mention if player.requester else "Autoplay"

        embed = discord.Embed(
            title="Now Playing",
            color=discord.Color.from_rgb(255, 255, 0),
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            description=f"[**{title}**]({url}) by **{uploader}**",
        )
        embed.add_field(name="Requested by", value=requester)
        embed.set_thumbnail(url=thumbnail)

        await ctx.send(embed=embed)
        # Clearing skip votes for each song
        if self.skip_votes.get(ctx.guild.id):
            self.skip_votes.pop(ctx.guild.id)

    # On queue end event
    @discordSuperUtils.CogManager.event(discordSuperUtils.MusicManager)
    async def on_queue_end(self, ctx):
        print(f"The queue has ended in {ctx}")
        await ctx.send("큐가 끝났어요.")
        # You could wait and check activity, etc...

    # On inactivity disconnect event
    @discordSuperUtils.CogManager.event(discordSuperUtils.MusicManager)
    async def on_inactivity_disconnect(self, ctx):
        print(f"I have left {ctx} due to inactivity")
        await ctx.send("사용하지않아 채널에서 나갔어요")

    # On ready event

    # Leave command
    @commands.command(name="나가")
    async def leave(self, ctx):
        if await self.MusicManager.leave(ctx):
            await ctx.send("👋")
            # Or
            # await message.add_reaction("👋")

    # Lyrics command
    @commands.command(name="가사")
    async def lyrics(self, ctx, *, query=None):
        if response := await self.MusicManager.lyrics(ctx, query):
            # If lyrics are found
            title, author, query_lyrics = response
            # Formatting the lyrics
            splitted = query_lyrics.split("\n")
            res = []
            current = ""
            for i, split in enumerate(splitted):
                if len(splitted) <= i + 1 or len(current) + len(splitted[i + 1]) > 1024:
                    res.append(current)
                    current = ""
                    continue
                current += split + "\n"
            # Creating embeds list for PageManager
            embeds = [
                discord.Embed(
                    title=f"'{title}'의 가사, 요청자 - '{author}', (페이지 {i + 1}/{len(res)})",
                    description=x,
                )
                for i, x in enumerate(res)
            ]
            # editing the embeds
            for embed in embeds:
                embed.timestamp = datetime.datetime.utcnow()

            page_manager = discordSuperUtils.PageManager(
                ctx,
                embeds,
                public=True,
            )

            await page_manager.run()

        else:
            await ctx.send("가사를 찾을 수가 없어요")

    # Now playing command
    @commands.command(name="지금곡")
    async def now_playing(self, ctx):
        if player := await self.MusicManager.now_playing(ctx):
            # Played duration
            duration_played = round(
                await self.MusicManager.get_player_played_duration(ctx, player)
            )

            # Loop status
            loop = (await self.MusicManager.get_queue(ctx)).loop
            if loop == discordSuperUtils.Loops.LOOP:
                loop_status = "반복기능이 활성화 되었어요. <:activ:896255701641474068>"
            elif loop == discordSuperUtils.Loops.QUEUE_LOOP:
                loop_status = "큐 반복기능이 활성화 되었어요. <:activ:896255701641474068>"
            else:
                loop_status = "반복 기능이 비활성화 되었어요. <:disactiv:896388083816218654>"

            # Fecthing other details
            thumbnail = player.data["videoDetails"]["thumbnail"]["thumbnails"][-1][
                "url"
            ]
            title = player.data["videoDetails"]["title"]
            url = player.url
            uploader = player.data["videoDetails"]["author"]
            views = player.data["videoDetails"]["viewCount"]
            rating = player.data["videoDetails"]["averageRating"]
            requester = player.requester.mention if player.requester else "Autoplay"

            embed = discord.Embed(
                title="Now playing",
                description=f"**{title}**",
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.from_rgb(0, 255, 255),
            )
            embed.add_field(name="현재 재생시간", value=parse_duration(duration_played))
            embed.add_field(name="재생길이", value=parse_duration(player.duration))
            embed.add_field(name="반복상태", value=loop_status)
            embed.add_field(name="요청자", value=requester)
            embed.add_field(name="업로더", value=uploader)
            embed.add_field(name="URL", value=f"[Click]({url})")
            embed.add_field(name="조회수", value=parse_count(int(views)))
            embed.add_field(name="별점", value=rating)
            embed.set_thumbnail(url=thumbnail)
            embed.set_image(url=r"https://i.imgur.com/ufxvZ0j.gif")
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)

            await ctx.send(embed=embed)

    # Join voice channel command
    @commands.command(name="들어와")
    async def join(self, ctx):
        if await self.MusicManager.join(ctx):
            await ctx.send(f"{ctx.author.voice.channel.mention}에 접속했어요!")

    # Play song command
    @commands.command(name="재생")
    async def play(self, ctx, *, query: str):
        # Calling the play function
        await Music.play_cmd(self, ctx, query)

    # Pause command
    @commands.command(name="일시정지")
    async def pause(self, ctx):
        if await self.MusicManager.pause(ctx):
            await ctx.send("일시정지했어요. ⏸")

    # Resume command
    @commands.command(name="이어재생")
    async def resume(self, ctx):
        if await self.MusicManager.resume(ctx):
            await ctx.send("이어서 재생할게요. ⏯")

    # Volume command
    @commands.command(name="볼륨")
    async def volume(self, ctx, volume: int = None):
        if volume is None:
            current_volume = await self.MusicManager.volume(ctx)
            await ctx.send("현재 볼륨 " + current_volume + "%")
        if await self.MusicManager.volume(ctx, volume) is not None:
            current_volume = await self.MusicManager.volume(ctx, volume)
            await ctx.send(f"볼름은 다음으로 설정했어요. `{current_volume}%`")

    # Song loop command
    @commands.command(name="루프")
    async def loop(self, ctx):
        is_loop = await self.MusicManager.loop(ctx)

        if is_loop is not None:
            await ctx.send(
                f"반복기능을 {'활성화 <:activ:896255701641474068>' if is_loop else '비활성화 <:disactiv:896388083816218654>'} 했어요")

    # Queue loop command
    @commands.command(name="큐루프")
    async def queueloop(self, ctx):
        is_loop = await self.MusicManager.queueloop(ctx)

        if is_loop is not None:
            await ctx.send(
                f"큐반복기능을 {'활성화 <:activ:896255701641474068>' if is_loop else '비활성화 <:disactiv:896388083816218654>'} 했어요")

    # History command
    @commands.command(name="노래기록")
    async def history(self, ctx):
        if queue := await self.MusicManager.get_queue(ctx):
            auto = "Autoplay"
            formatted_history = [
                f"제목: '{x.title}\n요청자: {x.requester.mention if x.requester else auto}"
                for x in queue.history
            ]

            embeds = discordSuperUtils.generate_embeds(
                formatted_history,
                "노래 기록",
                "지금까지 재생한 곡의 기록을 보여드려요",
                25,
                string_format="{}",
            )

            for embed in embeds:
                embed.timestamp = datetime.datetime.utcnow()

            await discordSuperUtils.PageManager(ctx, embeds, public=True).run()

    # Stop command
    @commands.command(name="정지")
    async def stop(self, ctx):
        await self.MusicManager.cleanup(ctx.voice_client, ctx.guild)
        await ctx.send("⏹️")

    # Skip command with voting
    @commands.command(name="스킵")
    async def skip(self, ctx, index: int = None):
        if queue := (await self.MusicManager.get_queue(ctx)):
            requester = (await self.MusicManager.now_playing(ctx)).requester

            # Checking if the song is autoplayed
            if requester is None:
                await ctx.send("자동재생 곡을 스킵했어요.⏩")
                await self.MusicManager.skip(ctx, index)

            # Checking if queue is empty and autoplay is disabled
            elif not queue.queue and not queue.autoplay:
                await ctx.send("큐의 마지막 곡을 스킵할 수 없어요")

            else:
                # Checking if guild id list is in skip votes dictionary
                if not self.skip_votes.get(ctx.guild.id):
                    self.skip_votes[ctx.guild.id] = []

                # Checking the voter
                voter = ctx.author

                # If voter is requester than skips automatically
                if voter == (await self.MusicManager.now_playing(ctx)).requester:
                    skipped_player = await self.MusicManager.skip(ctx, index)

                    await ctx.send("요청자의 요청으로 스킵했어요. ⏩")

                    if not skipped_player.requester:
                        await ctx.send("다음 자동재생곡으로 스킵했어요. ⏩")

                    # clearing the skip votes
                    self.skip_votes.pop(ctx.guild.id)

                # Voting
                elif (
                        voter.id not in self.skip_votes[ctx.guild.id]
                ):  # Checking if someone already voted
                    # Adding the voter id to skip votes
                    self.skip_votes[ctx.guild.id].append(voter.id)

                    # Calculating total votes
                    total_votes = len(self.skip_votes[ctx.guild.id])

                    # If total votes >=3 then it will skip
                    if total_votes >= 3:
                        skipped_player = await self.MusicManager.skip(ctx, index)

                        await ctx.send("투표로 스킵되어졌어요. ⏩")

                        if not skipped_player.requester:
                            await ctx.send("다음 자동재생곡으로 스킵했어요. ⏩")

                        # Clearing skip votes of the guild
                        self.skip_votes.pop(ctx.guild.id)

                    # Shows voting status
                    else:
                        await ctx.send(
                            f"스킵 투표가 추가되었어요, 현재 투표수 -  **{total_votes}/3**"
                        )

                # If someone uses vote command twice
                else:
                    await ctx.send("이미 현재곡에 투표하셨어요!")

    # Queue command
    @commands.command(name="큐")
    async def queue(self, ctx):
        if queue := await self.MusicManager.get_queue(ctx):
            auto = "Autoplay"
            formatted_queue = [
                f"제목: '{x.title}\n요청자: {x.requester.mention if x.requester else auto}"
                for x in queue.queue
            ]

            embeds = discordSuperUtils.generate_embeds(
                formatted_queue,
                "큐",  # Title of embed
                f"Now Playing: {await self.MusicManager.now_playing(ctx)}",
                25,  # Number of rows in one pane
                string_format="{}",
                color=11658814,  # Color of embed in decimal color
            )

            for embed in embeds:
                embed.timestamp = datetime.datetime.utcnow()

            await discordSuperUtils.PageManager(ctx, embeds, public=True).run()

    # Loop status command
    @commands.command(name="반복확인")
    async def loop_check(self, ctx):
        if queue := await self.MusicManager.get_queue(ctx):
            loop = queue.loop
            loop_status = None

            if loop == discordSuperUtils.Loops.LOOP:
                loop_status = "반복 기능이 활성화 되었어요. <:activ:896255701641474068>"

            elif loop == discordSuperUtils.Loops.QUEUE_LOOP:
                loop_status = "큐 반복 기능이 활성화 되었어요. <:activ:896255701641474068>"

            elif loop == discordSuperUtils.Loops.NO_LOOP:
                loop_status = "반복 기능이 비활성화 되었어요. <:disactiv:896388083816218654>"

            if loop_status:
                embed = discord.Embed(
                    title=loop_status,
                    color=0x00FF00,
                    timestamp=datetime.datetime.utcnow(),
                )

                await ctx.send(embed=embed)

    # Autoplay command
    @commands.command(name="자동재생")
    async def autoplay(self, ctx):
        is_autoplay = await self.MusicManager.autoplay(ctx)

        if is_autoplay is not None:
            if is_autoplay:
                await ctx.send('자동재생이 활성화되었어요.')
            else:
                await ctx.send('자동재생이 비활성화되었어요.')

    # Shuffle command
    @commands.command(name="셔플")
    async def shuffle(self, ctx):
        is_shuffle = await self.MusicManager.shuffle(ctx)

        if is_shuffle is not None:
            if is_shuffle:
                await ctx.send('셔플이 활성화되었어요.')
            else:
                await ctx.send('셔플이 비활성화되었어요.')

    # Previous/Rewind command
    @commands.command(name="이전곡")
    async def previous(self, ctx, index: int = None):
        if previous_player := await self.MusicManager.previous(ctx, index):
            await ctx.send(f"{previous_player[0].title}로부터 이전곡을 재생해요")

    # Before invoke checks. Add more commands if you wish to
    @join.before_invoke
    @play.before_invoke
    async def ensure_voice_state(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("You are not connected to any voice channel.")
            raise commands.CommandError()

        if (
                ctx.voice_client
                and ctx.voice_client.channel != ctx.author.voice.channel
        ):
            await ctx.send("Bot is already in a voice channel.")
            raise commands.CommandError()


def setup(bot):
    bot.add_cog(Music(bot))
