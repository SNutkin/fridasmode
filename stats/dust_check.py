# dust_check.py

def dust_check(match_data, hero_dict):
    """
    Checks how many times each team used Dust of Appearance in a match.

    Returns a dictionary with:
    - dust_used: True if any team used Dust, False otherwise
    - radiant_used: number of Dust uses by Radiant
    - dire_used: number of Dust uses by Dire
    - message: summary string
    """

    radiant_used = 0
    dire_used = 0

    # Loop through all players
    for player in match_data.get("players", []):
        purchase_log = player.get("purchase_log", [])
        for item in purchase_log:
            item_key = item.get("key", "").lower()
            if "dust" in item_key:
                # Player slot < 128 is Radiant, >= 128 is Dire
                if player["player_slot"] < 128:
                    radiant_used += 1
                else:
                    dire_used += 1

    dust_used = (radiant_used > 0 or dire_used > 0)
    message = f"Radiant used Dust {radiant_used} times, Dire used Dust {dire_used} times"

    return {
        "dust_used": dust_used,
        "radiant_used": radiant_used,
        "dire_used": dire_used,
        "message": message
    }
