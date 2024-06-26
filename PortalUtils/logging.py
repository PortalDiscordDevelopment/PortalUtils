import inspect

from discord import Color, DMChannel, Embed, Guild, Interaction, app_commands
from discord.ext import commands
from discord.utils import utcnow
from DPyUtils import Context

from .bot import Bot


class Logging(commands.Cog):
    """
    Logs bot stuff.
    """

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.Cog.listener("on_guild_join")
    @commands.Cog.listener("on_guild_remove")
    async def guild_logs(self, guild: Guild):
        """
        Logs guild joins and leaves to the `guild_logs` channel.

        Parameters
        ----------
        guild: Guild
            The guild that was joined or left.
        """
        log = self.bot.get_channel(self.bot.guild_logs)
        if log is None:
            self.bot.extra_events["on_guild_join"].remove(self.guild_logs)
            self.bot.extra_events["on_guild_remove"].remove(self.guild_logs)
            return
        jl, clr = ("Joined", "green") if self.bot.get_guild(guild.id) else ("Left", "red")
        owner = guild.owner
        if not owner and guild.owner_id is not None:
            owner = await self.bot.fetch_user(guild.owner_id)
        await log.send(
            embed=Embed(
                title=f"{jl} Server",
                color=getattr(Color, clr)(),
                description=f"""
Guild Name: `{guild}`
Guild ID: `{guild.id}`
Owner: `{owner}` (`{guild.owner_id}`){f'''
Humans: `{len([m for m in guild.members if not m.bot])}`
Bots: `{len([m for m in guild.members if m.bot])}`''' if self.bot.intents.members else ''}
Total Guilds: `{len(self.bot.guilds)}`""",
            )
        )

    # @commands.Cog.listener("on_command")
    # TODO: figure out what's going on with this; clean it up for only slash commands
    async def command_logs(self, ctx: Context):
        """
        Logs message commands to the `command_logs` channel.

        Parameters
        ----------
        ctx: Context
            The command context.
        """
        log = self.bot.get_channel(self.bot.command_logs)
        if log is None:
            self.bot.extra_events["on_command"].remove(self.command_logs)
            return
        if ctx.command.qualified_name.split()[0] == "jishaku":
            return
        cmd = ctx.prefix + " ".join((*ctx.invoked_parents, ctx.invoked_with))
        args = [x for x in ctx.args if not isinstance(x, (commands.Cog, commands.Context))]
        c = ctx.message.content.replace(cmd, "").strip()
        for a in args:
            c = c.replace(c.split()[0], "")
        args.append(c.strip())
        params = {k: v for k, v in ctx.command.params.items() if k not in ("self", "ctx")}
        argi = 0
        sig = []
        newargs = []
        for name, param in params.items():
            if argi >= len(args):
                break
            types = [str if param.annotation is inspect._empty else param.annotation]
            if ags := getattr(param.annotation, "__args__", None):
                types = [x for x in ags if x.__name__ != "NoneType"]
            types = tuple(types)
            if isinstance(args[argi], types) and param.kind.numerator != 2:
                sig.append(name)
                newargs.append(args[argi])
                argi += 1
                continue
            temp = []
            while isinstance(args[argi], types) and argi < len(args):
                temp.append(args[argi])
                argi += 1
            newargs.append(" ".join(map(str, temp)))
        await log.send(
            embed=Embed(
                title="Command Ran",
                description=f"""
User: `{ctx.author}` (`{ctx.author.id}`)
Guild: `{ctx.guild}`{f" (`{ctx.guild.id}`)" if ctx.guild else ''}
Channel: `{ctx.channel if not isinstance(ctx.channel, DMChannel) else "DM or Slash-Only Context"}` (`{ctx.channel.id}`)
Message: [`{ctx.message.id}`]({ctx.message.jump_url})
Command: `{cmd} {' '.join(':'.join(a) for a in zip(sig, map(str, newargs)))}`""",
                color=Color.dark_green(),
            )
        )

    @commands.Cog.listener("on_app_command")
    async def app_command_logs(self, interaction: Interaction, command: app_commands.Command):
        """
        Logs application commands to the `command_logs` channel.

        Parameters
        ----------
        interaction: Interaction
            The interaction that triggered the command.
        command: app_commands.Command
            The command that was triggered.
        """
        log = self.bot.get_channel(self.bot.command_logs)
        if log is None:
            self.bot.extra_events["on_app_command"].remove(self.app_command_logs)
            return
        await log.send(
            embed=Embed(
                title="Command Ran",
                description=f"""
User: `{interaction.user}` (`{interaction.user.id}`)
Guild: `{interaction.guild}`{f" (`{interaction.guild.id}`)" if interaction.guild else ''}
Channel: [`{f"#{interaction.channel}" if not isinstance(interaction.channel, DMChannel) else "DM or Slash-Only Context"}`]({interaction.channel.jump_url}) (`{interaction.channel.id}`)
Command: `/{command.qualified_name} {' '.join(f"{k}:{v}" for k, v in interaction.namespace.__dict__.items())}`""",
                color=Color.dark_green(),
                timestamp=utcnow(),
            ).set_footer(icon_url=interaction.user.display_avatar.url)
        )

    @commands.Cog.listener("on_command_error")
    async def error_logs(self, ctx: Context, err: Exception):
        """
        Prints command errors to the console.

        Parameters
        ----------
        ctx: Context
            The command context.
        err: Exception
            The error that occurred.
        """
        print(ctx.channel, ctx.author, err)


async def setup(bot: Bot):
    await bot.add_cog(Logging(bot))
