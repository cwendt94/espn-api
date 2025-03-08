import csv
from espn_api.baseball import League

# Configurable settings
LEAGUE_ID = 115120
seasons = [2025]  # Added 2025 for projected points
FETCH_FREE_AGENTS = True  # Set to False if you only want team players

# Define the CSV filename
csv_filename = "player_eligible_slots.csv"

# Open the CSV file for writing
with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    positionsToKeep = ["C", "1B", "2B", "3B", "SS", "OF", "DH", "SP", "RP"]
    
    # Write the header row - add Projected Points column
    writer.writerow(["Player ID", "Player Name", "Player Team", "Season", "Player Eligible POS", "Total Points", "Projected Points", "Source"])

    for year in seasons:
        print(f"Fetching data for {year}...")

        try:
            league = League(league_id=LEAGUE_ID, year=year)

            # Fetch all teams (and their players)
            for team in league.teams:
                for player in team.roster:
                    writer.writerow([
                        player.playerId,
                        player.name,
                        player.proTeam,
                        year,
                        ", ".join(item for item in player.eligibleSlots if item in positionsToKeep),  # Convert list to a string for CSV output
                        player.total_points,
                        player.projected_total_points,
                        "Team"
                    ])

            if FETCH_FREE_AGENTS:
                free_agents = league.free_agents(size=5000)
                for player in free_agents:
                    writer.writerow([
                        player.playerId,
                        player.name,
                        player.proTeam,
                        year,
                        ", ".join(item for item in player.eligibleSlots if item in positionsToKeep),  # Convert list to a string for CSV output
                        player.total_points,
                        player.projected_total_points,
                        "Free Agent"
                    ])

        except Exception as e:
            print(f"Failed to fetch data for {year}: {e}")

print(f"CSV export completed: {csv_filename}")
