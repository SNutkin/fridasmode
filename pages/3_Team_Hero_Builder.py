import streamlit as st
import random
import json
import os
import requests
from team_manager import load_teams
from stats.team_cost_check import load_hero_costs

# --- Page Setup ---
st.set_page_config(page_title="Team Builder", page_icon="🛠️")

st.title("🛠️ Dota 2 Team Builder")
st.write("Pick your 5 heroes, select your team, and see how the cost reduces your score.")

# --- Load hero costs JSON ---
hero_costs = load_hero_costs()

# --- Load teams JSON ---
teams = load_teams()
team_names = [t["name"] for t in teams["teams"]]


# --- Load hero metadata from OpenDota ---
@st.cache_data
def load_hero_metadata():
    url = "https://api.opendota.com/api/heroes"
    response = requests.get(url)
    response.raise_for_status()
    heroes = response.json()
    # Map by localized_name for easy lookup
    return {h["localized_name"]: h for h in heroes}

hero_metadata = load_hero_metadata()
heroes = list(hero_costs.keys())

# --- Helper: format hero labels with color dots ---
def format_hero_label(hero_name):
    meta = hero_metadata.get(hero_name, {})
    attr = meta.get("primary_attr", "unknown")
    if attr == "str":
        return f"🟥 {hero_name}"
    elif attr == "agi":
        return f"🟩 {hero_name}"
    elif attr == "int":
        return f"🟦 {hero_name}"
    elif attr == "all":
        return f"⬜ {hero_name}"
    elif attr == "unknown":
        return f"🎲 {hero_name}"
    return hero_name

def strip_label(label):
    return label.replace("🟥 ", "").replace("🟩 ", "").replace("🟦 ", "").replace("⬜ ", "").replace("🎲 ", "")

# --- Select your team ---
st.subheader("Select Your Team")
selected_team_name = st.selectbox("Choose your team:", team_names)
# Find the selected team's points
selected_team_obj = next((t for t in teams["teams"] if t["name"] == selected_team_name), None)
current_team_points = selected_team_obj["points"] if selected_team_obj else 0

if "selected_heroes" not in st.session_state:
    st.session_state.selected_heroes = ["(None)"] * 5

def set_random_team():
    st.session_state.selected_heroes = random.sample(heroes, 5)



def set_random_team(attr=None):
    if attr:
        filtered_heroes = [h for h in heroes if hero_metadata.get(h, {}).get("primary_attr") == attr]
        if len(filtered_heroes) >= 5:
            st.session_state.selected_heroes = random.sample(filtered_heroes, 5)
        else:
            st.warning(f"Not enough {attr.capitalize()} heroes to fill a team!")
    else:
        st.session_state.selected_heroes = random.sample(heroes, 5)

st.subheader("Select Your 5 Heroes")

# Randomize entire team button
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button("🎲 Mystery Full Team"):
        set_random_team()
        st.success(f"Randomized team: {', '.join(st.session_state.selected_heroes)}")
with col2:
    if st.button("🟥 All Strength"):
        set_random_team("str")
        st.success(f"Mystery Strength team: {', '.join(st.session_state.selected_heroes)}")
with col3:
    if st.button("🟩 All Agility"):
        set_random_team("agi")
        st.success(f"Mystery Agility team: {', '.join(st.session_state.selected_heroes)}")
with col4:
    if st.button("🟦 All Intelligence"):
        set_random_team("int")
        st.success(f"Mystery Intelligence team: {', '.join(st.session_state.selected_heroes)}")
with col5:
    if st.button("⬜ All Universal"):
        set_random_team("all")
        st.success(f"Mystery Universal team: {', '.join(st.session_state.selected_heroes)}")


selected_heroes = []
for i in range(5):
    options = ["(None)"] + [format_hero_label(h) for h in heroes]
    # Set the default value from session_state
    default_hero = st.session_state.selected_heroes[i] if i < len(st.session_state.selected_heroes) else "(None)"
    # Convert hero name to label for default
    if default_hero != "(None)":
        default_label = format_hero_label(default_hero)
    else:
        default_label = "(None)"
    hero_label = st.selectbox(
        f"Hero {i+1}",
        options=options,
        index=options.index(default_label),
        key=f"hero_{i}"
    )
    hero = strip_label(hero_label)
    st.session_state.selected_heroes[i] = hero if hero != "(None)" else "(None)"
    if hero != "(None)":
        selected_heroes.append(hero)

# --- Calculate cost + extra info ---
if selected_heroes:
    final_team = []
    total_cost = 0

    for hero_name in selected_heroes:
        meta = hero_metadata.get(hero_name, {})
        attr = meta.get("primary_attr", "unknown").capitalize()
        roles = ", ".join(meta.get("roles", [])) or "No roles"
        hero_cost = hero_costs.get(hero_name, 0)

        final_team.append({
            "hero": hero_name,
            "attr": attr,
            "roles": roles,
            "cost": hero_cost
        })
        total_cost += hero_cost

    # --- Show Results ---
    st.subheader("💰 Team Breakdown")
    for h in final_team:
        st.markdown(
            f"- **{h['hero']}** ({h['attr']}, {h['roles']}) → **{h['cost']} points**"
        )

    st.success(f"**New Lineup Cost: {total_cost} points**")

# --- Team Totals ---
    st.subheader("📊 Team Points")
    st.info(f"{selected_team_name} starting points: {current_team_points}")
    remaining = current_team_points - total_cost
    if remaining < 0:
        st.error(f"⚠️ Not enough points! You’d be {-remaining} over budget.")
    else:
        st.success(f"{selected_team_name} remaining points after lineup: {remaining}")
else:
    st.info("Select heroes or randomize a team to see the cost.")

