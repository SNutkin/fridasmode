import streamlit as st
import json
import os
from team_manager import load_teams, update_team_points
from dotenv import load_dotenv

# --- Simple password protection ---
load_dotenv() 
PASSWORD = os.environ.get("FRIDAS_ADMIN_PASSWORD", "")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    pwd = st.text_input("Enter admin password to add a team:", type="password")
    if st.button("Login"):
        if pwd == PASSWORD:
            st.session_state.authenticated = True
            st.success("Access granted!")
            st.rerun()
        else:
            st.error("Incorrect password.")
    st.stop()

# Load teams
teams_data = load_teams()

st.title("➕ Add a New Team")

# Team name input
team_name = st.text_input("Enter new team name:")

# Default starting points
starting_points = st.number_input("Starting points", min_value=0, value=7000, step=10)

st.subheader("Add Players")
mid_player = st.text_input("Mid Player")
carry_player = st.text_input("Carry Player")
offlane_player = st.text_input("Offlane Player")
soft_support_player = st.text_input("Soft Support Player")
hard_support_player = st.text_input("Hard Support Player")

coach = st.text_input("Coach")

if st.button("Add Team"):
    if not team_name.strip():
        st.error("❌ Team name cannot be empty.")
    elif any(t["name"].lower() == team_name.lower() for t in teams_data["teams"]):
        st.error("❌ Team already exists.")
    elif not all([mid_player, carry_player, offlane_player, soft_support_player, hard_support_player, coach]):
        st.error("❌ Please fill in all player and coach names.")
    else:
        # Add new team with players and coach
        teams_data["teams"].append({
            "name": team_name.strip(),
            "points": starting_points,
            "players": {
                "Mid": mid_player.strip(),
                "Carry": carry_player.strip(),
                "Offlane": offlane_player.strip(),
                "Soft Support": soft_support_player.strip(),
                "Hard Support": hard_support_player.strip()
            },
            "coach": coach.strip()
        })
        
        # Save JSON
        with open("teams.json", "w") as f:
            json.dump(teams_data, f, indent=4)
        
        st.success(f"✅ Team '{team_name}' added with {starting_points} points!")

        # Optional: show updated table
        st.subheader("Current Teams:")
        st.table([
            {
                "name": t["name"],
                "points": t["points"],
                "coach": t.get("coach", ""),
                "Mid": t.get("players", {}).get("Mid", ""),
                "Carry": t.get("players", {}).get("Carry", ""),
                "Offlane": t.get("players", {}).get("Offlane", ""),
                "Soft Support": t.get("players", {}).get("Soft Support", ""),
                "Hard Support": t.get("players", {}).get("Hard Support", "")
            }
            for t in teams_data["teams"]
        ])