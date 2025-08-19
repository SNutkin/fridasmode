import json

TEAMS_FILE = "teams.json"

def load_teams():
    """Load teams from JSON file."""
    with open(TEAMS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_teams(teams_data):
    """Save teams back to JSON file."""
    with open(TEAMS_FILE, "w", encoding="utf-8") as f:
        json.dump(teams_data, f, indent=4)

def update_team_points(team_name: str, points_change: int):
    """Update points for a specific team."""
    teams_data = load_teams()
    for team in teams_data["teams"]:
        if team["name"] == team_name:
            team["points"] += points_change
            break
    save_teams(teams_data)