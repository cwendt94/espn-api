from espn_api.football import League
from operator import attrgetter
from collections import defaultdict

class FantasyService:
	def __init__(self):
		self.league = League(306883, 2024)
		self.awards = defaultdict(list)
		self.players = []
		self.teams = self.league.teams

	def generateAwards(self):
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
		week = 6

		# Iterating over matchups
		for matchup in self.league.box_scores(week=week):

			# Make pile of all players to iterate over 
			self.players += matchup.away_lineup + matchup.home_lineup

			# If away team won, add the team to winners, else to losers
			if matchup.away_score > matchup.home_score:
				winners[matchup.away_team.team_name] = matchup.away_score
				losers[matchup.home_team.team_name] = matchup.home_score
			else:
				winners[matchup.home_team.team_name] = matchup.home_score
				losers[matchup.away_team.team_name] = matchup.away_score

			if matchup.away_score < 100:
				self.award(matchup.away_team.team_name, 'SUB-100 CLUB')
			if matchup.home_score < 100:
				self.award(matchup.home_team.team_name, 'SUB-100 CLUB')

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

		# Compute lowest scoring winner
		fort_son = min(winners, key=winners.get)

		# Compute highest scoring loser
		tough_luck = max(losers, key=losers.get)

		# Compute who had the lowest score of the week  
		week_low_team = min(losers, key=losers.get)
		week_low = self.getTeamFromName(week_low_team)

		# Compute who had the highest score of the week
		week_high_team = max(winners, key=winners.get)
		week_high = self.getTeamFromName(week_high_team)


		self.award(fort_son, 'FORTUNATE SON - Lowest scoring winner (' + str(winners[fort_son]) + ')')
		self.award(tough_luck, 'TOUGH LUCK - Highest scoring loser (' + str(losers[tough_luck]) + ')')

		self.award(week_high_team, 'BOOM GOES THE DYNAMITE - Highest weekly score (' + str(week_high) + ')')
		self.award(week_low_team, 'ASSUME THE POSITION - Lowest weekly score (' + str(week_low) + ')')
		self.award(diff_high_team, 'TOTAL DOMINATION - Beat opponent by largest margin (' + loss_high_team + ' by ' + str(week_high_diff) + ')')
		self.award(loss_low_team, 'SECOND BANANA - Beaten by slimmest margin (' + diff_low_team + ' by ' + str(week_low_diff) + ')')
		self.award(diff_low_team, 'GEEKED FOR THE EKE - Beat opponent by slimmest margin (' + loss_low_team + ' by ' + str(week_low_diff) + ')')

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
		self.computeHigh(['TE'], 'TIGHTEST END - TE high (', )

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

fantasy_service = FantasyService()
fantasy_service.generateAwards()
