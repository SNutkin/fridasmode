def fountain_death_check(match_data: dict, hero_dict: dict) -> list[dict]:
    """
    Checks if any heroes died to the enemy fountain within the first 20 minutes.
    
    Returns a list of dictionaries with:
    - hero name
    - player name
    - team
    - time of death
    """
    deaths = []

    for player in match_data.get("players", []):
        deaths_log = player.get("death_log", [])
        for death in deaths_log:
            time = death.get("time")
            # 20 minutes = 1200 seconds
            if time is not None and time <= 1200 and death.get("type") == "fountain":
                deaths.append({
                    "hero": hero_dict.get(player.get("hero_id"), f"Unknown Hero ({player.get('hero_id')})"),
                    "player": player.get("personaname", "Anonymous"),
                    "team": "Radiant" if player["player_slot"] < 128 else "Dire",
                    "time": time
                })

    return deaths