import os
from typing import Union
import aiosqlite
import aiohttp
import discord
import DPyUtils


class Embed(discord.Embed):
    _default_color: Union[discord.Color, int]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = self.color or self._default_color  # pylint: disable=no-member


class Bot(DPyUtils.Bot):
    def __init__(
        self,
        *args,
        color: Union[discord.Color, int] = None,
        error_logs: int = 0,
        guild_logs: int = 0,
        command_logs: int = 0,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.color: Union[discord.Color, int] = color
        self.error_logs = error_logs
        self.guild_logs = guild_logs
        self.command_logs = command_logs

        self.db: aiosqlite.Connection
        self.session: aiohttp.ClientSession
        self.Embed: discord.Embed = Embed
        self.Embed._default_color = self.color or discord.Embed.Empty

    async def start(self, *args, **kwargs):
        self.load_extension("jishaku")
        self.load_extension("PortalUtils.logging")
        self.load_extension("PortalUtils.helpc")
        if "data.db" in os.listdir():
            async with aiosqlite.connect(
                "data.db"
            ) as db, aiohttp.ClientSession() as session:
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
                + (
                    " WHERE name IN ({})".format(
                        ", ".join(f"'{table}'" for table in tables)
                    )
                    if tables
                    else ""
                )
            )
        ).fetchall()
        fmt = "\n".join(
            [
                "".join(x)
                for x in schema
                if any(x) and not x[0].startswith("sqlite_autoindex")
            ]
        )
        return f"```sql\n{fmt}```"
