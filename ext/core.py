from typing import Type

import discord
from discord.ext import commands





class KkutbotContext(commands.Context):
    """Custom Context object for kkutbot."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def send(self,
                   content=None,
                   *,
                   tts=False,
                   embed=None,
                   file=None,
                   files=None,
                   delete_after=None,
                   nonce=None,
                   allowed_mentions=None,
                   reference=None,
                   mention_author=None,
                   escape_emoji_formatting=False
                   ) -> discord.Message:
        if escape_emoji_formatting is False:
            content = content.format(**self.bot.dict_emojis()) if content else None
        return await super().send(content=content,
                                  tts=tts,
                                  embed=embed,
                                  file=file,
                                  files=files,
                                  delete_after=delete_after,
                                  nonce=nonce,
                                  allowed_mentions=allowed_mentions,
                                  reference=reference,
                                  mention_author=mention_author
                                  )

    async def reply(self, content=None, **kwargs) -> discord.Message:
        if not kwargs.get('escape_emoji_formatting', False):
            content = content.format(**self.bot.dict_emojis()) if content else None
        return await super().reply(content=content, **kwargs)


class KkutbotCommand(commands.Command):
    """Custom Commands object for kkutbot."""

    def __init__(self, func, **kwargs):
        super().__init__(func, **kwargs)


def command(name: str = None, cls: Type[commands.Command] = None, **attrs):
    cls = cls or KkutbotCommand

    def decorator(func):
        if isinstance(func, commands.Command):
            raise TypeError('Callback is already a command.')
        if ('user' in func.__annotations__) and (attrs.get('rest_is_raw') is not False):
            rest_is_raw = attrs.pop('rest_is_raw', True)
        else:
            rest_is_raw = attrs.pop('rest_is_raw', False)
        return cls(func, name=name, rest_is_raw=rest_is_raw, **attrs)

    return decorator


commands.command = command  # replace 'command' decorator in 'discord.ext.commands' module




