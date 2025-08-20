import streamlit as st
import json
import os

MATCHUPS_FILE = "matchups.json"

def load_matchups():
    if not os.path.exists(MATCHUPS_FILE):
        return []
    with open(MATCHUPS_FILE, "r") as f:
        return json.load(f)

st.title("📅 Match Schedule")

matchups = load_matchups()

if not matchups:
    st.info("No matchups scheduled yet.")
else:
    # Sort by date and time
    def sort_key(m):
        return (m.get("date", ""), m.get("time", ""))
    matchups_sorted = sorted(matchups, key=sort_key)
    for m in matchups_sorted:
        st.markdown(
            f"""
            <div style="background-color:#f9f9f9; color:#111; padding: 1em; border-radius: 8px; border: 1px solid #eee; margin-bottom: 1em;">
                <h4 style="margin-bottom:0.2em;">{m['team1']} <b>vs</b> {m['team2']}</h4>
                <b>Date:</b> {m.get('date','?')} &nbsp;&nbsp; <b>Time:</b> {m.get('time','?')}<br>
                <b>Odds:</b> {m.get('team1','?')}: {m.get('odds_team1','?')} | {m.get('team2','?')}: {m.get('odds_team2','?')}<br>
                <b>Watch:</b> <a href="https://twitch.tv/{m.get('twitch_channel','')}" target="_blank">twitch.tv/{m.get('twitch_channel','')}</a>
            </div>
            """,
            unsafe_allow_html=True
        )