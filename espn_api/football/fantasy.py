from espn_api.football import League
from operator import attrgetter
from collections import defaultdict

# Flatten list of team scores as they come in box_score format
class Fantasy_Team_Performance:
	def __init__(self, team_name, owner, score, point_differential, vs_team_name, vs_owner, roster):
		self.team_name = team_name
		self.owner = owner
		self.score = score
		self.diff = point_differential
		self.vs = vs_team_name
		self.vs_owner = vs_owner
		self.roster = roster

	def set_potential(self, potential):
		self.potential = potential
		self.potential_used = '{:,.2%}'.format(self.score / self.potential)

class Fantasy_Player:
	def __init__(self, name, team_name, score, position, lineup_slot, injury_status=None, projected_points=None, stats=None):
		self.name = name
		self.team_name = team_name
		self.score = score
		self.position = position
		self.lineup_slot = lineup_slot
		self.injury_status = injury_status
		self.projected_points = projected_points
		self.stats = stats
		self.last_name = self.name.split(None, 1)[1]

class Fantasy_Service:
	def __init__(self):
		# Hardcode league ID and year
		self.league = League(306883, 2024)
		self.awards = defaultdict(list)
		self.players = []
		self.scores = []
		self.week = 7

	def generateAwards(self):
		# Iterating over matchups
		for matchup in self.league.box_scores(week=self.week):

			lost_in_the_sauce = True

			for player in matchup.home_lineup:
				# If any players scored 3+ more than projected, the team is not lost in the sauce
				if player.lineupSlot not in ['K', 'BE', 'D/ST'] and player.points >= player.projected_points + 3:
					lost_in_the_sauce = False

				# Make pile of all players to iterate over 	
				self.players.append(Fantasy_Player(player.name, 
					matchup.home_team.team_name, 
					player.points, 
					player.position, 
					player.lineupSlot, 
					player.injuryStatus, 
					player.projected_points, 
					player.stats))

			if lost_in_the_sauce:
				# 1) Compute if any players on the home lineup exceeded their projected amount by 3+ 
				self.award(matchup.home_team.team_name, 'LOST IN THE SAUCE: No player scored 3+ more than projected')

			for player in matchup.away_lineup:
				if player.lineupSlot not in ['K', 'BE', 'D/ST'] and player.points > player.projected_points + 3:
					lost_in_the_sauce = False
				self.players.append(Fantasy_Player(player.name, 
					matchup.away_team.team_name, 
					player.points, 
					player.position, 
					player.lineupSlot, 
					player.injuryStatus, 
					player.projected_points, 
					player.stats))
			
			if lost_in_the_sauce:
				# 2) Compute if any players on the away lineup exceeded their projected amount by 3+ 
				self.award(matchup.away_team.team_name, 'LOST IN THE SAUCE: No non-special teams player scored 3+ more than projected')

			# Calculate the difference between home and sway scores
			diff = max([matchup.home_score, matchup.away_score]) - min([matchup.home_score, matchup.away_score])

			# Winning team gets a positive diff, losing team gets a negative diff
			if matchup.home_score < matchup.away_score:
				diff = 0-diff

			# Make list of team performances to iterate over
			self.scores.append(Fantasy_Team_Performance(matchup.home_team.team_name, 
				matchup.home_team.owners[0]['firstName'], 
				matchup.home_score, diff, 
				matchup.away_team.team_name,
				matchup.away_team.owners[0]['firstName'], 
				matchup.home_team.roster))
			self.scores.append(Fantasy_Team_Performance(matchup.away_team.team_name, 
				matchup.away_team.owners[0]['firstName'], 
				matchup.away_score, (0-diff), 
				matchup.home_team.team_name, 
				matchup.home_team.owners[0]['firstName'], 
				matchup.away_team.roster))
			
		# 3) Compute highest score of the week
		highest = max(self.scores, key=attrgetter('score'))
		self.award(highest.team_name, f'BOOM GOES THE DYNAMITE - Highest weekly score ({highest.score})')

		# 4) Compute lowest score of the week 
		lowest = min(self.scores, key=attrgetter('score'))
		self.award(lowest.team_name, f'ASSUME THE POSITION - Lowest weekly score ({lowest.score})')
	
		# 5) Compute lowest scoring winner
		fort_son = min([x for x in self.scores if x.diff > 0], key=attrgetter('score'))
		self.award(fort_son.team_name, f'FORTUNATE SON - Lowest scoring winner ({fort_son.score})')

		# 6) Compute highest scoring loser
		tough_luck = max([x for x in self.scores if x.diff < 0], key=attrgetter('score'))
		self.award(tough_luck.team_name, f'TOUGH LUCK - Highest scoring loser ({tough_luck.score})')

		# 7) Compute largest margin of victory
		big_margin = max(self.scores, key=attrgetter('diff'))
		self.award(big_margin.team_name, f'TOTAL DOMINATION - Beat opponent by largest margin ({big_margin.vs_owner} by {round(big_margin.diff, 2)})')

		# 8) Compute team that lost with smallest margin of victory
		small_margin = min([x for x in self.scores if x.diff > 0], key=attrgetter('diff'))
		self.award(small_margin.vs, f'SECOND BANANA - Beaten by slimmest margin ({small_margin.owner} by {round(small_margin.diff, 2)})')
		
		# 9) Compute team that won with smallest margin of victory
		self.award(small_margin.team_name, f'GEEKED FOR THE EKE - Beat opponent by slimmest margin ({small_margin.vs_owner} by {round(small_margin.diff, 2)})')

		for team in self.scores:
			team.set_potential(self.compute_potential(team, diff < 0))
			# 10) Award teams who didn't make it to 100 points
			if team.score < 100:
				self.award(team.team_name, 'SUB-100 CLUB')

		for player in self.players:
			if player.lineup_slot == 'QB':
				ints = 0 if player.stats[self.week]['breakdown'].get('passingInterceptions') == None else player.stats[self.week]['breakdown']['passingInterceptions']
				tds = 0 if player.stats[self.week]['breakdown'].get('passingTouchdowns') == None else player.stats[self.week]['breakdown']['passingTouchdowns']
				
				# 11) Compute if any starting QBs had equal num of TDs and INTs
				if ints != 0 and tds == ints:
					plural = 's' if tds > 1 else ''
					self.award(player.team_name, f'PERFECTLY BALANCED - {player.name} threw {int(tds)} TD{plural} and {int(ints)} INT{plural}')

			# 12) Award defenses who sucked
			elif player.lineup_slot == 'D/ST':
				if player.score < 2:
					self.award(player.team_name, f'THE BEST DEFENSE IS A GOOD OFFENSE - ({player.name}, {player.score})')

			# 13) Compute players who scored 2x projected
			if player.lineup_slot not in ['IR', 'BE', 'D/ST', 'K'] and player.score >= 2 * player.projected_points:
				self.award(player.team_name, f'DAILY DOUBLE - {player.name} scored >2x projected ({player.score}, {player.projected_points} projected)')

			# 14) Award players who didn't get hurt but scored nothing
			if player.lineup_slot not in ['IR', 'BE', 'D/ST', 'K'] and player.injury_status == 'ACTIVE' and player.score == 0:
				self.award(player.team_name, f'OUT OF OFFICE - ({player.name}, 0)')
			
			# 15) Award kickers who somehow didn't score any points
			elif player.lineup_slot == 'K' and player.injury_status == 'ACTIVE' and player.score == 0:
				self.award(player.team_name, f'GO KICK ROCKS - Kicker scored 0')

		# 16) Compute QB high
		qb_high = self.compute_top_scorer(self.get_starters_at_pos(['QB']))
		self.award(qb_high.team_name, f'PLAY CALLER BALLER: QB high ({qb_high.last_name}, {qb_high.score})')

		# 17) Compute TE high
		te_high = self.compute_top_scorer(self.get_starters_at_pos(['TE']))
		self.award(te_high.team_name, f'TIGHTEST END - TE high ({te_high.last_name}, {te_high.score})')

		# 18) Compute D/ST high
		d_st_high = self.compute_top_scorer(self.get_starters_at_pos(['D/ST']))
		self.award(d_st_high.team_name, f'FORT KNOX - D/ST high ({d_st_high.name}, {d_st_high.score})')

		# 19) Compute kicker high
		k_high = self.compute_top_scorer(self.get_starters_at_pos(['K']))
		self.award(k_high.team_name, f'KICK FAST, EAT ASS - Kicker high ({k_high.last_name}, {k_high.score})')

		# 20) Compute individual RB high
		rbs = self.get_starters_at_pos(['RB'])
		rb_high = self.compute_top_scorer(rbs)
		self.award(rb_high.team_name, f'SHINING STAR - RB high ({rb_high.last_name}, {round(rb_high.score, 2)})')

		# 21) Compute individual WR high
		wrs = self.get_starters_at_pos(['WR', 'WR/TE'])
		wr_high = self.compute_top_scorer(wrs)
		self.award(wr_high.team_name, f'SHINING STAR - WR high ({wr_high.last_name}, {round(wr_high.score, 2)})')

		# 22) Compute WR corps high
		wr_total_high = self.compute_top_scorer(wrs, True)
		self.award(wr_total_high.team_name, f'DEEP THREAT - WR corps high ({round(wr_total_high.score, 2)})')

		# 23) Compute RB corps high
		rb_total_high = self.compute_top_scorer(rbs, True)
		self.award(rb_total_high.team_name, f'PUT THE TEAM ON HIS BACKS - RB corps high ({round(rb_total_high.score, 2)})')

		# 24) Compute best manager who scored most of available points from roster
		potential_high = max(self.scores, key=attrgetter('potential_used'))
		self.award(potential_high.team_name, f'MINORITY REPORT - Scored highest percentage of possible points from roster ({potential_high.potential_used} of {potential_high.potential})')
		
		# 25) Compute worst manager who scored least of available points from roster
		potential_low = min(self.scores, key=attrgetter('potential_used'))
		self.award(potential_low.team_name, f'GOT BALLS - NONE CRYSTAL - Scored lowest percentage of possible points from roster ({potential_high.potential_used} of {potential_low.potential})')
		
		self.print_awards()

	# Add award to dict of teams
	def award(self, team_name, award_string):
		self.awards[team_name].append(award_string)

	# Print all awards for each team
	def print_awards(self):
		for team_name in self.awards:
			print(team_name)
			for award in self.awards[team_name]:
				print(award)
			print()

	def get_starters_at_pos(self, pos):
		# Compile list of players at position(s) pos
		return [player for player in self.players if player.lineup_slot in pos]

	# Compute highest value for given position(s)
	def compute_top_scorer(self, players, grouped_stat=False):
		filtered_dict = {}

		# Make a dictionary of team_name -> sum of scores from starters
		for team in self.league.teams:
			total = 0
			winner = self.compute_max_score([player for player in players if player.team_name == team.team_name])
			filtered_dict[team.team_name] = winner
			if grouped_stat:
				# Add up the scores of like positions
				total = sum(player.score for player in players if player.team_name == team.team_name)
				filtered_dict[team.team_name] = Fantasy_Player(winner.name, 
																winner.team_name, 
																total, 
																winner.lineup_slot, 
																winner.position)
		
		# Return player(s) with highest score
		return max(filtered_dict.values(), key=attrgetter('score'))
	
	# Return the max score of a given list of players
	def compute_max_score(self, players):
		return max(players, key=attrgetter('score'))

	# Compute a team's potential highest score given perfect start/sit decisions
	def compute_potential(self, team, lost_the_game):
		roster = []
		total_potential = 0

		# Assemble roster with all points scored including bench players
		for basic_player in team.roster:
			player_with_points = next((player for player in self.players if basic_player.name == player.name), None)
			if basic_player.lineupSlot != 'IR' and basic_player.stats[self.week].get('points') != None:
				if player_with_points == None:
					player_with_points = Fantasy_Player(basic_player.name, 
														team.team_name, 
														basic_player.stats[self.week]['points'], 
														basic_player.position, 
														basic_player.lineupSlot)
				roster.append(player_with_points)
		
		# Add individual contributors that don't need to be removed
		for pos in ['QB', 'K', 'D/ST']:
			total_potential += self.compute_start_sit(roster, [pos], lost_the_game).score

		te_high = self.compute_start_sit(roster, ['TE'], lost_the_game)
		total_potential += te_high.score
		roster.remove(te_high)

		max_rb = self.compute_start_sit(roster, ['RB'], lost_the_game)
		roster.remove(max_rb)
		total_potential += max_rb.score + self.compute_start_sit(roster, ['RB'], lost_the_game).score

		flex_used = False
		max_wr = self.compute_start_sit(roster, ['WR', 'TE', 'WR/TE'], lost_the_game)
		if max_wr.position == 'TE':
			flex_used = True
		roster.remove(max_wr)

		posits = ['WR'] if flex_used else ['WR', 'TE', 'WR/TE'] 
		second_wr = self.compute_start_sit(roster, posits, lost_the_game)

		if flex_used == False and second_wr.position == 'TE':
			flex_used = True
		roster.remove(second_wr)
		posits = ['WR'] if flex_used else ['WR', 'TE', 'WR/TE'] 
		third_wr = self.compute_start_sit(roster, posits, lost_the_game)
		total_potential += max_wr.score + second_wr.score + third_wr.score
		
		return round(total_potential, 2)

	def compute_start_sit(self, roster, pos, lost_the_game):
		starter = self.compute_max_score([x for x in roster if x.lineup_slot in pos])
		top_scorer = self.compute_max_score([x for x in roster if x.position in pos])

		if lost_the_game and top_scorer.lineup_slot == 'BE' and top_scorer.score >= starter.score * 2 and top_scorer.score >= starter.score + 5:
			self.award(top_scorer.team_name, f'START/SIT, GET HIT - Benched {top_scorer.last_name} scored {top_scorer.score} compared to starter {starter.last_name}\'s {starter.score}')
		return top_scorer

Fantasy_Service().generateAwards()
