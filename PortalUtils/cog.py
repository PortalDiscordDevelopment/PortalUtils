from typing import List

from discord import Interaction
from discord.ext.commands import Cog as _Cog

from .bot import Bot


class Cog(_Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.success = self.embed()
        self.error = self.embed(True)

    def t(self, key: str, interaction: Interaction, **kwargs) -> str:
        newkey = ".".join(
            (
                interaction.command.callback.__module__.split(".")[-1],
                *interaction.command.callback.__name__.split("_"),
                key,
            )
        )
        return self.bot.t(
            newkey,
            guild_id=interaction.guild_id,
            locale=interaction.locale,
            **kwargs,
        )

    def embed(self, is_err: bool = False):
        def do(
            keys: List[str],
            interaction: Interaction,
            *,
            incl_author: bool = True,
            **kwargs,
        ):
            if is_err:
                kwargs.setdefault("title", self.bot.t("errors.error"))
            e = (self.bot.EEmbed if is_err else self.bot.Embed)(
                **{k.replace("desc", "description"): self.t(k, interaction, **kwargs) for k in keys}
            )
            if incl_author:
                e.set_author(name=interaction.user, icon_url=interaction.user.display_avatar)
            return e

        return do


class GroupCog(Cog):
    __cog_is_app_commands_group__ = True
