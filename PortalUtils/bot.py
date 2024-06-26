import os
from typing import Union

import aiohttp
import aiosqlite
import jishaku
from discord import Color, Embed
from discord.ext import commands
from DPyUtils import load_extensions

from .tree import CommandTree

for f in ["NO_UNDERSCORE", "HIDE", "FORCE_PAGINATOR"]:
    setattr(jishaku.Flags, f, True)


class Embed(Embed):
    """
    A subclass of discord.Embed with an optional default color.
    Adds a default footer with the Portal Development copyright.
    """

    _default_color: Union[Color, int]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._footer = {"text": "\u00a9 2024 Portal Development. All rights reserved - /info"}
        self.color = self.color or self._default_color  # pylint: disable=no-member


class EEmbed(Embed):
    """
    A subclass of Embed with a default color of red.
    """

    def __init__(self, **kwargs):
        self._default_color = Color.red()
        super().__init__(**kwargs)


class PortalBotMixin:
    """
    A mixin for Bot and AutoShardedBot.

    Parameters
    ----------
    color: Union[Color, int]
        The default color for Embeds.
    error_logs: int
        The channel ID for error logs.
    guild_logs: int
        The channel ID for guild logs.
    command_logs: int
        The channel ID for command logs.
    **kwargs
        See `discord.ext.commands.Bot` or `discord.ext.commands.AutoShardedBot`.

    Attributes
    ----------
    color: Union[Color, int]
        The default color for Embeds.
    error_logs: int
        The channel ID for error logs.
    guild_logs: int
        The channel ID for guild logs.
    command_logs: int
        The channel ID for command logs.
    db: aiosqlite.Connection
        The database connection.
    session: aiohttp.ClientSession
        The aiohttp session.
    Embed: Embed
        The Embed class.
    EEmbed: Embed
        The error Embed class.

    Methods
    -------
    start(*args, **kwargs)
        Loads extensions and starts the bot.
    db_schema(*tables)
        Returns the schema for the given tables."""

    def __init__(
        self,
        *args,
        color: Union[Color, int] = None,
        error_logs: int = 0,
        guild_logs: int = 0,
        command_logs: int = 0,
        **kwargs,
    ):
        kwargs.setdefault("tree_cls", CommandTree)
        super().__init__(*args, **kwargs)
        self.color: Union[Color, int] = color
        self.error_logs = error_logs
        self.guild_logs = guild_logs
        self.command_logs = command_logs

        self.db: aiosqlite.Connection
        self.session: aiohttp.ClientSession
        self.Embed: Embed = Embed
        self.Embed._default_color = self.color
        self.EEmbed = EEmbed

    async def start(self, *args, **kwargs):
        await load_extensions(
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
        """
        Shows the SQLite schema for the given tables.
        If no tables are given, shows the schema for all tables.

        Parameters
        ----------
        tables: str
            The names of the tables to show the schema for."""
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
    """
    A subclass of `discord.ext.commands.Bot` with some default extensions and utilities.
    """

    pass


class AutoShardedBot(PortalBotMixin, commands.AutoShardedBot):
    """
    A subclass of `discord.ext.commands.AutoShardedBot` with some default extensions and utilities.
    """

    pass
