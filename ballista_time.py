from math import floor
from time import time
from nextcord import Colour as Color

nations = {
    'sandoria': {'name': 'San d\'Oria', 'color': Color.red()},
    'bastok': {'name': 'Bastok', 'color': Color.blue()},
    'windurst': {'name': 'Windurst', 'color': Color.green()}
}

zones = {
    'jugner': {'name': 'Jugner Forest'},
    'pashhow': {'name': 'Pashhow Marshlands'},
    'meriphataud': {'name': 'Meriphitaud Mountains'}
}


def get_game_date() -> dict:
    now = int(time() * 1000)
    game_now = floor(((now - 1009810800000) * 25) / 60 / 1000)

    return {
        'year': floor(game_now / 518400 + 886),
        'month': (floor(game_now / 43200) % 12) + 1,
        'day': (floor(game_now / 1440) % 30) + 1,
        'weekDay': floor((game_now % 11520) / 1440),
        'hour': floor((game_now % 1440) / 60),
        'minute': floor(game_now % 60)
    }


def increment_game_date(game_date: dict, days_to_increment: int = 1) -> dict:
    if days_to_increment == 0:
        return game_date

    game_date['day'] += days_to_increment
    while game_date['day'] > 30:
        game_date['month'] += 1
        game_date['day'] -= 30
    while game_date['month'] > 12:
        game_date['year'] += 1
        game_date['month'] -= 12
    return game_date


def game_date_to_epoch(year: int, month: int, day: int, hour: int = 0, minute: int = 0) -> int:
    v_time = (year - 886) * 518400 + (month - 1) * 43200 + (day - 1) * 1440 + hour * 60 + minute
    return int(((v_time * 60) / 25 + 1009810800))


def get_ballista_match(game_date: dict) -> dict:
    day = (game_date['day'] - 1) % 6
    month = game_date['month']
    ballista_match = {}

    if day == 1:
        ballista_match['zone'] = zones['jugner']
        if month < 4:
            ballista_match['team1'] = nations['sandoria']
            ballista_match['team2'] = nations['bastok']
        elif month < 8:
            ballista_match['team1'] = nations['bastok']
            ballista_match['team2'] = nations['windurst']
        else:
            ballista_match['team1'] = nations['sandoria']
            ballista_match['team2'] = nations['windurst']
    elif day == 3:
        ballista_match['zone'] = zones['pashhow']
        if month < 4:
            ballista_match['team1'] = nations['bastok']
            ballista_match['team2'] = nations['windurst']
        elif month < 8:
            ballista_match['team1'] = nations['sandoria']
            ballista_match['team2'] = nations['windurst']
        else:
            ballista_match['team1'] = nations['sandoria']
            ballista_match['team2'] = nations['bastok']
    elif day == 5:
        ballista_match['zone'] = zones['meriphataud']
        if month < 4:
            ballista_match['team1'] = nations['sandoria']
            ballista_match['team2'] = nations['windurst']
        elif month < 8:
            ballista_match['team1'] = nations['sandoria']
            ballista_match['team2'] = nations['bastok']
        else:
            ballista_match['team1'] = nations['bastok']
            ballista_match['team2'] = nations['windurst']
    else:
        return {}

    if game_date['day'] < 26:
        ballista_match['levelCap'] = floor((game_date['day'] - 1) / 6) * 10 + 30
    else:
        ballista_match['levelCap'] = 0

    ballista_match['entryStart'] = game_date_to_epoch(game_date['year'], game_date['month'], game_date['day'] - 1, 12)
    ballista_match['entryEnd'] = game_date_to_epoch(game_date['year'], game_date['month'], game_date['day'] - 1, 22)
    ballista_match['start'] = game_date_to_epoch(game_date['year'], game_date['month'], game_date['day'])
    ballista_match['end'] = game_date_to_epoch(game_date['year'], game_date['month'], game_date['day'] + 1)

    return ballista_match


def get_next_ballista_match(matches: int = 1, enter_only: bool = False) -> list:
    now = int(time())
    game_date = get_game_date()
    game_date_i = increment_game_date(game_date, game_date['day'] % 2)
    ballista_matches = []
    i = 0
    while len(ballista_matches) < matches:
        if i > 0:
            game_date_i = increment_game_date(game_date_i, 2)
        match = get_ballista_match(game_date_i)
        while (not enter_only and match['end'] < now) or (enter_only and match['entryEnd'] < now):
            game_date_i = increment_game_date(game_date_i, 2)
            match = get_ballista_match(game_date_i)
        ballista_matches.append(match)
        i += 1
    return ballista_matches


if __name__ == '__main__':
    print(get_next_ballista_match(matches=5, enter_only=True))
