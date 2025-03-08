from espn_api.baseball import League
from datetime import datetime, timedelta

# League settings
LEAGUE_ID = 502184563  # Test League
YEAR = 2025
SWID = "{90904167-F4FA-4FA1-8C8E-F96ACD0BE80E}"
espn_s2 = "AECSBjRKuvn9t8hPjMuj7f0kfgiVl7WQNo6LI5NVRYqOYZzuP%2Bl%2FIEWkq4%2FXJezzIgd8hbvZuCVMFIC2TxPbMGq0KfeolAS5oFu3UWLAbN6elZdtCSP1efdkbcrLZ9cS3OYeCtRozXEcAK4P9mKDG7BGWezfZejechs68nTMncFchuPkOjpQ7FHw4%2FqlQmfI0xw5HhNY8e0%2BaGgeaWOTyzu6rs66XG%2FKvmWONJWe8Y4%2Bvp2GRObrq4LV4l0fphwP0qEwDs%2FDVJKVf0mtu5CMV5zp"

# Create league object
league = League(league_id=LEAGUE_ID, year=YEAR, espn_s2=espn_s2, swid=SWID)

# Define the allowed positions to display
allowed_positions = ["C", "1B", "2B", "3B", "SS", "OF", "DH", "SP", "RP"]

# Fetch recent activity (up to 50 transactions)
recent_activity = league.recent_activity(size=50)

# Get current time
current_time = datetime.now()

# Print all transactions
print("Recent activity:")

for activity in recent_activity:
    # Extract date and convert it to a datetime object
    activity_time = datetime.fromtimestamp(activity.date / 1000)  # Convert from milliseconds to seconds
    
    # Calculate the time difference between now and the activity time
    time_diff = current_time - activity_time
    
    # Format the datetime object into a readable format (e.g., "Mar 3, 2025 2:30 PM")
    activity_time_str = activity_time.strftime("%b %d, %Y %I:%M %p")
        
    # Each activity can have multiple actions (add/drop/move), so loop through those
    for action in activity.actions:
        team, action_type, player, bid_amount = action  # Unpack 4 values
        
        # Extract pro team using the correct attribute name
        pro_team = getattr(player, 'proTeam', 'N/A')  # Use 'proTeam' instead of 'pro_team'
        
        # Get eligible positions for the player and filter by allowed positions
        eligible_positions = [pos for pos in player.eligibleSlots if pos in allowed_positions]
        
        # Only display eligible positions if there are any
        eligible_positions_str = ", ".join(eligible_positions) if eligible_positions else 'N/A'
        
        # Get projected points and current points (total points)
        projected_points = getattr(player, 'stats', {}).get(0, {}).get('projected_points', 'N/A')
        total_points = getattr(player, 'total_points', 'N/A')
        
        # Print action details including player positions, projected points, current points, and timestamp
        if action_type == "WAIVER ADDED":
            print(f"Date/Time: {activity_time_str}: {team} {action_type} {player.name} - Team: {pro_team} - POS: {eligible_positions_str} - Projected PTS: {projected_points} - 2025 PTS: {total_points} for ${bid_amount}")
        else:
            print(f"Date/Time: {activity_time_str}: {team} {action_type} {player.name} - Team: {pro_team} - POS: {eligible_positions_str} - Projected PTS: {projected_points} - 2025 PTS: {total_points}")
