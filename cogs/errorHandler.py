import logging
from discord.ext import commands
from discord import app_commands, Embed

class ErrorHandlerCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.bot.tree.on_error = self.on_app_command_error

    async def on_app_command_error(self, interaction, error):

        if isinstance(error, app_commands.CommandOnCooldown):
            retry_after = round(error.retry_after)

            if interaction.response.is_done():
                embed = Embed(
                description=f"Cooldown, réessayer dans **{round(retry_after)}s**.",
                color=0x7EFF42
            )
                await interaction.followup.send(
                    embed=embed,
                    ephemeral=True
                )
            else:
                embed = Embed(
                description=f"Cooldown, réessayer dans **{round(retry_after)}s**.",
                color=0x7EFF42
            )
                await interaction.response.send_message(
                    embed=embed,
                    ephemeral=True
                )

        elif isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "Vous n'avez pas les permissions pour cette commande.",
                ephemeral=True
            )

        else:
            logging.error(f"{error}")

async def setup(bot):
    await bot.add_cog(ErrorHandlerCog(bot))