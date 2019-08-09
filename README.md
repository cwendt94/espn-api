[![Build Status](https://travis-ci.org/cwendt94/ff-espn-api.svg?branch=master)](https://travis-ci.org/cwendt94/ff-espn-api) [![codecov](https://codecov.io/gh/cwendt94/ff-espn-api/branch/master/graphs/badge.svg)](https://codecov.io/gh/cwendt94/ff-espn-api) [![Join the chat at https://gitter.im/ff-espn-api/community](https://badges.gitter.im/ff-espn-api/community.svg)](https://gitter.im/ff-espn-api/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

# ff-espn-api

This package uses ESPN's Fantasy Football API to extract data from any public or private league. I am currently using this package for my leagues personal website and I plan to keep updating and adding features.

Please feel free to make suggestions, bug reports, and pull request for features or fixes!

This package was inspired and based off of [rbarton65/espnff](https://github.com/rbarton65/espnff).

## Installing
With Git:
```
git clone https://github.com/cwendt94/ff-espn-api
cd ff-espn-api
python3 setup.py install
```
With pip:
```
pip install ff_espn_api
```

## Usage
This will show you how to use `ff-espn-api` with private or public leagues

### Initial Start
Public League
```python
from ff_espn_api import League
league_id = 1234
year = 2018
league = League(league_id, year)
```
For private league you will need to get your swid and espn_s2.(Chrome Browser) You can find these two values after logging into
your espn fantasy football account on espn's website. Then right click anywhere on the website and click inspect
option. From there click Application on the top bar. On the left under Storage section click Cookies then http://fantasy.espn.com.
From there you should be able to find your swid and espn_s2 variables and values!
```python
from ff_espn_api import League
league_id = 1234
year = 2018
swid = '{03JFJHW-FWFWF-044G}'
espn_s2 = 'ASCWDWheghjwwqfwjqhgjkjgegkje'
league = League(league_id, year, espn_s2, swid)
```

### View teams information
```python
>>> from ff_espn_api import League
>>> league_id = 1234
>>> year = 2018
>>> league = League(league_id, year)
>>> league.teams
[Team(Team 1), Team(Team 2), Team(FANTASY GOD), Team(THE KING), Team(Team 5), Team(Team Viking Queen), Team(Team 7), Team(Team 8), Team(Team Mizrachi), Team(Team 10)]
>>> team = league.teams[0]
>>> team.roster
[Player(Travis Kelce), Player(Zach Ertz), Player(Josh Gordon), Player(Kenyan Drake), Player(Tarik Cohen), Player(Wil Lutz), Player(Dion Lewis), Player(Matthew Stafford), Player(Ezekiel Elliott), PLayer(Brandin Cooks), Player(Kerryon Johnson), Player(Mitchell Trubisky), Player(Bengals D/ST), Player(Courtland Sutton), Player(Spencer Ware), Player(Austin Ekeler)]
>>> team.wins
10
>>> team.losses
3
>>> team.final_standing
4
>>> team.team_name
'Team 1'
```
### View league draft
```python
>>> from ff_espn_api import League
>>> league_id = 1234
>>> year = 2018
>>> league = League(league_id, year)
>>> league.draft
[Pick(LeVeon Bell, Team(FANTASY GOD)), Pick(Todd Gurley II, Team(Team Mizrachi)), Pick(David Johnson, Team(Team 8)), Pick(Antonio Brown, Team(THE KING)), Pick(Ezekiel Elliott, Team(Team 7)), Pick(DeAndre Hopkins, Team(Team 2)), Pick(Julio Jones, Team(Team Viking Queen)), Pick(Alvin Kamara, Team(Team 10)), Pick(Odell Beckham Jr., Team(Team 5)), Pick(Kareem Hunt, Team(Team 1)), Pick(Michael Thomas, Team(Team 1))...]
>>> first_pick = league.draft[0]
>>> first_pick.playerName
"Le'Veon Bell"
>>> first_pick.round_num
1
>>> first_pick.round_pick
1
>>> first_pick.team
Team(FANTASY GOD)
>>>
```

### View league settings
```python
>>> from ff_espn_api import League
>>> league_id = 1234
>>> year = 2018
>>> league = League(league_id, year)
>>> settings = league.settings
>>> settings.reg_season_count
13
>>> settings.team_count
10
>>> settings.veto_votes_required
4
```
### Get scoreboard of current/specific week
```python
>>> from ff_espn_api import League
>>> league_id = 1234
>>> year = 2018
>>> league = League(league_id, year)
>>> league.scoreboard()
[Matchup(Team(Team 8), Team(THE KING)), Matchup(Team(Team 7), Team(Team 1)), Matchup(Team(Team 2), Team(Team Viking Queen)), Matchup(Team(Team Mizrachi), Team(FANTASY GOD)), Matchup(Team(Team 10), Team(Team 5))]
>>> week = 3
>>> matchups = league.scoreboard(week)
>>> matchups[0].home_score
89.2
>>> matchups[0].away_score
88.62
>>> matchups
[Matchup(Team(Team 1), Team(Team 10)), Matchup(Team(FANTASY GOD), Team(THE KING)), Matchup(Team(Team 7), Team(Team Viking Queen)), Matchup(Team(Team 5), Team(Team 2)), Matchup(Team(Team Mizrachi), Team(Team 8))]
>>> matchups[0].home_team
Team(Team 1)
>>> matchups[0].away_team
Team(Team 10)
```
### Get power rankings
```python
>>> from ff_espn_api import League
>>> league = League(1234, 2018)
>>> league.power_rankings(week=13)
[('70.85', Team(Team 7)), ('65.20', Team(Team 1)), ('62.45', Team(Team 8)), ('57.70', Team(THE KING)), ('45.10', Team(Team Mizrachi)), ('42.80', Team(Team 10)), ('40.65', Team(Team Viking Queen)), ('37.30', Team(Team 2)), ('27.85', Team(Team 5)), ('20.40', Team(FANTASY GOD))]
```

### Get box score of current/specific weel
```python
>>> from ff_espn_api import League
>>> league = League(1234, 2018)
>>> box_scores = league.box_scores(12)
>>> box_scores[0].home_team
Team(Team 1)
>>> box_scores[0].away_team
Team(Team Viking Queen)
>>> box_scores[0].home_score
69.24
>>> box_scores[0].away_score
87.62
>>> box_scores[0].home_lineup
[Player(Kareem Hunt, points:0, projected:0), Player(Travis Kelce, points:0, projected:0), Player(Zach Ertz, points:15, projected:9), Player(Josh Gordon, points:7, projected:8), Player(Kenyan Drake, points:21, projected:8), Player(Devin Funchess, points:0, projected:0), Player(Tarik Cohen, points:11, projected:8), Player(Wil Lutz, points:10, projected:7), Player(Dion Lewis, points:4, projected:9), Player(Matthew Stafford, points:5, projected:15), Player(Ezekiel Elliott, points:20, projected:17), Player(Brandin Cooks, points:0, projected:0), Player(Kerryon Johnson, points:0, projected:0), Player(Mitchell Trubisky, points:0, projected:0), Player(Bengals D/ST, points:6, projected:-3), Player(Courtland Sutton, points:7, projected:1)]
>>> box_scores[0].home_lineup[2].points
15.1
>>> box_scores[0].home_lineup[2].projected_points
9.97
>>> box_scores[0].home_lineup[2].slot_position
'TE'
>>> box_scores[0].home_lineup[2].position
'TE'
>>> box_scores[0].home_lineup[2].name
'Zach Ertz'
```

### Helper functions
```python
>>> from ff_espn_api import League
>>> league_id = 1234
>>> year = 2018
>>> league = League(league_id, year)
>>> league.load_roster_week(3)
>>> league.standings()
[Team(Team 8), Team(THE KING), Team(Team 7), Team(Team 1), Team(Team Viking Queen), Team(Team 2), Team(FANTASY GOD), Team(Team Mizrachi), Team(Team 10), Team(Team 5)]
>>> league.top_scorer()
Team(Team 8)
>>> league.least_scorer()
Team(FANTASY GOD)
>>> league.most_points_against()
Team(Team Mizrachi)
>>> league.top_scored_week()
(Team(Team Viking Queen), 219.74)
>>> league.least_scored_week()
(Team(Team 5), 41.48)
>>> league.get_team_data(1)
Team(Team 1)
```

### Run Tests
```
python3 setup.py nosetests
```