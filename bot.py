import sqlite3
from os.path import exists, dirname, join

from nextcord.ext import commands

import auto_response
from configuration import config

bot = commands.Bot(description='Ballista Bot!', command_prefix='!', case_insensitive=True, self_bot=False)
dir = dirname(__file__)


def initialize_db() -> sqlite3.Connection:
    conn = sqlite3.connect(join(dir, 'ballista.db'))
    cur = conn.cursor()
    cur.execute(
        '''CREATE TABLE ballista_report (entry_start INTEGER, 
                                         entry_end INTEGER, 
                                         actual_start INTEGER, 
                                         actual_end INTEGER ,
                                         recruitment_post INTEGER, 
                                         reminder INTEGER, 
                                         PRIMARY KEY(entry_start, entry_end, actual_start, actual_end));''')
    cur.close()
    return conn


@bot.event
async def on_ready():
    bot.conn = sqlite3.connect(join(dir, 'ballista.db'))
    bot.schedule_channel = bot.get_channel(config['SCHEDULE_CHANNEL'])
    if not bot.schedule_channel:
        print('ERROR: Could not locate schedule channel')
        exit()
    print(f'Logged in as {bot.user.name}#{bot.user.discriminator} [{bot.user.id}]')


@bot.event
async def on_message(message):
    try:
        await auto_response.reply_to_message(message)
        await bot.process_commands(message)
    except:
        pass


if __name__ == '__main__':
    if not exists(join(dir, 'ballista.db')):
        conn = initialize_db()
        conn.close()

    bot.load_extension('cogs.ballista_schedule')
    bot.run(config['TOKEN'])
