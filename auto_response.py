import nextcord
import requests
from cachetools import TTLCache

cache = TTLCache(maxsize=5, ttl=300)


async def reply_to_message(message: nextcord.Message):
    if 'is the server down' in message.content.lower():
        online_players = fetch_online()
        if online_players > 0:
            await message.reply(f'According to edenxi.com there are {online_players} players online.')
    else:
        return


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
