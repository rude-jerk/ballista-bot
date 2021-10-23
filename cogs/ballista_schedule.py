from random import choice

from nextcord import Embed
from nextcord.ext import commands, tasks

from ballista_time import get_next_ballista_match
from utils import *


class BallistaSchedule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(minutes=31)
    async def announce_ballista(self):
        matches = get_next_ballista_match(5, True)
        now = int(time())

        for match in matches:
            if match['entryStart'] <= now + (12 * 3600):  # within 12 hours
                notification = get_ballista_entry(self.bot.conn, match)
                if notification.recruitment_post == 0:
                    color = choice([match["team1"]["color"], match["team2"]["color"]])
                    recruitment_post = Embed(title=f'Ballista: {match["team1"]["name"]} vs {match["team2"]["name"]}'
                                                   f' <t:{match["start"]}:R>',
                                             color=color)
                    recruitment_post.add_field(name='Level Cap',
                                               value=f'{match["levelCap"] if match["levelCap"] > 0 else "Uncapped"}',
                                               inline=False)
                    recruitment_post.add_field(name='Zone', value=f'{match["zone"]["name"]}', inline=False)
                    recruitment_post.add_field(name='Entry Start', value=f'<t:{match["entryStart"]}:f>')
                    recruitment_post.add_field(name='Entry End', value=f'<t:{match["entryEnd"]}:f>')
                    recruitment_post.add_field(name='Match Start', value=f'<t:{match["start"]}:f>')
                    recruitment_post.add_field(name='Match End', value=f'<t:{match["end"]}:f>')
                    recruitment_post.set_footer(text='React to let others know you\'ll be there and '
                                                     'get a reminder ping 30 minutes before entry!')
                    notification_message = await self.bot.schedule_channel.send(embed=recruitment_post)
                    await notification_message.add_reaction("⚔️")
                    sent_notification = notification._replace(recruitment_post=notification_message.id)
                    if sent_notification:
                        update_ballista_entry(self.bot.conn, match, sent_notification)

    @tasks.loop(minutes=10)
    async def send_reminders(self):
        matches = get_next_ballista_match(5, True)
        now = int(time())

        for match in matches:
            if match['entryStart'] <= now + 1800:
                notification = get_ballista_entry(self.bot.conn, match)
                if notification.reminder == 0:
                    sent_notification = notification._replace(reminder=-1)
                    notification_message = await self.bot.schedule_channel.fetch_message(notification.recruitment_post)
                    users = set()
                    for reaction in notification_message.reactions:
                        async for user in reaction.users():
                            if user.id != self.bot.user.id:
                                users.add(user)
                    if len(users) > 0:
                        message = f'Reminder: `{match["zone"]["name"]}` `{match["team1"]["name"]} vs ' \
                                  f'{match["team2"]["name"]}` `Cap: {match["levelCap"]}` Entry <t:{match["entryStart"]}:R>\n'
                        for user in users:
                            message += f'<@{user.id}>'
                        reminder = await self.bot.schedule_channel.send(message)
                        sent_notification = notification._replace(reminder=reminder.id)

                    update_ballista_entry(self.bot.conn, match, sent_notification)

    @tasks.loop(minutes=18)
    async def reminder_cleanup(self):
        reminders = get_old_reminders(self.bot.conn)
        for reminder in reminders:
            reminder_message = await self.bot.schedule_channel.fetch_message(reminder.reminder)
            await reminder_message.delete()

    @commands.Cog.listener()
    async def on_ready(self):
        self.announce_ballista.start()
        self.send_reminders.start()
        self.reminder_cleanup.start()


def setup(bot):
    bot.add_cog(BallistaSchedule(bot))
