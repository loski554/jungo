from discord import app_commands, Interaction, Embed
from discord.ext import commands
from utils.colorsEmbed import COLORS

class HelpCog(commands.Cog):
    def __int__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Affiche toutes les commandes.")
    @app_commands.checks.cooldown(1, 30)
    async def help(self, interaction: Interaction):

        embed = Embed(
            title="[+] COMMANDES",
            color=COLORS["normal"]
        )
        embed.add_field(
            name="Modération", 
            value="`/mute` - Mute un membre\n`/warn` - Avertit un membre\n`/warns` - Historique des warns utilisateur\n`/remove_warn` - Supprime un warn\n`/clear` - Supprime des messages", 
            inline=False
        )
        embed.add_field(
            name="Administration", 
            value="`/setlogchannel` - Définit le channel de log\n`/setautorole` - Définit le rôle par défaut", 
            inline=False
        )
        embed.add_field(
            name="Informations", 
            value="`/userinfo` - Infos d'un membre\n`/autorole` - Affiche le rôle par défaut\n`/help` - Affiche toutes les commandes", 
            inline=False
        )

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(HelpCog(bot))