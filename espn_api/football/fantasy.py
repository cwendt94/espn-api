from espn_api.football import League
from operator import attrgetter
from collections import defaultdict

# Flatten list of team scores as they come in box_score format
class Fantasy_Team_Performance:
	def __init__(self, team_name, owner, score, point_differential, vs_team_name, vs_owner, lineup):
		self.team_name = team_name
		self.owner = owner
		self.score = score
		self.diff = point_differential
		self.vs_team_name = vs_team_name
		self.vs_owner = vs_owner
		self.lineup = lineup

	def set_potential(self, potential_high):
		self.potential_high = potential_high
		self.potential_used = '{:,.2%}'.format(self.score / potential_high)

class Fantasy_Player:
	def __init__(self, name, team_name, score):
		self.name = name
		self.team_name = team_name
		self.score = score

	def get_last_name(self):
		return self.name.split(None, 1)[1]

class Fantasy_Service:
	def __init__(self):
		# Hardcode league ID and year
		self.league = League(306883, 2024)
		self.awards = defaultdict(list)
		self.scores, self.qbs, self.tes, self.ks, self.wrs, self.rbs, self.dsts = [], [], [], [], [], [], []
		self.week = 7

	# Process team performances to be more iterable
	def process_matchup(self, lineup, team_name, score, owner_name, diff, vs_team_name, vs_owner):
		lost_in_the_sauce = True

		# +++ AWARD teams who didn't make it to 100 points
		if score < 100:
			self.awards[team_name].append(f'SUB-100 CLUB ({score})')

		new_performance = Fantasy_Team_Performance(team_name, owner_name, score, diff, vs_team_name, vs_owner, lineup)
		self.scores.append(new_performance)
		new_performance.set_potential(self.compute_potential(lineup, team_name, diff))

		for player in lineup:
			# Make pile of all players to iterate over 	
			new_player = Fantasy_Player(player.name, 
				team_name, 
				player.points)

			if player.lineupSlot not in ['K', 'BE', 'D/ST', 'IR']:
				# If any players scored 3+ more than projected, the team is not lost in the sauce
				if player.points >= player.projected_points + 3:
					lost_in_the_sauce = False

				# +++ AWARD players who scored 2x projected
				if player.points >= 2 * player.projected_points:
					self.awards[team_name].append(f'DAILY DOUBLE - {player.name} scored >2x projected ({player.points}, {player.projected_points} projected)')

				# +++ AWARD players who didn't get hurt but scored nothing
				if player.injuryStatus == 'ACTIVE' and player.points == 0:
					self.awards[team_name].append(f'OUT OF OFFICE - ({player.name}, 0)')

			# Compile lists of players at each position
			match player.lineupSlot:
				case 'QB':
					self.qbs.append(new_player)
					ints = 0 if player.stats[self.week]['breakdown'].get('passingInterceptions') == None else player.stats[self.week]['breakdown']['passingInterceptions']
					tds = 0 if player.stats[self.week]['breakdown'].get('passingTouchdowns') == None else player.stats[self.week]['breakdown']['passingTouchdowns']
				
					# +++ AWARD if any starting QBs had equal num of TDs and INTs
					if ints != 0 and tds == ints:
						plural = 's' if tds > 1 else ''
						self.awards[team_name].append(f'PERFECTLY BALANCED - {player.name} threw {int(tds)} TD{plural} and {int(ints)} INT{plural}')
				case 'TE':
					self.tes.append(new_player)
				case 'K':
					self.ks.append(new_player)
					# +++ AWARD kickers who somehow didn't score any points
					if player.injuryStatus == 'ACTIVE' and player.points == 0:
						self.awards[team_name].append(f'GO KICK ROCKS - Kicker scored 0')
				case 'RB':
					self.rbs.append(new_player)
				case 'WR':
					self.wrs.append(new_player)
				case 'WR/TE':
					self.wrs.append(new_player)
				case 'D/ST':
					self.dsts.append(new_player)
					# +++ AWARD defenses who sucked
					if player.points < 2:
						self.awards[team_name].append(f'THE BEST DEFENSE IS A GOOD OFFENSE - ({player.name}, {player.points})')
		
		# +++ AWARD team whose players didn't exceed projected amount by 3+
		if lost_in_the_sauce: 
			self.awards[team_name].append('LOST IN THE SAUCE: No non-special-teams player scored 3+ more than projected')

	def generateAwards(self):
		# Iterating over matchups
		for matchup in self.league.box_scores(week=self.week):

			# Calculate the difference between home and away scores
			diff = max([matchup.home_score, matchup.away_score]) - min([matchup.home_score, matchup.away_score])

			# Winning team gets a positive diff, losing team gets a negative diff
			if matchup.home_score < matchup.away_score:
				diff = 0-diff
			home = matchup.home_team
			away = matchup.away_team

			self.process_matchup(matchup.home_lineup, home.team_name, matchup.home_score, home.owners[0]['firstName'], diff, away.team_name, away.owners[0]['firstName'])
			self.process_matchup(matchup.away_lineup, away.team_name, matchup.away_score, away.owners[0]['firstName'], (0-diff), home.team_name, home.owners[0]['firstName'])
			
		# Score-based awards
		# +++ AWARD highest score of the week
		highest = max(self.scores, key=attrgetter('score'))
		self.awards[highest.team_name].append(f'BOOM GOES THE DYNAMITE - Highest weekly score ({highest.score})')

		# +++ AWARD lowest score of the week 
		lowest = min(self.scores, key=attrgetter('score'))
		self.awards[lowest.team_name].append(f'ASSUME THE POSITION - Lowest weekly score ({lowest.score})')
	
		# +++ AWARD lowest scoring winner
		fort_son = min([x for x in self.scores if x.diff > 0], key=attrgetter('score'))
		self.awards[fort_son.team_name].append(f'FORTUNATE SON - Lowest scoring winner ({fort_son.score})')

		# +++ AWARD highest scoring loser
		tough_luck = max([x for x in self.scores if x.diff < 0], key=attrgetter('score'))
		self.awards[tough_luck.team_name].append(f'TOUGH LUCK - Highest scoring loser ({tough_luck.score})')

		# +++ AWARD largest margin of victory
		big_margin = max(self.scores, key=attrgetter('diff'))
		self.awards[big_margin.team_name].append(f'TOTAL DOMINATION - Beat opponent by largest margin ({big_margin.vs_owner} by {round(big_margin.diff, 2)})')

		# +++ AWARD team that lost with smallest margin of victory
		small_margin = min([x for x in self.scores if x.diff > 0], key=attrgetter('diff'))
		self.awards[small_margin.vs_team_name].append(f'SECOND BANANA - Beaten by slimmest margin ({small_margin.owner} by {round(small_margin.diff, 2)})')
		
		# +++ AWARD team that won with smallest margin of victory
		self.awards[small_margin.team_name].append(f'GEEKED FOR THE EKE - Beat opponent by slimmest margin ({small_margin.vs_owner} by {round(small_margin.diff, 2)})')

		# +++ AWARD best manager who scored most of available points from roster
		potential_high = max(self.scores, key=attrgetter('potential_used'))
		self.awards[potential_high.team_name].append(f'MINORITY REPORT - Scored highest percentage of possible points from roster ({potential_high.potential_used} of {potential_high.potential_high})')
		
		# +++ AWARD worst manager who scored least of available points from roster
		potential_low = min(self.scores, key=attrgetter('potential_used'))
		self.awards[potential_low.team_name].append(f'GOT BALLS - NONE CRYSTAL - Scored lowest percentage of possible points from roster ({potential_low.potential_used} of {potential_low.potential_high})')
		
		# Individual player awards
		# +++ AWARD QB high
		qb_high = self.compute_top_scorer(self.qbs)
		self.awards[qb_high.team_name].append(f'PLAY CALLER BALLER - QB high ({qb_high.get_last_name()}, {qb_high.score})')

		# +++ AWARD TE high
		te_high = self.compute_top_scorer(self.tes)
		self.awards[te_high.team_name].append(f'TIGHTEST END - TE high ({te_high.get_last_name()}, {te_high.score})')

		# +++ AWARD D/ST high
		d_st_high = self.compute_top_scorer(self.dsts)
		self.awards[d_st_high.team_name].append(f'FORT KNOX - D/ST high ({d_st_high.name}, {d_st_high.score})')

		# +++ AWARD Compute K high
		k_high = self.compute_top_scorer(self.ks)
		self.awards[k_high.team_name].append(f'KICK FAST, EAT ASS - Kicker high ({k_high.get_last_name()}, {k_high.score})')

		# +++ AWARD individual RB high
		rb_high = self.compute_top_scorer(self.rbs)
		self.awards[rb_high.team_name].append(f'SPECIAL DELIVERY: GROUND - RB high ({rb_high.get_last_name()}, {round(rb_high.score, 2)})')

		# +++ AWARD individual WR high
		wr_high = self.compute_top_scorer(self.wrs)
		self.awards[wr_high.team_name].append(f'SPECIAL DELIVERY: AIR - WR high ({wr_high.get_last_name()}, {round(wr_high.score, 2)})')

		# +++ AWARD WR corps high
		wr_total_high = self.compute_top_scorer(self.wrs, True)
		self.awards[wr_total_high.team_name].append(f'DEEP THREAT - WR corps high ({round(wr_total_high.score, 2)})')

		# +++ AWARD RB corps high
		rb_total_high = self.compute_top_scorer(self.rbs, True)
		self.awards[rb_total_high.team_name].append(f'PUT THE TEAM ON HIS BACKS - RB corps high ({round(rb_total_high.score, 2)})')

		for team_name in self.awards:
			print(team_name)
			for award in self.awards[team_name]:
				print(award)
			print()

	# Compute highest value for given position(s)
	def compute_top_scorer(self, players, grouped_stat=False):
		filtered_dict = {}

		# Make a dictionary of team_name -> sum of scores from starters
		for team in self.league.teams:
			total = 0
			winner = max([player for player in players if player.team_name == team.team_name], key=attrgetter('score'))
			filtered_dict[team.team_name] = winner
			if grouped_stat:
				# Add up the scores of like positions
				total = sum(player.score for player in players if player.team_name == team.team_name)
				filtered_dict[team.team_name] = Fantasy_Player(winner.name, winner.team_name, total)
		
		# Return player(s) with highest score
		return max(filtered_dict.values(), key=attrgetter('score'))

	# Compute a team's potential highest score given perfect start/sit decisions
	def compute_potential(self, lineup, team_name, diff):
		roster = lineup.copy()
		total_potential = 0

		# Add individual contributors that don't need to be removed
		for pos in ['QB', 'K', 'D/ST']:
			new_total = self.compute_start_sit(roster, [pos], team_name, diff)
			total_potential += new_total.points

		# Best TE needs to be removed so as to not interfere with the flex position
		te_high = self.compute_start_sit(roster, ['TE'], team_name, diff)
		total_potential += te_high.points
		roster.remove(te_high)

		# Totalling up best 2 RBs
		max_rb = self.compute_start_sit(roster, ['RB'], team_name, diff)
		roster.remove(max_rb)
		second_rb = self.compute_start_sit(roster, ['RB'], team_name, diff)
		total_potential += max_rb.points + second_rb.points

		# Totalling up best 3 WRs (or TE if he's higher than a WR)
		# Only one TE can be used for flex position
		flex_used = False
		max_wr = self.compute_start_sit(roster, ['WR', 'TE', 'WR/TE'], team_name, diff)
		flex_used = True if max_wr.position == 'TE' else False
		roster.remove(max_wr)
		# Once a TE has been used for flex spot, only look at WRs
		positions = ['WR'] if flex_used else ['WR', 'TE', 'WR/TE'] 
		second_wr = self.compute_start_sit(roster, positions, team_name, diff)
		flex_used = True if flex_used == False and second_wr.position == 'TE' else False
		roster.remove(second_wr)
		positions = ['WR'] if flex_used else ['WR', 'TE', 'WR/TE'] 
		third_wr = self.compute_start_sit(roster, positions, team_name, diff)
		total_potential += max_wr.points + second_wr.points + third_wr.points
		
		return round(total_potential, 2)

	def compute_start_sit(self, roster, pos, team_name, diff):
		starter = max([x for x in roster if x.lineupSlot in pos], key=attrgetter('points'))
		top_scorer = max([x for x in roster if x.position in pos], key=attrgetter('points'))

		# If team lost and the significantly best scorer at a given position was on the bench or IR
		if diff < 0 and top_scorer.lineupSlot in ['BE', 'IR'] and top_scorer.points >= starter.points * 2 and top_scorer.points >= starter.points + 5:
			if top_scorer.points >= abs(diff) + starter.points:
				# +++ AWARD team that could have won with one different starter
				self.awards[team_name].append(f'BLUNDER - Starting {top_scorer.name} over {starter.name} would have been enough to win') 
			else:
				# +++ AWARD team that benched a significantly more effective player than starter
				self.awards[team_name].append(f'START/SIT, GET HIT - Benched {top_scorer.name.split(None, 1)[1]} scored {top_scorer.points} compared to starter {starter.name.split(None, 1)[1]}\'s {starter.points}')
		return top_scorer

Fantasy_Service().generateAwards()
