import random
from typing import Callable, Dict, List, Tuple


def build_division_record_dict(team_data_list: List[Dict]) -> Dict:
    """Create a DataFrame with each team's divisional record."""
    # Create a dictionary with each team's divisional record
    div_outcomes = {
        team_data["team_id"]: {"wins": 0, "divisional_games": 0}
        for team_data in team_data_list
    }

    # Loop through each team's schedule and outcomes and build the dictionary
    for team_data in team_data_list:
        team = team_data["team"]
        for opp, outcome in zip(team_data["schedule"], team_data["outcomes"]):
            if team_data["division_id"] == opp.division_id:
                if outcome == "W":
                    div_outcomes[team_data["team_id"]]["wins"] += 1
                if outcome == "T":
                    div_outcomes[team_data["team_id"]]["wins"] += 0.5

                div_outcomes[team_data["team_id"]]["divisional_games"] += 1

    # Calculate the divisional record
    div_record = {
        team_data["team_id"]: (
            div_outcomes[team_data["team_id"]]["wins"]
            / max(div_outcomes[team_data["team_id"]]["divisional_games"], 1)
        )
        for team_data in team_data_list
    }

    return div_record


def build_h2h_dict(team_data_list: List[Dict]) -> Dict:
    """Create a dictionary with each team's divisional record."""
    # Create a dictionary with each team's head to head record
    h2h_outcomes = {
        team_data["team_id"]: {
            opp["team_id"]: {"h2h_wins": 0, "h2h_games": 0}
            for opp in team_data_list
            if opp["team_id"] != team_data["team_id"]
        }
        for team_data in team_data_list
    }

    # Loop through each team's schedule and outcomes and build the dictionary
    for team_data in team_data_list:
        team = team_data["team"]
        for opp, outcome in zip(team_data["schedule"], team_data["outcomes"]):
            # Ignore teams that are not part of this tiebreaker
            if opp.team_id not in h2h_outcomes[team.team_id].keys():
                continue

            # Add the outcome to the dictionary
            if outcome == "W":
                h2h_outcomes[team.team_id][opp.team_id]["h2h_wins"] += 1
            if outcome == "T":
                h2h_outcomes[team.team_id][opp.team_id]["h2h_wins"] += 0.5

            h2h_outcomes[team.team_id][opp.team_id]["h2h_games"] += 1

    # # Calculate the head to head record
    # for team_data in team_data_list:
    #     for opp_data in team_data_list:
    #         h2h_outcomes[team_data["team_id"]][opp_data["team_id"]]["h2h_record"] = (
    #             h2h_outcomes[team_data["team_id"]][opp_data["team_id"]]["h2h_wins"]
    #             / max(
    #                 h2h_outcomes[team_data["team_id"]][opp_data["team_id"]][
    #                     "h2h_games"
    #                 ],
    #                 1,
    #             )
    #         )

    return h2h_outcomes


def sort_by_win_pct(team_data_list: List[Dict]) -> List[Dict]:
    """Take a list of team standings data and sort it using the TOTAL_POINTS_SCORED tiebreaker"""
    return sorted(team_data_list, key=lambda x: x["win_pct"], reverse=True)


def sort_by_points_for(team_data_list: List[Dict]) -> List[Dict]:
    """Take a list of team standings data and sort it using the TOTAL_POINTS_SCORED tiebreaker"""
    return sorted(team_data_list, key=lambda x: x["points_for"], reverse=True)


def sort_by_division_record(team_data_list: List[Dict]) -> List[Dict]:
    """Take a list of team standings data and sort it using the 3rd level tiebreaker"""
    division_records = build_division_record_dict(team_data_list)
    for team_data in team_data_list:
        team_data["division_record"] = division_records[team_data["team_id"]]
    return sorted(team_data_list, key=lambda x: x["division_record"], reverse=True)


def sort_by_points_against(team_data_list: List[Dict]) -> List[Dict]:
    """Take a list of team standings data and sort it using the 4th level tiebreaker"""
    return sorted(team_data_list, key=lambda x: x["points_against"], reverse=True)


def sort_by_coin_flip(team_data_list: List[Dict]) -> List[Dict]:
    """Take a list of team standings data and sort it using the 5th level tiebreaker"""
    for team_data in team_data_list:
        team_data["coin_flip"] = random.random()
    return sorted(team_data_list, key=lambda x: x["coin_flip"], reverse=True)


def sort_by_head_to_head(
    team_data_list: List[Dict],
) -> List[Dict]:
    """Take a list of team standings data and sort it using the H2H_RECORD tiebreaker"""
    # Create a dictionary with each team's head to head record
    h2h_dict = build_h2h_dict(team_data_list)

    # If there is only one team, return the dataframe as-is
    if len(team_data_list) < 2:
        return team_data_list

    # If there are only two teams, sort descending by H2H wins
    elif len(h2h_dict) == 2:
        # Filter the H2H DataFrame to only include the teams in question
        h2h_dict = build_h2h_dict(team_data_list)

        # Sum the H2H wins against all tied opponents
        for team_data in team_data_list:
            team_data["h2h_wins"] = sum(
                h2h_dict[team_data["team_id"]][opp_id]["h2h_wins"]
                for opp_id in h2h_dict[team_data["team_id"]].keys()
            )
        return sorted(team_data_list, key=lambda x: x["h2h_wins"], reverse=True)

    # If there are more than two teams...
    else:
        # Filter the H2H DataFrame to only include the teams in question
        h2h_dict = build_h2h_dict(team_data_list)

        # Check if the teams have all played each other an equal number of times
        matchup_counts = [
            h2h_dict[team_id][opp_id]["h2h_games"]
            for team_id in h2h_dict.keys()
            for opp_id in h2h_dict[team_id].keys()
        ]
        if len(set(matchup_counts)) == 1:
            # All teams have played each other an equal number of times
            # Sort the teams by total H2H wins against each other
            for team_data in team_data_list:
                team_data["h2h_wins"] = sum(
                    h2h_dict[team_data["team_id"]][opp_id]["h2h_wins"]
                    for opp_id in h2h_dict[team_data["team_id"]].keys()
                )
            return sorted(team_data_list, key=lambda x: x["h2h_wins"], reverse=True)
        else:
            # All teams have not played each other an equal number of times
            # This tiebreaker is invalid
            for team_data in team_data_list:
                team_data["h2h_wins"] = 0
            return team_data_list


def sort_team_data_list(
    team_data_list: List[Dict],
    tiebreaker_hierarchy: List[Tuple[Callable, str]],
) -> List[Dict]:
    """This recursive function sorts a list of team standings data by the tiebreaker hierarchy.
    It iterates through each tiebreaker, sorting any remaning ties by the next tiebreaker.

    Args:
        team_data_list (List[Dict]): List of team data dictionaries
        tiebreaker_hierarchy (List[Tuple[Callable, str]]): List of tiebreaker functions and columns to sort by

    Returns:
        List[Dict]: Sorted list of team data dictionaries
    """
    # If there are no more tiebreakers, return the standings list as-is
    if not tiebreaker_hierarchy:
        return team_data_list

    # If there is only one team to sort, return the standings list as-is
    if len(team_data_list) == 1:
        return team_data_list

    # Get the tiebreaker function and column name to group by
    tiebreaker_function = tiebreaker_hierarchy[0][0]
    tiebreaker_col = tiebreaker_hierarchy[0][1]

    # Apply the tiebreaker function to the standings list
    team_data_list = tiebreaker_function(team_data_list)

    # Loop through each remaining unique tiebreaker value to see if ties remain
    sorted_team_data_list = []
    for val in sorted(
        set([team_data[tiebreaker_col] for team_data in team_data_list]),
        reverse=True,
    ):
        # Filter the standings list to only include the teams with the current tiebreaker value
        team_data_subset = [
            team_data
            for team_data in team_data_list
            if team_data[tiebreaker_col] == val
        ]

        # Append the sorted subset to the final sorted standings list
        sorted_team_data_list = sorted_team_data_list + sort_team_data_list(
            team_data_subset,
            tiebreaker_hierarchy[1:],
        )

    return sorted_team_data_list
