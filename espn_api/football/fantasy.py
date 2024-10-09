from espn_api.football import League
from operator import attrgetter

# Add award to dict of teams
def award(team_name, award_string):
	if awards.get(team_name) != None:
		awards[team_name].append(award_string)
	else: 
		awards[team_name] = [award_string]

# Print all awards for each team
def printAwards(awards):
	for team in awards:
		print(team)
		for award in awards[team]:
			print(award)
		print()

# Compute highest value for given position(s)
def computeHigh(pos, players, award_string):
	fellas = [x for x in players if x.lineupSlot in pos]
	fellas_dict = {}
	for team in league.teams:
		fellas_dict[team.team_name] = sum(player.points for player in fellas if player.onTeamId == team.team_id)
	fella_team = max(fellas_dict, key=fellas_dict.get)
	award_string = award_string + ' ' + str(fellas_dict[fella_team]) + ')'
	award(fella_team, award_string)

league_id = 306883
league = League(league_id, 2024)
awards = {}
players = []

week = 5
box_scores = league.box_scores(week=week)

week_high = 0
week_high_team = ''
week_low = 200
week_low_team = ''
week_diff = 0
diff_team= ''
winners = {}
losers = {}

# Iterating over matchups
for matchup in box_scores:

	# Make pile of all players to iterate over 
	players += matchup.away_lineup + matchup.home_lineup

	# If away team won, add them to winners, else to losers
	if matchup.away_score > matchup.home_score:
		winners[matchup.away_team.team_name] = matchup.away_score
		losers[matchup.home_team.team_name] = matchup.home_score
	else:
		winners[matchup.home_team.team_name] = matchup.home_score
		losers[matchup.away_team.team_name] = matchup.away_score

	# Compute difference between scores
	temp_week_diff = round(abs(matchup.away_score - matchup.home_score))

	# Computer who won by the most points
	if temp_week_diff > week_diff:
		week_diff = temp_week_diff
		diff_team = matchup.away_team.team_name if matchup.away_score > matchup.home_score else matchup.home_team.team_name
		loss_team = matchup.away_team.team_name if matchup.away_score < matchup.home_score else matchup.home_team.team_name
	
	# Computer who had the highest score of the week
	if matchup.home_score > week_high:
		week_high = matchup.home_score
		week_high_team = matchup.home_team.team_name
	if matchup.away_score > week_high:
		week_high = matchup.away_score
		week_high_team = matchup.away_team.team_name

	# Compute who had the lowest score of the week  	
	if matchup.home_score < week_low:
		week_low = matchup.home_score
		week_low_team = matchup.home_team.team_name
	if matchup.away_score < week_low:
		week_low = matchup.away_score
		week_low_team = matchup.away_team.team_name

# Compute lowest scoring winner
fort_son = min(winners, key=winners.get)

# Compute highest scoring loser
tough_luck = max(losers, key=losers.get)

award(fort_son, 'FORTUNATE SON: Lowest scoring winner (' + str(winners[fort_son]) + ')')
award(tough_luck, 'TOUGH LUCK: Highest scoring loser (' + str(losers[tough_luck]) + ')')
award(week_high_team, 'BOOM GOES THE DYNAMITE: Highest weekly score (' + str(week_high) + ')')
award(week_low_team, 'ASSUME THE POSITION: Lowest weekly score (' + str(week_low) + ')')
award(diff_team, 'TOTAL DOMINATION: Beat opponent by largest margin (' + loss_team + ' by ' + str(week_diff) + ')')

computeHigh('QB', players, 'PLAY CALLER BALLER: QB high ():')

qbs = [x for x in players if x.lineupSlot == 'QB']

# Compute if any QBs had equal num of TDs and INTs
for qb in qbs:
	ints = 0 if qb.stats[week]['breakdown'].get('passingInterceptions') == None else qb.stats[week]['breakdown']['passingInterceptions']
	tds = 0 if qb.stats[week]['breakdown'].get('passingTouchdowns') == None else qb.stats[week]['breakdown']['passingTouchdowns']
	if ints != 0 and tds == ints:
		award(next((x.team_name for x in league.teams if x.team_id == qb.onTeamId), None), 'PERFECTLY BALANCED - ' + qb.name + ' threw equal number of TDs and INTs') 

# Compute TE high
computeHigh(['TE'], players, 'TIGHTEST END - TE high (', )

# Compute D/ST high
computeHigh(['D/ST'], players, 'FORT KNOX - D/ST high (')

# Compute kicker high
computeHigh(['K'], players, 'KICK FAST, EAT ASS - Kicker high (')

# Compute WR corps high
computeHigh(['WR', 'WR/TE'], players, 'DEEP THREAT - WR corps high (')

# Compute RB corps high
computeHigh(['RB'], players, 'PUT THE TEAM ON HIS BACKS - RB corps high (')

# Filter for even numbers
daily_doubles = filter(lambda x: x.lineupSlot not in ['IR', 'BE', 'D/ST'] and x.points >= 2 * x.projected_points, players)
for player in daily_doubles:
	dbl_team = next((y.team_name for y in league.teams if y.team_id == player.onTeamId), None)
	dbl_award_string = 'DAILY DOUBLE - ' + player.name + ' scored >2x projected (' + str(player.points) + ', ' + str(player.projected_points) + ' projected)'
	award(dbl_team, dbl_award_string)

printAwards(awards)
