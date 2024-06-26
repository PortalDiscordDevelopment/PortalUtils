from discord.ext import commands

from .bot import Bot


class CustomMinimalHelp(commands.MinimalHelpCommand):
    """
    A subclass of `discord.ext.commands.MinimalHelpCommand` that sends the help message as a single embed.
    """

    async def send_pages(self):
        desc = ""
        for page in self.paginator.pages:
            desc += page
        await self.context.send(embed=self.context.bot.Embed(description=desc))


async def setup(bot: Bot):
    bot.help_command = CustomMinimalHelp(command_attrs={"name": "help"}, verify_checks=False)
