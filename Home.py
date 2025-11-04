import streamlit as st
import requests
from datetime import datetime
from config import init_page, render_navbar
from auto_status_updater import update_projection_status

# Initialize
init_page("🏠 NBA AI Dashboard")
render_navbar("Home")

st.title("🏀 NBA Live Projections Dashboard")
st.markdown("### Today's Games and Injury Updates")

try:
    update_projection_status()
except Exception as e:
    st.warning(f"Auto-sync skipped due to: {e}")

# ---- Fetch Today's Games ----
def get_today_games():
    try:
        url = "https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json"
        r = requests.get(url)
        data = r.json()
        return data.get("scoreboard", {}).get("games", [])
    except:
        return []

# ---- Fetch Injuries ----
def get_injuries():
    try:
        url = "https://cdn.nba.com/static/json/injury/injuryReport_00.json"
        r = requests.get(url)
        data = r.json()
        return data.get("league", {}).get("standard", [])
    except:
        return []

games = get_today_games()
injuries = get_injuries()

if not games:
    st.warning("No NBA games scheduled for today.")
else:
    for game in games:
        home = game["homeTeam"]["teamTricode"]
        away = game["awayTeam"]["teamTricode"]
        start_time = datetime.strptime(game["gameTimeUTC"], "%Y-%m-%dT%H:%M:%SZ").strftime("%I:%M %p")

        with st.expander(f"{away} @ {home} — {start_time}"):
            st.write(f"**Game ID:** {game['gameId']}")
            team_injuries = [i for i in injuries if i.get("teamTricode") in [home, away]]
            if team_injuries:
                st.markdown("### Injury Report")
                for i in team_injuries:
                    st.write(f"**{i['teamTricode']}** — {i['playerName']}: {i['injuryDesc']}")
            else:
                st.info("No injuries reported for this matchup.")
