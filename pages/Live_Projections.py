import streamlit as st
import pandas as pd
import requests
import datetime as dt
from PIL import Image
from io import BytesIO
import os

st.set_page_config(page_title="🟢 Live Projections", layout="wide")
st.markdown("<style>body{background-color:black;color:white;}</style>", unsafe_allow_html=True)
TEAM_COLOR = "#E50914"
CONTRAST = "#00FFFF"

# Auto-refresh every 30 seconds
st_autorefresh = st.experimental_rerun if False else None
st_autorefresh = st.empty()
st_autorefresh = st.empty()
st.markdown("### Refreshing every 30 seconds ⏱️")
st.experimental_rerun = None
st_autorefresh = st.empty()

st_autorefresh = st.empty()
st_autorefresh = st_autorefresh
st_autorefresh_interval = 30000

# ---------------------- HELPERS ----------------------
def get_team_logo(team_code):
    return f"https://cdn.nba.com/logos/nba/{team_code}_logo.svg"

def get_player_photo(pid):
    urls = [
        f"https://cdn.nba.com/headshots/nba/latest/1040x760/{pid}.png",
        f"https://stats.nba.com/media/players/headshot/{pid}.png"
    ]
    for url in urls:
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200 and "image" in r.headers.get("Content-Type", ""):
                return Image.open(BytesIO(r.content))
        except Exception:
            continue
    return None

def get_live_game_data(team_code):
    """Fetch live JSON data for a given team."""
    try:
        today = dt.datetime.now().strftime("%Y-%m-%d")
        url = f"https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_{today}.json"
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return None
        games = resp.json().get("scoreboard", {}).get("games", [])
        for game in games:
            home = game["homeTeam"]["teamTricode"]
            away = game["awayTeam"]["teamTricode"]
            if home == team_code or away == team_code:
                return {
                    "status": game["gameStatusText"],
                    "home": home,
                    "away": away,
                    "home_score": game["homeTeam"]["score"],
                    "away_score": game["awayTeam"]["score"],
                    "gameId": game["gameId"]
                }
        return None
    except Exception:
        return None

def get_player_live_stats(game_id, player_name):
    """Fetch individual player live stats"""
    try:
        url = f"https://cdn.nba.com/static/json/liveData/boxscore/boxscore_{game_id}.json"
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return None
        players = r.json()["game"]["players"]
        for p in players:
            if p["name"]["firstLast"] == player_name:
                stats = p["statistics"]
                return {
                    "PTS": stats.get("points", 0),
                    "REB": stats.get("reboundsTotal", 0),
                    "AST": stats.get("assists", 0),
                    "PRA": stats.get("points", 0) + stats.get("reboundsTotal", 0) + stats.get("assists", 0)
                }
        return None
    except Exception:
        return None

# ---------------------- LOAD DATA ----------------------
path = "saved_projections.csv"
if not os.path.exists(path):
    st.info("No live projections found.")
    st.stop()

data = pd.read_csv(path)
live = data[data["status"] == "live"].copy()

if live.empty:
    st.info("No games currently live.")
    st.stop()

st.title("🟢 Live Projections (Real-Time Updates)")
st.caption("Auto-refreshes every 30 seconds to update stats.")

for _, row in live.iterrows():
    player_name = row["player"]
    opponent = row.get("opponent", "TBD")
    home_away = row.get("home_away", "")
    team_code = opponent.split(" ")[-1] if isinstance(opponent, str) else ""
    game_info = get_live_game_data(team_code)

    if not game_info:
        continue

    game_id = game_info["gameId"]
    live_stats = get_player_live_stats(game_id, player_name)
    if not live_stats:
        continue

    # Check if game is completed
    if game_info["status"] == "Final":
        # update and promote
        for stat in ["PTS", "REB", "AST", "PRA"]:
            data.loc[data["player"] == player_name, f"actual_{stat}"] = live_stats[stat]
        data.loc[data["player"] == player_name, "status"] = "completed"
        data.to_csv(path, index=False)
        continue

    col1, col2 = st.columns([1, 3])
    with col1:
        pid = None
        try:
            from nba_api.stats.static import players
            pid = next((p["id"] for p in players.get_active_players() if p["full_name"] == player_name), None)
        except Exception:
            pass
        img = get_player_photo(pid) if pid else None
        if img:
            st.image(img, width=140)
        st.markdown(f"**{player_name}**")
        st.caption(f"🆚 {opponent}<br>{home_away}<br>🎯 {game_info['status']}", unsafe_allow_html=True)

    with col2:
        cols = st.columns(4)
        for i, stat in enumerate(["PTS", "REB", "AST", "PRA"]):
            proj_val = row.get(stat, 0)
            live_val = live_stats.get(stat, 0)
            delta = live_val - proj_val
            icon = "✅" if live_val >= proj_val else "❌"
            with cols[i % 4]:
                st.metric(f"{stat} {icon}", f"{live_val}", f"Proj: {proj_val} | Δ {delta}")
    st.markdown("---")

# ---------------------- SAVE UPDATES ----------------------
data.to_csv(path, index=False)
