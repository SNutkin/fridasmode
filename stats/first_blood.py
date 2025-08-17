def get_first_blood(match_data: dict, hero_dict: dict) -> dict | None:
    """
    Find the first blood in the match using players' kill logs.
    Returns dict with hero name, player name, team, and time.
    """
    first_blood = None
    earliest_time = float("inf")

    for player in match_data.get("players", []):
        kills_log = player.get("kills_log", [])
        for kill in kills_log:
            time = kill.get("time")
            if time is not None and time < earliest_time:
                earliest_time = time
                first_blood = {
                    "hero": hero_dict.get(player.get("hero_id"), f"Unknown Hero ({player.get('hero_id')})"),
                    "player": player.get("personaname", "Anonymous"),
                    "team": "Radiant" if player["player_slot"] < 128 else "Dire",
                    "first_blood_time": time
                }

    return first_blood
