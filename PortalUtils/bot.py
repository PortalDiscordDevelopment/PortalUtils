import os
from typing import Union

import aiohttp
import aiosqlite
import discord
import DPyUtils
import jishaku
from discord.ext import commands

from .tree import CommandTree

for f in ["NO_UNDERSCORE", "HIDE", "FORCE_PAGINATOR"]:
    setattr(jishaku.Flags, f, True)


class Embed(discord.Embed):
    _default_color: Union[discord.Color, int]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._footer = {"text": "\u00a9 2022 Portal Development. All rights reserved - /info"}
        self.color = self.color or self._default_color  # pylint: disable=no-member


class EEmbed(Embed):
    def __init__(self, **kwargs):
        self._default_color = discord.Color.red()
        super().__init__(**kwargs)


class PortalBotMixin:
    def __init__(
        self,
        *args,
        color: Union[discord.Color, int] = None,
        error_logs: int = 0,
        guild_logs: int = 0,
        command_logs: int = 0,
        **kwargs,
    ):
        kwargs.setdefault("tree_cls", CommandTree)
        super().__init__(*args, **kwargs)
        self.color: Union[discord.Color, int] = color
        self.error_logs = error_logs
        self.guild_logs = guild_logs
        self.command_logs = command_logs

        self.db: aiosqlite.Connection
        self.session: aiohttp.ClientSession
        self.Embed: discord.Embed = Embed
        self.Embed._default_color = self.color
        self.EEmbed = EEmbed

    async def start(self, *args, **kwargs):
        await DPyUtils.load_extensions(
            self,
            directories=[],
            extra_cogs=[
                "jishaku",
                "PortalUtils.logging",
                "PortalUtils.helpc",
                "DPyUtils.ContextEditor2",
            ],
        )
        if "data.db" in os.listdir() and not hasattr(self, "db"):
            async with aiosqlite.connect("data.db") as db, aiohttp.ClientSession() as session:
                self.db = db
                self.session = session
                await super().start(*args, **kwargs)
        else:
            async with aiohttp.ClientSession() as session:
                self.session = session
                await super().start(*args, **kwargs)

    async def db_schema(self, *tables):
        if not hasattr(self, "db"):
            return "Bot has no active DB connection"
        schema = await (
            await self.db.execute(
                "SELECT sql FROM sqlite_master"
                + (" WHERE name IN ({})".format(", ".join(f"'{table}'" for table in tables)) if tables else "")
            )
        ).fetchall()
        fmt = "\n".join(["".join(x) for x in schema if any(x) and not x[0].startswith("sqlite_autoindex")])
        return f"```sql\n{fmt}```"


class Bot(PortalBotMixin, commands.Bot):
    pass


class AutoShardedBot(PortalBotMixin, commands.AutoShardedBot):
    pass
