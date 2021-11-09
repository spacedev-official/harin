import random
from typing import List

import discordSuperUtils
from discord.ext import commands


def random_chat(suggest):
    chatlist = [f"혹시 `하린아 {suggest}`를 사용하시려고 한건가요?",
                f"그 명령어는 없는데 `하린아 {suggest}`로 사용해보세요!",
                f"한번 `하린아 {suggest}`로 명령해보세요!"]
    return random.choice(chatlist)


class MyCommandGenerator(discordSuperUtils.CommandResponseGenerator):
    def generate(self, invalid_command: str, suggestion: List[str]) -> str:
        return random_chat(suggest=suggestion[0])


class CommandHint(commands.Cog,discordSuperUtils.CogManager.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ImageManager = discordSuperUtils.ImageManager()
        discordSuperUtils.CommandHinter(bot, MyCommandGenerator())
        super().__init__()


def setup(bot):
    bot.add_cog(CommandHint(bot))
