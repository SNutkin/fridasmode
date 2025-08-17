def get_first_blood(data: dict, hero_dict: dict) -> dict | None:
    """Find who got first blood in a match."""
    for player in data.get("players", []):
        if player.get("firstblood_claimed"):
            hero_id = player.get("hero_id")
            hero_name = hero_dict.get(hero_id, f"Unknown Hero ({hero_id})")
            player_slot = player.get("player_slot")
            name = player.get("personaname", "Anonymous")
            team = "Radiant" if player_slot < 128 else "Dire"

            return {
                "player": name,
                "hero": hero_name,
                "team": team,
                "first_blood_time": data.get("first_blood_time"),
            }
    return None

def team_same_attribute(data: dict, hero_dict: dict, heroes_info: dict) -> dict:
    """
    Check if all heroes on a team share the same primary attribute.
    Returns dict with info for Radiant and Dire, including hero names, attributes, and player names.
    """
    radiant = []
    dire = []

    for player in data.get("players", []):
        hero_id = player.get("hero_id")
        hero_name = hero_dict.get(hero_id, f"Unknown Hero ({hero_id})")
        hero_info = heroes_info.get(hero_id, {})
        attr = hero_info.get("primary_attr", "unknown")
        player_name = player.get("personaname", "Anonymous")

        entry = {"hero": hero_name, "attribute": attr, "player_name": player_name}
        if player["player_slot"] < 128:
            radiant.append(entry)
        else:
            dire.append(entry)

    def check(team_list):
        attrs = [h["attribute"] for h in team_list]
        all_same = len(set(attrs)) == 1 if attrs else False
        attr_type = attrs[0] if all_same else None
        return all_same, attr_type

    radiant_same, radiant_attr = check(radiant)
    dire_same, dire_attr = check(dire)

    return {
        "Radiant": {
            "all_same": radiant_same,
            "attribute": radiant_attr,
            "heroes": radiant,
        },
        "Dire": {
            "all_same": dire_same,
            "attribute": dire_attr,
            "heroes": dire,
        },
    }

