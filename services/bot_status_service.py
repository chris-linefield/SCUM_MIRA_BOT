import discord
from discord.ui import Button, View
from discord import Embed, Interaction
import asyncio
from datetime import datetime, timedelta  # Ajout de l'import manquant
import psutil

class StatusButton(Button):
    def __init__(self):
        super().__init__(
            label="🔍 Vérifier SCUM",
            style=discord.ButtonStyle.secondary,
            custom_id="check_scum_status"
        )

    async def callback(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)

        try:
            scum_running = "SCUM.exe" in [p.name() for p in psutil.process_iter()]
            status = "✅ **SCUM est en cours d'exécution**" if scum_running else "❌ **SCUM n'est pas en cours d'exécution**"

            embed = Embed(
                title="🔍 Statut de SCUM",
                description=status,
                color=discord.Color.green() if scum_running else discord.Color.red(),
                timestamp=datetime.now()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"⚠️ Erreur: {str(e)}", ephemeral=True)

class BotStatusService:
    def __init__(self, bot, channel_id):
        self.bot = bot
        self.channel_id = channel_id
        self.status_message = None
        self.last_ping = datetime.now()

    async def update_status(self):
        """Met à jour le message de statut avec un Embed"""
        try:
            channel = self.bot.get_channel(self.channel_id)
            if not channel:
                print(f"❌ Canal {self.channel_id} introuvable")
                return

            # Vérifier si SCUM est en cours d'exécution
            scum_running = "SCUM.exe" in [p.name() for p in psutil.process_iter()]

            # Créer l'Embed
            embed = Embed(
                title="🤖 **Statut du Bot M.I.R.A**",
                description="Informations en temps réel sur l'état du bot et de SCUM",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )

            # Ajouter les champs
            embed.add_field(
                name="🟢 Statut du Bot",
                value="**Opérationnel** ✅",
                inline=False
            )

            embed.add_field(
                name="🎮 Statut de SCUM",
                value="**En cours d'exécution** ✅" if scum_running else "**Hors ligne** ❌",
                inline=False
            )

            embed.add_field(
                name="⏱️ Dernier Ping",
                value=f"{self.last_ping.strftime('%d/%m/%Y %H:%M:%S')}",
                inline=False
            )

            embed.add_field(
                name="🔄 Prochaine mise à jour",
                value=f"{(datetime.now() + timedelta(seconds=15)).strftime('%H:%M:%S')}",
                inline=False
            )

            embed.set_footer(text="M.I.R.A - Système de Monitoring | Dernière vérification")

            # Créer la vue avec le bouton
            view = View()
            view.add_item(StatusButton())

            # Mettre à jour ou envoyer le message
            if self.status_message:
                await self.status_message.edit(embed=embed, view=view)
            else:
                self.status_message = await channel.send(embed=embed, view=view)

            self.last_ping = datetime.now()

        except Exception as e:
            print(f"⚠️ Erreur mise à jour statut: {e}")

    async def start_status_updates(self):
        """Démarre la boucle de mise à jour du statut"""
        while True:
            try:
                await self.update_status()
                await asyncio.sleep(15)  # Mise à jour toutes les 15 secondes
            except Exception as e:
                print(f"⚠️ Erreur boucle statut: {e}")
                await asyncio.sleep(15)