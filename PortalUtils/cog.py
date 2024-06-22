from typing import List

from discord import Interaction
from discord.ext.commands import Cog as _Cog

from .bot import Bot


class Cog(_Cog):
    """
    A subclass of `discord.ext.commands.Cog` that adds a `t` method for easy translation.

    Parameters
    ----------
    bot: Bot
        The bot instance.

    Methods
    -------
    t(key: str, interaction: Interaction, /, **kwargs) -> str
        Translates the given key using the interaction's locale.
        REQUIRES the bot to have a `t` method.
    """

    def __init__(self, bot: Bot):
        self.bot = bot

    def t(self, key: str, interaction: Interaction, /, **kwargs) -> str:
        """
        Translates the given key using the interaction's locale.
        Loads the full key from the command's callback function and location, then passes it to the bot's `t` method.

        Parameters
        ----------
        key: str
            The partial to translate.
        interaction: Interaction
            The interaction to get the locale from.
        **kwargs
            The keyword arguments to pass to the translation function.
        """
        if not hasattr(self.bot, "t"):
            raise AttributeError(
                "Bot has no method 't'. Configure a translation provider like `python-i18n` and add a `t` method to the bot, then try again."
            )
        module = interaction.command.callback.__module__.split(".")[-1]  # __module__ is cogs.*
        cmd = interaction.command.callback.__name__
        if (cmd_key := interaction.command.extras.get("i18n_key", None)) is not None:
            cmd = cmd_key
        full_key = ".".join((module, *cmd.split("_"), key))
        return self.bot.t(full_key, locale=interaction.locale, **kwargs)


class GroupCog(Cog):
    __cog_is_app_commands_group__ = True
