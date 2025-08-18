from dota_api import get_match_data, get_hero_dict
from stats import get_first_blood, team_same_attribute
from stats.early_bounty import early_bounty_check

ATTR_COLORS = {
    "str": "\033[91m",  # Red ANSI
    "agi": "\033[92m",  # Green
    "int": "\033[94m",  # Blue
    "unknown": "\033[107m"  # Default
}
RESET = "\033[0m"

def colored_attr(hero):
    color = ATTR_COLORS.get(hero["attribute"], RESET)
    return f"{color}{hero['hero']} ({hero['attribute'].capitalize()}) - {hero['player_name']}{RESET}" #make it pretty

if __name__ == "__main__":
    match_id = input("Enter Dota 2 match ID: ").strip()

    if not match_id.isdigit():
        print("❌ Invalid match ID. Must be a number.")
    else:
        hero_dict, hero_info = get_hero_dict()
        match_data = get_match_data(int(match_id))

        # First blood
        fb = get_first_blood(match_data, hero_dict)
        if fb:
            print(f"🩸 First Blood at {fb['first_blood_time']}s")
            print(f"➡️  {fb['player']} ({fb['team']}) playing {fb['hero']}")
        else:
            print("❌ Could not determine who got first blood.")

        # Team attribute check
        attrs = team_same_attribute(match_data, hero_dict, hero_info)
        for team, result in attrs.items():
            print(f"\n{team} lineup:")
            for hero in result["heroes"]:
                print("  -", colored_attr(hero))
            if result["all_same"]:
                print(f"✅ All heroes share the same attribute: {result['attribute'].capitalize()}")
            else:
                print(f"❌ Not all heroes share the same attribute.")


        bounty_result = early_bounty_check(match_data, hero_dict)

        print("\n💰 Bounty runes picked up before 30s:")
        if not bounty_result["pickups"]:
            print("  None")
        else:
            for b in bounty_result["pickups"]:
                minutes = int(b["time"] // 60)
                seconds = int(b["time"] % 60)
                print(f"  - {b['hero']} ({b['player_name']}, {b['team']}) at {minutes}m {seconds}s")

            if bounty_result["all_same"]:
                print(f"✅ All early bounty runes collected by {bounty_result['team']}. Securing 250 Points!")
            else:
                print("❌ Early bounty runes were split between teams. Noone gets any points!")