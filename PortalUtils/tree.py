import traceback
from logging import getLogger

from discord import AppCommandType, Interaction, InteractionType, NotFound
from discord.app_commands import CommandTree
from discord.app_commands.errors import CheckFailure, CommandInvokeError

log = getLogger(__name__)


class CommandTree(CommandTree):
    """
    A subclass of `discord.app_commands.CommandTree` with additional error handling and interaction checks.
    """

    async def on_error(self, interaction: Interaction, error: Exception):
        """
        Handles errors that occur during command invocation and sends them to the `error_logs` channel.

        Parameters
        ----------
        interaction: Interaction
            The interaction that triggered the command.
        error: Exception
            The error that occurred.
        """
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

    async def interaction_check(self, interaction: Interaction) -> bool:
        """
        Optionally pre-defers the response to an interaction.

        Parameters
        ----------
        interaction: Interaction
            The interaction to check.
        """
        defer = False
        if (
            interaction.type == InteractionType.application_command
            and getattr(interaction.command, "type", AppCommandType.chat_input) == AppCommandType.chat_input
        ):
            command, _ = self._get_app_command_options(interaction.data)
            defer = command.extras.get("defer", False)
        if defer:
            await interaction.response.defer(
                thinking=True, ephemeral=True
            )  # First followup ALWAYS matches state of defer!
        return True
