from discord.ext import commands
from discord import app_commands, Interaction, Member, Embed, utils
from utils.colorsEmbed import COLORS
from utils.database import get_warn_count

class UserCog(commands.Cog):

    def __int__(self, bot):
        self.bot = bot

    @app_commands.command(name="userinfo", description="Affiche les informations d'un utilisateur.")
    async def userinfo(self, interaction: Interaction, target: Member):
        await interaction.response.defer()
        roles = " ".join([role.mention for role in target.roles if role.name != "@everyone"])
        is_mod = interaction.user.guild_permissions.moderate_members

        embed = Embed(
            title=f"{target.display_name} informations",
            color=COLORS["normal"]
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="Rôles", value=f"{roles if roles else "Aucun"}")
        embed.add_field(name="Date du compte", value=f"<t:{int(target.created_at.timestamp())}:D>")
        embed.add_field(name="Rejoint le serveur", value=f"<t:{int(target.joined_at.timestamp())}:D>")
        embed.add_field(name="ID", value=f"`{target.id}`")
        embed.timestamp = utils.utcnow()
        if is_mod:
            nb_warns = await get_warn_count(interaction.guild_id, target.id)
            embed.add_field(name="Warns", value=nb_warns)

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="test")
    async def test(self, interaction: Interaction):
        await interaction.response.defer()

        embed = Embed(
            title="Test",
            description="This an embed test.",
            color=COLORS["normal"]
        )
        embed.set_thumbnail(url="../svg/shield-halved-solid-full.svg")
        embed.timestamp = utils.utcnow()

        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(UserCog(bot))