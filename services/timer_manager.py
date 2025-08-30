import asyncio
from datetime import datetime, timedelta
import discord
from utils.logger import logger

class TimerManager:
    def __init__(self):
        self.active_timers = {}  # {guild_id: {channel_id: {message_id: end_time}}}

    async def start_timer(self, guild_id: int, channel_id: int, duration_minutes: int, event_name: str):
        """Démarre un timer et envoie un message de suivi."""
        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        channel = discord.utils.get(self.bot.get_all_channels(), id=channel_id)
        if not channel:
            logger.error(f"Canal {channel_id} introuvable.")
            return False

        embed = discord.Embed(
            title=f"⏳ Timer pour : {event_name}",
            description=f"Temps restant : {duration_minutes} minutes",
            color=discord.Color.gold()
        )
        message = await channel.send(embed=embed)
        self.active_timers.setdefault(guild_id, {}).setdefault(channel_id, {})[message.id] = end_time

        # Mise à jour du timer toutes les minutes
        self.bot.loop.create_task(self._update_timer(guild_id, channel_id, message.id, event_name))
        return True

    async def _update_timer(self, guild_id: int, channel_id: int, message_id: int, event_name: str):
        """Met à jour le message du timer toutes les minutes."""
        try:
            while True:
                channel = self.bot.get_channel(channel_id)
                if not channel:
                    break

                message = await channel.fetch_message(message_id)
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
                    del self.active_timers[guild_id][channel_id][message_id]
                    break

                minutes, seconds = divmod(int(remaining), 60)
                embed = discord.Embed(
                    title=f"⏳ Timer pour : {event_name}",
                    description=f"Temps restant : {minutes} minutes et {seconds} secondes",
                    color=discord.Color.gold()
                )
                await message.edit(embed=embed)
                await asyncio.sleep(60)  # Mise à jour toutes les minutes
        except Exception as e:
            logger.error(f"Erreur dans la mise à jour du timer: {e}")

    def set_bot(self, bot):
        self.bot = bot
