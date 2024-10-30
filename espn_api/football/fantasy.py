import google.auth
from espn_api.football import League
from operator import attrgetter
from collections import defaultdict
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import requests
import json

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

MAGIC_ASCII_OFFSET = 66

TREND_RANGE = 'A3:J25'
COMMENTS_RANGE_OUTPUT = 'COMMENTS!B1:B12' 
POINTS_LETTER_OUTPUT = 'POINTS!B1'
WINS_RANGE_OUTPUT = 'POINTS!C18:C29'
WEEKLY_RANKINGS_RANGE_OUTPUT = 'POINTS!Q18:Q29'
ROS_RANKINGS_RANGE_OUTPUT = 'POINTS!P18:P29'
TEAM_NAMES_RANGE, TEAM_NAMES_RANGE_OUTPUT = 'TEAMS!B3:B14', 'TEAMS!B3:B14'
OWNER_NAMES_RANGE = 'TEAMS!C3:C14'
HISTORY_RANKINGS_RANGE = 'TEAMS!D3:D14'

# Flatten list of team scores as they come in box_score format
class Fantasy_Team_Performance:
	def __init__(self, team_name, owner, score, point_differential, vs_team_name, vs_owner, lineup, bench_total):
		self.team_name = team_name
		self.owner = owner['firstName'] + ' ' + owner['lastName']
		self.score = score
		self.diff = point_differential
		self.vs_team_name = vs_team_name
		self.vs_owner = vs_owner
		self.lineup = lineup
		self.bench_total = bench_total

	def set_potential(self, potential_high):
		self.potential_high = potential_high
		self.potential_used = '{:,.2%}'.format(self.score / potential_high)

	def get_first_name(self):
		return self.owner.split(' ', 1)[0]

class Fantasy_Player:
	def __init__(self, name, team_name, score, second_score=0):
		self.name = name
		self.team_name = team_name
		self.score = score
		self.second_score = second_score
		self.diff = self.score - self.second_score

	def get_last_name(self):
		return self.name.split(None, 1)[1]

	def get_first_name(self):
		return self.name.split(None, 1)[0]

	def get_mistake_first(self):
		return self.name.split('.', 1)[0]

	def get_mistake_second(self):
		return self.name.split('.', 1)[1]

class Fantasy_Service:
	def __init__(self):
		# Hardcode league ID and year
		self.league = League(306883, 2024)
		self.awards = defaultdict(list)
		self.scores, self.qbs, self.tes, self.ks, self.wrs, self.rbs, self.dsts, self.mistakes = [], [], [], [], [], [], [], []
		self.week = 8

		if os.path.exists('spreadsheet_id.json'):
			with open('spreadsheet_id.json') as f:
				self.SPREADSHEET_ID = json.load(f)['id']

		creds = None
		if os.path.exists("token.json"):
			creds = Credentials.from_authorized_user_file("token.json", SCOPES)
			# If there are no (valid) credentials available, let the user log in.
			if not creds or not creds.valid:
				if creds and creds.expired and creds.refresh_token:
					creds.refresh(Request())
				else:
					flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
					creds = flow.run_local_server(port=0)
					# Save the credentials for the next run
				with open("token.json", "w") as token:
					token.write(creds.to_json())

		self.service = build("sheets", "v4", credentials=creds)
		# Call the Sheets API
		self.sheet = self.service.spreadsheets()

		# Iterating over matchups
		for matchup in self.league.box_scores(week=self.week):
			# Calculate the difference between home and away scores
			diff = max([matchup.home_score, matchup.away_score]) - min([matchup.home_score, matchup.away_score])

			# Winning team gets a positive diff, losing team gets a negative diff
			if matchup.home_score < matchup.away_score:
				diff = 0-diff
			home = matchup.home_team
			away = matchup.away_team

			self.process_matchup(matchup.home_lineup, home.team_name, matchup.home_score, home.owners[0], diff, away.team_name, away.owners[0]['firstName'])
			self.process_matchup(matchup.away_lineup, away.team_name, matchup.away_score, away.owners[0], (0-diff), home.team_name, home.owners[0]['firstName'])
		
		try:
			result = (self.sheet.values()
				.get(spreadsheetId=self.SPREADSHEET_ID, range=TEAM_NAMES_RANGE_OUTPUT).execute())
			self.teams = result.get("values", [])
			if not self.teams:
				print("No data found in initial teams sheet call")
		except HttpError as error:
			print(f"An error occurred: {error}")

		# self.update_team_names(True)

	# Process team performances to be iterable
	def process_matchup(self, lineup, team_name, score, owner_name, diff, vs_team_name, vs_owner):
		lost_in_the_sauce = True
		award_list = []

		# +++ AWARD teams who didn't make it to 100 points
		if score < 100:
			self.awards[team_name].append(f'SUB-100 CLUB ({score})')
		for pos in [['QB'], ['K'], ['D/ST'], ['RB'], ['WR'], ['TE'], ['WR', 'TE', 'WR/TE']]:
			award_list += self.compute_start_sit(lineup, pos, team_name, diff)
		self.process_award_list(award_list, team_name)

		bench_total = 0

		for player in lineup:
			# Make pile of all players to iterate over 	
			new_player = Fantasy_Player(player.name, team_name, player.points)
			if player.points >= 40:
				self.awards[team_name].append(f'40 BURGER ({player.name}, {player.points})')
			if player.lineupSlot == 'BE' or player.lineupSlot == 'IR':
				bench_total += player.points
			if diff < 0 and player.lineupSlot not in ['BE', 'IR']:
				if player.injuryStatus == 'QUESTIONABLE':
					self.awards[team_name].append(f'INSULT TO INJURY - ({player.name}, {player.points})')
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
		
		new_performance = Fantasy_Team_Performance(team_name, owner_name, score, diff, vs_team_name, vs_owner, lineup, bench_total)
		self.scores.append(new_performance)
		new_performance.set_potential(self.compute_potential(lineup, team_name, diff))

		# +++ AWARD team whose players didn't exceed projected amount by 3+
		if lost_in_the_sauce: 
			self.awards[team_name].append('LOST IN THE SAUCE: No non-special-teams player scored 3+ more than projected')

	# Iterate over scores and teams to generate awards for each team
	def generate_awards(self):
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
		self.awards[small_margin.vs_team_name].append(f'SECOND BANANA - Beaten by slimmest margin ({small_margin.get_first_name()} by {round(small_margin.diff, 2)})')
		
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

		# +++ AWARD RB corps high
		bench_total_high = max(self.scores, key=attrgetter('bench_total'))
		self.awards[bench_total_high.team_name].append(f'BIGLY BENCH - Bench total high ({round(bench_total_high.bench_total, 2)})')

		biggest_mistake = max(self.mistakes, key=attrgetter('diff'))
		self.awards[biggest_mistake.team_name].append(f'BIGGEST MISTAKE - Starting {biggest_mistake.get_mistake_first()} ({biggest_mistake.score}) over {biggest_mistake.get_mistake_second()} ({biggest_mistake.second_score})')
		self.do_sheet_awards()

		i = 1
		for team_name in self.teams:
			print(f'{i}) {team_name[0]}')
			for award in self.awards[team_name[0]]:
				print(award)
			i += 1
			print()

	# UPDATE team names in sheet
	def update_team_names(self, do_sheets_calls):
		try:
			result = (self.sheet.values()
				.get(spreadsheetId=self.SPREADSHEET_ID, range=OWNER_NAMES_RANGE).execute())
			owners = result.get("values", [])
			if not owners:
				print("No data found in update_team_names sheet call for owners")

			new_team_names = []
			for row in owners:
				team_name = next(score for score in self.scores if score.owner == row[0]).team_name
				new_team_names.append([team_name])

			if do_sheets_calls:
				try:
					body = {"values": new_team_names}
					result = (self.service.spreadsheets()
    					.values()
        					.update(
        						spreadsheetId=self.SPREADSHEET_ID,
        						range=TEAM_NAMES_RANGE_OUTPUT,
        						valueInputOption='USER_ENTERED',
        						body=body).execute())
					print(f"{result.get('updatedCells')} cells updated.")
				except HttpError as err:
					print(f"An error occurred: {err}")
			else:
				print('No update sheets calls have been authorized: update_team_names')

		except HttpError as error:
			print(f"An error occurred: {error}")

	# GET previous weeks rankings and UPDATE them in HISTORY of sheet
	def update_previous_week(self, do_sheets_calls):
		column = chr(self.week + 1 + MAGIC_ASCII_OFFSET)
		PREVIOUS_RANKINGS_RANGE_OUTPUT = 'HISTORY!' + column + '2:' + column + '13'
		
		try:
			result = (self.sheet.values().get(spreadsheetId=self.SPREADSHEET_ID, range=HISTORY_RANKINGS_RANGE).execute())
			rankings = result.get("values", [])

			if not rankings:
				print("No data found.")
				return
			rankings_list = []
			for rank in rankings:
				rankings_list.append([rank[0]])

			if do_sheets_calls:
				try:
					body = {"values": rankings_list}
					result = (self.service.spreadsheets()
    					.values()
        				.update(
        					spreadsheetId=self.SPREADSHEET_ID,
        					range=PREVIOUS_RANKINGS_RANGE_OUTPUT,
        					valueInputOption='USER_ENTERED',
        					body=body).execute())
					print(f"{result.get('updatedCells')} cells updated.")
				except HttpError as err:
					print(f"An error occurred: {err}")
			else:
				print('No update sheets calls have been authorized: update_weekly_column')
		except HttpError as error:
			print(f"An error occurred: {error}")
		

	# UPDATE new column letter in sheet
	def update_weekly_column(self, do_sheets_calls):
		character = self.week + MAGIC_ASCII_OFFSET

		if do_sheets_calls:
			try:
				body = {"values": [[chr(character)]]}
				result = (self.service.spreadsheets()
    				.values()
        			.update(
        				spreadsheetId=self.SPREADSHEET_ID,
        				range=POINTS_LETTER_OUTPUT,
        				valueInputOption='USER_ENTERED',
        				body=body).execute())
				print(f"{result.get('updatedCells')} cells updated.")
			except HttpError as err:
				print(f"An error occurred: {err}")
		else:
			print('No update sheets calls have been authorized: update_weekly_column')

	# GET team order of weekly scores and UPDATE scores in new column for each team in sheet
	def update_weekly_scores(self, do_sheets_calls):
		column = chr(self.week + MAGIC_ASCII_OFFSET)
		POINTS_RANGE_OUTPUT_NAME = 'POINTS!' + column + '3:' + column + '14'
		
		score_list = []
		for row in self.teams:
			team_score = next(score for score in self.scores if score.team_name == row[0]).score
			score_list.append([team_score])
			
		if do_sheets_calls:
			try:
				body = {"values": score_list}
				result = (self.service.spreadsheets()
    				.values()
        			.update(
        				spreadsheetId=self.SPREADSHEET_ID,
        				range=POINTS_RANGE_OUTPUT,
        				valueInputOption='USER_ENTERED',
        				body=body).execute())
				print(f"{result.get('updatedCells')} cells updated.")
			except HttpError as errorr:
				print(f"An error occurred: {errorr}")
		else:
			print('No update sheets calls have been authorized: update_weekly_scores')
	
	# GET team order of win total and UPDATE win total for winning teams in sheet
	def update_wins(self, do_sheets_calls):
		new_wins = []
		for row in self.teams:
			if next(score for score in self.scores if score.team_name == row[0]).diff > 0:
				new_wins.append([int(row[1]) + 1])
			else:
				new_wins.append([int(row[1])])

		if not values:
			print("No data found.")
			return

		if do_sheets_calls:
			try:
				body = {"values": new_wins}
				result = (self.service.spreadsheets()
    				.values()
        			.update(
        				spreadsheetId=self.SPREADSHEET_ID,
        				range=WINS_RANGE_OUTPUT,
        				valueInputOption='USER_ENTERED',
        				body=body).execute())
				print(f"{result.get('updatedCells')} cells updated.")
			except HttpError as errorr:
				print(f"An error occurred: {errorr}")
		else:
			print('No update sheets calls have been authorized: update_wins')

	# GET trends for each team generated by sheet for ranking-trend-based awards
	def do_sheet_awards(self):	
		try:
			result = (self.sheet.values()
				.get(spreadsheetId=self.SPREADSHEET_ID, range=TREND_RANGE).execute())
			values = result.get("values", [])

			if not values:
				print("No data found.")
				return
			i = 0
			for row in values:
				if i % 2 == 0:
					if len(row) > 0 and len(row[3]) == 2 and int(row[3][1]) > 2:
						if '▼' in row[3]:
							self.awards[row[1].split('\n', 1)[0]].append('FREE FALLIN\' - Dropped 3 spots in the rankings')
						else:
							self.awards[row[1].split('\n', 1)[0]].append('TO THE MOON! - Rose 3 spots in the rankings')
				i += 1
				
		except HttpError as err:
			print(err)

	# GET weekly roster ranking scores from FantasyPros and UPDATE weekly roster ranking scores in sheet 
	def get_weekly_roster_rankings(self, do_sheets_calls):
		r = requests.get('https://mpbnfl.fantasypros.com/api/getLeagueAnalysisJSON?key=nfl~021c6923-33f0-4763-a84a-6327f62fded2&period=week')
		data = r.json()
		
		rankings_list = []
		# for team in data['standings']:
		for row in self.teams:
			for team in data['standings']:
				if row[0] == team['teamName']:
					num = round(float(team['percentAsNumber']) * 100)
					rankings_list.append([num])

		if do_sheets_calls:
			try:
				body = {"values": rankings_list}
				result = (self.service.spreadsheets()
    				.values()
        			.update(
        				spreadsheetId=self.SPREADSHEET_ID,
        				range=WEEKLY_RANKINGS_RANGE_OUTPUT,
        				valueInputOption='USER_ENTERED',
        				body=body).execute())
				print(f"{result.get('updatedCells')} cells updated.")

			except HttpError as err:
				print(f"An error occurred: {err}")
		else:
			print('No update sheets calls have been authorized: get_weekly_roster_rankings')

	# GET RoS roster ranking scores from FantasyPros and UPDATE RoS roster rankings scores in sheet
	def get_ros_roster_rankings(self, do_sheets_calls):
		r = requests.get('https://mpbnfl.fantasypros.com/api/getLeagueAnalysisJSON?key=nfl~021c6923-33f0-4763-a84a-6327f62fded2&period=ros')
		data = r.json()

		rankings_list = []
		# for team in data['standings']:
		for row in self.teams:
			for team in data['standings']:
				if row[0] == team['teamName']:
					num = round(float(team['percentAsNumber']) * 100)
					rankings_list.append([num])

		if do_sheets_calls:
			try:
				body = {"values": rankings_list}
				result = (self.service.spreadsheets()
    				.values()
        			.update(
        				spreadsheetId=self.SPREADSHEET_ID,
        				range=ROS_RANKINGS_RANGE_OUTPUT,
        				valueInputOption='USER_ENTERED',
        				body=body).execute())
				print(f"{result.get('updatedCells')} cells updated.")

			except HttpError as err:
				print(f"An error occurred: {err}")
		else:
			print('No update sheets calls have been authorized: get_weekly_roster_rankings')

	# GET team order for commens and UPDATE comment values in sheet
	def update_comments(self, do_sheets_calls):
		award_list = []
		for row in self.teams:
			award_string = ''
			ctr = len(self.awards[row[0]])
			for award in self.awards[row[0]]:
				ctr_string = '\n' if ctr - 1 > 0 else ''
				award_string += award + ctr_string
			award_list.append([award_string])
		if do_sheets_calls:	
			try:
				body = {"values": award_list}
				result = (self.service.spreadsheets()
    				.values()
        			.update(
        				spreadsheetId=self.SPREADSHEET_ID,
        				range=COMMENTS_RANGE_OUTPUT,
        				valueInputOption='USER_ENTERED',
        				body=body).execute())
				print(f"{result.get('updatedCells')} cells updated.")
			except HttpError as error:
				print(f"An error occurred: {error}")
		else:
			print('No update sheets calls have been authorized: update_comments')

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
		for pos in [['QB'], ['K'], ['D/ST'], ['RB'], ['RB'], ['TE'], ['WR'], ['WR'], ['WR', 'TE', 'WR/TE']]:
			new_total = max([player for player in roster if player.position in pos], key=attrgetter('points'))
			total_potential += new_total.points
			roster.remove(new_total)

		return round(total_potential, 2)

	# Compare starter's score at a given position to the top scorer at that position on the team and award if benched player scored significantly higher
	def compute_start_sit(self, roster, pos, team_name, diff):
		starters = [player for player in roster if player.lineupSlot in pos]
		benched_players = [player for player in roster if player.lineupSlot in ['BE', 'IR'] and player.position in pos]
		award_list = []
		for play in benched_players:
			starter = min([player for player in starters if player.lineupSlot in pos], key=attrgetter('points'))
			if diff < 0 and play.points >= abs(diff) + starter.points:
				award_list.append(f'BLUNDER - Starting {play.name} ({play.points}) over {starter.name} ({starter.points}) would have been enough to win (lost by {round(abs(diff), 2)})') 
			elif diff < 0 and play.points >= starter.points * 2 and play.points >= starter.points + 5:
				award_list.append(f'START/SIT, GET HIT - Benched {play.name} scored {play.points} compared to starter {starter.name} scoring {starter.points}')
			if play.points > starter.points:
				self.mistakes.append(Fantasy_Player(play.name + '.' + starter.name, team_name, play.points, starter.points))
		return award_list

	# Find the greatest of the START/SIT awards to actually append to award list
	def process_award_list(self, award_list, team_name):
		best_start_sit = 0
		final_start_sit = ''
		for award in award_list:
			if 'START/SIT' in award:
				words = award.split()
				index = words.index('scored')
				index2 = words.index('scoring')
				new_diff = float(words[index + 1]) - float(words[index2 + 1])
				if new_diff > best_start_sit:
					best_start_sit = new_diff
					final_start_sit = award
		if final_start_sit != '':
			self.awards[team_name].append(final_start_sit)

service = Fantasy_Service()
service.generate_awards()

# service.update_weekly_column(True)
# service.update_weekly_scores(True)
# service.update_wins(True)

# service.get_weekly_roster_rankings(True)
# service.get_ros_roster_rankings(True)
# service.generate_awards()
# service.update_comments(True)

# service.update_previous_week(True)

# 0) tues morning: change week number to current week 
# 1) tues morning: run generate awards, copy to keep 
# 2) tues morning: run update_weekly_column, update_weekly_scores, update_wins
# 3) thursday morning: run get_weekly_roster_rankings, get_ros_roster_rankings
# 4) thursday morning: run do_sheet_awards via generate_awards, update_comments
# 5) thursday morning: run update_previous_week
