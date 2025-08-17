def early_bounty_check(match_data: dict, hero_dict: dict, cutoff: int = 30) -> dict:
    """
    Detect players who picked up a bounty rune before <cutoff> seconds.
    Uses runes_log from players[].
    
    Returns a dict:
      {
        "all_same": True/False,
        "team": "Radiant"/"Dire"/None,
        "pickups": [ {hero, player_name, team, time}, ... ]
      }
    """
    players = match_data.get("players", [])
    early_bounties = []

    for player in players:
        runes_log = player.get("runes_log", [])
        hero_id = player.get("hero_id")
        hero_name = hero_dict.get(hero_id, f"Unknown ({hero_id})")
        player_slot = player.get("player_slot")
        team = "Radiant" if player_slot < 128 else "Dire"
        player_name = player.get("personaname", "Unknown Player")

        for rune in runes_log:
            if rune.get("key") == 5 and rune.get("time", 99999) < cutoff:
                early_bounties.append({
                    "hero": hero_name,
                    "player_name": player_name,
                    "team": team,
                    "time": rune["time"]
                })

    # Check if all early bounty runes belong to the same team
    if not early_bounties:
        return {"all_same": False, "team": None, "pickups": []}

    first_team = early_bounties[0]["team"]
    all_same = all(b["team"] == first_team for b in early_bounties)

    return {
        "all_same": all_same,
        "team": first_team if all_same else None,
        "pickups": early_bounties
    }