import streamlit as st
import json
import os
from team_manager import load_teams
from datetime import datetime

MATCHUPS_FILE = "matchups.json"

def load_matchups():
    if not os.path.exists(MATCHUPS_FILE):
        return []
    with open(MATCHUPS_FILE, "r") as f:
        return json.load(f)

def save_matchups(matchups):
    with open(MATCHUPS_FILE, "w") as f:
        json.dump(matchups, f, indent=4)

st.title("➕ Add or Edit a Matchup")

teams_data = load_teams()
team_names = [t["name"] for t in teams_data["teams"]]

if len(team_names) < 2:
    st.warning("At least two teams are required to create a matchup.")
    st.stop()

matchups = load_matchups()
matchup_labels = [f"{m['team1']} vs {m['team2']} ({m.get('date','?')} {m.get('time','')})" for m in matchups]

st.subheader("Select a matchup to edit or leave blank to add new")
selected_idx = st.selectbox(
    "Edit existing matchup", 
    options=[-1] + list(range(len(matchups))),
    format_func=lambda i: "Add new matchup" if i == -1 else matchup_labels[i]
)

if selected_idx == -1:
    # Add new matchup
    col1, col2 = st.columns(2)
    with col1:
        team1 = st.selectbox("Team 1", team_names, key="team1_new")
    with col2:
        team2 = st.selectbox("Team 2", [n for n in team_names if n != team1], key="team2_new")
    date = st.date_input("Match Date", key="date_new")
    time = st.time_input("Match Start Time", key="time_new")
    twitch_channel = st.text_input("Twitch Channel (just the channel name, e.g. dota2ti)", key="twitch_new")
    st.markdown("#### Odds (e.g. 2.5 means 2.5x payout for a win)")
    col3, col4 = st.columns(2)
    with col3:
        odds_team1 = st.number_input(f"Odds for {team1}", min_value=1.01, value=2.0, step=0.01, key="odds_team1_new")
    with col4:
        odds_team2 = st.number_input(f"Odds for {team2}", min_value=1.01, value=2.0, step=0.01, key="odds_team2_new")
    if st.button("Add Matchup"):
        if team1 == team2:
            st.error("Teams must be different.")
        elif not twitch_channel.strip():
            st.error("Please enter a Twitch channel.")
        else:
            # Generate a unique id
            next_id = max([m.get("id", 0) for m in matchups], default=0) + 1
            matchups.append({
                "id": next_id,
                "team1": team1,
                "team2": team2,
                "date": str(date),
                "time": str(time),
                "twitch_channel": twitch_channel.strip(),
                "odds_team1": odds_team1,
                "odds_team2": odds_team2
            })
            save_matchups(matchups)
            st.success(f"Matchup added: {team1} vs {team2} on {date} at {time} (twitch.tv/{twitch_channel.strip()})")
            st.rerun()
else:
    # Edit existing matchup
    matchup = matchups[selected_idx]
    col1, col2 = st.columns(2)
    with col1:
        team1 = st.selectbox("Team 1", team_names, index=team_names.index(matchup["team1"]), key="team1_edit")
    with col2:
        team2 = st.selectbox("Team 2", [n for n in team_names if n != team1], 
                             index=[n for n in team_names if n != team1].index(matchup["team2"]) if matchup["team2"] != team1 else 0, 
                             key="team2_edit")
    date = st.date_input("Match Date", value=datetime.strptime(matchup.get("date", str(datetime.today().date())), "%Y-%m-%d"), key="date_edit")
    # Handle time parsing
    try:
        default_time = datetime.strptime(matchup.get("time", "19:00:00"), "%H:%M:%S").time()
    except Exception:
        default_time = datetime.strptime("19:00:00", "%H:%M:%S").time()
    time = st.time_input("Match Start Time", value=default_time, key="time_edit")
    twitch_channel = st.text_input("Twitch Channel (just the channel name, e.g. dota2ti)", value=matchup.get("twitch_channel", ""), key="twitch_edit")
    st.markdown("#### Odds (e.g. 2.5 means 2.5x payout for a win)")
    col3, col4 = st.columns(2)
    with col3:
        odds_team1 = st.number_input(f"Odds for {team1}", min_value=1.01, value=float(matchup.get("odds_team1", 2.0)), step=0.1, key="odds_team1_edit")
    with col4:
        odds_team2 = st.number_input(f"Odds for {team2}", min_value=1.01, value=float(matchup.get("odds_team2", 2.0)), step=0.1, key="odds_team2_edit")
    colA, colB = st.columns([1,1])
    with colA:
        if st.button("Update Matchup"):
            if team1 == team2:
                st.error("Teams must be different.")
            elif not twitch_channel.strip():
                st.error("Please enter a Twitch channel.")
            else:
                matchup["team1"] = team1
                matchup["team2"] = team2
                matchup["date"] = str(date)
                matchup["time"] = str(time)
                matchup["twitch_channel"] = twitch_channel.strip()
                matchup["odds_team1"] = odds_team1
                matchup["odds_team2"] = odds_team2
                save_matchups(matchups)
                st.success(f"Matchup updated: {team1} vs {team2} on {date} at {time} (twitch.tv/{twitch_channel.strip()})")
                st.rerun()
    with colB:
        if st.button("Delete Matchup"):
            matchups.pop(selected_idx)
            save_matchups(matchups)
            st.warning("Matchup deleted.")
            st.rerun()

st.divider()
st.header("Current Matchups")
matchups = load_matchups()
if not matchups:
    st.info("No matchups yet.")
else:
    for idx, m in enumerate(matchups):
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(
                f"**{m['team1']} vs {m['team2']}**  \n"
                f"📅 {m.get('date','?')} ⏰ {m.get('time','?')}  \n"
                f"💸 Odds: {m.get('team1','?')}: {m.get('odds_team1','?')} | {m.get('team2','?')}: {m.get('odds_team2','?')}  \n"
                f"📺 [twitch.tv/{m.get('twitch_channel','')}]"
                f"(https://twitch.tv/{m.get('twitch_channel','')})"
            )
        with col2:
            if st.button("🗑️ Delete", key=f"delete_matchup_{idx}"):
                matchups.pop(idx)
                save_matchups(matchups)
                st.warning("Matchup deleted.")
                st.rerun()