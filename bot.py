import random
import sqlite3
from time import time
from os.path import exists, dirname, join

from nextcord.ext import commands

import auto_response
from configuration import config

bot = commands.Bot(description='Ballista Bot!', command_prefix='!', case_insensitive=True, self_bot=False)
dir = dirname(__file__)
bot.ping_response_time = time() + 2500
bot.allow_password_request = True
ping_responses = ['ヾ(･ω･*)ﾉ', 'ಠಿヮಠ', '(´⊙ω⊙`)！', 'ᕦ⊙෴⊙ᕤ', '(●´⌓`●)', '( ͡ಠ ʖ̯ ͡ಠ)', '(ﾟ▽ﾟ｀*)?', '(´×ω×`)',
                  '(╯°□°）╯︵ ┻━┻', 'ლ(¯ロ¯"ლ)', '(づ ◕‿◕ )づ', '☆ﾐ(o*･ω･)ﾉ', 'ฅ(^◕ᴥ◕^)ฅ', 'U・ᴥ・U', 'σ( •̀ ω •́ σ)',
                  'ヽ(o´∀`)ﾉ♪♬', ' 	( ͠° ͟ʖ ͡°)', ' 	ʕ ᵔᴥᵔ ʔ']


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
    cur.execute(
        '''CREATE TABLE reset_log (discord_user TEXT,
                                   request_time INTEGER,
                                   user_name TEXT,
                                   character_name TEXT,
                                   email_address TEXT,
                                   submitted TEXT,
                                   PRIMARY KEY(discord_user, request_time));'''
    )
    cur.close()
    return conn


@bot.event
async def on_ready():
    bot.conn = sqlite3.connect(join(dir, 'ballista.db'))
    bot.schedule_channel = bot.get_channel(config['SCHEDULE_CHANNEL'])
    if not bot.schedule_channel:
        print('ERROR: Could not locate schedule channel')
        exit()
    bot.password_channel = bot.get_channel(config['PASSWORD_CHANNEL'])
    if not bot.password_channel:
        print('ERROR: Count not locate password channel')
        exit()
    print(f'Logged in as {bot.user.name}#{bot.user.discriminator} [{bot.user.id}]')


@bot.event
async def on_message(message):
    try:
        await auto_response.reply_to_message(message)
        await bot.process_commands(message)
        if bot.user.mentioned_in(message) and bot.ping_response_time < time() \
                and not message.author.bot and random.randint(1, 10) > 7:
            await message.channel.send(random.choice(ping_responses))
            bot.ping_response_time = time() + random.randint(120, 4500)
    except:
        pass


if __name__ == '__main__':
    if not exists(join(dir, 'ballista.db')):
        conn = initialize_db()
        conn.close()

    bot.load_extension('cogs.ballista_schedule')
    bot.load_extension('cogs.password_reset')
    bot.run(config['TOKEN'])
