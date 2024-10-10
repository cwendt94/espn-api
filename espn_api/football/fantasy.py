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

	# Compile list of players at position(s) pos
	filtered_players = [x for x in players if x.lineupSlot in pos]
	filtered_dict = {}

	# Make a dictionary of team_name -> sum of players at that position
	for team in league.teams:
		filtered_dict[team.team_name] = sum(player.points for player in filtered_players if player.onTeamId == team.team_id)
	
	# Compute team with highest value
	top_team = max(filtered_dict, key=filtered_dict.get)
	player_myst = whoWasThat(top_team, filtered_dict[top_team], filtered_players)
	award_string = award_string + player_myst + str(filtered_dict[top_team]) + ')'
	award(top_team, award_string)

# Attempt to match what player did the thing 
def whoWasThat(team_name, score, players):
	team = getTeam(team_name)
	for player in players:
		# print(player.points)
		if player.points == score and player.onTeamId == team.team_id:
			return player.name + ', '
	return ''

# Get team name for a team_id
def getTeamName(id):
	return next((y.team_name for y in league.teams if y.team_id == id), None)

def getTeam(name):
	return next((y for y in league.teams if y.team_name == name), None)

LEAGUE_ID = 306883
YEAR = 2024
league = League(LEAGUE_ID, YEAR)
awards = {}
players = []

week = 5
box_scores = league.box_scores(week=week)

week_high = 0
week_high_team = ''
week_low = 200
week_low_team = ''
week_high_diff = 0
week_low_diff = 200
diff_high_team = ''
diff_low_team = ''
winners = {}
losers = {}

# Iterating over matchups
for matchup in box_scores:

	# Make pile of all players to iterate over 
	players += matchup.away_lineup + matchup.home_lineup

	# If away team won, add the team to winners, else to losers
	if matchup.away_score > matchup.home_score:
		winners[matchup.away_team.team_name] = matchup.away_score
		losers[matchup.home_team.team_name] = matchup.home_score
	else:
		winners[matchup.home_team.team_name] = matchup.home_score
		losers[matchup.away_team.team_name] = matchup.away_score

	if matchup.away_score < 100:
		award(matchup.away_team.team_name, 'SUB-100 CLUB')
	if matchup.home_score < 100:
		award(matchup.home_team.team_name, 'SUB-100 CLUB')

	# Compute difference between scores
	temp_week_high_diff = round(abs(matchup.away_score - matchup.home_score))
	temp_week_low_diff = round(abs(matchup.away_score - matchup.home_score))

	# Computer who won by the most points
	if temp_week_high_diff > week_high_diff:
		week_high_diff = temp_week_high_diff
		diff_high_team = matchup.away_team.team_name if matchup.away_score > matchup.home_score else matchup.home_team.team_name
		loss_high_team = matchup.away_team.team_name if matchup.away_score < matchup.home_score else matchup.home_team.team_name
	
	# Compute who won by the fewest points
	if temp_week_low_diff < week_low_diff:
		week_low_diff = temp_week_low_diff
		diff_low_team = matchup.away_team.team_name if matchup.away_score > matchup.home_score else matchup.home_team.team_name
		loss_low_team = matchup.away_team.team_name if matchup.away_score < matchup.home_score else matchup.home_team.team_name

	# Compute who had the highest score of the week
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

award(fort_son, 'FORTUNATE SON - Lowest scoring winner (' + str(winners[fort_son]) + ')')
award(tough_luck, 'TOUGH LUCK - Highest scoring loser (' + str(losers[tough_luck]) + ')')

award(week_high_team, 'BOOM GOES THE DYNAMITE - Highest weekly score (' + str(week_high) + ')')
award(week_low_team, 'ASSUME THE POSITION - Lowest weekly score (' + str(week_low) + ')')
award(diff_high_team, 'TOTAL DOMINATION - Beat opponent by largest margin (' + loss_high_team + ' by ' + str(week_high_diff) + ')')
award(loss_low_team, 'SECOND BANANA - Beaten by slimmest margin (' + diff_low_team + ' by ' + str(week_low_diff) + ')')
award(diff_low_team, 'GEEKED FOR THE EKE - Beat opponent by slimmest margin (' + loss_low_team + ' by ' + str(week_low_diff) + ')')

computeHigh('QB', players, 'PLAY CALLER BALLER: QB high (')

qbs = [x for x in players if x.lineupSlot == 'QB']

# Compute if any QBs had equal num of TDs and INTs
for qb in qbs:
	ints = 0 if qb.stats[week]['breakdown'].get('passingInterceptions') == None else qb.stats[week]['breakdown']['passingInterceptions']
	tds = 0 if qb.stats[week]['breakdown'].get('passingTouchdowns') == None else qb.stats[week]['breakdown']['passingTouchdowns']
	if ints != 0 and tds == ints:
		plural = 's' if tds > 1 else ''
		award_string = 'PERFECTLY BALANCED - ' + qb.name + ' threw ' + str(int(tds)) + ' TD' + plural + ' and ' + str(int(ints)) + ' INT' + plural
		award(getTeamName(qb.onTeamId), award_string) 

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

# Compute players who scored 2x projected
daily_doubles = filter(lambda x: x.lineupSlot not in ['IR', 'BE', 'D/ST'] and x.points >= 2 * x.projected_points, players)
for player in daily_doubles:
	dbl_award_string = 'DAILY DOUBLE - ' + player.name + ' scored >2x projected (' + str(player.points) + ', ' + str(player.projected_points) + ' projected)'
	award(getTeamName(player.onTeamId), dbl_award_string)

printAwards(awards)
