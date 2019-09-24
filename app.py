import math
import nflgame

K = 100

def find_player(last_name, first_name = None):
    for k, p in nflgame.players.items():
        if p.last_name == last_name:
            if first_name is None:
                return k, p.team
            else:
                if p.first_name == first_name:
                    return k, p.team
    return None

def is_success(down, distance, yards_gained):
    if down == 1 and yards_gained >= distance * 0.5:
        return True
    elif down == 2 and yards_gained >= distance * 0.7:
        return True
    elif down >= 3 and yards_gained >= distance:
        return True
    return False

def quarterback_success(game, quarterback_id):
    plays = 0
    pos_plays = 0
    neg_plays = 0
    neg_air_success = 0
    pos_air_success = 0
    for p in game.drives.plays():
        down = p.down
        distance = p.yards_togo
        yards_gained = 0
        air_yds = 0
        is_air = False
        is_quarterback = False

        for e in p.events:
            is_quarterback = is_quarterback or e['playerid'] == quarterback_id
            if 'passing_incmp_air_yds' in e:
                air_yds = e['passing_incmp_air_yds']
                is_air = True
            elif 'passing_cmp_air_yds' in e:
                air_yds = e['passing_cmp_air_yds']
                is_air = True
            if 'passing_yds' in e:
                yards_gained = e['passing_yds']

        if not is_quarterback or not is_air:
            continue

        plays += 1

        if is_quarterback and is_air:
            if air_yds > 1:
                pos_plays += 1
                if is_success(down, distance, yards_gained):
                    pos_air_success += 1
            else:
                neg_plays += 1
                if is_success(down, distance, yards_gained):
                    neg_air_success += 1
    
    pay_success_rate = pos_air_success / (pos_plays <= 0 and -1 or pos_plays)
    nay_success_rate = neg_air_success / (neg_plays <= 0 and -1 or neg_plays)
    return {
        'pos_plays': pos_plays,
        'neg_plays': neg_plays,
        'pos_air_success': pos_air_success,
        'neg_air_success': neg_air_success,
        'pos_air_success_rate': pay_success_rate,
        'neg_air_success_rate': nay_success_rate,
    }

mahomes_id = '00-0033873' # find_player('Mahomes')
mason_rudolph_id = '00-0034771'
jackson_id = '00-0034796' # find_player('Jackson', 'Lamar')

player_id, team_id = find_player('Mayfield', 'Baker')

games = nflgame.games(2019, week=[1, 2, 3], home=team_id, away=team_id)

totals = {}
for game in games:
    success = quarterback_success(game, player_id)
    print(game)
    print(success)
    for k, v in success.items():
        if not (k in totals):
            totals[k] = 0
        totals[k] += success[k]
if totals['pos_plays'] > 0:
    print('pos_success_rate', totals['pos_air_success'] / totals['pos_plays'])

if totals['neg_plays'] > 0:
    print('neg_success_rate', totals['neg_air_success'] / totals['neg_plays'])

def third_down_ratings():
    for g in games:
        print(g)
        stats = {
            g.home: {
                'att': 0,
                'success': 0,
                'rating': 1500,
            },
            g.away: {
                'att': 0,
                'success': 0,
                'rating': 1500,
            },
        }
        for p in g.drives.plays():
            if p.down == 3:
                success = False
                expectation = 1 / (math.e ** (p.yards_togo / 8))
                for e in p.events:
                    if 'third_down_att' in e and not 'third_down_failed' in e:
                        success = True
                win = success and 1.0 or 0.0
                stats[p.team]['rating'] += K * (win - expectation)
                stats[p.team]['att'] += 1
                if success:
                    stats[p.team]['success'] += 1
        
        for team, stat in stats.items():
            print(team)
            print(' attempts:', stat['att'])
            print(' pct:', stat['success'] / stat['att'])
            print(' rating:', stat['rating'])
