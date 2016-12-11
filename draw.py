'''
This program runs a simulation of the Round of 16
UEFA Champions League Draw of the 2016-2017 season.

TODO:
    Add functionality to compute the number of possible
    draws as seen here: https://gist.github.com/joriki/4345452
'''

from collections import defaultdict
import sys, random, copy

group_winners = [
    ("A", "ENG", "Arsenal"),
    ("B", "ITA", "Napoli"),
    ("C", "SPA", "Barcalona"),
    ("D", "SPA", "Atletico Madrid"),
    ("E", "FRA", "Monaco"),
    ("F", "GER", "Borussia Dortmund"),
    ("G", "ENG", "Leicester City"),
    ("H", "ITA", "Juventus")
]

group_runners = [
    ("A", "FRA", "PSG"),
    ("B", "POR", "Benfica"),
    ("C", "ENG", "Manchester City"),
    ("D", "GER", "Bayern Munich"),
    ("E", "GER", "Bayer Leverkusen"),
    ("F", "SPA", "Real Madrid"),
    ("G", "POR", "Porto"),
    ("H", "SPA", "Sevilla")
]

if len(sys.argv) != 2:
    print("Usage:", sys.argv[0], "<num of simulations>")
    sys.exit(-1)

valid_draws = defaultdict(list) # Holds all valid draws
draws = {}                      # Holds the count of the simulations
n = int(sys.argv[1])            # Number of simulations

def init_draws():
    for winner in group_winners:
        for runner_up in group_runners:
            if winner[0] != runner_up[0] and winner[1] != runner_up[1]:
                draws[(winner, runner_up)] = 0
                valid_draws[runner_up].append(winner)
    return

def generate_valid_draws(winners, runners_up):
    vd = defaultdict(list)
    for winner in winners:
        for runner_up in runners_up:
            if winner[0] != runner_up[0] and winner[1] != runner_up[1]:
                vd[runner_up].append(winner)
    return vd

def get_optimal_draw(vd, runners_up, winners):
    # First check if there is a team with only
    # one possible, and force that draw
    for ru in runners_up:
        if len(vd[ru]) == 1:
            return ru, vd[ru][0]

    # Otherwise, draw a random runner up and find the
    # least common winner to avoid conflicts
    ru = random.choice(runners_up)
    teams = {}
    # Only choose teams the runner up can draw, init them to zero.
    for team in vd[ru]:
        teams[team] = teams.get(team, 0)

    # Count the occurances of the teams the runner up can draw from above.
    # Return the minimum occuring one to avoid conflicts.
    for r in runners_up:
        for team in vd[r]:
            if team in teams:
                teams[team] = teams.get(team, 0) + 1

    return ru, min(teams, key=teams.get)

def simulate_draw():
    # Make copies of the lists of teams before each simulation
    # TODO: Maybe we can avoid this? Will speed things up.
    tmp_valid_draws = copy.deepcopy(valid_draws)
    tmp_group_runners = copy.deepcopy(group_runners)
    tmp_group_winners = copy.deepcopy(group_winners)

    while tmp_group_runners and tmp_group_winners:
        # When half-way complete, try to avoid conflicts
        if len(tmp_group_runners) < 5:
            runner_up, winner = get_optimal_draw(tmp_valid_draws,
                    tmp_group_runners, tmp_group_winners)
        else:
            # Otherwise, draw a runner up and winner normally
            runner_up = random.choice(tmp_group_runners)
            winner = random.choice(tmp_valid_draws[runner_up])

        # Remove drawn teams from list
        tmp_group_runners.remove(runner_up)
        tmp_group_winners.remove(winner)

        # Counting number of match ups
        draws[(winner, runner_up)] += 1

        # Regenerate valid draws
        tmp_valid_draws = generate_valid_draws(tmp_group_winners,
                tmp_group_runners)

    return

# -----------------------------------------------------------------------------

init_draws()
for i in range(n):
    simulate_draw()

for match, count in draws.items():
    if count != 0:
        print("{:18} {} {:18}".format(match[0][2], "vs", match[1][2]),
                "|", count, "/", n, "=", "{0:.5}".format(count / n))

