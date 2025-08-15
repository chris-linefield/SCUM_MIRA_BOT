import discord
from discord.ui import Button
from discord import Interaction
from controllers.garage_controller import RavitaillementGarageButton

class DeliveryButton(Button):
    def __init__(self):
        super().__init__(
            label="🚚 Commande Garagiste",
            style=discord.ButtonStyle.green,
            custom_id="delivery_command"
        )

    async def callback(self, interaction: Interaction):
        garagiste_button = RavitaillementGarageButton()
        await garagiste_button.callback(interaction)
