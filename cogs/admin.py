import logging
import aiosqlite
from discord.ext import commands
from discord import app_commands, Interaction, TextChannel, Role, Embed, utils
from utils.database import DB_PATH, get_autorole, get_log_channel
from utils.colorsEmbed import COLORS

cogs_items = ["moderation", "admin", "errorHandler", "events", "user", "help"]

class AdminCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def cogs_autocomplete(self, interaction: Interaction, current: str):
        return [
            app_commands.Choice(name=cog, value=cog)
            for cog in cogs_items
            if current.lower() in cog.lower()
        ][:25]
    
    @app_commands.command(name="reload")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.autocomplete(cog=cogs_autocomplete)
    async def reload(self, interaction: Interaction, cog: str):

        text=f"cog **{cog}** has been reload."

        try:
            await self.bot.reload_extension(f"cogs.{cog}")
            await interaction.response.send_message(text, ephemeral=True)
            logging.info(f"{cog}.py was reloaded.")
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)

    @app_commands.command(name="setlogchannel", description="Définit le channel de logs")
    @app_commands.checks.has_permissions(administrator=True)
    async def setlogchannel(self, interaction: Interaction, channel: TextChannel):
        await interaction.response.defer(ephemeral=True)

        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT INTO config (guild_id, log_channel_id) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET log_channel_id = excluded.log_channel_id",
                (interaction.guild.id, channel.id)
            )
            await db.commit()

            logging.info(f"Channel de logs défini : {channel.name}")
            await interaction.followup.send(f"Channel de logs défini sur {channel.mention}", ephemeral=True)

            embed = Embed(
                title="[+] LOG CHANNEL SET",
                color=COLORS["normal"]
            )
            embed.add_field(name="Channel", value=f"<#{channel.id}>")
            embed.add_field(name="Effectué par", value=interaction.user.mention)
            embed.timestamp = utils.utcnow()
            
            log_channel = await get_log_channel(self.bot, interaction.guild_id)
            if log_channel:
                await log_channel.send(embed=embed)


    @app_commands.command(name="setautorole", description="Définit un rôle pour les nouveau utilisateur.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setautorole(self, interaction: Interaction, role: Role):
        await interaction.response.defer(ephemeral=True)
        log_channel = await get_log_channel(self.bot, interaction.guild_id)

        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT INTO config (guild_id, autorole_id) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET autorole_id = excluded.autorole_id",
                (interaction.guild.id, role.id)
            )
            await db.commit()

            logging.info(f"{role.name} role set by default.")
            await interaction.followup.send(f"Rôle **{role.mention}** enregistré comme rôle par défaut.", ephemeral=True)
        
        embed = Embed(
            title="[+] AUTOROLE SET",
            color=COLORS["normal"]
        )
        embed.add_field(name="Rôle", value=role.mention)
        embed.add_field(name="Effectué par", value=interaction.user.mention)
        embed.timestamp = utils.utcnow()

        if log_channel:
            await log_channel.send(embed=embed)

    @app_commands.command(name="autorole", description="Affiche le role attribué par défaut.")
    @app_commands.checks.has_permissions(administrator=True)
    async def autorole(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)
        role_id = await get_autorole(interaction.guild_id)
        if not role_id:
            await interaction.followup.send("Pas de rôle par défaut définit pour ce serveur.")
            return
        role = interaction.guild.get_role(role_id)
        if role is None:
            await interaction.followup.send("Aucun rôle par défaut trouvé pour ce serveur.")
            return
        await interaction.followup.send(f"{role.mention} est définit par défaut.")

async def setup(bot):
    await bot.add_cog(AdminCog(bot))