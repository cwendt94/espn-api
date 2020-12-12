#%%
import sys
import os

script_path = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(script_path, "../.."))
sys.path.append(project_root)

import json
import pandas as pd
from espn_api.basketball.league import League
from espn_api.basketball.player import Player


def load_cookies() -> dict:
    cookies_path = os.path.join(project_root, "data", "espn_keys.json")
    with open(cookies_path, "r") as file_obj:
        cookies = json.load(file_obj)
    return cookies


def get_one_stats(one_player: Player, stats_season: str, stats_type: str) -> dict:
    """parse stats from one player

    :param one_player: one player object
    :type one_player: Player
    :param stats_season: can be "2020_stats" or "2020_projected"
    :type stats_season: str
    :param stats_type: can be "avg" or "total"
    :type stats_type: str
    :return: data with player info and required stats, if no valid data is presented, then only return player info
    :rtype: dict
    """
    player_info = dict(
        name=one_player.name, position=one_player.position, pro_team=one_player.proTeam
    )
    this_stats = one_player.stats
    season_lookup = {"2020_stats": "002020", "2021_projected": "102021"}
    season_key = season_lookup[stats_season]
    all_stats_from_season = this_stats.get(season_key, None)
    if all_stats_from_season is not None:
        stats_dict = all_stats_from_season.get(stats_type, None)
        results_dict = dict(player_info, **stats_dict)
    else:
        results_dict = player_info
    return results_dict


def get_all_stats(
    all_players: list, stats_season: str, stats_type: str
) -> pd.DataFrame:
    all_stats = [
        get_one_stats(one_player, stats_season=stats_season, stats_type=stats_type)
        for one_player in free_agents
    ]
    return pd.DataFrame(all_stats)


# %%


league_id = 189331
cookies = load_cookies()
my_league = League(
    league_id=league_id, year=2021, espn_s2=cookies["espn_s2"], swid=cookies["swid"]
)
free_agents = my_league.free_agents(size=1100)

data_dir = os.path.join(project_root, "data")
stats_2020 = get_all_stats(free_agents, stats_season="2020_stats", stats_type="avg")
stats_2020.to_csv(os.path.join(data_dir, "stats_2020.csv"), index=False)
projected_2021 = get_all_stats(
    free_agents, stats_season="2021_projected", stats_type="avg"
)
projected_2021.to_csv(os.path.join(data_dir, "projected_2021.csv"), index=False)

# %%
