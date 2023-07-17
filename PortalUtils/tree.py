import traceback

from discord import AppCommandType, InteractionType
from discord.app_commands import CommandTree
from discord.app_commands.errors import CheckFailure, CommandInvokeError
from DPyUtils import Interaction


class CommandTree(CommandTree):
    async def on_error(self, interaction: Interaction, error: Exception):
        await interaction.send(error, ephemeral=True)
        if isinstance(error, CommandInvokeError):
            error = error.original
        tb = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        print(tb)
        if isinstance(error, CheckFailure):
            tb = f"{error.__name__.__module}.{error.__name__.__class__}: {error}"
        if cid := getattr(interaction.client, "error_logs", 0):
            await interaction.client.get_channel(cid).send(
                f"{interaction.user} ran {interaction.command.qualified_name} in {interaction.channel.mention} (`{interaction.guild_id}`)\n{interaction.namespace}```py\n{tb}```"
            )

    async def _call(self, interaction: Interaction) -> None:
        defer = True
        if (
            interaction.type == InteractionType.application_command
            and getattr(interaction.command, "type", AppCommandType.chat_input) == AppCommandType.chat_input
        ):
            command, options = self._get_app_command_options(interaction.data)
            defer = command.extras.get("defer", True)
        if defer:
            await interaction.response.defer(thinking=True)
        await super()._call(interaction)
