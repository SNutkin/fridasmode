import streamlit as st
from team_manager import load_teams
import pandas as pd

st.title("🏆 Tournament Team Scores")

# Load teams
teams_data = load_teams()
teams_list = teams_data["teams"]

# Convert to DataFrame
df = pd.DataFrame(teams_list)

# Sort by points descending
df_sorted = df.sort_values("points", ascending=False).reset_index(drop=True)

# Add emoji for top 3
def rank_emoji(index):
    if index == 0:
        return "🥇"
    elif index == 1:
        return "🥈"
    elif index == 2:
        return "🥉"
    else:
        return ""

df_sorted["Rank"] = [rank_emoji(i) for i in df_sorted.index]

# Display table with Rank, Team Name, Points
st.table(df_sorted[["Rank", "name", "points"]])