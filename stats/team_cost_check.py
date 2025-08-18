import json

def load_hero_costs(path="hero_costs.json") -> dict:
    """
    Loads hero cost mapping from a JSON file.
    JSON should be like: {"hero_name": 100, "anti-mage": 120, ...}
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def team_cost_check(match_data: dict, hero_dict: dict, hero_costs: dict) -> dict:
    """
    Calculates the total cost of heroes picked by each team.
    Randomed heroes get negative cost as penalty.

    Returns a dictionary:
    - 'Radiant_total', 'Dire_total': total cost per team
    - 'Radiant_heroes', 'Dire_heroes': list of heroes with player and cost
    - 'most_costly_pick': dict for each team showing the hero with highest cost
    - 'overinvested_team': team with higher total cost
    """
    radiant_total = 0
    dire_total = 0
    radiant_heroes = []
    dire_heroes = []

    for player in match_data.get("players", []):
        hero_id = player.get("hero_id")
        hero_name = hero_dict.get(hero_id, f"Unknown Hero ({hero_id})")
        cost = hero_costs.get(hero_name, 0)  # Default cost 0 if not in JSON

        if player.get("randomed", False):
            cost = -200  # 200 points Added to randomed heroes

        hero_info = {"hero": hero_name, "cost": cost, "player": player.get("personaname", "Anonymous")}

        if player["player_slot"] < 128:
            radiant_total += cost
            radiant_heroes.append(hero_info)
        else:
            dire_total += cost
            dire_heroes.append(hero_info)

    # Determine most costly pick per team
    def most_costly(heroes_list):
        if not heroes_list:
            return None
        return max(heroes_list, key=lambda h: h["cost"])

    most_costly_pick = {
        "Radiant": most_costly(radiant_heroes),
        "Dire": most_costly(dire_heroes)
    }

    # Determine overinvested team
    overinvested_team = None
    if radiant_total > dire_total:
        overinvested_team = "Radiant"
    elif dire_total > radiant_total:
        overinvested_team = "Dire"

    return {
        "Radiant_total": radiant_total,
        "Dire_total": dire_total,
        "Radiant_heroes": radiant_heroes,
        "Dire_heroes": dire_heroes,
        "most_costly_pick": most_costly_pick,
        "overinvested_team": overinvested_team
    }
