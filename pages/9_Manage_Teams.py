import streamlit as st
import json
import os

from team_manager import load_teams, update_team_points




st.title("🛠️ Manage Teams")

# Load current teams
teams_data = load_teams()
team_names = [t["name"] for t in teams_data["teams"]]

def show_teams_table():
    st.subheader("Current Teams")
    st.table(teams_data["teams"])
show_teams_table()
# --- Delete a Team ---
st.subheader("❌ Delete a Team")
team_to_delete = st.selectbox("Select a team to delete", [""] + team_names)

if st.button("Delete Team"):
    if team_to_delete:
        teams_data["teams"] = [t for t in teams_data["teams"] if t["name"] != team_to_delete]
        with open("teams.json", "w") as f:
            json.dump(teams_data, f, indent=4)
        st.success(f"Team '{team_to_delete}' has been deleted.")
        
    else:
        st.warning("Please select a team to delete.")

# --- Adjust Team Points ---
st.subheader("✏️ Adjust Team Points")
team_to_adjust = st.selectbox("Select a team to adjust points", [""] + team_names)
point_change = st.number_input("Points to add/subtract", value=0, step=1)

if st.button("Apply Points Change"):
    if team_to_adjust:
        # Update points
        for team in teams_data["teams"]:
            if team["name"] == team_to_adjust:
                team["points"] += point_change
                team["points"] = max(team["points"], 0)  # prevent negative total
                break
        with open("teams.json", "w") as f:
            json.dump(teams_data, f, indent=4)
        st.success(f"Team '{team_to_adjust}' new total points: {team['points']}")
    else:
        st.warning("Please select a team to adjust points.")
