import asyncio
import datetime
import os
import aiosqlite
import discord
import neispy.error
from discord.ext import commands
from neispy import Neispy
from discord_components import (
    Select,
    SelectOption,
    Interaction
)
from Naver_Api.Api import Naver
from dotenv import load_dotenv
load_dotenv(verbose=True)
N = Naver(os.getenv("NAVER_CLIENT"),os.getenv("NAVER_SECRET"))
class Search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

    @commands.group(name="학교검색", invoke_without_command=True)
    async def main_school(self, ctx, school=None):
        if school is None:
            return await ctx.reply("학교명을 입력해주세요!")
        msg = await ctx.send("검색중이니 조금만 기다려주세요! <a:loading:888625946565935167>")
        async with Neispy(KEY=os.getenv("NEIS_TOKEN")) as neis:
            scinfo = await neis.schoolInfo(SCHUL_NM=school)
            if len(scinfo) >= 2:
                await msg.delete()
                many_msg = await ctx.send(
                    f"학교명이 같은 학교가 `{len(scinfo[:25])}`개 있어요.\n아래에서 검색하시려는 학교를 선택해주세요.",
                    components=[
                        Select(
                            placeholder="학교를 선택해주세요.",
                            options=[
                                SelectOption(label=i.SCHUL_NM, value=f"{i.SD_SCHUL_CODE}",
                                             description="지역 - {}".format(i.LCTN_SC_NM), emoji="🏫") for i in
                                scinfo[:25]
                            ],
                            custom_id="search"
                        ),
                    ],
                )
                try:
                    interaction = await self.bot.wait_for("select_option", check=lambda i: i.user.id == ctx.author.id and i.message.id == many_msg.id, timeout=30)
                    value = interaction.values[0]
                    # stamp = str(time.mktime(datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S').timetuple()))[:-2]
                except asyncio.TimeoutError:
                    await many_msg.delete()
                    return

                for i in scinfo:
                    if i.SD_SCHUL_CODE == value:
                        em = discord.Embed(
                            title=f"{i.SCHUL_NM}| {i.ENG_SCHUL_NM}( {i.LCTN_SC_NM} )",
                            description=f"주소: {i.ORG_RDNMA}\n대표번호: {i.ORG_TELNO}\nFax: {i.ORG_FAXNO}\n홈페이지: {i.HMPG_ADRES}",
                            colour=discord.Colour.random()
                        )
                        em.add_field(name="소속교육청", value=f"```{i.ATPT_OFCDC_SC_NM}```")
                        em.add_field(name="타입", value=f"```{i.COEDU_SC_NM} | {i.HS_SC_NM}```")
                        await many_msg.edit(embed=em, components=[])
            else:
                em = discord.Embed(
                    title=f"{scinfo[0].SCHUL_NM}| {scinfo[0].ENG_SCHUL_NM}( {scinfo[0].LCTN_SC_NM} )",
                    description=f"주소: {scinfo[0].ORG_RDNMA}\n대표번호: {scinfo[0].ORG_TELNO}\nFax: {scinfo[0].ORG_FAXNO}\n홈페이지: {scinfo[0].HMPG_ADRES}",
                    colour=discord.Colour.random()
                )
                em.add_field(name="소속교육청", value=f"```{scinfo[0].ATPT_OFCDC_SC_NM}```")
                em.add_field(name="타입", value=f"```{scinfo[0].COEDU_SC_NM} | {scinfo[0].HS_SC_NM}```")
                await msg.delete()
                await ctx.reply(embed=em)

    @main_school.command(name="급식")
    async def school_meal(self, ctx, school=None, dates=None):
        if school is None:
            return await ctx.reply("학교명을 입력해주세요!")
        if dates is None:
            now = datetime.datetime.now()
            dates = f"{now.year}{now.month}{now.day}"
        msg = await ctx.reply("검색중이니 조금만 기다려주세요! <a:loading:888625946565935167>")
        neis = Neispy(KEY=os.getenv("NEIS_TOKEN"))
        scinfo = await neis.schoolInfo(SCHUL_NM=school)
        if len(scinfo) >= 2:
            await msg.delete()
            many_msg = await ctx.send(
                f"학교명이 같은 학교가 `{len(scinfo[:25])}`개 있어요.\n아래에서 검색하시려는 학교를 선택해주세요.",
                components=[
                    Select(
                        placeholder="학교를 선택해주세요.",
                        options=[
                            SelectOption(label=i.SCHUL_NM, value=i.SD_SCHUL_CODE,
                                         description="지역 - {}".format(i.LCTN_SC_NM), emoji="🏫") for i in scinfo[:25]
                        ],
                    ),
                ],
            )
            try:
                interaction = await self.bot.wait_for("select_option", check=lambda i: i.user.id == ctx.author.id and i.message.id == many_msg.id, timeout=30)
                value = interaction.values[0]
                # stamp = str(time.mktime(datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S').timetuple()))[:-2]
            except asyncio.TimeoutError:
                await many_msg.delete()
                return
            for i in scinfo:
                if i.SD_SCHUL_CODE == value:
                    ae = i.ATPT_OFCDC_SC_CODE  # 교육청코드
                    se = i.SD_SCHUL_CODE  # 학교코드
                    diet_dict = {
                        "1": "조식",
                        "2": "중식",
                        "3": "석식"
                    }

                    async def callback(interaction: Interaction):
                        values = interaction.values[0]
                        print(values)
                        if interaction.user.id == ctx.author.id:
                            try:
                                scmeal = await neis.mealServiceDietInfo(ae, se, MLSV_YMD=dates, MMEAL_SC_CODE=values)
                            except neispy.error.DataNotFound:
                                await interaction.send(f"선택하신 `{diet_dict[values]}`의 메뉴를 찾을 수 없어요..")
                                return
                            meal = scmeal[0].DDISH_NM.replace("<br/>", "\n")
                            em = discord.Embed(
                                title=f"{i.SCHUL_NM} | {diet_dict[values]}",
                                description=f"```fix\n{meal}```"
                            )
                            await interaction.edit_origin(embed=em, components=[
                                self.bot.components_manager.add_callback(
                                    Select(
                                        options=[
                                            SelectOption(label="조식", value="1", emoji="🌅"),
                                            SelectOption(label="중식", value="2", emoji="☀"),
                                            SelectOption(label="석식", value="3", emoji="🌙")
                                        ],
                                    ),
                                    callback,
                                )
                            ])

                    await many_msg.delete()
                    await ctx.send(
                        "조회할 급식을 선택해주세요.",
                        components=[
                            self.bot.components_manager.add_callback(
                                Select(
                                    options=[
                                        SelectOption(label="조식", value="1", emoji="🌅"),
                                        SelectOption(label="중식", value="2", emoji="☀"),
                                        SelectOption(label="석식", value="3", emoji="🌙")
                                    ],
                                ),
                                callback,
                            )
                        ]
                    )
        else:
            ae = scinfo[0].ATPT_OFCDC_SC_CODE  # 교육청코드
            se = scinfo[0].SD_SCHUL_CODE  # 학교코드
            diet_dict = {
                "1": "조식",
                "2": "중식",
                "3": "석식"
            }

            async def callback(interaction: Interaction):
                values = interaction.values[0]
                print(values)
                if interaction.user.id == ctx.author.id:
                    try:
                        scmeal = await neis.mealServiceDietInfo(ae, se, MLSV_YMD=dates, MMEAL_SC_CODE=values)
                    except neispy.error.DataNotFound:
                        await interaction.send(f"선택하신 `{diet_dict[values]}`의 메뉴를 찾을 수 없어요..")
                        return
                    meal = scmeal[0].DDISH_NM.replace("<br/>", "\n")
                    em = discord.Embed(
                        title=f"{scinfo[0].SCHUL_NM} | {diet_dict[values]}",
                        description=f"```fix\n{meal}```"
                    )
                    await interaction.edit_origin(embed=em, components=[
                        self.bot.components_manager.add_callback(
                            Select(
                                options=[
                                    SelectOption(label="조식", value="1", emoji="🌅"),
                                    SelectOption(label="중식", value="2", emoji="☀"),
                                    SelectOption(label="석식", value="3", emoji="🌙")
                                ],
                            ),
                            callback,
                        )
                    ])

            await msg.delete()
            await ctx.reply(
                "조회할 급식을 선택해주세요.",
                components=[
                    self.bot.components_manager.add_callback(
                        Select(
                            options=[
                                SelectOption(label="조식", value="1", emoji="🌅"),
                                SelectOption(label="중식", value="2", emoji="☀"),
                                SelectOption(label="석식", value="3", emoji="🌙")
                            ],
                        ),
                        callback,
                    )
                ]
            )

    @main_school.command(name="시간표")
    async def school_schedule(self, ctx, school=None, dates=None):
        if school is None:
            return await ctx.reply("학교명을 입력해주세요!")
        if dates is None:
            now = datetime.datetime.now()
            dates = f"{now.year}{now.month}{now.day}"
        msg = await ctx.reply("검색중이니 조금만 기다려주세요! <a:loading:888625946565935167>")
        neis = Neispy(KEY=os.getenv("NEIS_TOKEN"))
        scinfo = await neis.schoolInfo(SCHUL_NM=school)
        if len(scinfo) >= 2:
            await msg.delete()
            many_msg = await ctx.reply(
                f"학교명이 같은 학교가 `{len(scinfo[:25])}`개 있어요.\n아래에서 검색하시려는 학교를 선택해주세요.",
                components=[
                    Select(
                        placeholder="학교를 선택해주세요.",
                        options=[
                            SelectOption(label=i.SCHUL_NM, value=i.SD_SCHUL_CODE,
                                         description="지역 - {}".format(i.LCTN_SC_NM), emoji="🏫") for i in scinfo[:25]
                        ],
                    ),
                ],
            )
            try:
                interaction = await self.bot.wait_for("select_option", check=lambda
                    i: i.user.id == ctx.author.id and i.message.id == many_msg.id, timeout=30)
                value = interaction.values[0]
                # stamp = str(time.mktime(datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S').timetuple()))[:-2]
            except asyncio.TimeoutError:
                await many_msg.delete()
                return
            for i in scinfo:
                if i.SD_SCHUL_CODE == value:
                    ae = i.ATPT_OFCDC_SC_CODE  # 교육청코드
                    se = i.SD_SCHUL_CODE  # 학교코드
                    diet_dict = {
                        "1": "조식",
                        "2": "중식",
                        "3": "석식"
                    }

                    async def callback(interaction: Interaction):
                        values = interaction.values[0]
                        print(values)
                        if interaction.user.id == ctx.author.id:
                            try:
                                scmeal = await neis.mealServiceDietInfo(ae, se, MLSV_YMD=dates, MMEAL_SC_CODE=values)
                            except neispy.error.DataNotFound:
                                await interaction.send(f"선택하신 `{diet_dict[values]}`의 메뉴를 찾을 수 없어요..")
                                return
                            meal = scmeal[0].DDISH_NM.replace("<br/>", "\n")
                            em = discord.Embed(
                                title=f"{i.SCHUL_NM} | {diet_dict[values]}",
                                description=f"```fix\n{meal}```"
                            )
                            await interaction.edit_origin(embed=em, components=[
                                self.bot.components_manager.add_callback(
                                    Select(
                                        options=[
                                            SelectOption(label="조식", value="1", emoji="🌅"),
                                            SelectOption(label="중식", value="2", emoji="☀"),
                                            SelectOption(label="석식", value="3", emoji="🌙")
                                        ],
                                    ),
                                    callback,
                                )
                            ])

                    await many_msg.delete()
                    await ctx.send(
                        "조회할 급식을 선택해주세요.",
                        components=[
                            self.bot.components_manager.add_callback(
                                Select(
                                    options=[
                                        SelectOption(label="조식", value="1", emoji="🌅"),
                                        SelectOption(label="중식", value="2", emoji="☀"),
                                        SelectOption(label="석식", value="3", emoji="🌙")
                                    ],
                                ),
                                callback,
                            )
                        ]
                    )
        else:
            ae = scinfo[0].ATPT_OFCDC_SC_CODE  # 교육청코드
            se = scinfo[0].SD_SCHUL_CODE  # 학교코드
            diet_dict = {
                "1": "조식",
                "2": "중식",
                "3": "석식"
            }

            async def callback(interaction: Interaction):
                values = interaction.values[0]
                print(values)
                if interaction.user.id == ctx.author.id:
                    try:
                        scmeal = await neis.mealServiceDietInfo(ae, se, MLSV_YMD=dates, MMEAL_SC_CODE=values)
                    except neispy.error.DataNotFound:
                        await interaction.send(f"선택하신 `{diet_dict[values]}`의 메뉴를 찾을 수 없어요..")
                        return
                    meal = scmeal[0].DDISH_NM.replace("<br/>", "\n")
                    em = discord.Embed(
                        title=f"{scinfo[0].SCHUL_NM} | {diet_dict[values]}",
                        description=f"```fix\n{meal}```"
                    )
                    await interaction.edit_origin(embed=em, components=[
                        self.bot.components_manager.add_callback(
                            Select(
                                options=[
                                    SelectOption(label="조식", value="1", emoji="🌅"),
                                    SelectOption(label="중식", value="2", emoji="☀"),
                                    SelectOption(label="석식", value="3", emoji="🌙")
                                ],
                            ),
                            callback,
                        )
                    ])

            await msg.delete()
            await ctx.send(
                "조회할 급식을 선택해주세요.",
                components=[
                    self.bot.components_manager.add_callback(
                        Select(
                            options=[
                                SelectOption(label="조식", value="1", emoji="🌅"),
                                SelectOption(label="중식", value="2", emoji="☀"),
                                SelectOption(label="석식", value="3", emoji="🌙")
                            ],
                        ),
                        callback,
                    )
                ]
            )

    @commands.command(name="단축")
    async def shorturl(self, ctx, *, orgurl):
        res = await N.ShortUrl(url=orgurl)
        print(res)
        if res["code"] == '200':
            embed = discord.Embed(title="단축성공! ✅")
            if len(orgurl) > 100:
                call_url = f'{orgurl[:100]}...'
            else:
                call_url = orgurl
            embed.add_field(name=f"요청한 원본링크: {call_url}", value="** **", inline=False)
            embed.add_field(name=f"단축된 링크: {res['result']['url']}", value="\n** **", inline=False)
            embed.add_field(name="단축된 링크QR이미지", value="** **", inline=False)
            embed.set_image(url=f"{res['result']['url']}.qr")
            await ctx.reply(embed=embed)
        else:
            embed = discord.Embed(title=f"ERROR..단축실패 ❌\n에러코드: {res['code']}",description="에러메시지: " + res["message"])
            if len(orgurl) > 100:
                call_url = f'{orgurl[:100]}...'
            else:
                call_url = orgurl
            embed.add_field(name=f"요청한 원본링크: {call_url}", value="** **", inline=False)
            await ctx.reply(embed=embed)

    @commands.command(name="영화검색")
    async def search_movie(self, ctx, *, query):
        global emoji_star, ST_AR1, AC
        a = await N.Movie(query=query)
        print(a)
        embed = discord.Embed(colour=discord.Colour.blue())
        num = 1
        for i in a["items"][:3]:
            director = i["director"]
            direct = str(director).replace("|", "\n")
            actor = i["actor"]
            act = str(actor).replace("|", "\n")
            if i["subtitle"] == '':
                sub = 'ERROR! (정보없음)'
            else:
                sub = i["subtitle"]
            title = i["title"]
            tit = title.replace("<b>", "")
            ti = tit.replace("</b>", "")
            embed.add_field(name=f'#{str(num)}\n제목: **{ti}({sub})**', value='** **', inline=False)
            embed.add_field(name="개봉일", value=i["pubDate"])
            dire = f'{act[:10]}...'
            num += 1

            star = i["userRating"]
            STAR1 = star[:1]
            STAR2 = star[2:3]
            if int(STAR2) >= 5:
                ST_AR1 = int(STAR1) + 1
                print(ST_AR1)
            elif int(STAR2) <= 4:
                ST_AR1 = int(STAR1) + 0
                print(ST_AR1)

            if ST_AR1 == 0:
                emoji_star = '☆☆☆☆☆'
                print('0')
            elif ST_AR1 == 1 or ST_AR1 == 2:
                emoji_star = '★☆☆☆☆'
                print('1')
            elif ST_AR1 == 3 or ST_AR1 == 4:
                emoji_star = '★★☆☆☆'
                print('2')
            elif ST_AR1 == 5 or ST_AR1 == 6:
                emoji_star = '★★★☆☆'
                print('3')
            elif ST_AR1 == 7 or ST_AR1 == 8:
                emoji_star = '★★★★☆'
                print('4')
            elif ST_AR1 == 9 or ST_AR1 == 10:
                emoji_star = '★★★★★'
                print('5')
            print(STAR1)
            embed.add_field(name="평점", value=f'{STAR1}.{STAR2}점, 별점: {emoji_star}({ST_AR1}점)')
            embed.add_field(name="감독", value=dire, inline=False)
            if act == '':
                embed.add_field(name="배우", value='ERROR! (정보없음)', inline=False)
            else:
                embed.add_field(name="배우", value=act, inline=False)
                if len(act) > 15:
                    embed.add_field(name="배우", value=f'{act[:15]}...', inline=False)
            embed.add_field(name="바로가기", value=f"[자세한 내용 보러가기]({i['link']})\n[포스터보러가기]({i['image']})\n{'-----' * 10}")
            embed.set_footer(text='별점은 소숫점1의 자리에서 반올림한 값으로 계산합니다.')
            print(i["userRating"])
        await ctx.send(embed=embed)

    @commands.command(name="뉴스검색")
    async def search_news(self, ctx, *, search):
        a = await N.News(query=search)
        print(a)
        embed = discord.Embed(title='뉴스 검색결과!')
        num = 0
        for i in a["items"][:3]:
            title = i["title"]
            tit = str(title).replace("<b>", "")
            ti = tit.replace("</b>", "")
            T = ti.replace("&quot;", "")
            link = i["originallink"]
            des = i["description"]
            d_e = des.replace("</b>", "")
            d = d_e.replace("<b>", "")
            D = d.replace("&quot;", "")
            DE = D.replace("&amp;", "")
            num += 1
            '''b = str(a["total"])
            c = b[:1]
            d = b[2:5]
            e = b[6:9]'''
            embed.add_field(name=f"#{str(num)}", value=f'기사제목- {str(T)}', inline=False)
            embed.add_field(name="미리보기", value=str(DE), inline=False)
            embed.add_field(name="게시일", value=i["pubDate"][:-6])
            embed.add_field(name="** **", value=f"[자세한 내용 보러가기](<{str(link)}>)\n{'-----' * 10}", inline=False)
            embed.set_footer(text=f'검색된 뉴스 기사 총갯수: {a["total"]}개')
        await ctx.send(embed=embed)
        # await ctx.send(f'{title}\n{link}\n{des}')

    @commands.command(name="카페검색")
    async def search_cafe(self, ctx, *, search):
        a = await N.Cafe(query=search)
        print(a)
        embed = discord.Embed(title=f'카페 게시글 검색결과!\n{"-----" * 10}')
        num = 0
        for i in a["items"][:3]:
            title = i["title"]
            tit = str(title).replace("<b>", "")
            ti = tit.replace("</b>", "")
            T = ti.replace("&quot;", "")
            link = i["link"]
            des = i["description"]
            d_e = des.replace("</b>", "")
            d = d_e.replace("<b>", "")
            D = d.replace("&quot;", "")
            DE = D.replace("&amp;", "")
            num += 1
            embed.add_field(name=f"#{str(num)}\n제목", value=str(T), inline=False)
            embed.add_field(name="미리보기", value=str(DE), inline=False)
            embed.add_field(name="바로가기", value=f"[자세한 내용 보러가기](<{str(link)}>)", inline=False)
            embed.set_footer(text=f'검색된 카페 게시글 총갯수: {a["total"]}개')
        await ctx.send(embed=embed)

    @commands.command(name="웹검색")
    async def search_web(self, ctx, *, search):
        a = await N.Webkr(query=search)
        print(a)
        embed = discord.Embed(title=f'네이버 검색결과!\n{"-----" * 10}')
        num = 0
        for i in a["items"][:3]:
            title = i["title"]
            tit = str(title).replace("<b>", "")
            ti = tit.replace("</b>", "")
            T = ti.replace("&quot;", "")
            link = i["link"]
            des = i["description"]
            d_e = des.replace("</b>", "")
            d = d_e.replace("<b>", "")
            D = d.replace("&quot;", "")
            DE = D.replace("&amp;", "")
            num += 1
            embed.add_field(name=f"#{str(num)}\n제목", value=str(T), inline=False)
            embed.add_field(name="미리보기", value=str(DE), inline=False)
            embed.add_field(name="바로가기", value=f"[자세한 내용 보러가기](<{str(link)}>)", inline=False)
            embed.set_footer(text=f'검색된 총갯수: {a["total"]}개')
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Search(bot))
