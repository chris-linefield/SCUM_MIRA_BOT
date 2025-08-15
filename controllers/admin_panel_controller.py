# controllers/admin_panel_controller.py
import discord
from discord.ui import View, Button
from discord import Interaction, Embed
from controllers.balance_controller import BankBalanceButton
from controllers.delivery_controller import DeliveryButton

def send_admin_panel_message():
    embed = Embed(
        title="🛠️ **Panel Administration - M.I.R.A**",
        description=(
            "*Un terminal s'allume devant vous, affichant les options disponibles.*\n\n"
            "**🔹 Actions disponibles :**\n"
            "- Consulter votre solde bancaire\n"
            "- [Admin] Commande Garagiste"
        ),
        color=discord.Color.dark_blue()
    )
    view = View()
    view.add_item(BankBalanceButton())
    view.add_item(DeliveryButton())
    return embed, view

async def setup_admin_panel(bot, channel_id: int):
    channel = bot.get_channel(channel_id)
    if channel:
        embed, view = send_admin_panel_message()
        await channel.send(embed=embed, view=view)
    else:
        print(f"❌ Canal {channel_id} introuvable.")
