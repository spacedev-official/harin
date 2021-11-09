import json
import random
from datetime import timedelta
from typing import Union

import discord
from discord.ext import commands

from ext.config import config

with open('general/wordlist.json', 'r', encoding="utf-8") as f:
    wordlist = json.load(f)

with open('general/DUlaw.json', 'r', encoding="utf-8") as f:
    DU = json.load(f)




def time_convert(time: Union[int, float, timedelta]) -> str:
    if isinstance(time, (int, float)):
        time = timedelta(seconds=time)
    if time.days > 0:
        return f"{time.days}일"
    if time.seconds >= 3600:
        return f"{time.seconds // 3600}시간"
    if time.seconds >= 60:
        return f"{time.seconds // 60}분"
    return f"{time.seconds}초"


def split_string(n: str, unit=2000, t="\n") -> tuple:
    n = n.split(t)
    x = []
    r = []
    for idx, i in enumerate(n):
        x.append(i)
        if idx + 1 == len(n) or sum([len(j) for j in x + [n[idx+1]]]) + len(x) > unit:
            r.append("\n".join(x))
            x = []
    return tuple(r)


def get_word(_word: str) -> list:
    du = get_DU(_word[-1])
    return_list = []
    for x in du:
        if x in wordlist:
            return_list += wordlist[x[-1]]
    return return_list


def get_DU(_word: str) -> list:
    if _word[-1] in DU:
        return DU[_word[-1]]
    else:
        return [_word[-1]]


def is_admin(ctx: commands.Context) -> bool:
    return ctx.author.id in config('admin')


def choose_first_word(special: bool = False) -> str:
    while True:
        random_list = random.choice(list(wordlist.values()))
        bot_word = random.choice(random_list)
        if len(get_word(bot_word)) >= 3:
            if special:
                if len(bot_word) == 3:
                    break
            else:
                break
    return bot_word
