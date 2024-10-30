from espn_api.football import League, Team
import plotly.graph_objects as go
from plotly.colors import n_colors

from espn_api.football.weekly_record import weekly_record

leagues = []

# PCFL
leagues.append(League(league_id=36123815,
                      year=2024,
                      espn_s2="****",
                      swid="****",
                      debug=False))

# JFFFL
leagues.append(League(league_id=1973794,
                      year=2024,
                      espn_s2="****",
                      swid="****",
                      debug=False))


def setup_all_data(league: League):
    # most processing happens here
    populate_weekly_scores(league)

    # sort the list by previous simulated points for getting previous power rank
    league.teams.sort(key=lambda x: x.previous_simulated_points, reverse=True)
    previous_power_rank = 1
    for team in league.teams:
        team.previous_power_rank = previous_power_rank
        previous_power_rank = previous_power_rank + 1

    # sort the list by total simulated points for printing by current power rankings
    league.teams.sort(key=lambda x: (x.simulated_points, x.wins, x.points_for), reverse=True)


def populate_weekly_scores(league: League):
    i = 0
    while i < league.current_week - 1:
        week_i_scores = []
        for team in league.teams:
            week_i_scores.append(team.scores[i])
        week_i_scores.sort()
        for team in league.teams:
            wins = week_i_scores.index(team.scores[i])
            ties = 0
            if week_i_scores.count(team.scores[i]) > 1:
                ties = week_i_scores.count(team.scores[i]) - 1
            losses = len(week_i_scores) - wins - ties - 1
            team.simulated_wins = team.simulated_wins + wins
            team.simulated_losses = team.simulated_losses + losses
            team.simulated_ties = team.simulated_ties + ties
            sim_points = wins + 0.5 * ties
            week = i + 1
            team.weekly_records.append(
                weekly_record(week=week, wins=wins, losses=losses, ties=ties, sim_points=sim_points))
            team.previous_simulated_points = team.simulated_points
            team.simulated_points = team.simulated_points + sim_points
        i = i + 1


def populate_header_vals(league: League):
    header_vals = []
    header_vals.append('<b>Team</b>')
    i = 1
    while i < league.current_week:
        header_vals.append('<b>' + str(i) + '</b>')
        i = i + 1
    header_vals.append('<b>Ovr Record</b>')
    header_vals.append('<b>ESPN Record</b>')
    return header_vals


def populate_weekly_records(team: Team, league: League):
    team_weekly_records = []
    i = 0
    while i < league.current_week - 1:
        team_weekly_records.append(
            str(team.weekly_records[i].wins) + "-" + str(team.weekly_records[i].losses) + "-" + str(
                team.weekly_records[i].ties))
        i = i + 1
    return team_weekly_records


def populate_colors(team: Team, league: League):
    red_colors = n_colors('rgb(200, 0, 0)', 'rgb(255, 200, 200)', len(league.teams) // 2, colortype='rgb')
    green_colors = n_colors('rgb(152,251,152)', 'rgb(34,139,34)', len(league.teams) // 2, colortype='rgb')
    all_colors = red_colors + green_colors
    c = []
    i = 0
    while i < league.current_week - 1:
        c.append(all_colors[team.weekly_records[i].wins])
        i = i + 1
    return c


def calc_ties(team: Team, league: League):
    if team.wins + team.losses == league.current_week - 1:
        return 0
    else:
        return league.current_week - 1 - team.wins - team.losses


# MAIN STARTS HERE
for league in leagues:

    setup_all_data(league)

    header_vals = populate_header_vals(league)

    teams = []
    colors = []
    all_team_weekly_records = []
    tot_rec = []
    espn_rec = []

    for team in league.teams:
        teams.append(team.team_name)
        all_team_weekly_records.append(populate_weekly_records(team, league))
        colors.append(populate_colors(team, league))
        tot_rec.append(str(team.simulated_wins) + "-" + str(team.simulated_losses) + "-" + str(team.simulated_ties))
        espn_rec.append(str(team.wins) + "-" + str(team.losses) + "-" + str(calc_ties(team, league)))

    all_team_weekly_records = list(zip(*all_team_weekly_records))
    colors = list(zip(*colors))
    colors.insert(0, 'white')
    colors.append('white')
    colors.append('white')

    table_cols = [teams]
    for record in all_team_weekly_records:
        table_cols.append(record)
    table_cols.append(tot_rec)
    table_cols.append(espn_rec)

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=header_vals,
            line_color='black', fill_color='grey',
            align='center', font=dict(color='black', size=12)
        ),
        cells=dict(
            values=table_cols,
            fill_color=colors,
            line_color='black',
            align='center', font=dict(color='black', size=11)
        ),
        columnwidth=[2.5, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    )
    ])

    fig.show()
