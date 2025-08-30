import discord
from discord.ext import commands
from config.constants import ROLES, CHANNELS, METIER_NAMES, METIER_COLORS, REGISTRATION_CHANNEL_ID
from utils.logger import logger
from views.registration_view import send_registration_message
from views.shop_view import ShopView

class DiscordService:
    @staticmethod
    async def purge_channel(channel: discord.TextChannel):
        """Purge tous les messages d'un canal."""
        try:
            await channel.purge()
            logger.info(f"Canal {channel.name} purgé avec succès.")
        except Exception as e:
            logger.error(f"Erreur lors de la purge du canal {channel.name}: {e}")

    @staticmethod
    async def send_shop_panel(bot: commands.Bot, merchant_type: str):
        """Envoie le panel marchand dans le canal dédié."""
        channel = bot.get_channel(CHANNELS[merchant_type])
        if not channel:
            logger.error(f"Canal {merchant_type} introuvable.")
            return

        await DiscordService.purge_channel(channel)

        role = channel.guild.get_role(ROLES[merchant_type])
        if role:
            await channel.send(content=f"<@&{role.id}>", embed=discord.Embed(
                title=f"🏪 {METIER_NAMES[merchant_type]}",
                description=f"Bienvenue dans la boutique {METIER_NAMES[merchant_type]} ! Utilisez les boutons ci-dessous pour interagir.",
                color=METIER_COLORS[merchant_type]
            ), view=ShopView(merchant_type, bot))
        else:
            await channel.send(embed=discord.Embed(
                title=f"🏪 {METIER_NAMES[merchant_type]}",
                description=f"Bienvenue dans la boutique {METIER_NAMES[merchant_type]} ! Utilisez les boutons ci-dessous pour interagir.",
                color=METIER_COLORS[merchant_type]
            ), view=ShopView(merchant_type, bot))

        logger.info(f"Panel {merchant_type} envoyé dans le canal {channel.name}.")

    @staticmethod
    async def send_registration_panel(bot: commands.Bot):
        """Envoie le panel d'inscription dans le canal dédié."""
        channel = bot.get_channel(REGISTRATION_CHANNEL_ID)
        if not channel:
            logger.error(f"Canal d'inscription introuvable.")
            return

        await DiscordService.purge_channel(channel)
        embed, view = send_registration_message()
        await channel.send(embed=embed, view=view)
        logger.info(f"Panel d'inscription envoyé dans le canal {channel.name}.")