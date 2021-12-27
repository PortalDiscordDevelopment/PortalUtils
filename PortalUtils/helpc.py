from discord.ext import commands
import DPyUtils


class CustomMinimalHelp(commands.MinimalHelpCommand):
    async def send_pages(self):
        desc = ""
        for page in self.paginator.pages:
            desc += page
        await self.context.send(embed=self.context.bot.Embed(description=desc))


def setup(bot: DPyUtils.Bot):
    bot.help_command = CustomMinimalHelp(
        command_attrs={"name": "help"},
        verify_checks=False,
    )
