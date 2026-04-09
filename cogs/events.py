import logging
from discord.ext import commands
from discord import Embed, utils, Member, Interaction
from utils.database import get_log_channel, get_autorole
from utils.colorsEmbed import COLORS

class EventsCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: Member):
        channel = await get_log_channel(self.bot, member.guild.id)

        if channel is None:
            logging.warning(f"Pas de channel logs pour le serveur: {member.guild.name}.")
            return
        
        embed = Embed(
            title=f"[+] {member.name}",
            color=COLORS["green"]
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Compte créé le", value=f"<t:{int(member.created_at.timestamp())}:D>")
        embed.timestamp = utils.utcnow()

        if channel:
            await channel.send(embed=embed)
        
        autorole_id = await get_autorole(member.guild.id)
        if not autorole_id:
            return
        role = member.guild.get_role(autorole_id)
        if role is None:
            return
        await member.add_roles(role)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = await get_log_channel(self.bot, member.guild.id)

        if channel is None:
            logging.warning(f"Pas de channel logs pour le serveur: {member.guild.name}.")
            return
        
        embed = Embed(
            title=f"[-] {member.name}",
            color=COLORS["red"]
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Compte créé le", value=f"<t:{int(member.created_at.timestamp())}:D>")
        embed.timestamp = utils.utcnow()

        if channel:
            await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(EventsCog(bot))