import json
import os
from dota_api import get_match_data, get_hero_dict
from stats import (
    get_first_blood,
    team_same_attribute,
    fountain_death_check,
    early_bounty_check,
    aegis_denial_check,
    dagon_check,
    dust_check,
    load_hero_costs,
    team_cost_check,
)
from team_manager import load_teams, update_team_points
import streamlit as st

MATCHES_FILE = "matches.json"


def load_analyzed_matches():
    if not os.path.exists(MATCHES_FILE):
        return []
    with open(MATCHES_FILE, "r") as f:
        return json.load(f)


def save_analyzed_matches(matches):
    with open(MATCHES_FILE, "w") as f:
        json.dump(matches, f, indent=2)


ATTR_COLORS = {
    "str": "red",
    "agi": "green",
    "int": "blue",
    "all": "yellow",
    "unknown": "white",
}


def colored_attr(hero):
    color = ATTR_COLORS.get(hero["attribute"], "white")
    return f"<span style='color: {color};'>{hero['hero']} ({hero['attribute'].capitalize()}) - {hero['player_name']}</span>"


def main():
    st.image("fridasmode.png", use_container_width=True)
    # Load analyzed matches
    analyzed_matches = load_analyzed_matches()

    # Layout: two columns for input and recall
    col_input, col_dropdown = st.columns([2, 1])

    with col_input:
        # Step 1 - Match ID input
        match_id = st.text_input("Enter Dota 2 match ID:", key="match_id_input")
        btn_col1, btn_col2 = st.columns([1, 1])
        with btn_col1:
            analyze_clicked = st.button("Analyze")
        with btn_col2:
            clear_clicked = st.button("Clear")

    with col_dropdown:
        selected_match_id = st.selectbox(
            "Or select a previously analyzed match:",
            options=[""] + analyzed_matches[::-1],  # show most recent first
            key="match_id_select",
        )
        if selected_match_id and selected_match_id != st.session_state.get("match_id", ""):
            st.session_state.match_id = selected_match_id
            st.session_state.reset_trigger = False
            match_id = selected_match_id

    # Initialize session state for match_id if not already set
    if "match_id" not in st.session_state:
        st.session_state.match_id = ""

    if "reset_trigger" not in st.session_state:
        st.session_state.reset_trigger = False

    if analyze_clicked:
        if not match_id or not match_id.isdigit():
            st.error("❌ Invalid match ID. Must be a number.")
            return

        hero_dict, hero_info = get_hero_dict()
        match_data = get_match_data(int(match_id))
        hero_costs = load_hero_costs("hero_costs.json")

        # Save into session_state so Streamlit remembers
        st.session_state.match_id = match_id
        st.session_state.match_data = match_data
        st.session_state.hero_dict = hero_dict
        st.session_state.hero_info = hero_info
        st.session_state.hero_costs = hero_costs

        # Save match_id to matches.json if not already present
        if match_id not in analyzed_matches:
            analyzed_matches.append(match_id)
            save_analyzed_matches(analyzed_matches)

    if clear_clicked:
        st.session_state.match_id = ""
        st.session_state.reset_trigger = True

    if st.session_state.reset_trigger:
        st.session_state.reset_trigger = False
        return  # just return to stop processing current run

    # Step 2 - If match already loaded, display analysis
    if "match_data" in st.session_state and st.session_state.match_id:
        match_data = st.session_state.match_data
        hero_dict = st.session_state.hero_dict
        hero_info = st.session_state.hero_info
        hero_costs = st.session_state.hero_costs

        # Hero cost check
        st.subheader("💲 Team Cost Check:")
        team_costs = team_cost_check(match_data, hero_dict, hero_costs)

        st.success(f"Radiant total cost: {team_costs['Radiant_total']}")
        st.error(f"Dire total cost: {team_costs['Dire_total']}\n")

        st.subheader("🟢 Radiant Heroes:")
        for h in team_costs["Radiant_heroes"]:
            st.write(f"Radiant - {h['player']} picked {h['hero']} ({h['cost']} cost)")
        st.subheader("🔴 Dire Heroes:")
        for h in team_costs["Dire_heroes"]:
            st.write(f"Dire - {h['player']} picked {h['hero']} ({h['cost']} cost)")

        st.subheader("Most costly picks:")
        for team, hero in team_costs["most_costly_pick"].items():
            if hero:
                st.write(f"{team}: {hero['player']} picked {hero['hero']} ({hero['cost']} cost)")

        if team_costs["overinvested_team"]:
            st.write(f"Team that overinvested: {team_costs['overinvested_team']}")
        else:
            st.write("Both teams spent equally.")

        # First blood
        st.subheader("🩸 Instant First Blood:")
        fb = get_first_blood(match_data, hero_dict)
        if fb:
            st.success(f"🗡 First Blood at {fb['first_blood_time']}s")
            st.write(f"➡️  {fb['player']} ({fb['team']}) playing {fb['hero']}")
        else:
            st.error("❌ Could not determine who got first blood.")

        # All one attribute check
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
        st.subheader("💰 Bounty runes Challenge:")
        bounty_result = early_bounty_check(match_data, hero_dict)
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
                st.success(
                    f"{death['hero']} ({death['player']}) died to enemy fountain on {death['team']} at {death['time']}s"
                )
        else:
            st.warning("No heroes died to the enemy fountain within the first 20 minutes.")

        # Aegis denial check
        st.subheader("🛡️ Aegis Denial Challenge:")
        denials = aegis_denial_check(match_data, hero_dict)
        if denials:
            for d in denials:
                st.success(
                    f"{d['hero']} ({d['player']}) lost the Aegis on {d['team']} at {d['time']}s, denied by {d['denied_by']}"
                )
        else:
            st.warning("No Aegis was denied in this match.")

        # Dagon check
        st.subheader("🔮 Dagon Check:")
        dagon_teams = dagon_check(match_data, hero_dict)
        if dagon_teams:
            for t in dagon_teams:
                st.success(
                    f"All 5 heroes on {t['team']} had Dagon level {t['dagon_level']} at the same time at {t['time']}s:"
                )
                st.success(", ".join(t["heroes"]))
        else:
            st.warning("No team had all 5 heroes buy Dagon of the same level simultaneously.")

        # Dust check
        st.subheader("🧹 Dust Check:")
        dust_stats = dust_check(match_data, hero_dict)
        st.info(dust_stats["message"])

        # Tournament scoring section
        st.title("🏆 Tournament Match Analyzer")
        teams_data = load_teams()
        team_names = [t["name"] for t in teams_data["teams"]]

        radiant_team = st.selectbox("Select Radiant Team", team_names)
        dire_team_options = [t for t in team_names if t != radiant_team]
        dire_team = st.selectbox("Select Dire Team", dire_team_options)

        radiant_change = -team_costs["Radiant_total"]
        dire_change = -team_costs["Dire_total"]

        # Example: add 10 points if they got First Blood
        if fb:
            if fb["team"] == "Radiant":
                radiant_change += 10
                st.write(f"🟢 Radiant team got First Blood! +10 points")
            else:
                dire_change += 10
                st.write(f"🔴 Dire team got First Blood! +10 points")

        if not dust_stats["dust_used"]:
            st.success("✅ No team used Dust! Awarding 10 points to both teams.")
            radiant_change += 10
            dire_change += 10
        else:
            st.write("❌ Dust was used in this match. No points awarded.")

        st.write(f"Points change → {radiant_team}: {radiant_change}, {dire_team}: {dire_change}")

        # Calculate new totals
        radiant_current = next(t["points"] for t in teams_data["teams"] if t["name"] == radiant_team)
        dire_current = next(t["points"] for t in teams_data["teams"] if t["name"] == dire_team)

        radiant_new_total = radiant_current + radiant_change
        dire_new_total = dire_current + dire_change
        st.write(f"New totals → {radiant_team}: {radiant_new_total}, {dire_team}: {dire_new_total}")

        if st.button("✅ Confirm and Update Tournament Points"):
            update_team_points(radiant_team, radiant_change)
            update_team_points(dire_team, dire_change)
            st.success("Points updated successfully!")


if __name__ == "__main__":
    main()

