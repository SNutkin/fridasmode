import requests

def get_hero_dict():
    """Fetch hero data from OpenDota and build id -> localized_name map."""
    url = "https://api.opendota.com/api/heroes"
    response = requests.get(url)
    response.raise_for_status()
    heroes = response.json()
    hero_dict = {hero["id"]: hero["localized_name"] for hero in heroes}
    hero_info = {hero["id"]: hero for hero in heroes}  # keep full info
    return hero_dict, hero_info

def get_match_data(match_id: int) -> dict:
    """Fetch full match data from OpenDota."""
    url = f"https://api.opendota.com/api/matches/{match_id}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
