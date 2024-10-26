from espn_api.football import League
from operator import attrgetter
from collections import defaultdict

# Flatten list of team scores as they come in box_score format
class Score:
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
		self.potential_used = self.score / self.potential

class Top_Scorer:
	def __init__(self, name, team_name, score, position, lineup_slot, injury_status=None, projected_points=None, stats=None):
		self.name = name
		self.team_name = team_name
		self.score = score
		self.position = position
		self.lineup_slot = lineup_slot
		self.injury_status = injury_status
		self.projected_points = projected_points
		self.stats = stats

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

			# Make pile of all players to iterate over 
			for player in matchup.home_lineup:
				if player.lineupSlot not in ['K', 'BE', 'D/ST'] and player.points >= player.projected_points + 3:
					lost_in_the_sauce = False
				self.players.append(Top_Scorer(player.name, matchup.home_team.team_name, player.points, player.position, player.lineupSlot, player.injuryStatus, player.projected_points, player.stats))
			if lost_in_the_sauce:
				self.award(matchup.home_team.team_name, 'LOST IN THE SAUCE: No player scored 3+ more than projected')

			for player in matchup.away_lineup:
				if player.lineupSlot not in ['K', 'BE', 'D/ST'] and player.points > player.projected_points + 4:
					lost_in_the_sauce = False
				self.players.append(Top_Scorer(player.name, matchup.away_team.team_name, player.points, player.position, player.lineupSlot, player.injuryStatus, player.projected_points, player.stats))
			if lost_in_the_sauce:
				self.award(matchup.away_team.team_name, 'LOST IN THE SAUCE: No non-special teams player scored 3+ more than projected')

			diff = max([matchup.home_score, matchup.away_score]) - min([matchup.home_score, matchup.away_score])

			if matchup.home_score < matchup.away_score:
				diff = 0-diff

			# Make new list of matchups to iterate over
			self.scores.append(Score(matchup.home_team.team_name, matchup.home_team.owners[0]['firstName'], matchup.home_score, diff, matchup.away_team.team_name, matchup.away_team.owners[0]['firstName'], matchup.home_team.roster))
			self.scores.append(Score(matchup.away_team.team_name, matchup.away_team.owners[0]['firstName'], matchup.away_score, (0-diff), matchup.home_team.team_name, matchup.home_team.owners[0]['firstName'], matchup.away_team.roster))
			
		# 1) Compute highest score of the week
		highest = max(self.scores, key=attrgetter('score'))
		self.award(highest.team_name, f'BOOM GOES THE DYNAMITE - Highest weekly score ({highest.score})')

		# 2) Compute lowest score of the week 
		lowest = min(self.scores, key=attrgetter('score'))
		self.award(lowest.team_name, f'ASSUME THE POSITION - Lowest weekly score ({lowest.score})')
	
		# 3) Compute lowest scoring winner
		fort_son = min([x for x in self.scores if x.diff > 0], key=attrgetter('score'))
		self.award(fort_son.team_name, f'FORTUNATE SON - Lowest scoring winner ({fort_son.score})')

		# 4) Compute highest scoring loser
		tough_luck = max([x for x in self.scores if x.diff < 0], key=attrgetter('score'))
		self.award(tough_luck.team_name, f'TOUGH LUCK - Highest scoring loser ({tough_luck.score})')

		# 5) Compute largest margin of victory
		big_margin = max(self.scores, key=attrgetter('diff'))
		self.award(big_margin.team_name, f'TOTAL DOMINATION - Beat opponent by largest margin ({big_margin.vs_owner} by {round(big_margin.diff, 2)})')

		# 6) Compute team that lost with smallest margin of victory
		small_margin = min([x for x in self.scores if x.diff > 0], key=attrgetter('diff'))
		self.award(small_margin.vs, f'SECOND BANANA - Beaten by slimmest margin ({small_margin.owner} by {round(small_margin.diff, 2)})')
		
		# 7) Compute team that won with smallest margin of victory
		self.award(small_margin.team_name, f'GEEKED FOR THE EKE - Beat opponent by slimmest margin ({small_margin.vs_owner} by {round(small_margin.diff, 2)})')

		for team in self.scores:
			team.set_potential(self.compute_potential(team, diff < 0))
			# 8) Award teams who didn't make it to 100 points
			if team.score < 100:
				self.award(team.team_name, 'SUB-100 CLUB')

		# 9) Compute if any QBs had equal num of TDs and INTs
		for qb in [x for x in self.players if x.lineup_slot == 'QB']:
			ints = 0 if qb.stats[self.week]['breakdown'].get('passingInterceptions') == None else qb.stats[self.week]['breakdown']['passingInterceptions']
			tds = 0 if qb.stats[self.week]['breakdown'].get('passingTouchdowns') == None else qb.stats[self.week]['breakdown']['passingTouchdowns']
			if ints != 0 and tds == ints:
				plural = 's' if tds > 1 else ''
				award_string = f'PERFECTLY BALANCED - {qb.name} threw {int(tds)} TD{plural} and {int(ints)} INT{plural}'
				self.award(self.get_team_name_from_id(qb.onTeamId), award_string)

		# 10) Compute QB high
		qb_high = self.compute_top_scorer('QB', True)
		self.award(qb_high.team_name, f'PLAY CALLER BALLER: QB high ({qb_high.name.split(None, 1)[1]}, {qb_high.score})')

		# 11) Compute TE high
		te_high = self.compute_top_scorer(['TE'], True)
		self.award(te_high.team_name, f'TIGHTEST END - TE high ({te_high.name.split(None, 1)[1]}, {te_high.score})')

		# 12) Compute D/ST high
		d_st_high = self.compute_top_scorer(['D/ST'], True)
		self.award(d_st_high.team_name, f'FORT KNOX - D/ST high ({d_st_high.name}, {d_st_high.score})')

		# 13) Compute kicker high
		k_high = self.compute_top_scorer(['K'], True)
		self.award(k_high.team_name, f'KICK FAST, EAT ASS - Kicker high ({k_high.name.split(None, 1)[1]}, {k_high.score})')

		# 14) Compute WR corps high
		wr_total_high = self.compute_top_scorer(['WR', 'WR/TE'])
		self.award(wr_total_high.team_name, f'DEEP THREAT - WR corps high ({wr_total_high.score})')

		# 15) Compute RB corps high
		rb_total_high = self.compute_top_scorer(['RB'])
		self.award(rb_total_high.team_name, f'PUT THE TEAM ON HIS BACKS - RB corps high ({round(rb_total_high.score, 2)})')

		# 16) Compute RB corps high
		rb_high = self.compute_top_scorer(['RB'], True)
		self.award(rb_high.team_name, f'SHINING STAR - RB high ({rb_high.name.split(None, 1)[1]}, {round(rb_high.score, 2)})')

		# 17) Compute RB corps high
		wr_high = self.compute_top_scorer(['WR', 'WR/TE'], True)
		self.award(wr_high.team_name, f'SHINING STAR - WR high ({wr_high.name.split(None, 1)[1]}, {round(wr_high.score, 2)})')

		# 18) Award defenses who went negative
		defenses = [x for x in self.players if x.lineup_slot == 'D/ST']
		for defense in defenses:
			if defense.score < 2:
				self.award(defense.team_name, f'THE BEST DEFENSE IS A GOOD OFFENSE - ({defense.name}, {defense.score})')

		# 19) Award players who didn't get hurt but scored nothing
		for player in self.players:
			if player.lineup_slot not in ['IR', 'BE', 'D/ST'] and player.injury_status == 'ACTIVE' and player.score == 0:
				self.award(player.team_name, f'OUT OF OFFICE - ({player.name}, 0)')

		# 20) Compute players who scored 2x projected
		daily_doubles = filter(lambda x: x.lineup_slot not in ['IR', 'BE', 'D/ST', 'K'] and x.score >= 2 * x.projected_points, self.players)
		for dbl_player in daily_doubles:
			dbl_award_string = f'DAILY DOUBLE - {dbl_player.name} scored >2x projected ({dbl_player.score}, {dbl_player.projected_points} projected)'
			self.award(dbl_player.team_name, dbl_award_string)

		# 21) Compute best manager who scored most of available points from roster
		potential_high = max(self.scores, key=attrgetter('potential_used'))
		self.award(potential_high.team_name, f'MINORITY REPORT - Scored highest percentage of possible points from roster ({'{:,.2%}'.format(potential_high.potential_used)} of {potential_high.potential})')
		
		# 22) Compute worst manager who scored least of available points from roster
		potential_low = min(self.scores, key=attrgetter('potential_used'))
		self.award(potential_low.team_name, f'GOT BALLS - NONE CRYSTAL - Scored lowest percentage of possible points from roster ({'{:,.2%}'.format(potential_low.potential_used)} of {potential_low.potential})')
		
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

	# Compute highest value for given position(s)
	def compute_top_scorer(self, pos, seek_player=False):

		# Compile list of players at position(s) pos
		filtered_players = [x for x in self.players if x.lineup_slot in pos]
	 
		filtered_dict = {}

		# Make a dictionary of team_name -> sum of scores from starting players at that position
		for team in self.league.teams:
			sum_total = sum(player.score for player in filtered_players if player.team_name == team.team_name)
			small = max(player.score for player in filtered_players if player.team_name == team.team_name)
	
			filtered_dict[team.team_name] = small if seek_player else sum_total
		
		# Compute team with highest score
		team_name = max(filtered_dict, key=filtered_dict.get)
		high_score = filtered_dict[team_name]
		return self.get_player_from_score(team_name, high_score, filtered_players) if seek_player else Top_Scorer('', team_name, high_score, pos, pos)
	
	# Compute a team's potential highest score given perfect start/sit decisions
	def compute_potential(self, team, did_u_lose_tho):
		roster = []
		total_potential = 0
		for player in team.roster:
			player_points = next((y for y in self.players if y.name == player.name), None)
			if player_points == None and player.stats[self.week].get('points') != None:
				player_points = Top_Scorer(player.name, team.team_name, player.stats[self.week]['points'], player.position, player.lineupSlot)
			if player.stats[self.week].get('points') != None and player.lineupSlot != 'IR':
				roster.append(player_points)
		
		for pos in ['QB', 'K', 'D/ST']:
			total_potential += self.compute_start_sit(roster, [pos], did_u_lose_tho).score

		te_high = self.compute_start_sit(roster, ['TE'], did_u_lose_tho)
		total_potential += te_high.score
		roster.remove(te_high)

		max_rb = self.compute_start_sit(roster, ['RB'], did_u_lose_tho)
		roster.remove(max_rb)
		total_potential += max_rb.score + self.compute_start_sit(roster, ['RB'], did_u_lose_tho).score

		flex_used = False
		max_wr = self.compute_start_sit(roster, ['WR', 'TE', 'WR/TE'], did_u_lose_tho)
		if max_wr.position == 'TE':
			flex_used = True
		roster.remove(max_wr)

		posits = ['WR'] if flex_used else ['WR', 'TE', 'WR/TE'] 
		second_wr = self.compute_start_sit(roster, posits, did_u_lose_tho)

		if flex_used == False and second_wr.position == 'TE':
			flex_used = True
		roster.remove(second_wr)
		posits = ['WR'] if flex_used else ['WR', 'TE', 'WR/TE'] 
		third_wr = self.compute_start_sit(roster, posits, did_u_lose_tho)
		total_potential += max_wr.score + second_wr.score + third_wr.score
		
		return round(total_potential, 2)

	def compute_start_sit(self, roster, pos, did_u_lose_tho):
		starter = max([x for x in roster if x.lineup_slot in pos], key=attrgetter('score'))
		top_scorer = max([x for x in roster if x.position in pos], key=attrgetter('score'))
		if did_u_lose_tho and top_scorer.lineup_slot == 'BE' and top_scorer.score >= starter.score * 2 and top_scorer.score >= starter.score + 5:
			top_name = top_scorer.name.split()[1]
			starter_name = starter.name.split()[1]
			self.award(top_scorer.team_name, f'START/SIT, GET HIT - Benched {top_name} scored {top_scorer.score} compared to starter {starter_name}\'s {starter.score}')
		return top_scorer

	# Attempt to match what player did the thing 
	def get_player_from_score(self, team_name, sum_of_scores, filtered_players):
		for player in filtered_players:
			if player.score == sum_of_scores and player.team_name == team_name:
				return player
		return None

	# Get team name from team_id
	def get_team_name_from_id(self, team_id):
		return next((y.team_name for y in self.league.teams if y.team_id == team_id), None)

Fantasy_Service().generateAwards()
