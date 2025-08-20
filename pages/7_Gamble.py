import streamlit as st
import json
import os
from team_manager import load_teams

BETS_FILE = "bets.json"
MATCHUPS_FILE = "matchups.json"

def save_teams(data):
    with open("teams.json", "w") as f:
        json.dump(data, f, indent=4)

def load_bets():
    if not os.path.exists(BETS_FILE):
        return []
    with open(BETS_FILE, "r") as f:
        return json.load(f)

def save_bets(bets):
    with open(BETS_FILE, "w") as f:
        json.dump(bets, f, indent=4)

def load_matchups():
    if not os.path.exists(MATCHUPS_FILE):
        return []
    with open(MATCHUPS_FILE, "r") as f:
        return json.load(f)

st.title("🎲 Team Gambling")

teams_data = load_teams()
team_names = [t["name"] for t in teams_data["teams"]]
matchups = load_matchups()

if len(team_names) < 2 or not matchups:
    st.warning("At least two teams and one matchup are required.")
    st.stop()

# --- Place a new bet ---
st.header("Place a New Bet")
col1, spacer, col2 = st.columns([2, 0.5, 3])

with col1:
    betting_team = st.selectbox("Team placing bet", team_names, key="betting_team")

with col2:
    matchup_options = [f"{m['team1']} vs {m['team2']}" for m in matchups]
    matchup_idx = st.selectbox("Select Matchup", range(len(matchup_options)), format_func=lambda i: matchup_options[i])
    selected_matchup = matchups[matchup_idx]
    team_to_win = st.radio("Which team will win?", [selected_matchup["team1"], selected_matchup["team2"]])
    points_gambled = st.number_input("Points gambled", min_value=1, step=10)
    submit = st.button("Log Bet")

    if submit:
        betting = next((t for t in teams_data["teams"] if t["name"] == betting_team), None)
        if not betting:
            st.error("Team not found.")
        elif points_gambled > betting["points"]:
            st.error(f"{betting_team} does not have enough points to gamble!")
        else:
            bets = load_bets()
            bets.append({
                "betting_team": betting_team,
                "matchup_id": selected_matchup["id"],
                "team_to_win": team_to_win,
                "points_gambled": points_gambled,
                "status": "pending"
            })
            save_bets(bets)
            st.success(f"Bet logged: {betting_team} bets {points_gambled} points on {team_to_win} to win {selected_matchup['team1']} vs {selected_matchup['team2']}.")

st.divider()

# --- Pending Bets ---
st.header("Pending Bets")
bets = load_bets()
pending_bets = [b for b in bets if b["status"] == "pending"]

if not pending_bets:
    st.info("No pending bets.")
else:
    for i, bet in enumerate(pending_bets):
        matchup = next((m for m in matchups if m["id"] == bet.get("matchup_id")), None)
        matchup_str = f"{matchup['team1']} vs {matchup['team2']}" if matchup else "Unknown Matchup"
        team_to_win = bet.get("team_to_win", "N/A")
        st.markdown(
            f"""
            <div style="background-color:#f9f9f9; color:#111; padding: 1em; border-radius: 8px; border: 1px solid #eee; margin-bottom: 1em;">
                <b>{bet['betting_team']}</b> bets <b>{bet['points_gambled']}</b> points on <b>{team_to_win}</b> to win <b>{matchup_str}</b>
            </div>
            """,
            unsafe_allow_html=True
        )
        colA, colB, colC = st.columns([1,1,1])
        with colA:
            if st.button(f"✅ Mark as Won (Double Points)", key=f"won_{i}"):
                betting = next((t for t in teams_data["teams"] if t["name"] == bet["betting_team"]), None)
                if betting:
                    betting["points"] += bet["points_gambled"]
                    save_teams(teams_data)
                bet["status"] = "won"
                save_bets(bets)
                st.success(f"{bet['betting_team']} won the bet and doubled their points gambled!")
                st.rerun()
        with colB:
            if st.button(f"❌ Mark as Lost (Lose Points)", key=f"lost_{i}"):
                betting = next((t for t in teams_data["teams"] if t["name"] == bet["betting_team"]), None)
                if betting:
                    betting["points"] -= bet["points_gambled"]
                    save_teams(teams_data)
                bet["status"] = "lost"
                save_bets(bets)
                st.error(f"{bet['betting_team']} lost the bet and lost their points gambled!")
                st.rerun()
        with colC:
            if st.button(f"🗑️ Delete Bet", key=f"delete_{i}"):
                bets.remove(bet)
                save_bets(bets)
                st.warning("Bet deleted.")
                st.rerun()

# --- Resolved Bets (optional) ---
with st.expander("Show Resolved Bets"):
    resolved_bets = [b for b in bets if b["status"] in ("won", "lost")]
    if not resolved_bets:
        st.write("No resolved bets yet.")
    else:
        for i, bet in enumerate(resolved_bets):
            matchup = next((m for m in matchups if m["id"] == bet.get("matchup_id")), None)
            matchup_str = f"{matchup['team1']} vs {matchup['team2']}" if matchup else "Unknown Matchup"
            outcome = "✅ Won" if bet["status"] == "won" else "❌ Lost"
            team_to_win = bet.get("team_to_win", "N/A")
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(
                    f"{bet['betting_team']} bet on {team_to_win} to win {matchup_str} — {bet['points_gambled']} points — {outcome}"
                )
            with col2:
                if st.button("🗑️ Delete", key=f"delete_resolved_{i}"):
                    bets.remove(bet)
                    save_bets(bets)
                    st.warning("Resolved bet deleted.")
                    st.rerun()