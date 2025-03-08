from espn_api.baseball import League
from datetime import datetime, timedelta
import requests

SLACK_WEBHOOK_URL = 'https://hooks.slack.com/services/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'

def send_to_slack(message):
    payload = {"text": message}
    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    if response.status_code != 200:
        print(f"Error sending message to Slack: {response.status_code}, {response.text}")
    else:
        print("Message sent to Slack successfully.")

LEAGUE_ID = 502184563
YEAR = 2025
SWID = "{90904167-F4FA-4FA1-8C8E-F96ACD0BE80E}"
espn_s2 = "AECSBjRKuvn9t8hPjMuj7f0kfgiVl7WQNo6LI5NVRYqOYZzuP%2Bl%2FIEWkq4%2FXJezzIgd8hbvZuCVMFIC2TxPbMGq0KfeolAS5oFu3UWLAbN6elZdtCSP1efdkbcrLZ9cS3OYeCtRozXEcAK4P9mKDG7BGWezfZejechs68nTMncFchuPkOjpQ7FHw4%2FqlQmfI0xw5HhNY8e0%2BaGgeaWOTyzu6rs66XG%2FKvmWONJWe8Y4%2Bvp2GRObrq4LV4l0fphwP0qEwDs%2FDVJKVf0mtu5CMV5zp"

league = League(league_id=LEAGUE_ID, year=YEAR, espn_s2=espn_s2, swid=SWID)

allowed_positions = ["C", "1B", "2B", "3B", "SS", "OF", "DH", "SP", "RP"]

recent_activity = league.recent_activity(size=50)

current_time = datetime.now()

# Start with an empty message
slack_message = ""
activity_found = False  # Flag to check if anything was added

for activity in recent_activity:
    activity_time = datetime.fromtimestamp(activity.date / 1000)
    time_diff = current_time - activity_time

    if time_diff <= timedelta(days=1):
        activity_found = True  # Found at least one recent activity
        activity_time_str = activity_time.strftime("%b %d, %Y %I:%M %p")

        for action in activity.actions:
            team, action_type, player, bid_amount = (*action, None, None)[0:4]

            # Extract the actual team name from the team object
            clean_team = f"Team {team.team_name}"

            pro_team = getattr(player, 'proTeam', 'N/A')
            eligible_positions = [pos for pos in player.eligibleSlots if pos in allowed_positions]
            eligible_positions_str = ", ".join(eligible_positions) if eligible_positions else 'N/A'
            projected_points = getattr(player, 'stats', {}).get(0, {}).get('projected_points', 'N/A')
            total_points = getattr(player, 'total_points', 'N/A')

            if action_type == "WAIVER ADDED":
                message = (
                    f"Date/Time: {activity_time_str}: {clean_team} {action_type} {player.name} - "
                    f"Team: {pro_team} - POS: {eligible_positions_str} - "
                    f"Projected PTS: {projected_points} - 2025 PTS: {total_points} for ${bid_amount}"
                )
            else:
                message = (
                    f"Date/Time: {activity_time_str}: {clean_team} {action_type} {player.name} - "
                    f"Team: {pro_team} - POS: {eligible_positions_str} - "
                    f"Projected PTS: {projected_points} - 2025 PTS: {total_points}"
                )

            slack_message += message + "\n"



# Only send message if there was activity
if activity_found:
    full_message = "Recent activity (last 24 hours):\n" + slack_message
    send_to_slack(full_message)