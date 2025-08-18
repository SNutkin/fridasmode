def aegis_denial_check(match_data: dict, hero_dict: dict) -> list[dict]:
    """
    Checks if any player denied the Aegis in the match.
    Returns a list of dictionaries with:
    - hero name
    - player name
    - team
    - time of Aegis loss
    - denied_by: "Self" or "Enemy"
    """
    denials = []

    for player in match_data.get("players", []):
        deaths_log = player.get("death_log", [])
        for death in deaths_log:
            if death.get("type") == "aegis":
                player_team = "Radiant" if player["player_slot"] < 128 else "Dire"

                # Determine if denied by self or enemy
                killer_slot = death.get("killer")  # player_slot of killer
                if killer_slot is None:
                    denied_by = "Self"
                else:
                    killer_team = "Radiant" if killer_slot < 128 else "Dire"
                    denied_by = "Enemy" if killer_team != player_team else "Self"

                denials.append({
                    "hero": hero_dict.get(player.get("hero_id"), f"Unknown Hero ({player.get('hero_id')})"),
                    "player": player.get("personaname", "Anonymous"),
                    "team": player_team,
                    "time": death.get("time", "Unknown"),
                    "denied_by": denied_by
                })

    return denials
