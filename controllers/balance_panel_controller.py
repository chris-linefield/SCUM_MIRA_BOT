import discord
from discord.ui import View
from controllers.balance_controller import BankBalanceButton

async def setup_balance_panel(bot, channel_id: int):
    """Configure le panel de solde bancaire accessible à tous"""
    channel = bot.get_channel(channel_id)
    if channel:
        embed = discord.Embed(
            title="💰 Consulter votre solde bancaire",
            description=(
                "Cliquez sur le bouton ci-dessous pour consulter votre solde bancaire SCUM.\n\n"
            ),
            color=discord.Color.gold()
        )
        view = View()
        view.add_item(BankBalanceButton())
        await channel.send(embed=embed, view=view)
    else:
        print(f"❌ Canal {channel_id} introuvable pour le panel de solde")
