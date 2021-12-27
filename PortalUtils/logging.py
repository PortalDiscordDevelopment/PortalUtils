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
                title=f"{jl} {guild}",
                color=getattr(discord.Color, "dark_" + clr)(),
                description=f"""
Guild ID: `{guild.id}`
Owner: `{owner}` (`{owner.id}`)
Humans: `{len([m for m in guild.members if not m.bot])}`
Bots: `{len([m for m in guild.members if m.bot])}`
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
        ran = ctx.message.content.split()
        cmd, args = ran[0], ran[1:]
        sig = [
            a.split("=")[0]
            for a in ctx.command.signature.replace("<", "")
            .replace(">", "")
            .replace("[", "")
            .replace("]", "")
            .split()
        ]
        await log.send(
            embed=discord.Embed(
                title="Command Ran",
                description=f"""
User: `{ctx.author}` (`{ctx.author.id}`)
Guild: `{ctx.guild}`{f" (`{ctx.guild.id}`)" if ctx.guild else ''}
Channel: `{ctx.channel if not isinstance(ctx.channel, discord.DMChannel) else "DM"}` (`{ctx.channel.id}`)
Message: [`{ctx.message.id}`]({ctx.message.jump_url})
Command: `{cmd} {' '.join(':'.join(a) for a in zip(sig, args))}`""",
                color=discord.Color.dark_green(),
            )
        )


def setup(bot: DPyUtils.Bot):
    bot.add_cog(Logging(bot))