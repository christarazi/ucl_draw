# Copyright (C) 2017 Chris Tarazi
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''
This file contains the simulator code for simulating the Round of 16 in the
UEFA Champions League for the 2016-2017 season.
'''

from collections import defaultdict
import sys
import random
import copy

group_winners = [
    ("A", "ENG", "Manchester United"),
    ("B", "FRA", "PSG"),
    ("C", "ITA", "AS Roma"),
    ("D", "SPA", "FC Barcelona"),
    ("E", "ENG", "Liverpool"),
    ("F", "ENG", "Manchester City"),
    ("G", "TUR", "Besiktas"),
    ("H", "ENG", "Tottenham Hotspur")
]

group_runners = [
    ("A", "SWT", "FC Basel"),
    ("B", "GER", "Bayern Munich"),
    ("C", "ENG", "Chelsea"),
    ("D", "ITA", "Juventus"),
    ("E", "SPA", "Sevilla"),
    ("F", "UKR", "Shakhtar Donetsk"),
    ("G", "POR", "Porto"),
    ("H", "SPA", "Real Madrid")
]

valid_draws = defaultdict(list)  # Holds all valid draws
draws = {}                       # Holds the count of the simulations

# -----------------------------------------------------------------------------
# Private API - only used within this file
# -----------------------------------------------------------------------------


def _init_draws():
    '''
    Initialize |draws| and |valid_draws| to their default values.
    '''
    for winner in group_winners:
        for runner_up in group_runners:
            if winner[0] != runner_up[0] and winner[1] != runner_up[1]:
                draws[(winner, runner_up)] = 0
                valid_draws[runner_up].append(winner)
    return


def _generate_valid_draws(winners, runners_up):
    '''
    Generates all valid draws based on |winners| and |runners_up|.
    Specifically, teams are only matched up if they are from different
    countries and from different groups. For example, Bayern Munich cannot
    draw Borussia Dortmund because they're both from Germany. Similarly,
    Sevilla cannot draw Juventus because they're both in the same group.
    This is what is meant by "generating valid draws". For more info, check out
    UEFA's website on the rules of the draw.

    Returns: dict of valid draws, |vd|
    '''
    vd = defaultdict(list)
    for winner in winners:
        for runner_up in runners_up:
            if winner[0] != runner_up[0] and winner[1] != runner_up[1]:
                vd[runner_up].append(winner)
    return vd


def _get_optimal_draw(vd, runners_up, winners):
    '''
    Ensures that the draw is optimal by forcing certain moves. There are two
    scenarios where a move must be forced:

    1) When a team only has one possible team left to draw.
    This scenario is simple to solve.

    2) When there are multiple runners up which have the same winner in
    common.
    This scenario is handled by choosing the winner which occurs the
    least in the pool of runners-up. This is done to prevent conflicts, e.g. if
    the least winner is not chosen, then there will be a duplicate draw. In
    other words, a winner could be drawn to face two different runners-up. If
    you watch the live draw on TV, you'll notice that the administrators will
    do this (if it is necessary) when the draw is halfway through.

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


def _need_optimal_draw(vd, runners_up):
    '''
    Heuristic for avoiding a conflict early on in the draw.
    '''
    # Check if there is a team with less than 3 possibilities.
    for ru in runners_up:
        if len(vd[ru]) < 3:
            return True
    return False


def _simulate_draw():
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
        if (_need_optimal_draw(tmp_valid_draws, tmp_group_runners) or
                len(tmp_group_runners) < 5):
            runner_up, winner = _get_optimal_draw(tmp_valid_draws,
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
        tmp_valid_draws = _generate_valid_draws(tmp_group_winners,
                                                tmp_group_runners)
    return

# -----------------------------------------------------------------------------
# Public API - invoked from outside this file
# -----------------------------------------------------------------------------


def count_possible_draws():
    '''
    This function calculates the total number of possible outcomes in the draw.
    Source:
    https://gist.github.com/joriki/4345452
    http://math.stackexchange.com/q/262629

    Returns: total number of outcomes, |count|
    '''
    count = 0
    paired = [False] * 8        # 8 teams on each side

    # Start of recurse() ------------------------------------------------------
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
    # End of recurse() --------------------------------------------------------

    recurse(0)
    return count


def execute_simulation(n):
    '''
    Executes the simulations |n| times. This function is invoked when the user
    clicks the button to run the simulation.

    Returns: simulation results, list of winners, list of runners up
             |draws|,            |group_winners|, |group_runners|
    '''
    _init_draws()
    for i in range(n):
        _simulate_draw()

    return draws, group_winners, group_runners


def pretty_table(draws):
    '''
    Converts |draws| into a nicely formatted table. |table| is a list of
    sub-lists, with each sub-list containing a winner from |group_winners| and
    all the drawn runners-up from |group_runners|. Each sub-list is sorted by
    the highest odds, so when looking at the table, it is easy to see what is
    the most likely draw.

    Returns: formatted table containing the match ups, |table|
    '''
    table = []
    for w in group_winners:
        matchup = []
        for r in group_runners:
            odds = draws.get((w, r), None)
            if odds and draws[(w, r)] != 0:
                matchup.append((w, r, odds))

        # Sort by highest odds
        table.append(sorted(matchup, key=lambda x: x[2], reverse=True))

    return table
