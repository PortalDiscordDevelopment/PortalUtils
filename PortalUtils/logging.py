import inspect
import discord
import DPyUtils
from discord.ext import commands


class Logging(commands.Cog):
    """
    Logs bot stuff.
    """

    def __init__(self, bot: DPyUtils.Bot):
        self.bot = bot

    @commands.Cog.listener("on_guild_join")
    @commands.Cog.listener("on_guild_remove")
    async def guild_logs(self, guild: discord.Guild):
        log = self.bot.get_channel(self.bot.guild_logs)
        if log is None:
            self.bot.extra_events["on_guild_join"].remove(self.guild_logs)
            self.bot.extra_events["on_guild_remove"].remove(self.guild_logs)
            return
        jl, clr = (
            ("Joined", "green") if self.bot.get_guild(guild.id) else ("Left", "red")
        )
        owner = guild.owner
        if not owner:
            owner = await self.bot.fetch_user(guild.owner_id)
        await log.send(
            embed=discord.Embed(
                title=f"{jl} Server",
                color=getattr(discord.Color, clr)(),
                description=f"""
Guild Name: `{guild}`
Guild ID: `{guild.id}`
Owner: `{owner}` (`{owner.id}`){f'''
Humans: `{len([m for m in guild.members if not m.bot])}`
Bots: `{len([m for m in guild.members if m.bot])}`''' if self.bot.intents.members else ''}
Total Guilds: `{len(self.bot.guilds)}`""",
            )
        )

    @commands.Cog.listener("on_command")
    async def command_logs(self, ctx: DPyUtils.Context):
        log = self.bot.get_channel(self.bot.command_logs)
        if log is None:
            self.bot.extra_events["on_command"].remove(self.command_logs)
            return
        if ctx.command.qualified_name.split()[0] == "jishaku":
            return
        cmd = ctx.prefix + " ".join((*ctx.invoked_parents, ctx.invoked_with))
        args = [
            x for x in ctx.args if not isinstance(x, (commands.Cog, commands.Context))
        ]
        c = ctx.message.content.replace(cmd, "").strip()
        for a in args:
            c = c.replace(c.split()[0], "")
        args.append(c.strip())
        sig = []
        params = {
            k: v for k, v in ctx.command.params.items() if k not in ("self", "ctx")
        }
        argi = 0
        npt = []
        for name, param in params.items():
            types = [str if param.annotation is inspect._empty else param.annotation]
            if ags := getattr(param.annotation, "__args__", None):
                types = [x for x in ags if x.__name__ != "NoneType"]
            types = tuple(types)
            if isinstance(args[argi], types):
                sig.append(name)
                argi += 1
            npt.append((name, param, types))
        argi = 0
        newargs = []
        for name, param, types in npt:
            if param.kind.numerator != 2:
                newargs.append(args[argi])
                argi += 1
                continue
            temp = []
            while isinstance(args[argi], types):
                temp.append(args[argi])
                argi += 1
            newargs.append(" ".join(map(str, temp)))
        await log.send(
            embed=discord.Embed(
                title="Command Ran",
                description=f"""
User: `{ctx.author}` (`{ctx.author.id}`)
Guild: `{ctx.guild}`{f" (`{ctx.guild.id}`)" if ctx.guild else ''}
Channel: `{ctx.channel if not isinstance(ctx.channel, discord.DMChannel) else "DM or Slash-Only Context"}` (`{ctx.channel.id}`)
Message: [`{ctx.message.id}`]({ctx.message.jump_url})
Command: `{cmd} {' '.join(':'.join(a) for a in zip(sig, map(str, newargs)))}`""",
                color=discord.Color.dark_green(),
            )
        )


def setup(bot: DPyUtils.Bot):
    bot.add_cog(Logging(bot))
