import traceback
from logging import getLogger

from discord import AppCommandType, Interaction, InteractionType, NotFound
from discord.app_commands import CommandTree
from discord.app_commands.errors import CheckFailure, CommandInvokeError

log = getLogger(__name__)


class CommandTree(CommandTree):
    async def on_error(self, interaction: Interaction, error: Exception):
        try:
            await interaction.send("An error occured.")
            await interaction.send(error, ephemeral=True)
        except NotFound as e:
            await interaction.channel.send(
                "An error occured, and the original interaction could not be found.\n{error}"
            )
        if isinstance(error, CommandInvokeError):
            error = error.original
        tb = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        if isinstance(error, (CheckFailure, ValueError)):
            tb = f"{error.__class__.__name__}: {error}"
        log.error(tb)
        if cid := getattr(interaction.client, "error_logs", 0):
            await interaction.client.get_channel(cid).send(
                f"{interaction.user} ran {interaction.command.qualified_name} in {interaction.channel.mention} (`{interaction.guild_id}`)\n{interaction.namespace} ```py\n{tb}```"
            )

    async def interaction_check(self, interaction: Interaction) -> None:
        defer = False
        if (
            interaction.type == InteractionType.application_command
            and getattr(interaction.command, "type", AppCommandType.chat_input) == AppCommandType.chat_input
        ):
            command, options = self._get_app_command_options(interaction.data)
            defer = command.extras.get("defer", False)
        if defer:
            await interaction.response.defer(
                thinking=True, ephemeral=True
            )  # First followup ALWAYS matches state of defer!
        return True
