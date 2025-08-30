# registration_view.py
import discord
from discord.ui import View, Modal, TextInput
from discord import Interaction, Embed
from repositories.user_repository import UserRepository
from utils.helpers import is_valid_steam_id
from utils.logger import logger

class SteamLinkButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="📋 Compléter l'enregistrement",
            style=discord.ButtonStyle.green,
            custom_id="complete_registration"
        )

    async def callback(self, interaction: Interaction):
        user_repo = UserRepository()
        if user_repo.is_user_registered(interaction.user.id):
            await interaction.response.send_message(
                "⚠️ Vous êtes déjà enregistré dans le système M.I.R.A.",
                ephemeral=True
            )
            return
        await interaction.response.send_modal(SteamRegistrationModal())

class SteamRegistrationModal(Modal):
    def __init__(self):
        super().__init__(title="M.I.R.A - Enregistrement Pénitentiaire")
        self.user_repo = UserRepository()
        self.name = TextInput(label="📝 Nom et prénom complet", placeholder="Ex: Jean Dupont", required=True, max_length=100)
        self.age = TextInput(label="🎂 Âge biologique", placeholder="Ex: 32", required=True, max_length=3)
        self.crime = TextInput(label="⚖️ Crime(s) commis", placeholder="Ex: Vol à main armée, trahison", required=True, style=discord.TextStyle.short)
        self.sentence = TextInput(label="⏳ Durée de condamnation", placeholder="Ex: 10 ans", required=True, max_length=50)
        self.steam_id = TextInput(label="🔢 Identité numérique (SteamID64)", placeholder="Ex: 76561198027290903", required=True, min_length=17, max_length=17)
        self.add_item(self.name)
        self.add_item(self.age)
        self.add_item(self.crime)
        self.add_item(self.sentence)
        self.add_item(self.steam_id)

    async def on_submit(self, interaction: Interaction):
        if not is_valid_steam_id(self.steam_id.value):
            await interaction.response.send_message(
                "❌ **Erreur M.I.R.A** : Format d'identité numérique invalide. Doit contenir exactement 17 chiffres.",
                ephemeral=True
            )
            return

        success = self.user_repo.link_steam_id(
            interaction.user.id,
            self.steam_id.value,
            self.name.value,
            self.age.value,
            self.crime.value,
            self.sentence.value
        )

        if not success:
            await interaction.response.send_message(
                "❌ **Erreur M.I.R.A** : Échec de l'enregistrement. Vérifiez votre SteamID.",
                ephemeral=True
            )
            return

        # Envoie un message de confirmation publique
        await interaction.response.send_message(f"✅ **Enregistrement validé, unité {interaction.user.id}**", ephemeral=True)

        # Envoie un message privé avec les informations confidentielles
        try:
            private_embed = Embed(
                title="🔒 ACCÈS AUTORISÉ - M.I.R.A",
                description="Un terminal s'allume devant vous avec un bruit mécanique.\nUn message clignote en vert sur l'écran:",
                color=discord.Color.dark_green()
            )
            private_embed.add_field(
                name="🔊 M.I.R.A (voix synthétique) :",
                value=f"Bienvenue, **{self.name.value}**, âgé de **{self.age.value} ans**, condamné pour **{self.crime.value}** ({self.sentence.value}).\nVotre enregistrement est complet.",
                inline=False
            )
            private_embed.add_field(name="🌐 Adresse IP de l'île", value="176.57.173.98:28702", inline=False)
            private_embed.add_field(name="🔑 Mot de passe d'accès", value="MIRA072025", inline=False)
            private_embed.add_field(name="🎮 SteamID enregistré", value=self.steam_id.value, inline=False)
            private_embed.set_footer(text="⚠️ Ces informations sont confidentielles. Toute divulgation sera punie.")

            await interaction.user.send(embed=private_embed)
        except discord.Forbidden:
            logger.warning(f"Impossible d'envoyer un message privé à {interaction.user} (DM fermés).")
            await interaction.followup.send(
                "⚠️ **Attention** : Vos informations d'accès ont été enregistrées, mais je ne peux pas vous envoyer de message privé (vérifiez vos paramètres Discord).\n"
                "Voici vos informations (à conserver précieusement) :\n"
                f"- **Adresse IP** : 176.57.173.98:28702\n"
                f"- **Mot de passe** : MIRA072025\n"
                f"- **SteamID** : {self.steam_id.value}",
                ephemeral=True
            )

        logger.info(f"Utilisateur {interaction.user.id} ({self.name.value}) a complété son enregistrement.")

def send_registration_message():
    embed = Embed(
        title="ENREGISTREMENT OBLIGATOIRE - M.I.R.A",
        description="*La pièce est froide et stérile. Une voix synthétique résonne:*\n\n**🔊 M.I.R.A :** \"Bienvenue, unité désignée. Complétez votre enregistrement.\"",
        color=discord.Color.dark_red()
    )
    embed.add_field(
        name="📝 **Informations requises**",
        value="**Nom et prénom** : Identité officielle\n"
              "**Âge** : Âge biologique\n"
              "**Crime(s)** : Infractions commises\n"
              "**Durée de peine** : Temps de condamnation\n"
              "**SteamID64** : Votre identité numérique (17 chiffres)",
        inline=False
    )
    embed.set_footer(text="⚠️ Conformité immédiate requise.")
    view = View(timeout=None)
    view.add_item(SteamLinkButton())
    return embed, view