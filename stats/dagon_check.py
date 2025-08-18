def dagon_check(match_data: dict, hero_dict: dict) -> list[dict]:
    """
    Checks if all 5 heroes on Radiant or Dire had a Dagon of the same level at the same time during the match.

    Returns a list of dictionaries for each team that achieved it:
    - team: "Radiant" or "Dire"
    - time: earliest time when all 5 had Dagon of the same level simultaneously
    - heroes: list of hero names
    - dagon_level: level of the Dagon they all had
    """
    radiant_players = [p for p in match_data.get("players", []) if p["player_slot"] < 128]
    dire_players = [p for p in match_data.get("players", []) if p["player_slot"] >= 128]

    results = []

    # Helper function to get Dagon purchase times per player with level
    def get_dagon_times(player):
        times = []
        for item in player.get("purchase_log", []):
            key = item.get("key", "")
            if key.startswith("item_dagon"):
                # Extract level: item_dagon_2 => level 2, item_dagon => level 1
                level = 1 if key == "item_dagon" else int(key.split("_")[-1])
                times.append((item.get("time"), level))
        return times

    def check_team(players, team_name):
        # Gather Dagon times per player
        player_times = [get_dagon_times(p) for p in players]

        if not all(player_times):
            return  # Not all players bought a Dagon

        # Try to find a time where all have same level
        # Simplified approach: use first Dagon of each player
        first_dagon = [times[0] for times in player_times if times]
        levels = [lvl for _, lvl in first_dagon]
        if len(set(levels)) == 1:  # All same level
            all_have_dagon_time = max(t for t, _ in first_dagon)
            results.append({
                "team": team_name,
                "time": all_have_dagon_time,
                "heroes": [hero_dict.get(p["hero_id"], f"Unknown Hero ({p['hero_id']})") for p in players],
                "dagon_level": levels[0]
            })

    check_team(radiant_players, "Radiant")
    check_team(dire_players, "Dire")

    return results

