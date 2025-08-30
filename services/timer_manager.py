# timer_manager.py
import asyncio
from datetime import datetime, timedelta
import discord
from utils.logger import logger

class TimerManager:
    def __init__(self):
        self.active_timers = {}  # {guild_id: {channel_id: {message_id: end_time}}}
        self.update_tasks = {}   # Pour stocker les tâches de mise à jour

    async def start_timer(self, bot: discord.Client, guild_id: int, channel_id: int, duration_minutes: int, event_name: str):
        """Démarre un timer avec mise à jour toutes les secondes."""
        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        channel = bot.get_channel(channel_id)
        if not channel:
            logger.error(f"Canal {channel_id} introuvable.")
            return False

        # Envoie le message initial
        embed = discord.Embed(
            title=f"⏳ Timer pour : {event_name}",
            description=f"Temps restant : {duration_minutes} minutes",
            color=discord.Color.gold()
        )
        message = await channel.send(embed=embed)

        # Stocke les infos du timer
        if guild_id not in self.active_timers:
            self.active_timers[guild_id] = {}
        if channel_id not in self.active_timers[guild_id]:
            self.active_timers[guild_id][channel_id] = {}
        self.active_timers[guild_id][channel_id][message.id] = end_time

        # Démarre la tâche de mise à jour
        self.update_tasks[(guild_id, channel_id, message.id)] = bot.loop.create_task(
            self._update_timer(bot, guild_id, channel_id, message.id, event_name)
        )
        return True

    async def _update_timer(self, bot: discord.Client, guild_id: int, channel_id: int, message_id: int, event_name: str):
        """Met à jour le timer toutes les secondes."""
        try:
            while True:
                channel = bot.get_channel(channel_id)
                if not channel:
                    break

                # Récupère le message existant
                try:
                    message = await channel.fetch_message(message_id)
                except discord.NotFound:
                    break  # Message supprimé

                end_time = self.active_timers[guild_id][channel_id][message_id]
                remaining = (end_time - datetime.now()).total_seconds()

                if remaining <= 0:
                    # Timer terminé
                    embed = discord.Embed(
                        title=f"🔔 Événement : {event_name}",
                        description="**L'événement commence MAINTENANT !**",
                        color=discord.Color.green()
                    )
                    await message.edit(embed=embed)
                    await channel.send(f"@everyone {event_name} commence maintenant !")

                    # Nettoyage
                    del self.active_timers[guild_id][channel_id][message_id]
                    if (guild_id, channel_id, message_id) in self.update_tasks:
                        del self.update_tasks[(guild_id, channel_id, message_id)]
                    break

                # Calcul du temps restant
                minutes, seconds = divmod(int(remaining), 60)
                hours, minutes = divmod(minutes, 60)

                # Met à jour l'embed
                embed = discord.Embed(
                    title=f"⏳ Timer pour : {event_name}",
                    description=f"Temps restant : **{hours:02d}:{minutes:02d}:{seconds:02d}**",
                    color=discord.Color.gold()
                )
                await message.edit(embed=embed)
                await asyncio.sleep(1)  # Attend 1 seconde

        except Exception as e:
            logger.error(f"Erreur dans la mise à jour du timer: {e}")
            if (guild_id, channel_id, message_id) in self.update_tasks:
                del self.update_tasks[(guild_id, channel_id, message_id)]

    async def cancel_timer(self, guild_id: int, channel_id: int, message_id: int):
        """Annule un timer en cours."""
        if (guild_id, channel_id, message_id) in self.update_tasks:
            self.update_tasks[(guild_id, channel_id, message_id)].cancel()
            del self.update_tasks[(guild_id, channel_id, message_id)]
            if guild_id in self.active_timers and channel_id in self.active_timers[guild_id] and message_id in self.active_timers[guild_id][channel_id]:
                del self.active_timers[guild_id][channel_id][message_id]
            return True
        return False