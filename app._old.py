from dota_api import get_match_data, get_hero_dict
from stats import get_first_blood, team_same_attribute, fountain_death_check, early_bounty_check, aegis_denial_check, dagon_check, dust_check, load_hero_costs, team_cost_check
from team_manager import load_teams, update_team_points
import streamlit as st



ATTR_COLORS = {
    "str": "red",
    "agi": "green",
    "int": "blue",
    "all": "yellow",
    "unknown": "white"
}

def colored_attr(hero):
    color = ATTR_COLORS.get(hero["attribute"], "white")
    return f"<span style='color: {color};'>{hero['hero']} ({hero['attribute'].capitalize()}) - {hero['player_name']}</span>"

def main():


    st.image("fridasmode.png", use_container_width=True)
    
    match_id = st.text_input("Enter Dota 2 match ID:")
    
    if st.button("Analyze"):
        if not match_id.isdigit():
            st.error("❌ Invalid match ID. Must be a number.")
        else:
            hero_dict, hero_info = get_hero_dict()
            match_data = get_match_data(int(match_id))

            # Hero cost check
            st.subheader("💲 Team Cost Check:")
            hero_costs = load_hero_costs("hero_costs.json")
            team_costs = team_cost_check(match_data, hero_dict, hero_costs)

            st.success(f"Radiant total cost: {team_costs['Radiant_total']}")
            st.error(f"Dire total cost: {team_costs['Dire_total']}\n")
            st.subheader("Heroes picked by each team:") 
            st.subheader("🟢 Radiant Heroes:")
            for h in team_costs["Radiant_heroes"]:
                st.write(f"Radiant - {h['player']} picked {h['hero']} ({h['cost']} cost)")
            st.subheader("🔴 Dire Heroes:")
            for h in team_costs["Dire_heroes"]:
                st.write(f"Dire - {h['player']} picked {h['hero']} ({h['cost']} cost)")

            st.subheader("\nMost costly picks:")
            for team, hero in team_costs["most_costly_pick"].items():
                if hero:
                    st.write(f"{team}: {hero['player']} picked {hero['hero']} ({hero['cost']} cost)")

            if team_costs["overinvested_team"]:
                st.write(f"\nTeam that overinvested: {team_costs['overinvested_team']}")
            else:
                st.write("\nBoth teams spent equally.")

            # First blood
            st.subheader("🩸 Instant First Blood:")
            fb = get_first_blood(match_data, hero_dict)
            if fb:
                st.success(f"🗡 First Blood at {fb['first_blood_time']}s")
                st.write(f"➡️  {fb['player']} ({fb['team']}) playing {fb['hero']}")
            else:
                st.error("❌ Could not determine who got first blood.")

            # All one Attri check

            st.subheader("🌈 Pick a Colour Challenge:")
            attrs = team_same_attribute(match_data, hero_dict, hero_info)
            for team, result in attrs.items():
                st.subheader(f"{team} lineup:")
                for hero in result["heroes"]:
                    st.markdown("  - " + colored_attr(hero), unsafe_allow_html=True)
                if result["all_same"]:
                    st.success(f"✅ All heroes share the same attribute: {result['attribute'].capitalize()}")
                else:
                    st.warning("❌ Not all heroes share the same attribute.")

            # Early bounty check
            bounty_result = early_bounty_check(match_data, hero_dict)

            st.subheader("💰 Bounty runes Challenge:")
            if not bounty_result["pickups"]:
                st.write("  None")
            else:
                for b in bounty_result["pickups"]:
                    minutes = int(b["time"] // 60)
                    seconds = int(b["time"] % 60)
                    st.write(f"  - {b['hero']} ({b['player_name']}, {b['team']}) at {minutes}m {seconds}s")

                if bounty_result["all_same"]:
                    st.success(f"✅ All early bounty runes collected by {bounty_result['team']}. Securing 250 Points!")
                else:
                    st.warning("❌ Early bounty runes were split between teams. No one gets any points!")

            # Fountain death check
            st.subheader("🏰 Fountain Deaths Challenge:")
            fountain_deaths = fountain_death_check(match_data, hero_dict)
            if fountain_deaths:
                for death in fountain_deaths:
                    st.success(f"{death['hero']} ({death['player']}) died to enemy fountain on {death['team']} at {death['time']}s")
            else:
                st.warning("No heroes died to the enemy fountain within the first 20 minutes.")

            # Aegis denial check
            st.subheader("🛡️ Aegis Denial Challenge:")    
            denials = aegis_denial_check(match_data, hero_dict)

            if denials:
                for d in denials:
                    st.success(f"{d['hero']} ({d['player']}) lost the Aegis on {d['team']} at {d['time']}s, denied by {d['denied_by']}")
            else:
                st.warning("No Aegis was denied in this match.")
            # Dagon check
            st.subheader("🔮 Dagon Check:" )
            dagon_teams = dagon_check(match_data, hero_dict)

            if dagon_teams:
                for t in dagon_teams:
                    st.success(f"All 5 heroes on {t['team']} had Dagon level {t['dagon_level']} at the same time at {t['time']}s:")
                    st.success(", ".join(t["heroes"]))
            else:
                st.warning("No team had all 5 heroes buy Dagon of the same level simultaneously.")

            # Dust Check

            dust_stats = dust_check(match_data, hero_dict)
            st.subheader("🧹 Dust Check:")
            st.info(dust_stats["message"])


            st.title("🏆 Tournament Match Analyzer")

            # Load teams
            teams_data = load_teams()
            team_names = [t["name"] for t in teams_data["teams"]]

            # User selects match
            if match_id:
                #match_data = get_match_data(match_id)
                #hero_dict = get_hero_dict()
                #hero_costs = load_hero_costs("hero_costs.json")

                # Run analysis
                cost_stats = team_cost_check(match_data, hero_dict, hero_costs)

                # Display results
                st.subheader("Hero Cost Analysis")
                #st.json(cost_stats)

                # Dropdown to assign Radiant/Dire to tournament teams
                radiant_team = st.selectbox("Select Radiant Team", team_names)
                dire_team = st.selectbox("Select Dire Team", team_names)

                # Apply point changes based on results
                radiant_change = -cost_stats["Radiant_total"]  # deduct hero cost
                dire_change = -cost_stats["Dire_total"]

                # Example: add 10 points if they got First Blood
                fb = get_first_blood(match_data, hero_dict)
                if fb:
                    if fb["team"] == "Radiant":
                        radiant_change += 10
                        st.write(f"Radiant team got First Blood! +10 points")
                    else:
                        dire_change += 10
                        st.write(f"Dire team got First Blood! +10 points")  
                st.write(f"Points change → {radiant_team}: {radiant_change}, {dire_team}: {dire_change}")

                if st.button("✅ Confirm and Update Tournament Points"):
                    update_team_points(radiant_team, radiant_change)
                    update_team_points(dire_team, dire_change)
                    st.success("Points updated successfully!")


if __name__ == "__main__":
    main()