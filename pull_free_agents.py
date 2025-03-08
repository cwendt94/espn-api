import csv
from espn_api.baseball import League
league = League(league_id=502184563, year=2025)
#espn_s2='AECSBjRKuvn9t8hPjMuj7f0kfgiVl7WQNo6LI5NVRYqOYZzuP%2Bl%2FIEWkq4%2FXJezzIgd8hbvZuCVMFIC2TxPbMGq0KfeolAS5oFu3UWLAbN6elZdtCSP1efdkbcrLZ9cS3OYeCtRozXEcAK4P9mKDG7BGWezfZejechs68nTMncFchuPkOjpQ7FHw4%2FqlQmfI0xw5HhNY8e0%2BaGgeaWOTyzu6rs66XG%2FKvmWONJWe8Y4%2Bvp2GRObrq4LV4l0fphwP0qEwDs%2FDVJKVf0mtu5CMV5zp', swid='90904167-F4FA-4FA1-8C8E-F96ACD0BE80E')

# Fetch all free agents (increase size to get all)
free_agents = league.free_agents(size=50)

# Define the CSV filename
csv_filename = "free_agents_pos.csv"
positionsToKeep = ["C", "1B", "2B", "3B", "SS", "OF", "DH", "SP", "RP"]

# Open the CSV file for writing
with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    # Write the header row
    writer.writerow(["Name", "Player ID", "Projected Points", "Eligible Pos"])
    # Write player data
    for player in free_agents:
        writer.writerow([
            player.name,
            player.playerId,
            player.projected_total_points,
            ", ".join(item for item in player.eligibleSlots if item in positionsToKeep)  # Convert list to a string for CSV output
        ])

print(f"CSV export completed: {csv_filename}")