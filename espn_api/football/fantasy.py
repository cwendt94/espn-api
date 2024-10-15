from espn_api.football import League
from operator import attrgetter
from collections import defaultdict

class Score:
	def __init__(self, home_team, home_score, away_team, away_score):
		self.winning_score = home_score if home_score > away_score else away_score
		self.losing_score = away_score if home_score > away_score else home_score
		self.winning_team = home_team if self.winning_score == home_score else away_team
		self.losing_team = away_team if self.winning_score == away_score else home_team

class FantasyService:
	def __init__(self):
		self.league = League(306883, 2024)
		self.awards = defaultdict(list)
		self.players = []
		self.teams = self.league.teams
		self.scores = []

	def generateAwards(self):
		week_high = 0
		week_high_team = ''
		week_low = 200
		week_low_team = ''
		week_high_diff = 0
		week_low_diff = 200
		diff_high_team = ''
		diff_low_team = ''
		week = 6

		# Iterating over matchups
		for matchup in self.league.box_scores(week=week):

			# Make pile of all players to iterate over 
			self.players += matchup.away_lineup + matchup.home_lineup

			# Make new list of matchups to iterate over
			self.scores.append(Score(matchup.home_team, matchup.home_score, matchup.away_team, matchup.away_score))

		# Compute highest score of the week
		highest = max(self.scores, key=attrgetter('winning_score'))
		self.award(highest.winning_team.team_name, 'BOOM GOES THE DYNAMITE - Highest weekly score (' + str(week_high) + ')')

		# Compute lowest score of the week 
		lowest = min(self.scores, key=attrgetter('losing_score'))
		self.award(lowest.losing_team.team_name, 'ASSUME THE POSITION - Lowest weekly score (' + str(week_low) + ')')
		
		# Compute lowest scoring winner
		fort_son = min(self.scores, key=attrgetter('winning_score'))
		self.award(fort_son.winning_team.team_name, 'FORTUNATE SON - Lowest scoring winner (' + str(fort_son.winning_score) + ')')

		# Compute highest scoring loser
		tough_luck = max(self.scores, key=attrgetter('losing_score'))
		self.award(tough_luck.losing_team.team_name, 'TOUGH LUCK - Highest scoring loser (' + str(tough_luck.losing_score) + ')')

		for score in self.scores:
				
			# Compute difference between scores
			temp_week_high_diff = round(score.winning_score - score.losing_score)
			temp_week_low_diff = temp_week_high_diff

			# Award teams who didn't make it to 100 points
			if score.losing_score < 100:
				self.award(score.losing_team.team_name, 'SUB-100 CLUB')
			if score.winning_score < 100:
				self.award(score.winning_team.team_name, 'SUB-100 CLUB')

			# Compute who won by the most points
			if temp_week_high_diff > week_high_diff:
				week_high_diff = temp_week_high_diff
				diff_high_team = score.winning_team
				loss_high_team = score.losing_team
	
			# Compute who won by the fewest points
			if temp_week_low_diff < week_low_diff:
				week_low_diff = temp_week_low_diff
				diff_low_team = score.winning_team
				loss_low_team = score.losing_team

		self.award(diff_high_team.team_name, 'TOTAL DOMINATION - Beat opponent by largest margin (' + loss_high_team.team_name + ' by ' + str(week_high_diff) + ')')
		self.award(loss_low_team.team_name, 'SECOND BANANA - Beaten by slimmest margin (' + diff_low_team.team_name + ' by ' + str(week_low_diff) + ')')
		self.award(diff_low_team.team_name, 'GEEKED FOR THE EKE - Beat opponent by slimmest margin (' + loss_low_team.team_name + ' by ' + str(week_low_diff) + ')')

		qbs = [x for x in self.players if x.lineupSlot == 'QB']

		# Compute if any QBs had equal num of TDs and INTs
		for qb in qbs:
			ints = 0 if qb.stats[week]['breakdown'].get('passingInterceptions') == None else qb.stats[week]['breakdown']['passingInterceptions']
			tds = 0 if qb.stats[week]['breakdown'].get('passingTouchdowns') == None else qb.stats[week]['breakdown']['passingTouchdowns']
			if ints != 0 and tds == ints:
				plural = 's' if tds > 1 else ''
				award_string = 'PERFECTLY BALANCED - ' + qb.name + ' threw ' + str(int(tds)) + ' TD' + plural + ' and ' + str(int(ints)) + ' INT' + plural
				self.award(self.getTeamName(qb.onTeamId), award_string)

		# Compute QB high
		self.computeHigh('QB', 'PLAY CALLER BALLER: QB high (')

		# Compute TE high
		self.computeHigh(['TE'], 'TIGHTEST END - TE high (')

		# Compute D/ST high
		self.computeHigh(['D/ST'], 'FORT KNOX - D/ST high (')

		# Compute kicker high
		self.computeHigh(['K'], 'KICK FAST, EAT ASS - Kicker high (')

		# Compute WR corps high
		self.computeHigh(['WR', 'WR/TE'], 'DEEP THREAT - WR corps high (')

		# Compute RB corps high
		self.computeHigh(['RB'], 'PUT THE TEAM ON HIS BACKS - RB corps high (')

		# Compute players who scored 2x projected
		daily_doubles = filter(lambda x: x.lineupSlot not in ['IR', 'BE', 'D/ST'] and x.points >= 2 * x.projected_points, self.players)
		for player in daily_doubles:
			dbl_award_string = 'DAILY DOUBLE - ' + player.name + ' scored >2x projected (' + str(player.points) + ', ' + str(player.projected_points) + ' projected)'
			self.award(self.getTeamName(player.onTeamId), dbl_award_string)

		self.printAwards()

	# Add award to dict of teams
	def award(self, team_name, award_string):
		self.awards[team_name].append(award_string)

	# Print all awards for each team
	def printAwards(self):
		for team_name in self.awards:
			print(team_name)
			for award in self.awards[team_name]:
				print(award)
			print()

	# Compute highest value for given position(s)
	def computeHigh(self, pos, award_string):

		# Compile list of players at position(s) pos
		filtered_players = [x for x in self.players if x.lineupSlot in pos]
		filtered_dict = {}

		# Make a dictionary of team_name -> sum of players at that position
		for team in self.teams:
			total = sum(player.points for player in filtered_players if player.onTeamId == team.team_id)
			filtered_dict[team.team_name] = total
		
		# Compute team with highest value
		top_team = max(filtered_dict, key=filtered_dict.get)
		player_myst = self.whoWasThat(top_team, filtered_dict[top_team], filtered_players)
		award_string = award_string + player_myst + str(filtered_dict[top_team]) + ')'
		self.award(top_team, award_string)

	# Attempt to match what player did the thing 
	def whoWasThat(self, team_name, score, filtered_players):
		team = self.getTeamFromName(team_name)
		for player in filtered_players:
			# print(player.points)
			if player.points == score and player.onTeamId == team.team_id:
				return player.name.rsplit(' ', 1)[1] + ', '
		return ''

	# Get team name for a team_id
	def getTeamName(self, id):
		return next((y.team_name for y in self.teams if y.team_id == id), None)

	def getTeamFromName(self, name):
		return next((y for y in self.teams if y.team_name == name), None)

FantasyService().generateAwards()
