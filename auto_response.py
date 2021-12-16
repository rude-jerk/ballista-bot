import nextcord
import requests
from cachetools import TTLCache

cache = TTLCache(maxsize=5, ttl=120)
reply_cache = TTLCache(maxsize=20, ttl=120)

questions = ['is the server down', ['is', 'server', 'down'], ['is', 'server', 'dead'], ['is', 'eden', 'down']]
ignoreList = [218477886871437313, 343953414335496195, 301558021098569729]


async def reply_to_message(message: nextcord.Message):
    if contains_server_down_question(message.content) and message.author.id not in ignoreList \
            and not is_recent_reply(message.author.id):
        online_players = fetch_online()
        if online_players > 0:
            reply_cache[message.author.id] = 1
            await message.reply(f'According to edenxi.com there are {online_players} players online.')
    else:
        return


def contains_server_down_question(message: str):
    message = message.lower()
    for question in questions:
        if isinstance(question, str):
            if question in message:
                return True
        if isinstance(question, list):
            all_in = True
            for word in question:
                if word not in message.split(' '):
                    all_in = False
            if all_in:
                return True
    return False


def fetch_online():
    try:
        return cache['online_players']
    except KeyError:
        try:
            r = requests.get('https://edenxi.com/api/v1/misc/status', timeout=5)
            if r.status_code == 200:
                online_players = int(r.content)
                cache['online_players'] = online_players
                return online_players
            else:
                return 0
        except:
            return 0


def is_recent_reply(author_id):
    try:
        if reply_cache[author_id] == 1:
            return True
    except:
        pass
    return False
