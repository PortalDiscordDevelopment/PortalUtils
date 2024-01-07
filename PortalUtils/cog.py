from typing import List

from discord import Interaction
from discord.ext.commands import Cog as _Cog

from .bot import Bot


class Cog(_Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    def t(self, key: str, interaction: Interaction, /, **kwargs) -> str:
        module = interaction.command.callback.__module__.split(".")[-1]
        fn = (interaction.command.extras.get("i18n_key", None) or interaction.command.callback.__name__).split("_")
        full_key = ".".join((module, *fn, key))
        return self.bot.t(full_key, locale=interaction.locale, **kwargs)


class GroupCog(Cog):
    __cog_is_app_commands_group__ = True
