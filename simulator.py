'''
This file contains the simulator code for simulating the Round of 16 in the
UEFA Champions League for the 2016-2017 season.
'''

from collections import defaultdict
import sys
import random
import copy

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

valid_draws = defaultdict(list)  # Holds all valid draws
draws = {}                       # Holds the count of the simulations


def init_draws():
    '''
    Initialize |draws| and |valid_draws| to their default values.
    '''
    for winner in group_winners:
        for runner_up in group_runners:
            if winner[0] != runner_up[0] and winner[1] != runner_up[1]:
                draws[(winner, runner_up)] = 0
                valid_draws[runner_up].append(winner)
    return


def generate_valid_draws(winners, runners_up):
    '''
    Generates all valid draws based on |winners| and |runners_up|.
    Specifically, teams are only matched up if they are from different
    countries and from different groups. For example, Bayern Munich cannot
    draw Borussia Dortmund because they're both from Germany. Similarly,
    Sevilla cannot draw Juventus because they're both in the same group.
    This is what is meant by "generating valid draws".

    Returns: dict of valid draws, |vd|
    '''
    vd = defaultdict(list)
    for winner in winners:
        for runner_up in runners_up:
            if winner[0] != runner_up[0] and winner[1] != runner_up[1]:
                vd[runner_up].append(winner)
    return vd


def get_total_possible_draws():
    '''
    This function calculates the total number of possible outcomes in the draw.
    Source:
    https://gist.github.com/joriki/4345452
    http://math.stackexchange.com/q/262629

    Returns: total number of outcomes, |count|
    '''
    count = 0
    paired = [False] * 8        # 8 teams on each side

    def recurse(n):
        nonlocal count
        if n == 8:
            count += 1
        else:
            for i in range(8):
                if i != n and not paired[i] and \
                        group_winners[n][1] != group_runners[i][1]:
                    paired[i] = True
                    recurse(n + 1)
                    paired[i] = False
    # -------------------------------------------------------------------------
    recurse(0)
    return count


def get_optimal_draw(vd, runners_up, winners):
    '''
    Ensures that the draw is optimal by forcing certain moves such as when
    teams only have one possible draw. Also when the draw is more than halfway
    completed, there are multiple runners up which have the same winner in
    common. To prevent conflicts, the winner which occurs the least in the
    pool of runners up must be chosen. If you watch the live draw on TV, you'll
    notice that the administrators will do this (if it is necessary) when the
    draw is halfway through.

    Returns: a pair (or tuple) of a runner up |ru| and a winner
    '''
    # First check if there is a team with only one possible draw,
    # and force that draw.
    for ru in runners_up:
        if len(vd[ru]) == 1:
            return ru, vd[ru][0]

    # Otherwise, draw a random runner up and find the least common winner to
    # avoid conflicts.
    ru = random.choice(runners_up)
    teams = {}
    # Only choose teams the runner up can draw, init them to zero.
    for team in vd[ru]:
        teams[team] = teams.get(team, 0)

    # Count the occurrences of the teams the runner up can draw from above.
    # Return the minimum occurring one to avoid conflicts.
    for r in runners_up:
        for team in vd[r]:
            if team in teams:
                teams[team] = teams.get(team, 0) + 1

    return ru, min(teams, key=teams.get)


def simulate_draw():
    '''
    Simulates a single draw.
    '''
    # Make copies of the lists of teams before each simulation.
    # Thanks to a comment on reddit for the suggestion.
    tmp_group_winners = copy.copy(group_winners)
    tmp_group_runners = copy.copy(group_runners)
    tmp_valid_draws = copy.copy(valid_draws)

    while tmp_group_runners and tmp_group_winners:
        # When half-way complete, try to avoid conflicts
        if len(tmp_group_runners) < 5:
            runner_up, winner = get_optimal_draw(tmp_valid_draws,
                                                 tmp_group_runners,
                                                 tmp_group_winners)
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


def execute_simulation(n):
    '''
    Executes the simulations |n| times. This function is invoked when the user
    clicks the button to run the simulation.

    Returns: the simulation, |draws|
    '''
    init_draws()
    for i in range(n):
        simulate_draw()

    return draws
