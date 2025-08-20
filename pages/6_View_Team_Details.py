import streamlit as st
from team_manager import load_teams

st.title("👀 View Team Details")

teams_data = load_teams()
team_names = [t["name"] for t in teams_data["teams"]]

if not team_names:
    st.warning("No teams available.")
else:
    col1, spacer, col2 = st.columns([2, 0.5, 3])
    with col1:
        selected_team_name = st.selectbox("Select a team:", team_names)
    with col2:
        team = next((t for t in teams_data["teams"] if t["name"] == selected_team_name), None)
        if team:
            st.markdown(
                f"""
                <div style="background-color:#ABABAB; color:#111; padding: 1.5em 1em 1em 1em; border-radius: 12px; border: 3px solid #eee;">
                    <h2 style="margin-bottom:0.5em; color:#111;">🏆 {team['name']}</h2>
                    <p><b>Points:</b> <span style="color:#27ae60;font-weight:bold;">{team['points']}</span></p>
                    <p><b>Coach:</b> {team.get('coach', 'N/A')}</p>
                    <hr>
                    <b>Players:</b>
                    <table style="width:100%;margin-top:.55em; color:#111;">
                        <tr><td>🥇 <b>Mid</b></td><td>{team.get('players', {}).get('Mid', 'N/A')}</td></tr>
                        <tr><td>🥈 <b>Carry</b></td><td>{team.get('players', {}).get('Carry', 'N/A')}</td></tr>
                        <tr><td>🥉 <b>Offlane</b></td><td>{team.get('players', {}).get('Offlane', 'N/A')}</td></tr>
                        <tr><td>🏅 <b>Soft Support</b></td><td>{team.get('players', {}).get('Soft Support', 'N/A')}</td></tr>
                        <tr><td>🎖 <b>Hard Support</b></td><td>{team.get('players', {}).get('Hard Support', 'N/A')}</td></tr>
                    </table>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.error("Team not found.")