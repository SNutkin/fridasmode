import streamlit as st
import json
from team_manager import load_teams, update_team_points

# Load teams
teams_data = load_teams()

st.title("➕ Add a New Team")

# Team name input
team_name = st.text_input("Enter new team name:")

# Default starting points
starting_points = st.number_input("Starting points", min_value=0, value=0, step=1)

if st.button("Add Team"):
    if not team_name.strip():
        st.error("❌ Team name cannot be empty.")
    elif any(t["name"].lower() == team_name.lower() for t in teams_data["teams"]):
        st.error("❌ Team already exists.")
    else:
        # Add new team
        teams_data["teams"].append({"name": team_name.strip(), "points": starting_points})
        
        # Save JSON
        with open("teams.json", "w") as f:
            json.dump(teams_data, f, indent=4)
        
        st.success(f"✅ Team '{team_name}' added with {starting_points} points!")

        # Optional: show updated table
        st.subheader("Current Teams:")
        st.table(teams_data["teams"])