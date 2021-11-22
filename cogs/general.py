import io
import asyncio
from PycordPaginator import Paginator
import aiosqlite
import discord
from discord.ext import commands
import discordSuperUtils
class general(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ImageManager = discordSuperUtils.ImageManager()

    @commands.command(name="hellothisisverification")
    async def hellothisisverification(self,ctx):
        await ctx.send("gawi#9537(281566165699002379)")

    @commands.command(name="개발자")
    async def verification(self, ctx):
        await ctx.send("gawi#9537(281566165699002379)")

    @commands.command(name="도움",aliases=["도움말","help"])
    async def help(self,ctx):
        global embeds
        main = discord.Embed(
            title="메인페이지",
            description="""
안녕하세요! 하린봇을 이용해주셔서 감사드립니다.

도움말 목차는 아래와 같아요!

< 목차 >
• 1페이지 - 메인페이지
• 2페이지 - 서버 관리 ⚖
• 3페이지 - 도구 🧰
• 4페이지 - 뮤직 🎶
• 5페이지 - 생일 🎉
• 6페이지 - 학교검색 🏫
• 7페이지 - 출석체크 📅
• 8페이지 - 템플릿 🧩
• 9페이지 - 방송 <:streaming:911928055197478912>

[하린봇 초대](https://discord.com/api/oauth2/authorize?client_id=893841721958469703&permissions=8&scope=bot)
[서포트서버](https://discord.gg/Jk6VRvsnqa)
""",
            colour=discord.Colour.random()
        )
        main.set_thumbnail(url=self.bot.user.avatar_url)
        main.set_image(url="https://media.discordapp.net/attachments/889514827905630290/896359450544308244/37cae031dc5a6c40.png")
        main.set_footer(text=f"1 / 9페이지",icon_url=ctx.author.avatar_url)

        manage = discord.Embed(
            title="서버 관리 ⚖",
            description="""
이곳에서 서버 관리 명령어를 확인해보세요!    
이곳의 모든명령어는 관리자권한이 있어야 사용가능해요.
단, 처벌 조회는 예외에요.        
투표 소스 출처 - [minibox24/pollbot](https://github.com/minibox24/pollbot)
""",
            colour=discord.Colour.random()
        )
        manage.add_field(name="하린아 처벌 @유저",
                         value="```\n지정한 유저의 처벌기록을 보여드려요.\n```",
                         inline=False)
        manage.add_field(name="하린아 처벌 조회 @유저 처벌ID",
                         value="```\n지정한 유저의 처벌ID에 해당하는 기록을 보여드려요.\n```",
                         inline=False)
        manage.add_field(name="하린아 처벌 추가 @유저 (사유)",
                         value="```\n지정한 유저에게 경고를 부여해요. 사유는 선택사항이에요.\n```",
                         inline=False)
        manage.add_field(name="하린아 처벌 취소 @유저 처벌ID (사유)",
                         value="```\n지정한 유저에게 부여된 경고를 취소해요. 사유는 선택사항이에요.\n```",
                         inline=False)
        manage.add_field(name="하린아 뮤트 @유저 시간|0d0h0m0s (사유)",
                         value="```\n지정한 유저에게 뮤트를 설정한 시간동안 부여해요. 사유는 선택사항이에요.\n```",
                         inline=False)
        manage.add_field(name="하린아 언뮤트 @유저 (사유)",
                         value="```\n지정한 유저에게 부여된 뮤트를 취소해요. 사유는 선택사항이에요.\n```",
                         inline=False)
        manage.add_field(name="하린아 밴 @유저 시간|0d0h0m0s (사유)",
                         value="```\n지정한 유저를 밴하여 설정한 시간후에 언밴해요. 사유는 선택사항이에요.\n```",
                         inline=False)
        manage.add_field(name="하린아 언밴 @유저 (사유)",
                         value="```\n지정한 유저에게 부여된 뮤트를 취소해요. 사유는 선택사항이에요.\n```",
                         inline=False)
        manage.add_field(name="하린아 청소 갯수",
                         value="```\n지정한 갯수만큼 메세지를 지워요. 최대갯수는 99개에요.\n```",
                         inline=False)
        manage.add_field(name="하린아 서버공지 #채널 내용",
                         value="```\n지정한 채널에 입력한 내용의 공지사항글을 올려요.\n```",
                         inline=False)
        manage.add_field(name="하린아 티켓설정 #티켓채널 @지원팀역할 티켓안내내용",
                         value="```\n티켓기능을 사용하기위한 명령어에요.\n```",
                         inline=False)
        manage.add_field(name="하린아 티켓삭제 #티켓채널 메세지ID",
                         value="```\n설정한 티켓기능을 비활성화할 티켓채널과 해당 메세지ID를 입력해 비활성화해요.\n```",
                         inline=False)
        manage.add_field(name="하린아 투표 제목 항목1 항목2 항목3 •••",
                         value="```\n투표를 진행해요. 제목은 필수이며 항목은 최소 2개부터 최대 24개까지만 가능해요.\n```",
                         inline=False)
        manage.add_field(name="하린아 개표",
                         value="```\n하린이가 보낸 투표 메세지에 답장으로 위 명령어를 입력하면 투표결과를 알려줘요.\n```",
                         inline=False)
        manage.add_field(name="하린아 태그",
                         value="```\n태그목록을 보여드려요\n```",
                         inline=False)
        manage.add_field(name="하린아 태그 [제목]",
                         value="```\n입력한 태그를 보여드려요\n```",
                         inline=False)
        manage.add_field(name="하린아 태그 등록 [제목,설명]",
                         value="```\n태그를 등록해요.\n⚠제목과 설명을 구분하기위해 **꼭!** 쉼표가 있어야해요.\n```",
                         inline=False)
        manage.add_field(name="하린아 태그 수정 [제목,설명]",
                         value="```\n태그를 등록해요.\n⚠제목과 설명을 구분하기위해 **꼭!** 쉼표가 있어야해요.\n```",
                         inline=False)
        manage.add_field(name="하린아 태그 삭제 [제목]",
                         value="```\n등록된 태그중 해당하는 제목의 태그를 삭제해요.\n```",
                         inline=False)
        manage.add_field(name="⚠ 안내",
                         value="```\n아래 기능을 사용하기위해선 개별 길드를 생성하시고 봇을 초대하신뒤 사용하셔야합니다!.\n```",
                         inline=False)
        manage.add_field(name="하린아 setup [타겟길드ID] [입장전용채널ID]",
                         value="```\n뒷메나 테러 방지를 위한 대문설정을 해요.\n```",
                         inline=False)
        manage.add_field(name="하린아 edit [바꿀 입장전용채널ID]",
                         value="```\n이미 설정된 값에서 바꿀 입장전용채널ID로 변경해요.\n```",
                         inline=False)
        manage.add_field(name="하린아 delete [입장 전용채널ID]",
                         value="```\n대문기능을 비활성화 해요.\n```",
                         inline=False)
        manage.set_footer(text=f"2 / 9페이지",icon_url=ctx.author.avatar_url)

        util = discord.Embed(
            title="도구 🧰",
            description="""
        이곳에서 도구 관련 명령어를 확인해보세요!            
        """,
            colour=discord.Colour.random()
        )
        util.add_field(
            name="하린아 [옵션 or 설정]",
            value="```\n여러 기능을 설정할 수 있는 명령어에요!\n```",
            inline=False
        )
        util.add_field(
            name="하린아 프사 (@유저)",
            value="```\n유저를 지정하거나 하지않으면 자신의 프로필 사진을 불러와요!\n```",
            inline=False
        )
        util.add_field(
            name="하린아 서버정보",
            value="```\n명령어를 실행한 서버의 정보를 불러와요!\n```",
            inline=False
        )
        util.add_field(
            name="하린아 봇정보",
            value="```\n제 정보를 보여드려요!\n```",
            inline=False
        )
        util.add_field(
            name="하린아 [랭크 or 레벨] (@user)",
            value="```\n지정한 유저 혹은 자신의 레벨카드를 보여드려요.\n```",
            inline=False
        )
        util.add_field(
            name="하린아 리더보드",
            value="```\n현재 길드의 레벨순위정보판을 보여드려요.\n```",
            inline=False
        )
        util.add_field(
            name="하린아 초대정보 (@user)",
            value="```\n지정한 유저 혹은 자신의 초대정보를 보여줘요.\n```",
            inline=False
        )
        util.add_field(
            name="하린아 메일 (전체)",
            value="```\n전체 옵션을 사용하지않으면 수신된 메일을 보여주고 사용하면 모든 메일을 볼 수 있어요!\n```",
            inline=False
        )
        util.add_field(
            name="하린아 애니검색 [애니제목]",
            value="```\n애니를 검색해요.\n```",
            inline=False
        )
        util.add_field(
            name="하린아 애니 댓글달기 [댓글내용]",
            value="```\n애니 검색결과 메세지에 답장형태로 사용하여 댓글을 남겨요. 부적절한 댓글은 무통보삭제가 되요.\n```",
            inline=False
        )
        util.add_field(
            name="하린아 애니 댓글수정 [댓글내용]",
            value="```\n애니 검색결과 메세지에 답장형태로 사용하여 댓글을 수정해요. 부적절한 댓글은 무통보삭제가 되요.\n```",
            inline=False
        )
        util.add_field(
            name="하린아 애니 댓글삭제",
            value="```\n애니 검색결과 메세지에 답장형태로 사용하여 남긴 댓글을 삭제해요. 부적절한 댓글은 무통보삭제가 되요.\n```",
            inline=False
        )
        util.set_footer(text=f"3 / 9페이지",icon_url=ctx.author.avatar_url)

        music = discord.Embed(
            title="뮤직 🎶",
            description="""
                이곳에서 노래 관련 명령어를 확인해보세요!            
                """,
            colour=discord.Colour.random()
        )
        music.add_field(
            name="하린아 들어와",
            value="```\n현재 접속한 음성채널에 접속해요.\n```",
            inline=False
        )
        music.add_field(
            name="하린아 재생 인자값",
            value="```\n입력한 인자값(제목 또는 링크)을 불러와 재생해요.\n```",
            inline=False
        )
        music.add_field(
            name="하린아 가사",
            value="```\n현재 재생중인 곡의 가사를 불러와요.\n```",
            inline=False
        )
        music.add_field(
            name="하린아 지금곡",
            value="```\n현재 재생중인 노래의 정보를 불러와요.\n```",
            inline=False
        )
        music.add_field(
            name="하린아 일시정지",
            value="```\n현재 재생중인 곡을 일시정지해요.\n```",
            inline=False
        )
        music.add_field(
            name="하린아 이어재생",
            value="```\n일시정지된 곡을 이어서 재생해요.\n```",
            inline=False
        )
        music.add_field(
            name="하린아 볼륨 (설정할볼륨)",
            value="```\n설정할 볼륨으로 볼륨을 조절해요. 입력하지 않으면 현재 볼륨을 보여줘요.\n```",
            inline=False
        )
        music.add_field(
            name="하린아 루프",
            value="```\n반복기능을 활성화하거나 비활성화해요.\n```",
            inline=False
        )
        music.add_field(
            name="하린아 큐루프",
            value="```\n큐반복기능을 활성화하거나 비활성화해요.\n```",
            inline=False
        )
        music.add_field(
            name="하린아 노래기록",
            value="```\n지금까지 재생됐던 노래기록을 불러와요.\n```",
            inline=False
        )
        music.add_field(
            name="하린아 정지",
            value="```\n현재 재생중인 곡을 완전히 정지해요.\n```",
            inline=False
        )
        music.add_field(
            name="하린아 스킵",
            value="```\n현재 재생중인 곡을 스킵하거나 요청해요.\n```",
            inline=False
        )
        music.add_field(
            name="하린아 큐",
            value="```\n현재 대기중인 큐목록을 보여줘요.\n```",
            inline=False
        )
        music.add_field(
            name="하린아 반복확인",
            value="```\n현재 설정된 반복상태를 보여줘요.\n```",
            inline=False
        )
        music.add_field(
            name="하린아 셔플",
            value="```\n셔플기능을 활성화하거나 비활성화해요.\n```",
            inline=False
        )
        music.add_field(
            name="하린아 자동재생",
            value="```\n자동재생기능을 활성화하거나 비활성화해요.\n```",
            inline=False
        )
        music.add_field(
            name="하린아 이전곡",
            value="```\n이전곡을 재생해요.\n```",
            inline=False
        )
        music.add_field(
            name="하린아 나가",
            value="```\n현재 접속한 음성채널에서 노래를 멈추고 나가요.\n```",
            inline=False
        )
        music.set_footer(text=f"4 / 9페이지",icon_url=ctx.author.avatar_url)

        birthday = discord.Embed(
            title="생일 🎉",
            description="""
                이곳에서 생일 관련 명령어를 확인해보세요!            
                """,
            colour=discord.Colour.random()
        )
        birthday.add_field(
            name="하린아 생일등록",
            value="```\n자신의 생일을 등록해요.\n```",
            inline=False
        )
        birthday.add_field(
            name="하린아 생일삭제",
            value="```\n등록된 자신의 생일을 삭제해요.\n```",
            inline=False
        )
        birthday.add_field(
            name="하린아 생일 (@user)",
            value="```\n자신 혹은 지정한 유저의 생일을 조회해요.\n```",
            inline=False
        )
        birthday.add_field(
            name="하린아 생일목록",
            value="```\n현재길드에 등록된 멤버들의 생일을 보여줘요.\n```",
            inline=False
        )
        birthday.set_footer(text=f"5 / 8페이지",icon_url=ctx.author.avatar_url)

        school = discord.Embed(
            title="학교검색 🏫",
            description="""
                이곳에서 학교검색 관련 명령어를 확인해보세요!            
                """,
            colour=discord.Colour.random()
        )
        school.add_field(
            name="하린아 학교검색 학교명",
            value="```\n학교의 정보를 조회해볼 수 있는 명령어에요!\n```",
            inline=False
        )
        school.add_field(
            name="하린아 학교검색 급식 학교명",
            value="```\n학교급식을 조회해볼 수 있는 명령어에요!\n```",
            inline=False
        )
        school.set_footer(text=f"6 / 9페이지",icon_url=ctx.author.avatar_url)

        chulcheck = discord.Embed(
            title="출석체크 📅",
            description="""
                        이곳에서 출석체크 관련 명령어를 확인해보세요!
                        출석체크를 하게된다면 __유저명이 공개되는것에 동의__하게 됩니다.        
                        """,
            colour=discord.Colour.random()
        )
        chulcheck.add_field(
            name="하린아 출석체크",
            value="```출석체크를 할 수 있어요!단, 하루에 한번만 가능해요.```",
            inline=False
        )
        chulcheck.add_field(
            name="하린아 출석체크 리더보드",
            value="```\n출석체크 순위표를 확인할 수 있어요!\n```",
            inline=False
        )
        chulcheck.set_footer(text=f"7 / 9페이지", icon_url=ctx.author.avatar_url)
        template = discord.Embed(
            title="템플릿 🧩",
            description="서버 템플릿에 관련한 명령어를 확인해보세요.\n등록하게된다면 __서버명과 채널들의 이름이 공개되는것에 동의__하게 됩니다.",
            colour=discord.Colour.random()
        )
        template.add_field(
            name="하린아 템플릿사용 템플릿ID",
            value="```\n입력한 ID의 템플릿을 사용해요.어드민 권한이 있어야해요.\n```",
            inline=False
        )
        template.add_field(
            name="하린아 템플릿삭제 템플릿ID",
            value="```\n입력한 ID의 템플릿을 삭제해요.어드민 권한이 있어야해요.\n```",
            inline=False
        )
        template.add_field(
            name="하린아 템플릿목록",
            value="```\n저장된 템플릿 목록을 불러와요.\n```",
            inline=False
        )
        template.add_field(
            name="하린아 템플릿찾기 (템플릿ID)",
            value="```\n입력한 ID 혹은 현재길드의 템플릿을 불러와요.\n```",
            inline=False
        )
        template.add_field(
            name="하린아 템플릿등록",
            value="```\n현재 길드를 템플릿화해요.어드민 권한이 있어야해요.\n```",
            inline=False
        )
        template.set_footer(text="8 / 9페이지",icon_url=ctx.author.avatar_url)

        broadcast = discord.Embed(
            title="방송 <:streaming:911928055197478912>",
            description="트위치/유튜브 알림과 검색에 관련한 명령어를 확인해보세요.\n트위치/유튜브 알림 채널은 무료플랜은 1개, 프리미엄플랜은 5개까지 등록가능합니다.",
            colour=discord.Colour.random()
        )
        broadcast.add_field(
            name="하린아 트위치",
            value="```\n트위치 스트리밍 알림 서비스에 등록된 채널 목록을 보여드려요.\n```",
            inline=False
        )
        broadcast.add_field(
            name="하린아 트위치 등록 @알림역할 #알림채널 [유저ID]",
            value="```\n트위치 스트리밍 알림 서비스에 등록해요.\n```",
            inline=False
        )
        broadcast.add_field(
            name="하린아 트위치 해제",
            value="```\n트위치 스트리밍 알림 서비스에서 해제해요.\n```",
            inline=False
        )
        broadcast.add_field(
            name="하린아 유튜브 [채널이름]",
            value="```\n입력한 채널이름으로 검색해요.\n```",
            inline=False
        )
        broadcast.add_field(
            name="하린아 유튜브 등록 @알림역할 #알림채널 [채널ID]",
            value="```\n유튜브 업로드 알림 서비스에 등록해요.\n```",
            inline=False
        )
        broadcast.add_field(
            name="하린아 유튜브 해제",
            value="```\n유튜브 업로드 알림 서비스에서 해제해요.\n```",
            inline=False
        )
        broadcast.set_footer(text="9 / 9페이지", icon_url=ctx.author.avatar_url)

        """game = discord.Embed(
            title="게임 🎮",
            description="게임과 관련한 명령어를 확인해보세요.\n게임플레이를 하게된다면 __유저명이 공개되는것에 동의__하게 됩니다.\n끝말잇기는 끝봇의 [오픈소스](https://github.com/janu8ry/kkutbot)를 사용하였습니다.\n마피아는 다음의 [오픈소스](https://github.com/frin0911/Mafia-Bot)를 사용하였습니다.",
            colour=discord.Colour.random()
        )
        game.add_field(
            name="하린아 끝말잇기",
            value="```\n저와 또는 길드유저와 함께 끝말잇기를 해요.\n```",
            inline=False
        )
        game.add_field(
            name="하린아 끝말잇기 리더보드",
            value="```\n끝말잇기 리더보드를 볼수있어요.\n```",
            inline=False
        )
        game.add_field(
            name="하린아 마피아",
            value="```\n길드유저와 함께 마피아게임을 해요. 최소인원은 4명이고 최대인원은 23명입니다.\n```",
            inline=False
        )
        game.set_footer(text="9 / 9페이지", icon_url=ctx.author.avatar_url)"""

        embeds = [main,manage,util,music,birthday,school,chulcheck,template,broadcast]
        desc = {
            "메인 페이지": "목차가 있는 메인페이지",
            "⚖서버 관리": "서버 관리 명령어가 있는 페이지.",
            "🧰도구":"간편히 사용할 수 있는 명령어가 있는 페이지.",
            "🎶뮤직":"노래 명령어가 있는 페이지.",
            "🎉생일": "생일 명령어가 있는 페이지.",
            "🏫학교검색": "학교검색 명령어가 있는 페이지.",
            "📅출석체크": "출석체크 명령어가 있는 페이지.",
            "🧩템플릿":"템플릿 명령어가 있는 페이지.",
            "📡방송":"트위치/유튜브 관련 명령어가 있는 페이지."
        }
        e = Paginator(
            client=self.bot.components_manager,
            embeds=embeds,
            channel=ctx.channel,
            only=ctx.author,
            ctx=ctx,
            use_select=True,
            desc=desc)
        await e.start()

    @commands.command(name="메일", help="`ㅎ메일 (전체)`로 메일을 확인합니다.")
    async def read_mail(self, ctx, mode=None):
        if mode is None:
            dictcommand = await self.read_email_from_db(ctx=ctx)
            database = dictcommand["database"]
            contents = dictcommand["contents"]
            cur = dictcommand["cur"]
            uncheck_cur = dictcommand["uncheck_cur"]
            timess = dictcommand["timess"]
            pages = dictcommand["pages"]
            check2 = await cur.fetchone()
            uncheck_cur_fetchone = await uncheck_cur.fetchone()
            if uncheck_cur_fetchone is None:
                await database.execute("INSERT INTO uncheck VALUES (?, ?)", (ctx.author.id, str(pages)))
                await database.commit()
                mal = discord.Embed(title=f"📫하린봇 메일함 | {str(pages)}개 수신됨",
                                    description="주기적으로 메일함을 확인해주세요! 소소한 업데이트 및 이벤트개최등 여러소식을 확인해보세요.",
                                    colour=ctx.author.colour)
                cur_page = 1
            else:
                if str(pages) == str(uncheck_cur_fetchone[1]):
                    mal = discord.Embed(title=f"📫하린봇 메일함 | 수신된 메일이 없어요.",
                                        description="주기적으로 메일함을 확인해주세요! 소소한 업데이트 및 이벤트개최등 여러소식을 확인해보세요.",
                                        colour=ctx.author.colour)
                    mal.add_field(name="📭빈 메일함", value="✅모든 메일을 읽으셨어요. 전체메일을 보고싶으시면 '하린아 메일 전체'를 입력하세요.")
                    return await ctx.send(embed=mal)
                await database.execute("UPDATE uncheck SET check_s = ? WHERE user_id = ?",
                                       (str(pages), ctx.author.id))
                await database.commit()
                mal = discord.Embed(title=f"📫하린봇 메일함 | {pages - int(uncheck_cur_fetchone[1])}개 수신됨",
                                    description="주기적으로 메일함을 확인해주세요! 소소한 업데이트 및 이벤트개최등 여러소식을 확인해보세요.",
                                    colour=ctx.author.colour)
                cur_page = int(uncheck_cur_fetchone[1])
            # noinspection DuplicatedCode
            mal.add_field(name=f"{pages}중 {cur_page}번째 메일({timess[contents[cur_page - 1]]}작성)",
                          value=contents[cur_page - 1])
            message = await ctx.send(embed=mal)
            # getting the message object for editing and reacting

            await message.add_reaction("◀️")
            await message.add_reaction("▶️")

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"] and reaction.message.id == message.id

            while True:
                try:
                    reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)
                    # waiting for a reaction to be added - times out after x seconds, 60 in this
                    # example

                    if str(reaction.emoji) == "▶️" and cur_page != pages:
                        if check2 is None:
                            cur_page += 1
                            mal = discord.Embed(title=f"📫하린봇 메일함 | {str(pages)}개 수신됨",
                                                description="주기적으로 메일함을 확인해주세요! 소소한 업데이트 및 이벤트개최등 여러소식을 확인해보세요.",
                                                colour=ctx.author.colour)
                            mal.add_field(name=f"{pages}중 {cur_page}번째 메일", value=contents[cur_page - 1])
                        else:
                            cur_page += 1
                            mal = discord.Embed(title=f"📫하린봇 메일함 | {pages - int(uncheck_cur_fetchone[1])}개 수신됨",
                                                description="주기적으로 메일함을 확인해주세요! 소소한 업데이트 및 이벤트개최등 여러소식을 확인해보세요.",
                                                colour=ctx.author.colour)
                            mal.add_field(name=f"{pages}중 {cur_page}번째 메일({timess[contents[cur_page - 1]]}작성)",
                                          value=contents[cur_page - 1])
                        await message.edit(embed=mal)

                    elif str(reaction.emoji) == "◀️" and cur_page > 1:
                        if check2 is None:
                            cur_page -= 1
                            mal = discord.Embed(title=f"📫하린봇 메일함 | {str(pages)}개 수신됨",
                                                description="주기적으로 메일함을 확인해주세요! 소소한 업데이트 및 이벤트개최등 여러소식을 확인해보세요.",
                                                colour=ctx.author.colour)
                            mal.add_field(name=f"{pages}중 {cur_page}번째 메일", value=contents[cur_page - 1])
                        else:
                            cur_page -= 1
                            mal = discord.Embed(title=f"📫하린봇 메일함 | {pages - int(uncheck_cur_fetchone[1])}개 수신됨",
                                                description="주기적으로 메일함을 확인해주세요! 소소한 업데이트 및 이벤트개최등 여러소식을 확인해보세요.",
                                                colour=ctx.author.colour)
                            mal.add_field(name=f"{pages}중 {cur_page}번째 메일({timess[contents[cur_page - 1]]}작성)",
                                          value=contents[cur_page - 1])
                        await message.edit(embed=mal)
                except asyncio.TimeoutError:
                    break
        elif mode == "전체":
            dictcommand = await self.read_email_from_db(ctx=ctx)
            contents = dictcommand["contents"]
            timess = dictcommand["timess"]
            pages = dictcommand["pages"]
            mal = discord.Embed(title=f"📫하린봇 메일함",
                                description="주기적으로 메일함을 확인해주세요! 소소한 업데이트 및 이벤트개최등 여러소식을 확인해보세요.",
                                colour=ctx.author.colour)
            cur_page = 1
            # noinspection DuplicatedCode
            mal.add_field(name=f"{pages}중 {cur_page}번째 메일({timess[contents[cur_page - 1]]}작성)",
                          value=contents[cur_page - 1])
            message = await ctx.send(embed=mal)

            await message.add_reaction("◀️")
            await message.add_reaction("▶️")

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"] and reaction.message.id == message.id
                # This makes sure nobody except the command sender can interact with the "menu"

            while True:
                try:
                    reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)
                    # waiting for a reaction to be added - times out after x seconds, 60 in this
                    # example

                    if str(reaction.emoji) == "▶️" and cur_page != pages:
                        cur_page += 1
                        mal = discord.Embed(title=f"📫하린봇 메일함",
                                            description="주기적으로 메일함을 확인해주세요! 소소한 업데이트 및 이벤트개최등 여러소식을 확인해보세요.",
                                            colour=ctx.author.colour)
                        mal.add_field(name=f"{pages}중 {cur_page}번째 메일({timess[contents[cur_page - 1]]}작성)",
                                      value=contents[cur_page - 1])
                        await message.edit(embed=mal)

                    elif str(reaction.emoji) == "◀️" and cur_page > 1:
                        cur_page -= 1
                        mal = discord.Embed(title=f"📫하린봇 메일함",
                                            description="주기적으로 메일함을 확인해주세요! 소소한 업데이트 및 이벤트개최등 여러소식을 확인해보세요.",
                                            colour=ctx.author.colour)
                        mal.add_field(name=f"{pages}중 {cur_page}번째 메일({timess[contents[cur_page - 1]]}작성)",
                                      value=contents[cur_page - 1])
                        await message.edit(embed=mal)
                except asyncio.TimeoutError:
                    break

    @staticmethod
    async def read_email_from_db(ctx):
        contents = []
        timess = {}
        database = await aiosqlite.connect("db/db.sqlite")
        cur = await database.execute('SELECT * FROM mail')
        uncheck_cur = await database.execute('SELECT * FROM uncheck WHERE user_id = ?',(ctx.author.id,))
        mails = await cur.fetchall()
        for i in mails:
            contents.append(i[1])
            timess[i[1]] = i[2]
        pages = len(contents)
        return {"contents": contents, "timess": timess, "database": database, "cur": cur, "uncheck_cur":uncheck_cur, "pages": pages}

def setup(bot):
    bot.add_cog(general(bot))
