from abc import ABC, abstractmethod
from .box_player import BoxPlayer

from .constant import STATS_MAP

class BoxScore(ABC):
    ''' '''
    def __init__(self, data):
        self.winner = data['winner']
        
        self._process_team(data['home'], True)

        if 'away' in data:
            self._process_team(data['away'], False)
        else:
            self._process_team(None, False)

    @abstractmethod
    def _process_team(self, team_data, is_home_team):
        team = {}

        if team_data is not None:
            team['id'] = team_data['teamId']

        if is_home_team:
            self.home_team = team['id']
        else:
            self.away_team = team.get('id')
    
    def __repr__(self):
        away_team = self.away_team or "BYE"
        home_team = self.home_team or "BYE"
        return f'Box Score({away_team} at {home_team})'


class H2HCategoryBoxScore(BoxScore):
    '''Boxscore class for head to head categories leagues'''
    def __init__(self, data, pro_schedule, year, scoring_period = 0):
        super().__init__(data)

    def _process_team(self, team_data, is_home_team):
        super()._process_team(team_data, is_home_team)

        team = {}

        if team_data is not None:
            team['wins'] = team_data['cumulativeScore']['wins']
            team['losses'] = team_data['cumulativeScore']['losses']
            team['ties'] = team_data['cumulativeScore']['ties']

            team['stats'] = {}
            for stat_key, stat_dict in team_data['cumulativeScore']['scoreByStat'].items():
                team['stats'][STATS_MAP[int(stat_key)]] = {
                    'value': stat_dict['score'],
                    'result': stat_dict['result']
                }
        
        if is_home_team:
            self.home_wins = team['wins']
            self.home_losses = team['losses']
            self.home_ties = team['ties']
            self.home_stats = team['stats']
        else:
            self.away_wins = team.get('wins')
            self.away_losses = team.get('losses')
            self.away_ties = team.get('ties')
            self.away_stats = team.get('stats')


class H2HPointsBoxScore(BoxScore):
    '''Boxscore class for head to head points leagues'''
    def __init__(self, data, pro_schedule, year, scoring_period = 0):
        super().__init__(data)

        (self.home_team, self.home_score, self.home_projected, self.home_lineup) = self._get_team_data('home', data, pro_schedule, scoring_period, year)

        (self.away_team, self.away_score, self.away_projected, self.away_lineup) = self._get_team_data('away', data, pro_schedule, scoring_period, year)

    def _process_team(self, team_data, is_home_team):
        super()._process_team(team_data, is_home_team)
        # TODO implement setting the scores

    def _get_team_data(self, team, data, pro_schedule, week, year):
      if team not in data:
        return (0, 0, -1, [])  # -1 projected score indicates no projection available (bye week / missing)

      team_id = data[team]['teamId']
      team_projected = -1
      if 'totalPointsLive' in data[team]:
        team_score = round(data[team]['totalPointsLive'], 2)
        team_projected = round(data[team].get('totalProjectedPointsLive', -1), 2)
      else:
        team_score = round(data[team]['totalPoints'], 2)
      team_roster = data[team].get('rosterForCurrentScoringPeriod', {}).get('entries', [])
      team_lineup = [BoxPlayer(player, pro_schedule, week, year) for player in team_roster]

      return (team_id, team_score, team_projected, team_lineup)


class RotoBoxScore(BoxScore):
    '''Boxscore for rotisserie (ROTO) leagues.

    In roto there is no home/away matchup — all teams accumulate stats and are
    ranked against each other in each category.  One RotoBoxScore is returned
    per matchup period, containing every team's cumulative category stats and
    their league-wide rank in each category.

    Inherits from BoxScore so that isinstance(x, BoxScore) holds for all four
    baseball box-score shapes, but winner/home_team/away_team are always None
    since roto has no head-to-head matchup.

    Attributes:
        matchup_period (int): the matchup period this snapshot covers
        teams (list[dict]): one entry per team, each containing:
            - team       : team_id (int) initially; replaced with Team object
                           by League.box_scores()
            - total_points (float): cumulative roto points (sum of category ranks)
            - stats      : dict mapping stat name → {'score': float, 'rank': float}
            - lineup     : list[BoxPlayer] for the current scoring period
    '''
    def __init__(self, data, pro_schedule, year, scoring_period=0):
        # Skip BoxScore.__init__ — roto data has no winner/home/away keys.
        # Set the inherited attributes to None so callers can still access them.
        self.winner = None
        self.home_team = None
        self.away_team = None

        self.matchup_period = data.get('matchupPeriodId')
        self.teams = []

        for team_data in data.get('teams', []):
            team_id = team_data['teamId']
            live = team_data.get('totalPointsLive')
            total = round(live if live is not None else team_data.get('totalPoints', 0), 2)

            stats = {}
            for stat_id_str, stat_dict in team_data.get('cumulativeScore', {}).get('scoreByStat', {}).items():
                stat_name = STATS_MAP.get(int(stat_id_str), f'stat_{stat_id_str}')
                score = stat_dict['score']
                # ESPN sends the literal string 'Infinity' for rate stats (e.g. WHIP,
                # ERA) when the denominator is zero — coerce to float('inf') so
                # callers can do arithmetic/comparisons without type-switching.
                if score == 'Infinity':
                    score = float('inf')
                stats[stat_name] = {'score': score, 'rank': stat_dict['rank']}

            entries = team_data.get('rosterForCurrentScoringPeriod', {}).get('entries', [])
            lineup = [BoxPlayer(p, pro_schedule, scoring_period, year) for p in entries]

            self.teams.append({
                'team': team_id,
                'total_points': total,
                'stats': stats,
                'lineup': lineup,
            })

    def _process_team(self, team_data, is_home_team):
        # Roto has no home/away concept — this abstract method is required by
        # the BoxScore base class but is never called (RotoBoxScore overrides
        # __init__ entirely).
        pass

    def __repr__(self):
        return f'Roto Box Score(period:{self.matchup_period})'
