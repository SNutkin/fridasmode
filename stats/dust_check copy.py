def dust_check(match_data: dict, hero_dict: dict) -> dict:
    """
    Checks how many times each team used Dust of Appearance during the match.

    Returns a dictionary:
    - 'Radiant': number of times Dust was used
    - 'Dire': number of times Dust was used
    - 'message': special message if neither team used Dust
    """
    radiant_count = 0
    dire_count = 0

    for player in match_data.get("players", []):
        purchases = player.get("purchase_log", [])
        dust_times = [item for item in purchases if item.get("key") == "item_dust"]
        if player["player_slot"] < 128:
            radiant_count += len(dust_times)
        else:
            dire_count += len(dust_times)

    result = {
        "Radiant": radiant_count,
        "Dire": dire_count
    }

    if radiant_count == 0 and dire_count == 0:
        result["message"] = "Wow! Neither team used Dust in this game! Points for ALL!"
    else:
        result["message"] = f"Dust usage - Radiant: {radiant_count}, Dire: {dire_count}"

    return result