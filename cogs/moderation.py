import logging
from discord import app_commands, Interaction, Embed, Member, utils, Forbidden
from discord.ext import commands
from datetime import timedelta
from humanfriendly import parse_timespan, InvalidTimespan
from typing import Optional
from utils.database import get_log_channel, add_warn, get_warn_count, get_warns, get_warn, remove_warn
from utils.colorsEmbed import COLORS

class ModerationCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    # CLEAR COMMAND
    @app_commands.command(name="clear", description="Supprime des messages dans le channel")
    @app_commands.describe(
        amount="Nombre de messages a supprimé."
    )
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.checks.cooldown(1, 30)
    async def clear(self, interaction: Interaction, amount: app_commands.Range[int, 5, 100]):
        
        await interaction.response.defer(ephemeral=True)

        log_channel = await get_log_channel(self.bot, interaction.guild_id)

        if log_channel is None:
            logging.warning(f"Pas de channel logs pour le serveur: {interaction.guild.name}.")

        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(
            f"{len(deleted)} messages supprimés.", ephemeral=True
            )

        embed = Embed(
            title="[-] CLEAR",
            description=f"{len(deleted)} messages supprimés.",
            color=COLORS["commands"]
        )
        embed.add_field(name="Channel", value=interaction.channel.mention)
        embed.add_field(name="Modérateur", value=interaction.user.mention)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.timestamp = utils.utcnow()

        if log_channel:
                await log_channel.send(embed=embed)
        
    # MUTE COMMAND
    @app_commands.command(name="mute", description="Mute l'utilisateur une certaine durée.")
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.describe(
        target="Sélectionner un membre à mute.",
        duration="Durée du timeout. (1d, 5m, 10s)",
        reason="Raison du timeout."
    )
    async def mute(self, interaction: Interaction, target: Member, duration: str, reason: Optional[str]):

        await interaction.response.defer(ephemeral=True)
        log_channel = await get_log_channel(self.bot, interaction.guild_id)

        if log_channel is None:
            logging.warning(f"Pas de channel logs pour le serveur: {interaction.guild.name}.")

        try:
            real_duration = parse_timespan(duration)
        except InvalidTimespan:
            await interaction.followup.send(f"`{duration}` is invalid. Format : **1d, 2m, 20s**.", ephemeral=True)

        try:
            await target.timeout(
                utils.utcnow() + timedelta(seconds=real_duration), reason=reason
            )
        except Forbidden:
            await interaction.followup.send(f"Impossible de mute: **{target}**.", ephemeral=True)
        else:
            await interaction.followup.send(f"**{target}** à bien été mute pour {duration}.", ephemeral=True)
            
            embed = Embed(
                title="[+] MUTE INFOS",
                color=COLORS["commands"]
            )
            embed.add_field(name="Modérateur", value=interaction.user.mention)
            embed.add_field(name="Raison", value=f"{reason if reason else "Non fournie"}")
            embed.add_field(name="Utilisateur", value=target.name)
            embed.add_field(name="Durée", value=duration)
            embed.set_thumbnail(url=target.display_avatar.url)
            embed.add_field(name="ID", value=f"`{target.id}`")
            embed.timestamp = utils.utcnow()

            if log_channel:
                await log_channel.send(embed=embed)

    # WARN COMMAND
    @app_commands.command(name="warn", description="Warn un utilisateur.")
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.describe(
        target="Sélectionner un membre à warn.",
        reason="Raison du warn."
    )
    async def warn(self, interaction: Interaction, target: Member, reason: str):
        await interaction.response.defer(ephemeral=True)

        log_channel = await get_log_channel(self.bot, interaction.guild_id)

        # Simple verifications
        if target.id == self.bot.user.id:
            await interaction.followup.send("Vous tenter de warn le Bot.", ephemeral=True)
            return
        if target.id == interaction.user.id:
            await interaction.followup.send("Vous tenter de vous warn.", ephemeral=True)
            return
        if interaction.user.top_role < target.top_role:
            await interaction.followup.send("Vous n'avez pas les permissions.", ephemeral=True)
            return
        
        await add_warn(interaction.guild_id, target.id, interaction.user.id, reason)
        nb_warns = await get_warn_count(interaction.guild_id, target.id)

        embedWarn = Embed(color=COLORS["red"])
        embedWarn.add_field(name="Modérateur", value=interaction.user.mention)
        embedWarn.add_field(name="Nombre de warns", value=nb_warns)
        embedWarn.set_thumbnail(url=target.display_avatar.url)

        if nb_warns >= 5:
            try:
                await target.ban(reason="+5 warns")
            except Forbidden:
                await interaction.followup.send("Impossible de ban ce membre.", ephemeral=True)
                return

            embedWarn.title = "[+] BAN"
            embedWarn.add_field(name="Utilisateur", value=target.name)
            embedWarn.add_field(name="Raison", value=reason)

            await interaction.followup.send(f"{target.mention} a été banni(e) suite à de trop nombreux warn.", ephemeral=True)
        elif nb_warns >= 3:
            try:
                await target.timeout(
                    utils.utcnow() + timedelta(hours=2),
                    reason="+3 warns"
                )
            except Forbidden:
                await interaction.followup.send("Impossible de mute ce membre.", ephemeral=True)
                return

            embedWarn.title = "[+] WARN"
            embedWarn.add_field(name="Utilisateur", value=target.name)
            embedWarn.add_field(name="Raison", value=reason)

            await interaction.followup.send(f"{target.mention} à bien été warn.\n**WARN TOTAL: {nb_warns}**", ephemeral=True)
            
        else:
            embedWarn.title = "[+] WARN"
            embedWarn.add_field(name="Utilisateur", value=target.name)
            embedWarn.add_field(name="Raison", value=reason)

            await interaction.followup.send(f"{target.mention} à bien été warn.\n**WARN TOTAL: {nb_warns}**", ephemeral=True)
        
        
        embedWarn.add_field(name="ID", value=f"`{target.id}`")
        embedWarn.timestamp = utils.utcnow()

        if log_channel:
                await log_channel.send(embed=embedWarn)

    # REMOVE WARN COMMAND
    @app_commands.command(name="remove_warn", description="Retirer un warn existant.")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def remove_warn(self, interaction: Interaction, warn_id: int):
        await interaction.response.defer(ephemeral=True)
        
        warn = await get_warn(warn_id)
        log_channel = await get_log_channel(self.bot, interaction.guild_id)

        if not warn:
            await interaction.followup.send("Aucun warn avec cet ID.")
            return
        if warn[1] != interaction.guild_id:
            await interaction.followup.send("Warn appartenant à un autre serveur.")
            return
        
        await remove_warn(warn_id)
        await interaction.followup.send(f"Warn {warn_id} de l'utilisateur <@{warn[2]}> a bien été supprimé.")

        embed = Embed(
            title="[-] WARN SUPPRIMÉ",
            color=COLORS["commands"]
        )
        embed.add_field(name=f"Warn ID", value=warn_id, inline=False)
        embed.add_field(name="Raison originale", value=warn[4], inline=False)
        embed.add_field(name="Membre ID", value=warn[2], inline=False)
        embed.add_field(name="Modérateur", value=interaction.user.mention, inline=False)
        embed.timestamp = utils.utcnow()

        if log_channel:
            await log_channel.send(embed=embed)

    # PRINT WARNS FROM A USER
    @app_commands.command(name="warns", description="Afficher tout les warns d'un utilisateur.")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warns(self, interaction: Interaction, target: Member):
        await interaction.response.defer(ephemeral=True)

        warns = await get_warns(interaction.guild_id, target.id)

        if not warns:
            await interaction.followup.send(f"{target.mention} n'a pas de warn.")
            return
        
        embed = Embed(
            title=f"Warns de {target.name}",
            color=COLORS["commands"]
        )
        for warn in warns:
            embed.add_field(name=f"Warn #{warn[0]}", value=f"Raison : {warn[4]}\nDate : {warn[5]}" )

        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ModerationCog(bot))
