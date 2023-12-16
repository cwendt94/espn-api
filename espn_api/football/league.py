import json
from itertools import combinations
from typing import Callable, Dict, List, Tuple, Union

import pandas as pd


from ..base_league import BaseLeague
from .team import Team
from .matchup import Matchup
from .pick import Pick
from .box_score import BoxScore
from .box_player import BoxPlayer
from .player import Player
from .activity import Activity
from .settings import Settings
from .utils import power_points, two_step_dominance
from .constant import POSITION_MAP, ACTIVITY_MAP


class League(BaseLeague):
    '''Creates a League instance for Public/Private ESPN league'''
    def __init__(self, league_id: int, year: int, espn_s2=None, swid=None, fetch_league=True, debug=False):
        super().__init__(league_id=league_id, year=year, sport='nfl', espn_s2=espn_s2, swid=swid, debug=debug)

        if fetch_league:
            self.fetch_league()

    def fetch_league(self):
        self._fetch_league()

    def _fetch_league(self):
        data = super()._fetch_league(SettingsClass=Settings)

        self.nfl_week = data['status']['latestScoringPeriod']
        self._fetch_players()
        self._fetch_teams(data)
        self._fetch_draft()

    def _fetch_teams(self, data):
        '''Fetch teams in league'''
        super()._fetch_teams(data, TeamClass=Team)

        # replace opponentIds in schedule with team instances
        for team in self.teams:
            team.division_name = self.settings.division_map.get(team.division_id, '')
            for week, matchup in enumerate(team.schedule):
                for opponent in self.teams:
                    if matchup == opponent.team_id:
                        team.schedule[week] = opponent

        # calculate margin of victory
        for team in self.teams:
            for week, opponent in enumerate(team.schedule):
                mov = team.scores[week] - opponent.scores[week]
                team.mov.append(mov)

    def _fetch_draft(self):
        '''Creates list of Pick objects from the leagues draft'''
        data = self.espn_request.get_league_draft()

        # League has not drafted yet
        if not data['draftDetail']['drafted']:
            return

        picks = data['draftDetail']['picks']
        for pick in picks:
            team = self.get_team_data(pick['teamId'])
            playerId = pick['playerId']
            playerName = ''
            if playerId in self.player_map:
                playerName = self.player_map[playerId]
            round_num = pick['roundId']
            round_pick = pick['roundPickNumber']
            bid_amount = pick['bidAmount']
            keeper_status = pick['keeper']
            nominatingTeam = self.get_team_data(pick['nominatingTeamId'])
            self.draft.append(Pick(team, playerId, playerName, round_num, round_pick, bid_amount, keeper_status, nominatingTeam))

    def _get_positional_ratings(self, week: int):
        params = {
            'view': 'mPositionalRatings',
            'scoringPeriodId': week,
        }
        data = self.espn_request.league_get(params=params)
        ratings = data.get('positionAgainstOpponent', {}).get('positionalRatings', {})

        positional_ratings = {}
        for pos, rating in ratings.items():
            teams_rating = {}
            for team, data in rating['ratingsByOpponent'].items():
                teams_rating[team] = data['rank']
            positional_ratings[pos] = teams_rating
        return positional_ratings

    def refresh(self):
        '''Gets latest league data. This can be used instead of creating a new League class each week'''
        data = super()._fetch_league()

        self.nfl_week = data['status']['latestScoringPeriod']
        self._fetch_teams(data)
    def load_roster_week(self, week: int) -> None:
        '''Sets Teams Roster for a Certain Week'''
        params = {
            'view': 'mRoster',
            'scoringPeriodId': week
        }
        data = self.espn_request.league_get(params=params)

        team_roster = {}
        for team in data['teams']:
            team_roster[team['id']] = team['roster']

        for team in self.teams:
            roster = team_roster[team.team_id]
            team._fetch_roster(roster, self.year)

    def standings(self) -> List[Team]:
        standings = sorted(self.teams, key=lambda x: x.final_standing if x.final_standing != 0 else x.standing, reverse=False)
        return standings

    def standings_weekly(self, week: int) -> pd.DataFrame:
        """This is the main function to get the standings for a given week.

        It controls the tiebreaker hierarchy and calls the recursive League()._sort_standings_df function.
        First, the division winners must be determined. Then, the rest of the teams are sorted.

        The standard tiebreaker hierarchy is:
            1. Head-to-head record among the tied teams
            2. Total points scored for the season
            3. Division record (if all tied teams are in the same division)
            4. Total points scored against for the season
            5. Coin flip

        Args:
            week (int): Week to get the standings for

        Returns:
            pd.DataFrame: Sorted standings DataFrame
        """
        # Build the standings DataFrame for the given week
        standings_df = pd.DataFrame()
        standings_df["team_id"] = [team.team_id for team in self.teams]
        standings_df["team_name"] = [team.team_name for team in self.teams]
        standings_df["division_id"] = [team.division_id for team in self.teams]
        standings_df["division_name"] = [team.division_name for team in self.teams]
        standings_df["wins"] = [
            sum([1 for outcome in team.outcomes[:week] if outcome == "W"])
            for team in self.teams
        ]
        standings_df["ties"] = [
            sum([1 for outcome in team.outcomes[:week] if outcome == "T"])
            for team in self.teams
        ]
        standings_df["losses"] = [
            sum([1 for outcome in team.outcomes[:week] if outcome == "L"])
            for team in self.teams
        ]
        standings_df["points_for"] = [sum(team.scores[:week]) for team in self.teams]
        standings_df["points_against"] = [
            sum([team.schedule[w].scores[w] for w in range(week)])
            for team in self.teams
        ]
        standings_df["win_pct"] = (
            standings_df["wins"] + standings_df["ties"] / 2
        ) / standings_df[["wins", "losses", "ties"]].sum(axis=1)
        standings_df.set_index("team_id", inplace=True)

        if self.settings.playoff_seed_tie_rule == "TOTAL_POINTS_SCORED":
            tiebreaker_hierarchy = [
                (self._sort_by_win_pct, "win_pct"),
                (self._sort_by_points_for, "points_for"),
                (self._sort_by_head_to_head, "h2h_wins"),
                (self._sort_by_division_record, "division_record"),
                (self._sort_by_points_against, "points_against"),
                (self._sort_by_coin_flip, "coin_flip"),
            ]
        elif self.settings.playoff_seed_tie_rule == "H2H_RECORD":
            tiebreaker_hierarchy = [
                (self._sort_by_win_pct, "win_pct"),
                (self._sort_by_head_to_head, "h2h_wins"),
                (self._sort_by_points_for, "points_for"),
                (self._sort_by_division_record, "division_record"),
                (self._sort_by_points_against, "points_against"),
                (self._sort_by_coin_flip, "coin_flip"),
            ]
        else:
            raise ValueError(
                "Unkown tiebreaker_method: Must be either 'TOTAL_POINTS_SCORED' or 'H2H_RECORD'"
            )

        # First assign the division winners
        division_winners = pd.DataFrame()
        for division_id in standings_df.division_id.unique():
            division_standings = standings_df[(standings_df.division_id == division_id)]
            division_winner = self._sort_standings_df(
                division_standings, tiebreaker_hierarchy
            ).iloc[0]
            division_winners = pd.concat(
                [division_winners, division_winner.to_frame().T]
            )

        # Sort the division winners
        sorted_division_winners = self._sort_standings_df(
            division_winners, tiebreaker_hierarchy
        )

        # Then sort the rest of the teams
        rest_of_field = standings_df.loc[
            ~standings_df.index.isin(division_winners.index)
        ]
        sorted_rest_of_field = self._sort_standings_df(
            rest_of_field, tiebreaker_hierarchy
        )

        # Combine all teams
        sorted_standings = pd.concat(
            [sorted_division_winners, sorted_rest_of_field],
            axis=0,
        )

        return sorted_standings

    def top_scorer(self) -> Team:
        most_pf = sorted(self.teams, key=lambda x: x.points_for, reverse=True)
        return most_pf[0]

    def least_scorer(self) -> Team:
        least_pf = sorted(self.teams, key=lambda x: x.points_for, reverse=False)
        return least_pf[0]

    def most_points_against(self) -> Team:
        most_pa = sorted(self.teams, key=lambda x: x.points_against, reverse=True)
        return most_pa[0]

    def top_scored_week(self) -> Tuple[Team, int]:
        top_week_points = []
        for team in self.teams:
            top_week_points.append(max(team.scores[:self.current_week]))
        top_scored_tup = [(i, j) for (i, j) in zip(self.teams, top_week_points)]
        top_tup = sorted(top_scored_tup, key=lambda tup: int(tup[1]), reverse=True)
        return top_tup[0]

    def least_scored_week(self) -> Tuple[Team, int]:
        least_week_points = []
        for team in self.teams:
            least_week_points.append(min(team.scores[:self.current_week]))
        least_scored_tup = [(i, j) for (i, j) in zip(self.teams, least_week_points)]
        least_tup = sorted(least_scored_tup, key=lambda tup: int(tup[1]), reverse=False)
        return least_tup[0]

    def get_team_data(self, team_id: int) -> Team:
        for team in self.teams:
            if team_id == team.team_id:
                return team
        return None

    def recent_activity(self, size: int = 25, msg_type: str = None, offset: int = 0) -> List[Activity]:
        '''Returns a list of recent league activities (Add, Drop, Trade)'''
        if self.year < 2019:
            raise Exception('Cant use recent activity before 2019')

        msg_types = [178,180,179,239,181,244]
        if msg_type in ACTIVITY_MAP:
            msg_types = [ACTIVITY_MAP[msg_type]]
        params = {
            'view': 'kona_league_communication'
        }

        filters = {"topics":{"filterType":{"value":["ACTIVITY_TRANSACTIONS"]},"limit":size,"limitPerMessageSet":{"value":25},"offset":offset,"sortMessageDate":{"sortPriority":1,"sortAsc":False},"sortFor":{"sortPriority":2,"sortAsc":False},"filterIncludeMessageTypeIds":{"value":msg_types}}}
        headers = {'x-fantasy-filter': json.dumps(filters)}
        data = self.espn_request.league_get(extend='/communication/', params=params, headers=headers)
        data = data['topics']
        activity = [Activity(topic, self.player_map, self.get_team_data, self.player_info) for topic in data]

        return activity

    def scoreboard(self, week: int = None) -> List[Matchup]:
        '''Returns list of matchups for a given week'''
        if not week:
            week = self.current_week

        params = {
            'view': 'mMatchupScore',
        }
        data = self.espn_request.league_get(params=params)

        schedule = data['schedule']
        matchups = [Matchup(matchup) for matchup in schedule if matchup['matchupPeriodId'] == week]

        for team in self.teams:
            for matchup in matchups:
                if matchup._home_team_id == team.team_id:
                    matchup.home_team = team
                elif matchup._away_team_id == team.team_id:
                    matchup.away_team = team

        return matchups

    def box_scores(self, week: int = None) -> List[BoxScore]:
        '''Returns list of box score for a given week\n
        Should only be used with most recent season'''
        if self.year < 2019:
            raise Exception('Cant use box score before 2019')
        matchup_period = self.currentMatchupPeriod
        scoring_period = self.current_week
        if week and week <= self.current_week:
            scoring_period = week
            for matchup_id in self.settings.matchup_periods:
              if week in self.settings.matchup_periods[matchup_id]:
                matchup_period = matchup_id
                break

        params = {
            'view': ['mMatchupScore', 'mScoreboard'],
            'scoringPeriodId': scoring_period,
        }

        filters = {"schedule":{"filterMatchupPeriodIds":{"value":[matchup_period]}}}
        headers = {'x-fantasy-filter': json.dumps(filters)}
        data = self.espn_request.league_get(params=params, headers=headers)

        schedule = data['schedule']
        pro_schedule = self._get_pro_schedule(scoring_period)
        positional_rankings = self._get_positional_ratings(scoring_period)
        box_data = [BoxScore(matchup, pro_schedule, positional_rankings, scoring_period, self.year) for matchup in schedule]

        for team in self.teams:
            for matchup in box_data:
                if matchup.home_team == team.team_id:
                    matchup.home_team = team
                elif matchup.away_team == team.team_id:
                    matchup.away_team = team
        return box_data

    def power_rankings(self, week: int=None):
        '''Return power rankings for any week'''

        if not week or week <= 0 or week > self.current_week:
            week = self.current_week
        # calculate win for every week
        win_matrix = []
        teams_sorted = sorted(self.teams, key=lambda x: x.team_id,
                              reverse=False)

        for team in teams_sorted:
            wins = [0]*len(teams_sorted)
            for mov, opponent in zip(team.mov[:week], team.schedule[:week]):
                opp = teams_sorted.index(opponent)
                if mov > 0:
                    wins[opp] += 1
            win_matrix.append(wins)
        dominance_matrix = two_step_dominance(win_matrix)
        power_rank = power_points(dominance_matrix, teams_sorted, week)
        return power_rank

    def free_agents(self, week: int=None, size: int=50, position: str=None, position_id: int=None) -> List[Player]:
        '''Returns a List of Free Agents for a Given Week\n
        Should only be used with most recent season'''

        if self.year < 2019:
            raise Exception('Cant use free agents before 2019')
        if not week:
            week = self.current_week

        slot_filter = []
        if position and position in POSITION_MAP:
            slot_filter = [POSITION_MAP[position]]
        if position_id:
            slot_filter.append(position_id)


        params = {
            'view': 'kona_player_info',
            'scoringPeriodId': week,
        }
        filters = {"players":{"filterStatus":{"value":["FREEAGENT","WAIVERS"]},"filterSlotIds":{"value":slot_filter},"limit":size,"sortPercOwned":{"sortPriority":1,"sortAsc":False},"sortDraftRanks":{"sortPriority":100,"sortAsc":True,"value":"STANDARD"}}}
        headers = {'x-fantasy-filter': json.dumps(filters)}

        data = self.espn_request.league_get(params=params, headers=headers)

        players = data['players']
        pro_schedule = self._get_pro_schedule(week)
        positional_rankings = self._get_positional_ratings(week)

        return [BoxPlayer(player, pro_schedule, positional_rankings, week, self.year) for player in players]

    def player_info(self, name: str = None, playerId: Union[int, list] = None) -> Union[Player, List[Player]]:
        ''' Returns Player class if name found '''

        if name:
            playerId = self.player_map.get(name)
        if playerId is None or isinstance(playerId, str):
            return None
        if not isinstance(playerId, list):
            playerId = [playerId]

        data = self.espn_request.get_player_card(playerId, self.finalScoringPeriod)

        if len(data['players']) == 1:
            return Player(data['players'][0], self.year)
        if len(data['players']) > 1:
            return [Player(player, self.year) for player in data['players']]

    def message_board(self, msg_types: List[str] = None):
        ''' Returns a list of league messages'''
        data = self.espn_request.get_league_message_board(msg_types)

        msg_topics = list(data.get('topicsByType', {}).keys())
        messages = []
        for topic in msg_topics:
            msgs = data['topicsByType'][topic]
            for msg in msgs:
                messages.append(msg)
        return messages

    def _build_division_record_dict(self) -> Dict:
        """Create a DataFrame with each team's divisional record."""
        # Get the list of teams
        team_ids = [team.team_id for team in self.teams]

        # Create a dictionary with each team's divisional record
        div_outcomes = {
            team.team_id: {"wins": 0, "divisional_games": 0} for team in self.teams
        }

        # Loop through each team's schedule and outcomes and build the dictionary
        for team in self.teams:
            for opp, outcome in zip(team.schedule[:week], team.outcomes[:week]):
                if team.division_id == opp.division_id:
                    if outcome == "W":
                        div_outcomes[team.team_id]["wins"] += 1
                    if outcome == "T":
                        div_outcomes[team.team_id]["wins"] += 0.5

                    div_outcomes[team.team_id]["divisional_games"] += 1

        # Calculate the divisional record
        div_record = {
            team_id: (
                div_outcomes[team_id]["wins"]
                / max(div_outcomes[team_id]["divisional_games"], 1)
            )
            for team_id in team_ids
        }

        return div_record

    def _build_h2h_df(self) -> pd.DataFrame:
        """Create a dataframe that contains the head-to-head victories between each team in the league"""
        # Get the list of teams
        team_ids = [team.team_id for team in self.teams]

        # Initialize the DataFrame
        h2h_df = pd.DataFrame(index=team_ids, columns=team_ids).replace(np.nan, 0)

        # Loop through each team
        for team in self.teams:
            # Get the team's schedule
            schedule = team.schedule
            outcomes = team.outcomes

            # Loop through each week
            for week, opp in enumerate(schedule):
                # Update the DataFrame
                if outcomes[week] == "W":
                    h2h_df.loc[team.team_id, opp.team_id] += 1

                if outcomes[week] == "T":
                    h2h_df.loc[team.team_id, opp.team_id] += 0.5

        return h2h_df

    def _sort_by_win_pct(self, standings_df: pd.DataFrame) -> pd.DataFrame:
        """Take a DataFrame of standings and sort it using the TOTAL_POINTS_SCORED tiebreaker"""
        return standings_df.sort_values(by="win_pct", ascending=False)

    def _sort_by_points_for(self, standings_df: pd.DataFrame) -> pd.DataFrame:
        """Take a DataFrame of standings and sort it using the TOTAL_POINTS_SCORED tiebreaker"""
        return standings_df.sort_values(by="points_for", ascending=False)

    def _sort_by_division_record(self, standings_df: pd.DataFrame) -> pd.DataFrame:
        division_records = build_division_record_df(self)
        standings_df["division_record"] = standings_df.index.map(division_records)
        return standings_df.sort_values(by="division_record", ascending=False)

    def _sort_by_points_against(self, standings_df: pd.DataFrame) -> pd.DataFrame:
        """Take a DataFrame of standings and sort it using the 3rd level tiebreaker"""
        return standings_df.sort_values(by="points_against", ascending=True)

    def _sort_by_coin_flip(self, standings_df: pd.DataFrame) -> pd.DataFrame:
        standings_df["coin_flip"] = np.random.rand(len(standings_df))
        return standings_df.sort_values(by="coin_flip", ascending=False)

    def _sort_by_head_to_head(
        self,
        standings_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """Take a DataFrame of standings and sort it using the H2H_RECORD tiebreaker"""
        # If there is only one team, return the dataframe as-is
        if len(standings_df) == 1:
            return standings_df

        # Filter the H2H DataFrame to only include the teams in question
        team_ids = standings_df.index.tolist()
        h2h_df = self._build_h2h_df().loc[team_ids, team_ids]

        # If there are only two teams, sort descending by H2H wins
        if len(h2h_df) == 2:
            standings_df["h2h_wins"] = h2h_df.sum(axis=1)
            return standings_df.sort_values(by="h2h_wins", ascending=False)

        # If there are more than two teams...
        if len(h2h_df) > 2:
            # Check if the teams have all played each other an equal number of times
            matchup_combos = list(combinations(team_ids, 2))
            matchup_counts = [
                h2h_df.loc[t1, t2] + h2h_df.loc[t2, t1] for t1, t2 in matchup_combos
            ]
            if len(set(matchup_counts)) == 1:
                # All teams have played each other an equal number of times
                # Sort the teams by total H2H wins against each other
                standings_df["h2h_wins"] = h2h_df.sum(axis=1)
                return standings_df.sort_values(by="h2h_wins", ascending=False)
            else:
                # All teams have not played each other an equal number of times
                # This tiebreaker is invalid
                standings_df["h2h_wins"] = 0
                return standings_df

    def _sort_standings_df(
        self,
        standings_df: pd.DataFrame,
        tiebreaker_hierarchy: List[Tuple[Callable, str]],
    ) -> pd.DataFrame:
        """This recursive function sorts a standings DataFrame by the tiebreaker hierarchy.
        It iterates through each tiebreaker, sorting any remaning ties by the next tiebreaker.

        Args:
            standings_df (pd.DataFrame): Standings DataFrame to sort
            tiebreaker_hierarchy (List[Tuple[Callable, str]]): List of tiebreaker functions and columns to sort by

        Returns:
            pd.DataFrame: Sorted standings DataFrame
        """
        # If there are no more tiebreakers, return the standings DataFrame as-is
        if not tiebreaker_hierarchy:
            return standings_df

        # If there is only one team to sort, return the standings DataFrame as-is
        if len(standings_df) == 1:
            return standings_df

        # Get the tiebreaker function and column name to group by
        tiebreaker_function = tiebreaker_hierarchy[0][0]
        tiebreaker_col = tiebreaker_hierarchy[0][1]

        # Apply the tiebreaker function to the standings DataFrame
        standings_df = tiebreaker_function(standings_df)

        # Loop through each remaining unique tiebreaker value to see if ties remain
        sorted_standings = pd.DataFrame()
        for val in sorted(standings_df[tiebreaker_col].unique(), reverse=True):
            standings_subset = standings_df[standings_df[tiebreaker_col] == val]

            # Sort all remaining teams with the next tiebreaker
            sorted_subset = self._sort_standings_df(
                standings_subset,
                tiebreaker_hierarchy[1:],
            )

            # Append the sorted subset to the final sorted standings DataFrame
            sorted_standings = pd.concat(
                [
                    sorted_standings,
                    sorted_subset,
                ]
            )

        return sorted_standings
