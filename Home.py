import streamlit as st
import pandas as pd
import requests
from config import init_page, render_navbar

# Initialize
init_page("🏠 NBA AI Dashboard")
render_navbar("Home")

st.title("🏀 NBA Live Projections Dashboard")
st.markdown("### Today's Games and Injury Updates")

# ---- Fetch Today's Games ----
def get_today_games():
    try:
        url = "https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json"
        r = requests.get(url)
        data = r.json()
        games = data.get("scoreboard", {}).get("games", [])
        return games
    except Exception as e:
        st.error(f"Error fetching games: {e}")
        return []

# ---- Fetch Injury Reports ----
def get_injuries():
    try:
        url = "https://cdn.nba.com/static/json/injury/injuryReport_00.json"
        r = requests.get(url)
        data = r.json()
        injuries = data.get("league", {}).get("standard", [])
        return injuries
    except Exception as e:
        st.error(f"Error fetching injuries: {e}")
        return []

games = get_today_games()
injuries = get_injuries()

if not games:
    st.warning("No NBA games scheduled for today.")
else:
    for game in games:
        home = game["homeTeam"]["teamTricode"]
        away = game["awayTeam"]["teamTricode"]
        start = game["gameTimeUTC"]

        with st.expander(f"{away} @ {home}"):
            st.write(f"**Start Time:** {start}")
            team_injuries = [i for i in injuries if i.get("teamTricode") in [home, away]]
            if team_injuries:
                st.write("### Injury Report")
                for i in team_injuries:
                    st.write(f"**{i['teamTricode']}** - {i['playerName']}: {i['injuryDesc']}")
            else:
                st.write("_No reported injuries impacting this game._")
